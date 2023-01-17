import json
from typing import Generic, Optional, Sequence, Type, TypeVar

from bson import ObjectId
from pydantic import BaseModel, Extra
from pymongo import MongoClient
from pymongo.collection import Collection as MongoCollection

from nonebot import get_driver

T = TypeVar("T", bound=BaseModel)


class MongoConfig(BaseModel, extra=Extra.ignore):
    mongo_host: Optional[str]
    mongo_port: Optional[int]
    mongo_username: Optional[str]
    mongo_password: Optional[str]


driver = get_driver()
config = MongoConfig.parse_obj(driver.config)
client = MongoClient(
    host="localhost",
    port=config.mongo_port,
    username=config.mongo_username,
    password=config.mongo_password,
)
db = client.minori


class WrappedModel(dict, Generic[T]):

    def __init__(self, model: T) -> None:
        data = json.loads(model.json(by_alias=True))
        self.update(data)
        if "_id" in self:
            self.pop("_id")
        self.document_class = type(model)


class Collection(Generic[T]):

    def __init__(self, name: str, document_type: Type[T]) -> None:
        self.collection: MongoCollection[WrappedModel[T]] = db[name]
        self.document_type = document_type

    def unwrap(self, data: WrappedModel[T]) -> T:
        if "_id" in data:
            data.pop("_id")
        return self.document_type.parse_obj(data)

    def save(self, data: T) -> ObjectId:
        wrapped = WrappedModel(data)
        result = self.collection.insert_one(wrapped)
        return result.inserted_id

    def get(self, id: ObjectId) -> Optional[T]:
        result = self.collection.find_one({"_id": id})
        return self.unwrap(result) if result is not None else None

    def query(self, query: dict, limit: Optional[int] = None) -> Sequence[T]:
        results = self.collection.find(query)
        if limit is not None:
            results = results.limit(limit)
        return [self.unwrap(result) for result in results]
