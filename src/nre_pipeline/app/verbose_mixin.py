from loguru import logger


class VerboseMixin:
    def __init__(self, verbose: bool = False, *args, **kwargs):
        logger.debug(
            "Initializing VerboseMixin, called by {}", self.__class__.__name__
        )
        super().__init__(*args, **kwargs)
        self._verbose = verbose

    def _debug_log(self, message: str):
        if self._verbose:
            logger.debug(message)
