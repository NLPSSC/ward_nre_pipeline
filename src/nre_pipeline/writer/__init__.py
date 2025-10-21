import os


DEFAULT_WRITE_BATCH_SIZE = 100
default_write_batch_size = os.getenv("DEFAULT_WRITE_BATCH_SIZE", None)
if default_write_batch_size is None:
    raise RuntimeError("DEFAULT_WRITE_BATCH_SIZE environment variable is not set")
else:
    DEFAULT_WRITE_BATCH_SIZE = int(default_write_batch_size)


__all__ = ["DEFAULT_WRITE_BATCH_SIZE"]
