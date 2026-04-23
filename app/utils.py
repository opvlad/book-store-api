import os


def remove_temp_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
