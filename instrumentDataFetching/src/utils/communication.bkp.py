from http.client import HTTPSConnection
from typing import Union
from .exception import HTTPSTATUSNOT200
import logging, json


class Communication:
    def __init__(self, url: str) -> None:
        self.url = url

    def fetch(self, method: str, path: str, payload: str, headers: dict, cookie: str, responseType: str) -> Union[str, dict]:
        """
        Fetch data from the server with the given method, path, payload, headers, and response type.
        """
        logging.debug('> URL : {}'.format(self.url))
        logging.debug('> METHOD : {}'.format(method))
        logging.debug('> PATH : {}'.format(path))

        cookie = self.__getCookie(payload="", headers=headers)
        logging.debug('> COOKIE : {}'.format(cookie))

        session = HTTPSConnection(self.url)  # Create a persistent session
        try:
            headers['Cookie'] = cookie
            logging.debug('> HEADERS : {}'.format(headers))
            session.request(method, path, payload, headers)

            response = session.getresponse()
            if response.status != 200:
                logging.debug('> ERROR Response from server : {}'.format(response.reason))
                raise HTTPSTATUSNOT200(f"HTTP Status: {response.status}, Reason: {response.reason}")

            data = response.read()
            if responseType == 'text':
                data = data.decode('utf-8')
            else:
                data = json.loads(data)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise e
        finally:
            self.close_session(session)

        return data

    def __getCookie(self, payload: str, headers: dict) -> Union[str, None]:
        """
        Fetch cookie from the server.
        """
        cookie: Union[str, None] = ''
        session = HTTPSConnection(self.url)  # Create a persistent session
        try:
            logging.debug('Fetching cookie...')
            session.request("GET", "/", payload, headers)

            response = session.getresponse()
            if response.status != 200:
                logging.debug('> ERROR Response from server : {}'.format(response.reason))
                raise HTTPSTATUSNOT200(f"HTTP Status: {response.status}, Reason: {response.reason}")

            cookie = response.getheader('Set-Cookie')
            logging.debug('cookie -> {}'.format(cookie))

        except Exception as e:
            logging.error(f"An error occurred while fetching cookie: {e}")
            raise e
        finally:
            self.close_session(session)

        return cookie

    def close_session(self, session) -> None:
        """
        Close the persistent HTTP session.
        """
        session.close()

# Usage example:
# communication = Communication("api.example.com")
# response = communication.fetch("GET", "/endpoint", payload="", headers={}, cookie=cookie, responseType="json")
# communication.close_session()
