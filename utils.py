import threading

class OneTimeTimer(threading.Timer):
    def __init__(self, interval, callback):
        super().__init__(interval, callback)
        self.is_triggered = False

    def run(self):
        if not self.is_triggered:
            super().run()
            self.is_triggered = True

class StoppableTimer:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.timer = None
        #self.stop_event = threading.Event()
        self.name = ''

    def start(self):
        self.timer = OneTimeTimer(self.interval, self.callback)
        self.timer.start()
        print(f'timer: {self.name} created and started')