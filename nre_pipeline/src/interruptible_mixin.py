import threading
from time import sleep

from loguru import logger


class InterruptibleMixin:
    def __init__(self, *args, user_interrupt: threading.Event | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_interrupt is None:
            user_interrupt = threading.Event()
        self._user_interrupt: threading.Event | None = user_interrupt
        self._listen_for_interrupt()

    def user_interrupted(self) -> bool:
        return self._user_interrupt is not None and self._user_interrupt.is_set()

    def _listen_for_interrupt(self):
        """Start a thread to listen for Ctrl-C and set user interrupt."""

        def interrupt_handler():
            try:
                while not self.user_interrupted():
                    sleep(0.1)
            except KeyboardInterrupt:
                logger.warning("User interrupt (Ctrl-C) detected. Stopping pipeline...")
                if self._user_interrupt is not None:
                    self._user_interrupt.set()

        t = threading.Thread(target=interrupt_handler, daemon=True)
        t.start()
