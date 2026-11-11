from ..utils.communication import Communication
from .delivery import Delivery
from pandas import DataFrame
import re, json
import pandas, logging
import dateparser

class NSE(Delivery):

    def __init__(self, config, dbConfigPath, symbolList) -> None:
        super().__init__(config, dbConfigPath, symbolList)

        self.communication = Communication(config['url'])

        self.period = config['period']
        self.headers    = config['headers']
        self.payload    = config['payload']
        self.method     = config['method']
        self.dataPath   = config['path']['data']
        self.cookie     = config['path']['cookie']

    def fetchData(self, symbol: str) -> DataFrame:
        logging.debug('> Fetching Delivery data...')
        data = self.__fetchDeliveryData(symbol)
        logging.debug('\n')

        return data


    def __fetchDeliveryData(self, symbol: str) -> DataFrame:
        logging.debug('> inserting Symbol in path...')
        dataPath = self.__insertSymbol(symbol, self.dataPath)
        logging.debug('> dataPath : {}'.format(dataPath))
        logging.debug('\n')


        logging.debug('> inserting Period in dataPath...')
        dataPath = self.__insertPeriod(self.period, dataPath)
        logging.debug('> dataPath : {}'.format(dataPath))
        logging.debug('\n')


        data = self.communication.fetch(self.method, dataPath, self.payload, \
            self.headers, self.cookie, 'json')
        data = self.__readDeliveryData(data['data'], symbol)
        logging.debug('> reading delivery data from nse data...')
        logging.debug(data)

        data = self.__dropDuplicateRecord(data)

        return data


    def __readDeliveryData(self, data, symbol):

        deliveryData = DataFrame([])
        for aRow in data:
            df = DataFrame({
                'Date' : [ aRow['CH_TIMESTAMP'] ],
                'Symbol' : [ symbol ],
                'Open'  : [ aRow['CH_OPENING_PRICE'] ],
                'High'  : [ aRow['CH_TRADE_HIGH_PRICE'] ],
                'Low'   : [ aRow['CH_TRADE_LOW_PRICE'] ],
                'Close'     : [ aRow['CH_CLOSING_PRICE'] ],
                'Trades'    : [ aRow['CH_TOTAL_TRADES'] ],
                'DeliverableVolume' : [ aRow['COP_DELIV_QTY'] ],
                'Volume' : [ aRow['CH_TOT_TRADED_QTY'] ],
                'DeliveryPercentage': [ aRow['COP_DELIV_PERC'] ],
                'Turnover' : [ aRow['CH_TOT_TRADED_VAL'] ]
            })
            deliveryData = pandas.concat([deliveryData, df])

        # deliveryData.set_index('Date', inplace=True)
        return deliveryData

    def __insertSymbol(self, symbol: str, path: str) -> str:
        symbol = re.sub(r'&', '%26', symbol)

        path = re.sub(r'symbol=\w+', 'symbol={}'.format(symbol), path)
        return path

    def __insertPeriod(self, period: str, path: str) -> str:

        fromDate = dateparser.parse(period).date()
        fromDate = fromDate.strftime('%d-%m-%Y')
        toDate   = dateparser.parse('today').date()
        toDate = toDate.strftime('%d-%m-%Y')

        path = re.sub(r'from_date', fromDate, path)
        path = re.sub(r'to_date', toDate, path)

        return path

    def __dropDuplicateRecord(self, data):

        data = data.reset_index()
        data.drop_duplicates(subset='Date', keep='first', inplace=True)
        # data.replace('-', 0, inplace=True)
        data.set_index('Date', inplace=True)

        return data
