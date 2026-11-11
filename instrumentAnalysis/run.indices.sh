if [ "$1" == "loop" ]; then
    python main.py -a=ta.indices.heikinAshiCandlestick,ta.indices.heikinAshiMA,ta.indices.candlestick,ta.indices.adx -symbolList='NIFTY 50' -t=1m -l=true
else
    python main.py -a=ta.indices.heikinAshiCandlestick,ta.indices.heikinAshiMA,ta.indices.candlestick,ta.indices.adx -t=1m -l=false
    # python main.py -a=ta.indices.heikinAshiCandlestick -t=1m -l=false -debug-level=DEBUG
fi
