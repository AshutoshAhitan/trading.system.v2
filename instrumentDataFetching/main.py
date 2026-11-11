# --------------------------------------------------------------
import time
from src.Indices.ohlcv.IndicesFactory import IndicesFactory
from src.Indices.constituent.IndexContituentFactory import IndexConstituentFactory
from src.Fundamentals.Fundamentals import Fundamentals
from src.Ohlcv.ohlcvFactory import ohlcvFactory
from src.Liquidity.LiquidityFactory import LiquidityFactory
from src.Delivery.deliveryFactory import DeliveryFactory
from src.TradingActivity.TradingActivityFactory import TradingActivityFactory
from src.Instrument.InstrumentFactory import InstrumentFactory
import argparse, logging
from src.Sectors.SectorsFactory import SectorsFactory
from src.Indices.fno.StrikePriceFactory import StrikePriceFactory
from src.Indices.stream.Stream import stream, test_stream
# --------------------------------------------------------------


# --------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-dataTobeFetched', help="type of data to be fetched for an Instrument",
        choices=['ohlcv', 
                 'ohlcv.stream',
                 'instruments', 
                 'instruments.liquidity', 
                 'delivery', 
                 'tradingActivity', 
                 'sectors', 
                 'fundamentals', 
                 'indices',
                 'indices.constituent', 
                 'indices.fno.ohlcv'], required=True)

    parser.add_argument('-symbolList', default='')

    parser.add_argument('-debug-level', help="debug level",
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
        default='INFO')

    parser.add_argument('-loop', default=False)
    parser.add_argument('-streaming', default=False)

    args = parser.parse_args()
    print(args)

    level = 'logging.{}'.format(args.debug_level)
    # logging.basicConfig(filename='./logs/logs.txt', format='%(asctime)s %(levelname)s > %(message)s', level=eval(level))
    logging.basicConfig(format='%(module)s : %(funcName)s> \n %(message)s', level=eval(level))

    args.streaming = bool(args.streaming)

    symbols = []
    if len(args.symbolList):
        symbols: list = args.symbolList.split(',')


    # --------------------------------------------------------------
    if args.dataTobeFetched in ['ohlcv']:

        ohlcv = ohlcvFactory.create(
                configPath='./config/ohlcv.json',
                dbConfigPath='./config/database.json',
                symbolList=symbols)
        ohlcv.fetch()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['instruments.liquidity']:
        liquidity = LiquidityFactory.create(
                configPath='./config/liquidity.json',
                dbConfigPath='./config/database.json',
                symbolList=symbols)

        liquidity.fetch()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['delivery']:

        delivery = DeliveryFactory.create(
            configPath='./config/delivery.json',
            dbConfigPath='./config/database.json',
            symbolList=symbols)

        delivery.fetch()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['tradingActivity']:

        tradingAcitvity = TradingActivityFactory.create(
                configPath='./config/tradingActivity.json',
                dbConfigPath='./config/database.json')

        tradingAcitvity.fetchTradingActivity().save()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['sectors']:

        sectors = SectorsFactory.create(
                configPath='./config/sectors.json',
                dbConfigPath='./config/database.json')

        sectors.save(sectors.fetch())


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['fundamentals']:

        fundamentals = Fundamentals(
                configPath='./config/fundamentals.json',
                dbConfigPath='./config/database.json', symbolList=symbols)

        fundamentals.fetch()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['indices']:

        indices = IndicesFactory.create(
                configPath='./config/indices.json',
                dbConfigPath='./config/database.json', symbolList=symbols)

        if args.loop:
            while True:
                logging.info(">> Fetching Indices OHLCV data ___")
                indices.fetch()
                logging.info('<< ________________')
                # time.sleep(0.050)
        else:
            indices.fetch()


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['ohlcv.stream']:
        stream(
            streamConfigPath='./config/indices.json',
            ohlcvConfigPath='./config/ohlcv.json',
            dbConfigPath='./config/database.json',
            pidFilePath='../instrumentStrategy/pid/app.long.pid')


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['indices.constituent']:

        indicesConstituent = IndexConstituentFactory.create(configPath='./config/indices.json',
                                                            dbConfigPath='./config/database.json')
        indicesConstituent.save(indicesConstituent.fetch())


    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['indices.fno.ohlcv']:

        indicesFnoOhlcv = StrikePriceFactory.create(
                configPath='./config/indices.json',
                dbConfigPath='./config/database.json')

        indicesFnoOhlcv.fetch()

    
    # --------------------------------------------------------------
    elif args.dataTobeFetched in ['instruments']:

        instruments = InstrumentFactory.create(
                configPath='./config/instrument.json',
                dbConfigPath='./config/database.json')

        instruments.w_fetchListedInstrument()
# --------------------------------------------------------------
