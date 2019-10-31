from Quirinius.DemoProvider import DemoProvider
from Quirinius.DifferentialPreprocessor import DifferentialPreprocessor
from Quirinius.FrameSaver import FrameSaver
from Quirinius.LivePreview import LivePreview
from Quirinius.PedestrianCounter import PedestrianCounter
from Quirinius.Receiver import Receiver

receiver = Receiver()
preprocessor = DifferentialPreprocessor()
visualizer = LivePreview()
saver = FrameSaver()

receiver.start()

while True:
    if receiver.is_dirty():
        frame = receiver.get_frame()
        processed = preprocessor.process_frame(frame)
        if processed is not None:
            visualizer.update(processed)
            saver.update(processed)
