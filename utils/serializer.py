"""
Helper functions to serialize data and other pythonic objects.
"""


import pickle
from pathlib import Path
from typing import Any, Union
from utils.logger import log


def write_to_pkl(file_path: Union[str, Path], obj: Any) -> None:
    file_object = open(file_path, "wb")
    log.info("Serializing to Pickle ...")
    pickle.dump(obj=obj, file=file_object)
    file_object.close()
    log.info(f"Sucessfully serialized to pickle at: {file_path}")


def load_fr_pkl(file_path: str) -> Any:
    file_object = open(file_path, "rb")
    return pickle.load(file_object)
