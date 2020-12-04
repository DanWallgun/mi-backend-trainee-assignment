from json import loads
from urllib.request import urlopen
from urllib.parse import urlencode


class AvitoApi:
    """
    A class used to access m.avito.ru api methods

    ...

    Attributes
    ----------
    __API_KEY : str
        the key used in api requests
    """

    __API_KEY = u'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'

    @staticmethod
    def __slocations(location: str) -> dict:
        API_URL = u'https://m.avito.ru/api/1/slocations'
        response = urlopen(
            API_URL + '?' + urlencode({
                'key': AvitoApi.__API_KEY,
                'q': location
            })
        )
        data = response.read()
        return loads(data.decode('utf-8'))

    @staticmethod
    def __items(location_id: int, query: str) -> dict:
        API_URL = u'https://m.avito.ru/api/9/items'
        response = urlopen(
            API_URL + '?' + urlencode({
                'key': AvitoApi.__API_KEY,
                'locationId': location_id,
                'query': query,
                'countOnly': True
            })
        )
        data = response.read()
        return loads(data.decode('utf-8'))

    @staticmethod
    def get_location_id(location: str) -> int:
        """The method attempts to find given
        location in Avito regions
        Returns id of the location on success
        Returns 'None' on fail

        Parameters
        ----------
        sound : str, optional
            The sound the animal makes (default is None)
        """
        data = AvitoApi.__slocations(location)
        if 'result' not in data or 'locations' not in data['result']:
            return None
        locations = data['result']['locations']
        if len(locations) < 1:
            return None
        for loc in locations:
            for name in loc['names'].values():
                if name == location:
                    return loc['id']
        return None

    @staticmethod
    def get_items_count(location_id: int, query: str) -> int:
        """The method attempts to get the number of Avito adverts
        for the given search query and region id
        Returns the number of the adverts on success
        Returns 'None' on fail"""
        data = AvitoApi.__items(location_id, query)
        if 'result' not in data or 'totalCount' not in data['result']:
            return None
        return data['result']['totalCount']
