import os
from datetime import datetime
from threading import Thread
from typing import Optional, Callable, Any, Iterable, Mapping

from DetectorKit import Receiver, DifferentialPreprocessor
from DetectorKit.FrameSaver import FrameSaver


class Server:
    def __init__(self, host="0.0.0.0", port=35813, ids=[42]):
        self.receiver = Receiver(host=host, port=port)
        self.preprocessor = DifferentialPreprocessor()
        time_object = datetime.now()
        time_string = time_object.strftime("%Y-%b-%d (%H-%M-%S-%f)")

        for id in ids:
            directory = f'./data/{id}  -  {time_string}/'
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.provider_saver = [(self.receiver.get_frame_provider(id), FrameSaver(f'./data/{id}  -  {time_string}/', ''))
                               for id in ids]
        self.thread = EvaluationThread(self.provider_saver, self.preprocessor)

    def start(self):
        self.receiver.start()
        self.thread.start()

    def stop(self):
        self.receiver.stop()
        self.thread.stop()


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
            for provider in self.provider_saver:
                if provider[0].is_dirty():
                    frame = provider[0].get_frame()
                    processed = self.preprocessor.process_frame(frame)
                    if processed is not None:
                        provider[1].update(processed)
