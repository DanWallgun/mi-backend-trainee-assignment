# Тестовое задание для стажера в Market Intelligence

## Запуск веб-сервера
Два контейнера: оффициальный docker образ MongoDB и контейнер, на котором работает сам api-веб-сервис на python. Первый образ подгружается, второй образ собирается локально по Dockerfile.  
Команда запуска:  
`docker-compose up`

## Overview
- Язык программирования - Python 3.8
- Персистентность - MongoDB
- Сервис позволяет следить за изменением количества объявлений по определённому поисковому запросу и региону в формате набора пар *(Количество объявлений, Timestamp)*
- Получение данных об объявлениях на Avito через `/api/1/slocations` и `/api/9/items` методы `m.avito.ru`
- 1 раз в час происходит опрос по каждой паре

## JSON API
- (Объект) Observer
    - `_id : str` - идентификатор отслеживаемой пары *(Регион, Поисковый запрос)*
    - `region_id : int` - идентификатор региона поиска, аналогичный используемому в `m.avito.ru/api`
    - `query : str` - текстовое представление поискового запроса
    - `counters : List[Counter]` - собранные счётчики  
    *Counter*
        - `count : int` - количество объявлений
        - `timestamp : int` - unix timestamp, соответствующий времени сбора данных
- (Метод) Добавить пару *(Регион, Поисковый запрос)* в отслеживаемые и получить её идентификатор
    - URL  
    `/add`
    - Method  
    `GET`
    - Параметры  
        - `region : str` - текстовое представление региона поиска. Регион должен быть в базе Avito  
        ![так не пойдет](docs/images/only-avito-regions.png)
        - `query : str` - текстовое представление поискового запроса
    - Возвращаемое значение  
    `Observer`
    - Пример запроса
    ```
    curl --get \
         --data-urlencode "region=Мурманск" \
         --data-urlencode "query=Лабрадор" \
         "http://localhost:80/add"

    {
        "query":"Лабрадор",
        "region_id":640160,
        "counters":[
            {"count":44,"timestamp":1607106469}
        ],
        "_id":"5fca7fa52d0bccc400767ef9"
    }
    ```  
- (Метод) Получить список счётчиков, полученных за данный период
    - URL  
    `/stat`
    - Method  
    `GET`
    - Параметры  
        - `id : str` - идентификатор отслеживаемой пары
        - `begin : int` - timestamp начала отслеживаемого периода
        - `end : int` - timestamp конца отслеживаемого периода
    - Возвращаемое значение  
    `Observer`, у которого список счётчиков ограничен на заданный в запросе период
    - Пример запроса
    ```
    curl --get \
         --data-urlencode "id=5fca7fa52d0bccc400767ef9" \
         --data-urlencode "begin=1607106480" \
         --data-urlencode "end=1607106560" \
         "http://localhost:80/stat"
    
    {
        "_id":"5fca7fa52d0bccc400767ef9",
        "query":"Лабрадор",
        "region_id":640160,
        "counters":[
            {"count":44,"timestamp":1607106486},
            {"count":44,"timestamp":1607106516},
            {"count":44,"timestamp":1607106546}
        ]
    }
    ```  

## Live example
**Возможно!**, сервис запущен на [AWS](http://ec2-54-234-254-151.compute-1.amazonaws.com:80).
- Протокол `HTTP`
- Домен `ec2-54-234-254-151.compute-1.amazonaws.com`
- Порт `80`
- URLs для методов
    - http://ec2-54-234-254-151.compute-1.amazonaws.com:80/add
    - http://ec2-54-234-254-151.compute-1.amazonaws.com:80/stat