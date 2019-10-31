const {app, dialog, BrowserWindow, Menu} = require('electron');
const fs = require('fs');

require('electron-reload')(__dirname, {
    // Note that the path to electron may vary according to the main file
    electron: require(`${__dirname}/node_modules/electron`)
});

module.exports.get_files = async function () {
    let filePaths = await dialog.showOpenDialog(win, {
        properties: ['openDirectory']
    });

    if (filePaths.filePaths.length !== 1) {
        return null;
    } else {
        let path = filePaths.filePaths[0];
        let dir = fs.readdirSync(path);
        let images = [];
        for (let i = 0; i < dir.length; i++) {
            if (dir[i].indexOf('png') !== -1) {
                images.push({
                    path: path + '/' + dir[i],
                    name: dir[i],
                    file: fs.readFileSync(path + '/' + dir[i])
                });
            }

        }
        return images;
    }
};

module.exports.write_files = async function (only_remove, only_move, destination) {
    for (let i = 0; i < only_remove.length; i++) {
        fs.unlinkSync(only_remove[i].path);
    }
    let uuid = create_UUID();
    for (let i = 0; i < only_move.length; i++) {
        let p = destination + '/' + only_move[i].label;
        if (!fs.existsSync(p)) {
            fs.mkdirSync(p);
        }
        p = p + '/' + uuid;
        if (!fs.existsSync(p)) {
            fs.mkdirSync(p);
        }
        fs.copyFileSync(only_move[i].path, p + '/' + only_move[i].name);
        fs.unlinkSync(only_move[i].path);
    }
};

function create_UUID(){
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

module.exports.get_destination = async function () {
    let filePaths = await dialog.showOpenDialog(win, {
        properties: ['openDirectory']
    });

    if (filePaths.filePaths.length !== 1) {
        return null;
    } else {
        return filePaths.filePaths[0];
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
            devTools: false
        }
    });

    if (process.platform === 'darwin') {
        const template = [
            {
                label: app.getName(),
                submenu: [{ role: 'about' }, { type: 'separator' }, { role: 'hide' }, { role: 'hideothers' }, { role: 'unhide' }, { type: 'separator' }, { role: 'quit' }]
            },
            {
                label: 'Edit',
                submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectall' }]
            },
            {
                label: 'View',
                submenu: [{ role: 'togglefullscreen' }]
            },
            {
                role: 'window',
                submenu: [{ role: 'minimize' }, { role: 'close' }]
            }
        ];

        Menu.setApplicationMenu(Menu.buildFromTemplate(template));
    } else {
        Menu.setApplicationMenu(null)
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
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    // Unter macOS ist es üblich ein neues Fenster der App zu erstellen, wenn
    // das Dock Icon angeklickt wird und keine anderen Fenster offen sind.
    if (win === null) {
        createWindow()
    }
})