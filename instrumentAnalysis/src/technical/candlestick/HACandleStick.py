from pandas.core.frame import DataFrame
from ..Technical import Technical
import logging, pandas as pd

class HACandleStick(Technical):
    """
    Heiken Ashi Candlestick Technical Analysis class.
    Generates Heiken Ashi candles from OHLCV data.
    """

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)

    def perform(self, data) -> DataFrame:
        """
        Main method to generate Heiken Ashi candles and add them to the original data.
        
        Parameters:
        -----------
        data : DataFrame
            DataFrame containing Open, High, Low, Close, Volume columns
            
        Returns:
        --------
        DataFrame
            Original DataFrame with added Heiken Ashi OHLCV columns
        """
        # Create a copy of the original data
        analysedData = DataFrame(data)
        
        # Generate Heiken Ashi candles
        analysedData = self.generateHekinAshi(data, analysedData)
        
        # Fill any NaN values with 0
        analysedData = analysedData.fillna(0)
        
        return analysedData

    def generateHekinAshi(self, ohlcv: DataFrame, analysedData: DataFrame) -> DataFrame:
        ha = ohlcv.copy()

        # Heikin-Ashi Close
        ha['HA_Close'] = (ohlcv['Open'] + ohlcv['High'] + ohlcv['Low'] + ohlcv['Close']) / 4

        # Heikin-Ashi Open
        ha['HA_Open'] = 0.0
        ha.loc[ha.index[0], 'HA_Open'] = (ohlcv['Open'].iloc[0] + ohlcv['Close'].iloc[0]) / 2

        for i in range(1, len(ohlcv)):
            ha.loc[ha.index[i], 'HA_Open'] = (
                ha.loc[ha.index[i-1], 'HA_Open'] +
                ha.loc[ha.index[i-1], 'HA_Close']
            ) / 2

        # Heikin-Ashi High & Low
        ha['HA_High'] = ha[['HA_Open', 'HA_Close']].join(ohlcv['High']).max(axis=1)
        ha['HA_Low']  = ha[['HA_Open', 'HA_Close']].join(ohlcv['Low']).min(axis=1)

        ha['HA_Close'] = ha['HA_Close'].round(2)
        ha['HA_Open'] = ha['HA_Open'].round(2)
        ha['HA_High'] = ha['HA_High'].round(2)
        ha['HA_Low'] = ha['HA_Low'].round(2)

        # Drop columns if they already exist to avoid overlap error
        for col in ['HA_Open', 'HA_High', 'HA_Low', 'HA_Close']:
            if col in analysedData.columns:
                analysedData = analysedData.drop(columns=[col])

        analysedData = analysedData.join(ha[['HA_Open', 'HA_High', 'HA_Low', 'HA_Close']])

        logging.debug(f'Heiken Ashi data generated with {len(ha)} candles')
        return ha
