import datetime

import numpy as np
from psycopg2.pool import ThreadedConnectionPool


class DBSingleSensorSaver:
    def __init__(self, sensor_id, owner):
        self.owner = owner
        self.id = sensor_id

    def update(self, processed, original):
        con = self.owner.pool.getconn()
        cur = con.cursor()

        t = datetime.datetime.now()
        s = self.id

        processed = np.clip(processed * 255.0, 0, 255)
        data = processed.astype('uint8').tobytes()

        cur.execute("INSERT INTO irdb.ir_data (capture, sensor, data) VALUES (%s,%s,%s) RETURNING ID", (t, s, data))
        returned_id = cur.fetchone()[0]

        cur.execute("INSERT INTO irdb.ir_data_original (for_id, data) VALUES (%s,%s)", (returned_id, original.tobytes()))
        con.commit()
        self.owner.pool.putconn(con)


class DBSaver:
    def __init__(self):
        self.pool = ThreadedConnectionPool(minconn=1,
                                           maxconn=5,
                                           user="irserver",
                                           password="zKwvQFNCWiQs",
                                           host="localhost",
                                           port="5432",
                                           database="irdb")

    def get_saver_for_id(self, sensor_id):
        return DBSingleSensorSaver(sensor_id, self)

    def close(self):
        self.pool.closeall()
