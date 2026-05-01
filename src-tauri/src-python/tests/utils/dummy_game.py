class DummyGame:
    def __init__(self):
        self.started = True
        self.stopped = False

    def start_battle(self, self_param=None):
        # We use 'self' as first param name to trigger the logic
        pass

    def stop_stream(self):
        self.stopped = True


class DummyMixin:
    def mixin_method(self):
        pass
