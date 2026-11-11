psql -U ashutosh -h 127.0.0.1 -d equities -c "\COPY stocks(symbol, company) FROM '/home/ashutosh/trading.sy
stem/instrumentDataFetching/data/nse.indices/EQUITY_L.csv' DELIMITER ',' CSV HEADER;"
