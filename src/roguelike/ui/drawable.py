"""Contains Drawable interface"""

import abc
import functools
import os
import typing as tp
from functools import wraps

from PIL import Image

from roguelike.const import IMAGE_RESOURCES_DIR

FuncT = tp.TypeVar('FuncT', bound=tp.Callable[..., tp.Any])


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
        height: tp.Optional[int] = None,
        flavour: tp.Optional[str] = None) -> Image:
    """Load image resource by resource_name"""

    image_path = os.path.join(IMAGE_RESOURCES_DIR, resource_name)
    if flavour is not None:
        image_path = os.path.join(IMAGE_RESOURCES_DIR, flavour, resource_name)

    img = Image.open(image_path)
    return img if width is None or height is None else resize_image(img, width, height)


INITIALIZED_ONJECTS_ID: tp.Set[str] = set()


def drawable(resource_path: str) -> tp.Callable[[FuncT], FuncT]:
    """Decorator for drawable classes"""

    assert resource_path.endswith('.png')

    def class_wrapper(cls):  # type: ignore

        @wraps(cls, updated=())
        class ResourceDrawable(cls, Drawable):
            def __init__(self, *args, **kwargs) -> None:  # type: ignore
                if not hasattr(self, '_flavour'):
                    self._flavour = kwargs.pop('draw_flavour', None)
                super(ResourceDrawable, self).__init__(*args, **kwargs)
                if hasattr(self, '_behaviour'):
                    resource_name, resource_format = resource_path.split('.')
                    self._image_resource_path = f'{resource_name}_{self._behaviour}.{resource_format}'
                else:
                    self._image_resource_path = resource_path

            def draw(self, width: int, height: int) -> Image:
                return load_image_resource(self._image_resource_path, width, height, self._flavour)

        return ResourceDrawable

    return class_wrapper
