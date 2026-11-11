
if [ "$1" == "fno" ]; then
	time python main.py -dataTobeFetched='indices.fno.ohlcv' -debug-level=$2
elif [ "$1" == "ohlcv.stream" ]; then
	time python main.py -dataTobeFetched='ohlcv.stream' -debug-level=$2
else
	time python main.py -dataTobeFetched='indices' -debug-level=$1
fi




