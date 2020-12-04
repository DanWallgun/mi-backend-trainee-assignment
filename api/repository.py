import abc
from uuid import uuid4
from typing import List

from bson import ObjectId
from pymongo.collection import Collection

from model import Observer, Counter


class ObserverRepository(abc.ABC):
    """
    Base class for all Observer Repo's
    """
    @abc.abstractmethod
    def insert(self, observer: Observer) -> Observer:
        """
        Inserts observer into repository
        """
        raise NotImplementedError

    @abc.abstractmethod
    def replace_by_id(self, id: str, observer: Observer) -> Observer:
        """
        Replaces observer object with given id with given observer
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self) -> List[Observer]:
        """
        Returns list of all observers
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, id: str) -> Observer:
        """
        Returns observer with given id
        """
        raise NotImplementedError


class ListObserverRepository(ObserverRepository):
    def __init__(self):
        self.__observers: List[Observer] = []

    def insert(self, observer: Observer) -> Observer:
        observer.id = uuid4()
        self.__observers.append(observer)
        return self.__observers[-1]

    def replace_by_id(self, id: str, observer: Observer) -> Observer:
        observer.id = ObjectId(id)
        self.__observers = list(filter(
            lambda obs: str(obs.id) != id,
            self.__observers
        ))
        return self.get_by_id(id)

    def get_all(self) -> List[Observer]:
        return self.__observers

    def get_by_id(self, id: str) -> Observer:
        observers = list(filter(
            lambda observer: str(observer.id) == id, self.__observers
        ))
        return observers[0] if len(observers) > 0 else None


class MongoDBObserverRepository(ObserverRepository):
    def __init__(self, observers_collection: Collection):
        self.__observers_collection: Collection = observers_collection

    @staticmethod
    def __create_observer_from_document(document: dict) -> Observer:
        observer = Observer(
            query=document['query'],
            region_id=document['region_id'],
        )
        observer.id = document['_id']
        for counter in document['counters']:
            observer.counters.append(
                Counter(
                    count=counter['count'],
                    timestamp=counter['timestamp']
                )
            )
        return observer

    def insert(self, observer: Observer) -> Observer:
        if hasattr(observer, 'id'):
            delattr(observer, 'id')
        returned = self.__observers_collection.insert_one(observer.dict())
        observer.id = returned.inserted_id
        return observer

    def replace_by_id(self, id: str, observer: Observer) -> Observer:
        self.__observers_collection.replace_one(
            {'_id': ObjectId(id)},
            observer.dict()
        )
        return self.get_by_id(id)

    def get_all(self) -> List[Observer]:
        observers: List[Observer] = []
        for document in self.__observers_collection.find():
            observers.append(
                MongoDBObserverRepository.__create_observer_from_document(
                    document
                )
            )
        return observers

    def get_by_id(self, id: str) -> Observer:
        document = self.__observers_collection.find_one({'_id': ObjectId(id)})
        if not document:
            return None
        return MongoDBObserverRepository.__create_observer_from_document(
            document
        )
