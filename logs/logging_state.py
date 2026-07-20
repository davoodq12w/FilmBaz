from contextlib import contextmanager

LOGGING_ENABLED = True


@contextmanager
def disable_logging():
    global LOGGING_ENABLED

    old = LOGGING_ENABLED

    LOGGING_ENABLED = False

    try:
        yield
    finally:
        LOGGING_ENABLED = old