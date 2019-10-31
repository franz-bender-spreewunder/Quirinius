from Quirinius.DemoProvider import DemoProvider
from Quirinius.DifferentialPreprocessor import DifferentialPreprocessor
from Quirinius.LivePreview import LivePreview
from Quirinius.PedestrianCounter import PedestrianCounter
from Quirinius.Receiver import Receiver

receiver = Receiver()
preprocessor = DifferentialPreprocessor()
visualizer = LivePreview()
counter = PedestrianCounter()

receiver.start()

demo = DemoProvider()

display_live = True

while True:
    processed = None
    new = False
    if display_live:
        if receiver.is_dirty():
            frame = receiver.get_frame()
            processed = preprocessor.process_frame(frame)
            new = True
        else:
            new = False
    else:
        processed = demo.get_frame()
        new = True

    if processed is not None and new:
        visualizer.update(processed)
        #counter.update(processed)
