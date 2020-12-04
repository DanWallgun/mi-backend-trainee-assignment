from typing import List, Optional

from pydantic import BaseModel, Field
from bson import ObjectId


class Counter(BaseModel):
    """
    A class used to store a pair (count, timestamp)
    for observation of adverts

    ...

    Attributes
    ----------
    count : int
        the number of adverts in particular observation
    timestamp : int
        the timestamp of particular observation
    """

    count: int
    timestamp: int


class Observer(BaseModel):
    """
    A model class representing Observer object
    Stores info about the search query and
    its counters

    ...

    Attributes
    ----------
    id : bson.ObjectId
        id of the observer
    query : str
        text representation of search query
    region_id: int
        id of the region of search
    counters: List[model.Counter]
        list of Counters for the observations
    """

    id: Optional[ObjectId] = Field(alias='_id')
    query: str
    region_id: int

    counters: List[Counter] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
