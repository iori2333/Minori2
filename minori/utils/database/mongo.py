import json
from typing import Generic, Optional, Sequence, Type, TypeVar

from bson import ObjectId
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection as MongoCollection

T = TypeVar("T", bound=BaseModel)

client = MongoClient("localhost", 27017, username="root", password="root")
db = client.minori


class WrappedModel(dict, Generic[T]):

    def __init__(self, model: T) -> None:
        data = json.loads(model.json())
        self.update(data)
        if "_id" in self:
            self.pop("_id")
        self.document_class = type(model)


class Collection(Generic[T]):

    def __init__(self, name: str, document_type: Type[T]) -> None:
        self.collection: MongoCollection[WrappedModel[T]] = db[name]
        self.document_type = document_type

    def unwrap(self, data: WrappedModel[T]) -> T:
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
