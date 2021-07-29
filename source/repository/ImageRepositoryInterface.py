from abc import ABCMeta, abstractmethod
from ..models.image import ImageEntity
from .repositories import RepoResponse, Any


class ImageRepository(metaclass=ABCMeta):
    @abstractmethod
    def upload_image(self, image_entity: ImageEntity, image_name: str) -> RepoResponse:
        raise NotImplementedError

    @abstractmethod
    def load_more_images(self, offset: int, limit: int) -> RepoResponse:
        raise NotImplementedError

    @abstractmethod
    def search_image(self, texture: bytes, album: Any) -> RepoResponse:
        raise NotImplementedError

    @abstractmethod
    def get_image_by_name(self, name: str) -> RepoResponse:
        raise NotImplementedError