import requests

class HTTPClient:

    def __init__(self, host, headers) -> None:

        self.session = requests.session()
        self.headers = headers
        self.host = host

    def get(self, path, isResponseTypeJson):
        url = f'{self.host}/{path}'
        response = self.session.get(url, headers = self.headers)
        if response.status_code == 200:
            if isResponseTypeJson == True: return response.json()
            else: return response.text
        else:
            print(response)
            raise Exception(f'> error in fetching {url} :: http status code : {response.status_code}')




