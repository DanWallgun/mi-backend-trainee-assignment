import asyncio
import time
import os
from datetime import datetime
import random

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

from avito import AvitoApi
from model import Observer, Counter
from repository import MongoDBObserverRepository

MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb://localhost:27017/'
)
OBSERVATION_PERIOD_SEC = float(os.getenv(
    'OBSERVATION_PERIOD_SEC',
    3600.0
))
PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')

avito = AvitoApi(PROXY_HOST, PROXY_PORT)

mongoClient = MongoClient(MONGODB_URI)
db = mongoClient['avito-observer']

repo = MongoDBObserverRepository(db.observers)

app = FastAPI()


async def update_counter_and_commit(observer: Observer):
    """
    Makes new observation and adds counter
    to the given observer's counters

    Parameters
    ----------
    observer : model.Observer
        the observer for whom a new observation will be made
    """
    count = avito.get_items_count(
        location_id=observer.region_id,
        query=observer.query
    )
    observer.counters.append(
        Counter(
            count=count,
            timestamp=datetime.utcnow().timestamp()
        )
    )
    repo.replace_by_id(observer.id, observer)


async def update_counters_routine(period: float = OBSERVATION_PERIOD_SEC):
    """
    Runs observers' counters' update with given period

    Parameters
    ----------
    period : float
        how many seconds should be between observations
    """
    while True:
        start_time = time.perf_counter()
        observers = repo.get_all()
        for observer in observers:
            if len(observer.counters) > 0:
                blind_time = datetime.utcnow().timestamp() \
                    - observers.counters[-1].timestamp
                if blind_time < period / 2:
                    continue
            await update_counter_and_commit(observer)
        elapsed_time = time.perf_counter() - start_time
        await asyncio.sleep(max(0, period - elapsed_time))


update_counters_task = None


@app.on_event("startup")
async def startup():
    loop = asyncio.get_running_loop()
    global update_counters_task
    update_counters_task = loop.create_task(update_counters_routine())


@app.on_event("shutdown")
async def shutdown():
    update_counters_task.cancel()


@app.get('/')
async def root():
    """
    Well, I'm running. Vroom-vroom
    """
    random.seed(datetime.utcnow().timestamp())
    return {'message': 'Running' + '.' * random.randint(1, 10)}


@app.get('/add')
async def add(region: str, query: str):
    """
    Adds a new observer for a given request
    Returns created observer
    """
    region_id = avito.get_location_id(location=region)
    if not region_id:
        raise HTTPException(status_code=404, detail="Region not found")
    observer = Observer(
        query=query,
        region_id=region_id
    )
    count = avito.get_items_count(location_id=region_id, query=query)
    observer.counters.append(
        Counter(
            count=count,
            timestamp=datetime.utcnow().timestamp()
        )
    )
    return repo.insert(observer)


@app.get('/stat')
async def stat(id: str, begin: int = 0, end: int = -1):
    """
    Returns accumulated statistics
    in the given time interval
    for observer with the given id
    """
    observer = repo.get_by_id(id)
    if not observer:
        raise HTTPException(status_code=404, detail="Observer not found")
    observer.counters = list(filter(
        lambda counter:
            begin <= counter.timestamp
            and (end < 0 or counter.timestamp <= end),
        observer.counters
    ))
    return observer
