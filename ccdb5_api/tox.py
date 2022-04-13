import logging

from .settings import *  # noqa


logging.captureWarnings(True)


# -----------------------------------------------------------------------------
# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "CRITICAL",
        },
    },
    "loggers": {
        "complaint_search": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["console"],
        },
    },
}
