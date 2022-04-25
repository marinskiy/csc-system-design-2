"""Contains Drawable interface"""

import abc
import functools
import os
import typing as tp

from PIL import Image

from roguelike.const import IMAGE_RESOURCES_DIR


class Drawable(abc.ABC):
    """Drawable Interface"""

    @abc.abstractmethod
    def draw(self, width: int, height: int) -> Image:
        raise NotImplementedError()


def resize_image(img: Image, width: int, height: int) -> Image:
    return img.resize((width, height), Image.ANTIALIAS)


@functools.lru_cache
def load_image_resource(
        resource_name: str,
        width: tp.Optional[int] = None,
        height: tp.Optional[int] = None) -> Image:
    """Load image resource by resource_name"""

    img = Image.open(os.path.join(IMAGE_RESOURCES_DIR, resource_name))
    return img if width is None or height is None else resize_image(img, width, height)


def drawable(resource_name: str):
    """Decorator for drawable classes"""

    assert resource_name.endswith('.png')

    def class_wrapper(cls):
        class ResourceDrawable(cls, Drawable):
            def __init__(self, *args, **kwargs):
                super(ResourceDrawable, self).__init__(*args, **kwargs)
                self._image_resource_name = resource_name
                functools.update_wrapper(self, cls)

            def draw(self, width: int, height: int) -> Image:
                return load_image_resource(self._image_resource_name, width, height)

        return ResourceDrawable

    return class_wrapper
