import os
import logging.config


config_dict = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s | %(message)s",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": "logs/app.log",
            "mode": "a",
            "encoding": "utf-8",
            # "delay": True,
        },
        "errors_file": {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": "ERROR",
            "filename": "logs/errors.log",
            "mode": "a",
            "encoding": "utf-8",
        }
    },

    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "errors_file"],
            "propagate": False,
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    }
}

os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(config_dict)
