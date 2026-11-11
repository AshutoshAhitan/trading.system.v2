import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from ..Technical import Technical
import logging

try:
    import talib
except ImportError:
    raise ImportError(
        "TA-Lib is required for ADX calculation. "
        "Install it with: pip install TA-Lib"
    )


class ADX(Technical):
    """
    ADX (Average Directional Index) Technical Indicator
    
    Uses TA-Lib library for calculation.
    
    ADX measures trend strength on a scale of 0-100:
    - Values above 25 indicate strong trend
    - Values below 20 indicate weak/no trend
    """

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)
        self.configurations = configurations
        
        # Support both new and legacy configuration formats
        self.adx_length = configurations.get('period', 14)  # ADX Smoothing
        self.di_length = configurations.get('period', 14)    # DI Length
        
        logging.debug(
            f"ADX initialized with adx_length={self.adx_length}, "
            f"di_length={self.di_length}"
        )

    def perform(self, data: DataFrame) -> DataFrame:
        """
        Calculate ADX (Average Directional Index) using TA-Lib
        
        Parameters:
        -----------
        data : DataFrame
            OHLCV data with columns: High, Low, Close
            
        Returns:
        --------
        DataFrame
            Original data with additional columns:
            - adx: Average Directional Index
            - posDI: Positive Directional Indicator (+DI)
            - posDISlope: Change in +DI
            - negDI: Negative Directional Indicator (-DI)
            - negDISlope: Change in -DI
        """
        
        analysedData = DataFrame(data)
        
        columnMapping = self.configurations.get('ohlcv.column.mapping', {})
        # Validate required columns
        if not all(col in analysedData.columns for col in 
                   [columnMapping.get('High', 'High'), 
                    columnMapping.get('Low', 'Low'), 
                    columnMapping.get('Close', 'Close')]):
            raise ValueError(
                "Input data must contain 'High', 'Low', and 'Close' columns."
            )
        
        HighColumn = columnMapping.get('High', 'High')
        LowColumn = columnMapping.get('Low', 'Low')
        CloseColumn = columnMapping.get('Close', 'Close')

        
        # Extract OHLC data as numpy arrays (TA-Lib requirement)
        high = data[HighColumn].values.astype(float)
        low = data[LowColumn].values.astype(float)
        close = data[CloseColumn].values.astype(float)
        
        # Calculate ADX and directional indicators using TA-Lib
        try:
            adx_values = talib.ADX(
                high, 
                low, 
                close, 
                timeperiod=self.adx_length
            )
            
            plus_di = talib.PLUS_DI(
                high, 
                low, 
                close, 
                timeperiod=self.di_length
            )
            
            minus_di = talib.MINUS_DI(
                high, 
                low, 
                close, 
                timeperiod=self.di_length
            )
            
        except Exception as e:
            logging.error(f"TA-Lib ADX calculation failed: {str(e)}")
            raise
        
        # Add calculated values to dataframe
        analysedData['adx'] = np.round(adx_values, 0)
        analysedData['posDI'] = np.round(plus_di, 2)
        analysedData['negDI'] = np.round(minus_di, 2)
        
        # Calculate slopes (rate of change)
        analysedData['posDISlope'] = np.round(
            analysedData['posDI'].diff(), 0
        )
        analysedData['negDISlope'] = np.round(
            analysedData['negDI'].diff(), 2
        )
        analysedData['adxSlope'] = np.round(
            analysedData['adx'].diff(), 2
        )
        
        # Fill NaN values with 0
        analysedData = analysedData.fillna(0)
        
        # Log summary statistics
        valid_adx = analysedData['adx'][analysedData['adx'] != 0]
        if len(valid_adx) > 0:
            logging.debug(
                f"ADX calculation completed. "
                f"ADX range: {valid_adx.min():.2f} - {valid_adx.max():.2f}, "
                f"Mean: {valid_adx.mean():.2f}"
            )
            logging.debug(analysedData[['Datetime', 'adx', 'posDI', 'negDI']].tail(10))
        
        return analysedData
