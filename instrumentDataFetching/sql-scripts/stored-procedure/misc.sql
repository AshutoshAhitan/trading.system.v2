
delete a from delivery a, 
(select * from delivery where date not in (select date from ohlcv where Timeframe='1d')) b
where a.Date=b.Date and a.Symbol=b.Symbol

