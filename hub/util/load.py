import re
import numpy as np
import pathlib
import exiftool  # type: ignore
from typing import Callable, Dict, List, Tuple, Union
from hub.util.exceptions import (
    HubAutoUnsupportedFileExtensionError,
    SampleCorruptedError,
    ImageReadError,
)
from PIL import Image  # type: ignore


IMAGE_SUFFIXES: List[str] = [".jpeg", ".jpg", ".png"]
SUPPORTED_SUFFIXES: List[str] = IMAGE_SUFFIXES


class SymbolicSample:
    def __init__(self, path: str):
        self.path = pathlib.Path(path)
        self._array = None

    @property
    def was_read(self):
        return self._array is not None

    @property
    def array(self) -> np.ndarray:
        self.read()
        return self._array

    @property
    def shape(self) -> Tuple[int, ...]:
        self.read()
        return self._array.shape

    @property
    def dtype(self) -> str:
        self.read()
        return self._array.dtype.name

    @property
    def compression(self) -> str:
        # TODO: raise exception if `read` wasn't called
        self.read()
        return self._compression

    def raw_bytes(self) -> bytes:
        with open(self.path, "rb") as image_file:
            return image_file.read()

    def read(self):
        if self._array is None:
            # TODO: explain this
            if self._array is not None:
                return self._array

            suffix = self.path.suffix.lower()

            if suffix in IMAGE_SUFFIXES:
                img = Image.open(self.path)

                # TODO: mention in docstring that if this loads correctly, the meta is assumed to be valid
                try:
                    self._array = np.array(img)
                except:
                    # TODO: elaborate on why it corrupted
                    raise SampleCorruptedError(self.path)

                # TODO: set meta values
                self._compression = img.format
                return self._array

            raise HubAutoUnsupportedFileExtensionError(self._suffix, SUPPORTED_SUFFIXES)

    def __str__(self):
        if self.was_read is None:
            return f"SymbolicSample(was_read=False, path={self.path})"

        return f"SymbolicSample(was_read=True, shape={self.shape}, compression='{self.compression}', dtype='{self.dtype}' path={self.path})"


def load(path: Union[str, pathlib.Path]) -> SymbolicSample:
    # TODO: mention that you can do `.numpy()` on this output to make it extremely easy to use
    return SymbolicSample(path)
