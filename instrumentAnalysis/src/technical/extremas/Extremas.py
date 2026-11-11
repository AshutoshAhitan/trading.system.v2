from pandas.core.series import Series
import trendln
from typing import List

class Extremas:
    
    @staticmethod
    def getMaximaPoints(data: Series, method: int) -> Series:

        maxima = Series([-1]*len(data))

        maximaIdx: List[int]
        _, maximaIdx = trendln.get_extrema(data, extmethod=method, accuracy=2)

        maxima.iloc[maximaIdx] = data.iloc[maximaIdx]

        return maxima



    @staticmethod
    def getMinimaPoints(data: Series, method: int) -> Series:

        minima = Series([-1]*len(data))

        minimaIdx: List[int]
        minimaIdx, _ = trendln.get_extrema(data, extmethod=method, accuracy=2)

        minima.iloc[minimaIdx] = data.iloc[minimaIdx]

        return minima
