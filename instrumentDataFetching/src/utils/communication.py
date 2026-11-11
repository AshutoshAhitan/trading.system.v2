import http.client
from http.client import HTTPSConnection
from typing import Union
from .exception import HTTPSTATUSNOT200
import logging, json

class Communication:

    def __init__(self, url: str) -> None:
        self.url = url


    def fetch(self, method, path, payload, headers, cookie, responseType) -> str:

        logging.debug('> URL : {}'.format(self.url))
        logging.debug('> METHOD : {} '.format(method))
        logging.debug('> PATH : {} '.format(path))

        connection = http.client.HTTPSConnection(self.url)
        try:
            headers['Cookie'] = cookie
            logging.debug('> HEADERS : {} '.format(headers))
            connection.request(method, path, payload, headers)

            response = connection.getresponse()
            if response.status != 200:
                logging.debug('> ERROR Response from server : {}'.format(response.reason))
                raise HTTPSTATUSNOT200()

            data = response.read()
            if responseType == 'text':
                data = data.decode('utf-8')
            else:
                data = json.loads(data)

        finally:
            connection.close()

        return data


    def __getCookie(self, payload: str, headers: dict) -> Union[str, None]:

        cookie: Union[str, None] = ''

        connection = http.client.HTTPSConnection(self.url)
        try:
            logging.debug('fetching cookie...')
            connection.request("GET", "/", payload, headers)

            response = connection.getresponse()
            if response.status != 200:
                logging.debug('> ERROR Response from server : {}'.format(response.reason))
                raise HTTPSTATUSNOT200()


            cookie  = response.getheader('Set-Cookie')
            logging.debug('cookie -> ', cookie)
        finally:
            connection.close()


        return cookie
