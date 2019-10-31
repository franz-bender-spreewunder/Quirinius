const {app, dialog, BrowserWindow, Menu} = require('electron');
const fs = require('fs');
const pg = require('pg');
const connectionString = process.env.DATABASE_URL || 'postgresql://frbender:VAvPhNMcTZWZ@localhost:3333/irdb';

const { Pool } = require('pg');
const pool = new Pool();

const client = new pg.Client(connectionString);
client.connect();

require('electron-reload')(__dirname, {
    // Note that the path to electron may vary according to the main file
    electron: require(`${__dirname}/node_modules/electron`)
});

module.exports.requestFrame = function (index) {
    /**
     * Request via SQL
     */

    const text = 'SELECT ' +
        'd.id, d.capture, d.sensor, d.data ' +
        'FROM irdb.ir_data d ' +
        'INNER JOIN irdb.ir_unlabeled u ' +
        'ON u.id = d.id ' +
        'WHERE d.capture > \'2019-10-24 17:45:00\' ' +
        'ORDER BY capture ASC ' +
        'LIMIT 1 ' +
        'OFFSET $1';

    return new Promise((res, rej) => {
        client.query(text, [index]).then(res2 => {
            res(res2.rows[0])
        }).catch(e => console.error(e.stack));
    });
};

module.exports.error = function () {
    dialog.showErrorBox('Couldn\'t label sequence', 'Not all images are loaded. \nPlease wait a moment and try again.');
};

module.exports.write_files = async function (only_remove, only_move, destination) {
    /**
     * Move via SQL
     */

    let remove_params = [];
    for(let i = 1; i <= only_remove.length + only_move.length; i++) {
        remove_params.push('$' + i);
    }
    const text_remove = 'DELETE ' +
        'FROM irdb.ir_unlabeled ' +
        `WHERE id in (${remove_params.join(',')})`;

    let insert_params = [];
    for(let i = 1; i <= only_move.length*2; i += 2) {
        insert_params.push(`($${i}, $${i+1}, currval('ir_labeled_sequence_id_seq'))`);
    }
    const text_insert = 'INSERT ' +
        'INTO irdb.ir_labeled (photo_id, sequence_label, sequence_id) ' +
        `VALUES ${insert_params.join(',')}`;

    let id_list = only_remove.concat(only_move).map((e) => e.id);
    let id_list_move = only_move.map((e) => e.id);
    let label_list_move = only_move.map((e) => parseInt(e.label));

    let move_data = [];
    for (let i = 0; i < id_list_move.length; i++) {
        move_data.push(id_list_move[i]);
        move_data.push(label_list_move[i]);
    }

    try {
        await client.query('BEGIN');
        console.log(text_remove);
        console.log(id_list);
        console.log(text_insert);
        console.log(move_data);
        await client.query(`SELECT nextval('ir_labeled_sequence_id_seq')`);
        await client.query(text_remove, id_list);
        await client.query(text_insert, move_data);
        await client.query('COMMIT');
        console.log("Jo");
    } catch (e) {
        await client.query('ROLLBACK');
        console.log("Nö");
        throw e;
    }
};


// Behalten Sie eine globale Referenz auf das Fensterobjekt.
// Wenn Sie dies nicht tun, wird das Fenster automatisch geschlossen,
// sobald das Objekt dem JavaScript-Garbagekollektor übergeben wird.

let win

function createWindow() {
    // Erstellen des Browser-Fensters.
    win = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 1000,
        minHeight: 800,
        webPreferences: {
            nodeIntegration: true,
            devTools: true
        }
    });

    if (process.platform === 'darwin') {
        const template = [
            {
                label: app.getName(),
                submenu: [{role: 'about'}, {type: 'separator'}, {role: 'hide'}, {role: 'hideothers'}, {role: 'unhide'}, {type: 'separator'}, {role: 'quit'}]
            },
            {
                label: 'Edit',
                submenu: [{role: 'undo'}, {role: 'redo'}, {type: 'separator'}, {role: 'cut'}, {role: 'copy'}, {role: 'paste'}, {role: 'selectall'}]
            },
            {
                label: 'View',
                submenu: [{role: 'togglefullscreen'}]
            },
            {
                role: 'window',
                submenu: [{role: 'minimize'}, {role: 'close'}]
            }
        ];

        //Menu.setApplicationMenu(Menu.buildFromTemplate(template));
    } else {
        //Menu.setApplicationMenu(null)
    }


    // and load the index.html of the app.
    win.loadFile('index.html')

    // Öffnen der DevTools.
    //win.webContents.openDevTools()

    // Ausgegeben, wenn das Fenster geschlossen wird.
    win.on('closed', () => {
        // Dereferenzieren des Fensterobjekts, normalerweise würden Sie Fenster
        // in einem Array speichern, falls Ihre App mehrere Fenster unterstützt.
        // Das ist der Zeitpunkt, an dem Sie das zugehörige Element löschen sollten.
        win = null
    })
}


app.on('ready', createWindow)

// Verlassen, wenn alle Fenster geschlossen sind.
app.on('window-all-closed', () => {
    // Unter macOS ist es üblich, für Apps und ihre Menu Bar
    // aktiv zu bleiben, bis der Nutzer explizit mit Cmd + Q die App beendet.
    //if (process.platform !== 'darwin') {
    app.quit();
    client.end();
    //}
})

app.on('activate', () => {
    // Unter macOS ist es üblich ein neues Fenster der App zu erstellen, wenn
    // das Dock Icon angeklickt wird und keine anderen Fenster offen sind.
    if (win === null) {
        createWindow()
    }
})