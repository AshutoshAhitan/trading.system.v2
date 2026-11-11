import logging, requests

class SecurityInfo(object):

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.headers = config['headers']

    def fetch(self, symbol):
        securityInfo = {}

        self.session.get(self.config['host'], headers=self.headers)

        securityInfoUrl = f'{self.config["host"]}/{self.config["securityInfo"]}'
        securityInfoUrl = securityInfoUrl.replace('{symbol}', symbol)

        logging.debug(f'> fetching : {securityInfoUrl}')
        response = self.session.get(url=securityInfoUrl, headers=self.headers)
        if response.status_code == 200:
            securityInfo = response.json()['securityInfo']
            logging.debug(f'> symbol : {symbol} :: security info : {securityInfo}')

        else:
            raise Exception(f'> error in fetching security info data for {symbol} :: http status code : {response.status_code}')

        return securityInfo

