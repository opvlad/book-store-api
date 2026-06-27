import os
import logging

logger = logging.getLogger(__name__)


def remove_temp_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
