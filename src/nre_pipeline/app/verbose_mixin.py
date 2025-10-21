from loguru import logger


class VerboseMixin:
    def __init__(self, verbose: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._verbose = verbose

    def _debug_log(self, message: str):
        if self._verbose:
            logger.debug(message)
