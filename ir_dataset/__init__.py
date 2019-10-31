from datetime import datetime
from ir_dataset.VisualizationHelper import VisualizationHelper
import numpy as np
import psycopg2


class IRDataSet:
    def __init__(self):
        self.conn = psycopg2.connect("dbname=irdb user=frbender password=VAvPhNMcTZWZ host=localhost port=3333")
        self.cur = self.conn.cursor()

        self.select_range_sql = (
            'SELECT '
            'id, capture, sensor, data '
            'FROM '
            'irdb.ir_data '
            'WHERE '
            'sensor = %s '
            'AND '
            'capture >= %s '
            'AND '
            'capture < %s '
            'ORDER BY capture ASC;'
        )

        self.select_sequence_ids_sql = (
            'SELECT '
            'DISTINCT ON (t.sequence_id) '
            't.sequence_id, '
            't.sequence_label '
            'FROM irdb.ir_labeled t;'
        )

        self.select_sequence_label_occurrences_sql = (
            'SELECT l.sequence_label, count(*) '
            'FROM (SELECT DISTINCT ON (t.sequence_id) t.sequence_id, t.sequence_label FROM irdb.ir_labeled t) l '
            'GROUP BY l.sequence_label;'
        )

        self.select_sequences_for_label_sql = (
            'SELECT '
            'l.sequence_id, '
            'd.id, '
            'd.capture, '
            'd.sensor, '
            'd.data '
            'FROM irdb.ir_labeled l '
            'JOIN irdb.ir_data d ON l.photo_id = d.id '
            'WHERE l.sequence_label = %s '
            'ORDER BY l.sequence_id, d.capture ASC '
            'LIMIT %s'
        )

        self.select_sequence_by_id_sql = (
            'SELECT '
            'd.id, '
            'd.capture, '
            'd.sensor, '
            'd.data '
            'FROM irdb.ir_labeled l '
            'JOIN irdb.ir_data d ON l.photo_id = d.id '
            'WHERE l.sequence_id = %s '
            'ORDER BY l.sequence_id, d.capture ASC '
            'LIMIT 100'
        )

        self.select_raw_range_sql = (
            'SELECT '
            'd.id, d.capture, d.sensor, d.data, dd.data '
            'FROM irdb.ir_data d '
            'JOIN irdb.ir_data_original dd '
            'ON d.id = dd.for_id '
            'WHERE '
            'd.sensor = %s '
            'AND '
            'd.capture >= %s '
            'AND '
            'd.capture < %s '
            'ORDER BY d.capture ASC;'
        )

    @staticmethod
    def data_to_photo(data, dtype='uint8'):
        image = np.frombuffer(data, dtype=dtype)
        image = image.reshape((24, 32))
        return image

    def get_unlabeled_in_range(self,
                               start=datetime.strptime('2019-09-23 11:00:00', '%Y-%m-%d %H:%M:%S'),
                               end=datetime.strptime('2019-09-23 11:01:00', '%Y-%m-%d %H:%M:%S'),
                               sensor=42):
        self.cur.execute(self.select_range_sql, (sensor, start, end))
        for (image_id, capture, sensor, data) in self.cur:
            image = IRDataSet.data_to_photo(data)
            yield (image_id, capture, sensor, image)

    def get_sequence_ids(self):
        self.cur.execute(self.select_sequence_ids_sql, ())
        for (sequence_id, sequence_label) in self.cur:
            yield (sequence_id, sequence_label)

    def get_sequence_label_occurrences(self):
        self.cur.execute(self.select_sequence_label_occurrences_sql)
        for (sequence_label, count) in self.cur:
            yield (sequence_label, count)

    def get_sequences_for_label(self, label=0, limit=10):
        self.cur.execute(self.select_sequences_for_label_sql, (label, limit * 100))
        current_sequence = []
        for (sequence_id, photo_id, capture, sensor, data) in self.cur:
            image = IRDataSet.data_to_photo(data)
            current_sequence.append((sequence_id, photo_id, capture, sensor, image))
            if len(current_sequence) >= 100:
                yield list(current_sequence)
                current_sequence.clear()

    def get_sequence_by_id(self, sequence_id):
        self.cur.execute(self.select_sequence_by_id_sql, (sequence_id,))
        current_sequence = []
        for (photo_id, capture, sensor, data) in self.cur:
            image = IRDataSet.data_to_photo(data)
            current_sequence.append((photo_id, capture, sensor, image))
        return current_sequence

    def get_raw_sequences_in_range(self,
                                   start=datetime.strptime('2019-10-24 17:00:00', '%Y-%m-%d %H:%M:%S'),
                                   end=datetime.strptime('2019-10-24 17:05:00', '%Y-%m-%d %H:%M:%S'),
                                   sensor=42):
        """
        Get the raw, unannotated data for a sensor in a certain time range

        :returns: generator outputting tuples in the form of (image id, capture date, sensor id, processed image, raw image)

        :Example:

        >>> data_set = IRDataSet()
        >>> sequences = data_set.get_raw_sequences_in_range()
        >>> for (image_id, capture, sensor, image, original_image) in sequences:
        >>>     imshow(image)
        """
        self.cur.execute(self.select_raw_range_sql, (sensor, start, end))
        current_sequence = []
        for (image_id, capture, sensor, data, original_data) in self.cur:
            image = IRDataSet.data_to_photo(data)
            original_image = IRDataSet.data_to_photo(original_data, dtype='float32')
            current_sequence.append((image_id, capture, sensor, image, original_image))
            if len(current_sequence) >= 100:
                yield list(current_sequence)
                current_sequence.clear()

    def close(self):
        self.conn.close()
