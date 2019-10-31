import psycopg2
import os
from cv2 import cv2
import time
from datetime import datetime

from psycopg2.extras import execute_values

conn = psycopg2.connect("dbname=irdb user=irserver password=zKwvQFNCWiQs host=localhost")
cur = conn.cursor()

path = "/home/ircounter/Detector/data/42  -  2019-Sep-20 (20-23-22-688270)"

print('Loading files...')

only_files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

print(f'total files: {str(len(only_files))}')

total = len(only_files)

time_last = time.time()
speed = 0

buffered = []

for i, f in enumerate(only_files):
    t = os.path.getmtime(f)
    image = cv2.imread(
        f,
        cv2.IMREAD_GRAYSCALE
    )

    bs = image.tobytes()
    new_t = datetime.fromtimestamp(t)

    buffered.append((new_t, 42, bs))

    if i % 100 == 0:
        execute_values(cur, "INSERT INTO irdb.ir_data (capture, sensor, data) VALUES %s", buffered)
        buffered = []
        conn.commit()
        progress = i * 100 / total
        time_diff = time.time() - time_last
        speed = 0.95 * speed + 0.05 * (50.0/time_diff)
        remaining = total - i
        time_remaining = remaining / speed
        print(f'done: {progress}\ntime remaining: {time_remaining}')

conn.commit()
cur.close()
conn.close()


