import logging, requests

class MarketCap(object):

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.headers = config['headers']

    def fetch(self, symbol):
        marketCap = {
                "totalMarketCap" : 0,
                "freeFloatMarketCap" : 0,
                "iwf" : 0
        }

        self.session.get(self.config['host'], headers=self.headers)

        marketcapUrl = f'{self.config["host"]}/{self.config["marketCap"]}'
        marketcapUrl = marketcapUrl.replace('{symbol}', symbol)

        logging.debug(f'> fetching : {marketcapUrl}')
        response = self.session.get(url=marketcapUrl, headers=self.headers)
        if response.status_code == 200:

            tradeInfo = response.json()['marketDeptOrderBook']['tradeInfo']
            logging.debug(f'> symbol : {symbol} :: market cap : {tradeInfo}')

            marketCap['totalMarketCap'] = tradeInfo['totalMarketCap']
            marketCap['freeFloatMarketCap'] = tradeInfo['ffmc']
            marketCap['iwf'] = round(marketCap['totalMarketCap']/marketCap['freeFloatMarketCap'], 2)

        else:
            raise Exception(f'> error in fetching market capitalization data for {symbol} :: http status code : {response.status_code}')

        return marketCap


