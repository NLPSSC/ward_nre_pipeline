import os
from loguru import logger


def _get_outqueue_max_docbatch_count():
    outqueue_max_docbatch_count = int(os.getenv("OUTQUEUE_MAX_DOCBATCH_COUNT", 1))
    logger.debug("OUTQUEUE_MAX_DOCBATCH_COUNT: {}", outqueue_max_docbatch_count)
    return outqueue_max_docbatch_count


def _get_inqueue_max_docbatch_count():
    inqueue_max_docbatch_count = int(os.getenv("INQUEUE_MAX_DOCBATCH_COUNT", 1))
    logger.debug("INQUEUE_MAX_DOCBATCH_COUNT: {}", inqueue_max_docbatch_count)
    return inqueue_max_docbatch_count


def _create_outqueue(manager):
    return manager.Queue(maxsize=_get_outqueue_max_docbatch_count())


def _create_inqueue(manager):
    return manager.Queue(maxsize=_get_inqueue_max_docbatch_count())
