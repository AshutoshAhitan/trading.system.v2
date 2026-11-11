from pandas.core.frame import DataFrame

def getSubsetOfData(data: DataFrame, subsetSize: int) -> DataFrame:

    analysedData = DataFrame([])

    dataLength = len(data)
    if dataLength <= subsetSize:
        analysedData = DataFrame(data)
    else:
        analysedData = DataFrame(data[len(data)-subsetSize:])

    analysedData = analysedData.reset_index()

    return analysedData
