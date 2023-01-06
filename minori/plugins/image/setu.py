from typing import Any
import requests
import os

from nonebot.log import logger

from minori.adapter import MessageSegment
from minori.utils.resource import manager


class Setu:
    SETU_API = r"https://api.lolicon.app/setu/v2"
    SETU_DIR = manager.resource_dir("image.setu")

    @classmethod
    def _decode(cls, content: Any) -> MessageSegment:
        if not content["data"]:
            return MessageSegment.plain("啊嘞，色图不见啦")
        url: str = content["data"][0]["urls"]["original"]
        filename = url.split("/")[-1]
        path = os.path.join(cls.SETU_DIR, filename)
        logger.debug(f"downloading {filename} to {path}")
        if not os.path.exists(path):
            res = requests.get(
                url,
                timeout=10,
                headers={
                    "user-agent":
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
                })
            with open(path, "wb") as f:
                f.write(res.content)
        return MessageSegment.image(path=path)

    @classmethod
    def keyword(cls, keyword: str = "") -> MessageSegment:
        res = requests.post(cls.SETU_API,
                            json={
                                "r18": 0,
                                "num": 1,
                                "size": ["original"],
                                "keyword": keyword,
                            })
        return cls._decode(res.json())
