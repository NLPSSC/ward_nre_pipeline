from threading import Thread


class ThreadLoopMixin:

    def __init__(self, target, *args, **kwargs) -> None:
        self.target = target
        self._thread = Thread(target=self.target, args=args, kwargs=kwargs)

    def start(self):
        self._thread.start()

    def join(self):
        self._thread.join()
