import pandas as pd
import talib as tb

# Assuming you have a DataFrame named 'df' with 'High', 'Low', and 'Close' columns
# Example data (replace with your actual data)
data = {'High': [10, 12, 11, 13, 15, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
            'Low': [8, 9, 8, 10, 12, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
            'Close': [9, 11, 10, 12, 14, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]}
df = pd.DataFrame(data)

df['ADX'] = tb.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
print(df.tail())
