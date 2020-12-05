from json import loads
import http.client
from urllib.parse import urlencode


class AvitoApi:
    """
    A class used to access m.avito.ru api methods

    ...

    Attributes
    ----------
    __API_KEY : str
        the key used in api requests
    __PROXY_HOST : str
        proxy host used in requests
    __PROXY_PORT : int
        proxy port used in requests
    """

    __API_KEY: str = u'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
    __PROXY_HOST: str = None
    __PROXY_PORT: int = None

    def __init__(self, proxy_host: str, proxy_port: str):
        if not proxy_host or not proxy_port:
            self.__PROXY_HOST = None
            self.__PROXY_PORT = None
        else:
            self.__PROXY_HOST = proxy_host
            self.__PROXY_PORT = int(proxy_port)

    def __proxied_request(self, urn: str) -> dict:
        if self.__PROXY_HOST:
            connection = http.client.HTTPSConnection(
                self.__PROXY_HOST,
                self.__PROXY_PORT
            )
            connection.set_tunnel('m.avito.ru', 443)
        else:
            connection = http.client.HTTPSConnection('m.avito.ru')
        connection.request('GET', urn)
        data = connection.getresponse().read()
        connection.close()
        return loads(data.decode('utf-8'))

    def __slocations(self, location: str) -> dict:
        urn = '/api/1/slocations' + '?' + urlencode({
            'key': AvitoApi.__API_KEY,
            'q': location
        })

        return self.__proxied_request(urn)

    def __items(self, location_id: int, query: str) -> dict:
        urn = '/api/9/items' + '?' + urlencode({
            'key': AvitoApi.__API_KEY,
            'locationId': location_id,
            'query': query,
            'countOnly': True
        })

        return self.__proxied_request(urn)

    def get_location_id(self, location: str) -> int:
        """
        The method attempts to find given
        location in Avito regions
        Returns id of the location on success
        Returns 'None' on fail
        """
        data = self.__slocations(location)
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

    def get_items_count(self, location_id: int, query: str) -> int:
        """
        The method attempts to get the number of Avito adverts
        for the given search query and region id
        Returns the number of the adverts on success
        Returns 'None' on fail
        """
        data = self.__items(location_id, query)
        if 'result' not in data or 'totalCount' not in data['result']:
            return None
        return data['result']['totalCount']
