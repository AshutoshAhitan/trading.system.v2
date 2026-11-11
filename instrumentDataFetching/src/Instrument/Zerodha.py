import pandas, logging
from .Instrument import Instrument

from kiteconnect import KiteConnect


class Zerodha(Instrument):

    def __init__(self, config: dict, dbConfigPath) -> None:
        super().__init__(config, dbConfigPath)
        self.config = config

    def fetchListedInstrument(self):

        kite = KiteConnect(api_key=self.config['zerodha.api.key'])
        kite.set_access_token(self.config["zerodha.access_token"])

        instruments =  kite.instruments()  # Fetch instruments for the specified exchange

        # Dataframe to hold the instrument data
        instruments = pandas.DataFrame.from_dict(instruments)
        logging.info(f'> fetched {len(instruments)} instruments from Zerodha')

        instruments = instruments[instruments.exchange.isin(self.config['exchange'])]  # Filter for exchange
        instruments = instruments[instruments.instrument_type.isin(self.config['type'])]  # Filter for Equity instruments
        instruments = instruments[instruments['segment'].isin(self.config['segment'])]  # Filter for specified segments

        logging.info(f'> filtered {len(instruments)} instruments for exchange {self.config["exchange"]} and type {self.config["type"]} and segment {self.config["segment"]}')

        # Filter out symbols containing a dash and series (e.g., "655AP33-SG")
        instruments = instruments[~instruments['tradingsymbol'].str.contains(r'-[A-Z0-9]+$', regex=True)]
        logging.info(f'> filtered {len(instruments)} instruments after removing symbols with dashes and series')

        instruments = instruments.rename(columns={
            'tradingsymbol': 'symbol',
            'name': 'company',
            'instrument_token': 'instrumentToken',
            'instrument_type': 'instrumentType',
        })

        logging.info(f'> filtered instruments columns:\n {instruments.columns}')
        logging.info(f'> listed instruments:\n {instruments[["symbol", "company", "instrumentToken", "instrumentType", "exchange"]].tail(10)}')

        return instruments
