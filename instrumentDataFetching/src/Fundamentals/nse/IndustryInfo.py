
import logging, requests

class IndustryInfo(object):

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.headers = config['headers']

    def fetch(self, symbol):
        industryInfo = {}

        self.session.get(self.config['host'], headers=self.headers)

        industryInfoUrl = f'{self.config["host"]}/{self.config["industryInfo"]}'
        industryInfoUrl = industryInfoUrl.replace('{symbol}', symbol)

        logging.debug(f'> fetching : {industryInfoUrl}')
        response = self.session.get(url=industryInfoUrl, headers=self.headers)
        if response.status_code == 200:
            industryInfo = response.json()['industryInfo']
            logging.debug(f'> symbol : {symbol} :: industry info : {industryInfo}')

        else:
            raise Exception(f'> error in fetching industry info data for {symbol} :: http status code : {response.status_code}')

        return industryInfo

