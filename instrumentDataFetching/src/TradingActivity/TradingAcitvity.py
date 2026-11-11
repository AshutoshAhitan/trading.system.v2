import abc

from pandas import DataFrame
from .FortnightTradingActivityNSDL import FortnightTradingActivityNSDL
from .DailyTradingAcitvityMoneyControl import DailyTradingAcitvityMoneyControl
from .DailyMFTradingActivityNSDL import DailyMFTradingActivityNSDL

class TradingActivity():

    def __init__(self, config, database) -> None:
        super().__init__()
        self.configuration = config
        self.database = database
        self.dailyTradingActivity = DailyTradingAcitvityMoneyControl(config['fiidii.daily'])
        self.fortnightlyTradingActivity = FortnightTradingActivityNSDL(config['fii.fortnightly'])
        self.mfDailyTradingActivity = DailyMFTradingActivityNSDL(config['mf.daily'])
        self.tradingActivityData = {
                'fiidii.daily' : DataFrame([]),
                'fii.fortnightly' : DataFrame([]),
                'mf.daily' : DataFrame([])
        }


    def fetchTradingActivity(self):

        self.tradingActivityData['fiidii.daily'] = self.dailyTradingActivity.fetch()
        # self.tradingActivityData['fii.fortnightly'] = self.fortnightlyTradingActivity.fetch()
        # self.tradingActivityData['mf.daily'] = self.mfDailyTradingActivity.fetch()

        return self


    def save(self):

        for tradingActivityType in self.tradingActivityData:
            if len(self.tradingActivityData[tradingActivityType]) > 0:
                self.database.saveRecords(self.configuration[tradingActivityType]['dest.table'], 
                                      self.configuration[tradingActivityType]['dest.table.primary.keys'], 
                                      self.tradingActivityData[tradingActivityType], 
                                      self.configuration[tradingActivityType]['dest.table.truncate'])

