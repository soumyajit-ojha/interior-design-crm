import os
from pathlib import Path

# LOGGER Constants configuration

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = os.path.join(BASE_DIR, "logs/")
# Check for either log dir existance if not create one.
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = "IgoloApi.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)
LOGGER_LEVEL = "INFO"
MAX_LOG_LINES = 10000

LOG_FILE = "IgoloApi.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "ignore_autoreload": {
            "()": "igolohomes.custom_logger.IgnoreReloadFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[%(levelname)s] %(asctime)s %(name)s: %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": LOGGER_LEVEL,
            "class": "igolohomes.custom_logger.LineCountRotatingFileHandler",  # custom handler
            "filename": LOG_PATH,
            "formatter": "verbose",
            "encoding": "utf8",
            "max_lines": MAX_LOG_LINES,  # max - lines
            "filters": ["ignore_autoreload"],
        },
    },
    "loggers": {
        "root": {
            "handlers": ["file"],
            "level": LOGGER_LEVEL,
            "propagate": False,
        },
    },
}
  