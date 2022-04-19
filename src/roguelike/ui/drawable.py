"""Contains Drawable interface"""

import abc

from PIL import Image


class Drawable(abc.ABC):
    """Drawable Interface"""

    @abc.abstractmethod
    def draw(self, width: int, height: int) -> Image:
        raise NotImplementedError()
