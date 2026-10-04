from contextlib import contextmanager

LOGGING_ENABLED = True


@contextmanager
def disable_logging():
    """
    disable creating log objects
    used for management commands that runs of service startapp.
    """
    global LOGGING_ENABLED

    old = LOGGING_ENABLED

    LOGGING_ENABLED = False

    try:
        yield
    finally:
        LOGGING_ENABLED = old