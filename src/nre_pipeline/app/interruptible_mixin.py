import threading
from time import sleep

from loguru import logger


class InterruptibleMixin:
    def __init__(self, *args, user_interrupt: threading.Event, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_interrupt: threading.Event = user_interrupt
        self._listen_for_interrupt()

    def user_interrupted(self) -> bool:
        return self._user_interrupt.is_set()

    def get_halt_processing_event(self) -> threading.Event:
        return self._user_interrupt

    def _listen_for_interrupt(self):
        """Start a thread to listen for Ctrl-C and set user interrupt."""

        def interrupt_handler():
            try:
                while not self.user_interrupted():
                    sleep(0.1)
            except KeyboardInterrupt:
                try:
                    logger.warning("User interrupt (Ctrl-C) detected. Stopping pipeline...")
                except Exception:
                    pass
                self._user_interrupt.set()
            except BrokenPipeError:
                # Handle process shutdown gracefully
                pass
            except Exception as e:
                try:
                    logger.error(f"Interrupt handler error: {e}")
                except Exception:
                    pass

        t = threading.Thread(target=interrupt_handler, daemon=True)
        t.start()
