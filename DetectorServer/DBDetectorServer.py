from threading import Thread

from DetectorKit import Receiver, DifferentialPreprocessor
from DetectorServer.DBSaver import DBSaver


class Server:
    def __init__(self, host="0.0.0.0", port=35813, ids=[42]):
        self.receiver = Receiver(host=host, port=port)
        self.preprocessor = DifferentialPreprocessor()
        self.saver = DBSaver()

        self.provider_saver = [(self.receiver.get_frame_provider(sensor_id), self.saver.get_saver_for_id(sensor_id))
                               for sensor_id in ids]

        self.thread = EvaluationThread(self.provider_saver, self.preprocessor)

    def start(self):
        self.receiver.start()
        self.thread.start()

    def stop(self):
        self.receiver.stop()
        self.thread.stop()

    def do_stuff(self):
        pass


class EvaluationThread(Thread):

    def __init__(self, provider_saver, preprocessor):
        super().__init__()
        self.please_stop = False
        self.provider_saver = provider_saver
        self.preprocessor = preprocessor

    def stop(self):
        self.please_stop = True

    def run(self) -> None:
        while not self.please_stop:
            for saver in self.provider_saver:
                if saver[0].is_dirty():
                    frame = saver[0].get_frame()
                    processed = self.preprocessor.process_frame(frame)
                    if processed is not None:
                        saver[1].update(processed, frame.get_image())
