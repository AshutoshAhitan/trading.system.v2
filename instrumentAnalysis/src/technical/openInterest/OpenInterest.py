from pandas.core.frame import DataFrame
from ..Technical import Technical
import numpy as np
import logging

class OpenInterest(Technical):
    def replace_zero_with_previous(self, series):
        """
        Replace 0 values in a pandas Series with the previous non-zero value.
        """
        s = series.copy()
        s = s.replace(0, np.nan)
        s = s.ffill()
        return s

    def __init__(self, configurations, dbConfigPath, symbolList) -> None:
        super().__init__(configurations, dbConfigPath, symbolList)
        self.configurations = configurations


    def calculate_oi_change(self, data: DataFrame) -> DataFrame:
        """
        Adds a column 'oi_change' to the DataFrame, representing the change in open interest (oi)
        between the current and previous row.
        """
        data = data.copy()
        # Replace 0 in oi_change with previous non-zero value
        data['oi_change'] = data['oi'].diff()
        data['oi_change'] = self.replace_zero_with_previous(data['oi_change'])
        data['oi_change'] = data['oi_change'].fillna(0)
        return data

    def perform(self, data) -> DataFrame:

        analysedData = DataFrame(data)
        analysedData = self.calculate_oi_change(analysedData)
        print(analysedData)
        return analysedData
    

