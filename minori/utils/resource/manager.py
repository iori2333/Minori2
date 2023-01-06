import json
import os
import os.path as osp
from typing import Mapping, Optional, Type, TypeVar

import toml
from pydantic import BaseModel, Extra
from PIL import Image as MImage
from PIL.Image import Image

from nonebot import get_driver
from nonebot.log import logger

driver = get_driver()

TM = TypeVar("TM", bound=BaseModel)


class Config(BaseModel, extra=Extra.ignore):
    resource_dir: str


class ResourceManager:

    def __init__(self) -> None:
        self._resource_dir = Config.parse_obj(driver.config).resource_dir
        os.makedirs(self._resource_dir, exist_ok=True)

    def json(self, identifier: str) -> dict[str, object]:
        paths = identifier.split(".")
        resource_path = osp.join(self._resource_dir, *paths) + ".json"
        try:
            with open(resource_path, "r", encoding="utf8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed loading resource: {identifier}: {e}")
            raise e

    def model(self, identifier: str, model: Type[TM]) -> TM:
        data = self.json(identifier)
        try:
            return model.parse_obj(data)
        except Exception as e:
            logger.error(f"Failed parsing model: {identifier}: {e}")
            raise e

    def toml(self, identifier: str) -> Mapping[str, object]:
        paths = identifier.split(".")
        resource_path = osp.join(self._resource_dir, *paths) + ".toml"
        try:
            with open(resource_path, "r", encoding="utf8") as f:
                return toml.load(f)
        except Exception as e:
            logger.error(f"Failed loading resource: {identifier}: {e}")
            raise e

    def image(self, identifier: str, ext: str = ".jpg") -> Image:
        paths = identifier.split(".")
        resource_path = osp.join(self._resource_dir, *paths) + ext
        try:
            im = MImage.open(resource_path)
        except Exception as e:
            logger.error(f"Failed loading resource: {identifier}: {e}")
            raise e
        return im

    def resource_dir(self, identifier: Optional[str] = None) -> str:
        path = self._resource_dir
        if identifier is not None:
            path = osp.join(path, *identifier.split("."))
        os.makedirs(path, exist_ok=True)
        return path
