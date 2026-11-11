# -----------------------------------------------------------------------
from datetime import datetime
import logging, argparse, os
import signal, threading
import multiprocessing
from src.technical.TechnicalFactory import TechnicalFactory
from src.marketBreadth.MarketBreadth import MarketBreadth
from src.fundamental.FundamentalFactory import FundamentalFactory
# -----------------------------------------------------------------------


# -------------- SIGNAL HANDLER ---------------- #
def send_sigusr2(pid):
    os.kill(pid, signal.SIGUSR2)


# -------------- PID HANDLER ---------------- #
def _pid(pidFilePath):
    try:
        with open(pidFilePath, 'r') as f:
            pid_str = f.read().strip()
            if not pid_str:
                return None
            pid = int(pid_str)
            return pid
    except Exception as e:
        logging.error(f"Error reading PID file: {e}")
        return None

def run_analysis(a, ta_choices, args, symbols):
    if a not in ta_choices:
        raise Exception(f'Invalid analysis choice: {a}')

    action = a.split('.')
    if len(action) == 3:
        analysisType = action[0] + '.' + action[1]
        analysisFunction = action[2]
    else:
        analysisType = action[0]
        analysisFunction = action[1]

    if analysisType == 'fa':
        analysis = FundamentalFactory.create(f'./config/fundamental/{analysisFunction}.json',
                                     './config/database.json',
                                    symbols, analysisName=analysisFunction)
    elif analysisType == 'ta.equities':
        analysis = TechnicalFactory.create(f'./config/technical/equities/{analysisFunction}.json',
                                     './config/database.json',
                                    symbols, technicalAnalysisName=analysisFunction)
    elif analysisType == 'ta.indices':
        analysis = TechnicalFactory.create(f'./config/technical/indices/{analysisFunction}.json',
                                     './config/database.json',
                                    symbols, technicalAnalysisName=analysisFunction)
    elif analysisType == 'breadth':
        analysis = MarketBreadth(f'./config/breadth/{analysisFunction}.json',
                                 './config/database.json',
                                 symbols)
    elif analysisType == 'ta.indices.oi':
        analysis = TechnicalFactory.create(f'./config/technical/indices/{analysisFunction}.json',
                                     './config/database.json',
                                    symbols, technicalAnalysisName=analysisFunction)
    else:
        raise Exception('Invalid analysis type.')

    analysis.compute(timeframe=args.t)


if __name__ == '__main__':
    # Save PID to file
    with open("./pid/app.pid", "w") as pidfile:
        pidfile.write(str(os.getpid()))

    wake_event = threading.Event()

    def sigusr2_handler(signum, frame):
        wake_event.set()

    signal.signal(signal.SIGUSR2, sigusr2_handler)

    parser = argparse.ArgumentParser()

    parser.add_argument('-debug-level', help="debug level",
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
        default='INFO')
    parser.add_argument('-symbolList')
    parser.add_argument('-a')
    ta_choices=['ta.equities.volume', 
                 'ta.equities.ma', 
                 'ta.equities.volatility', 
                 'ta.equities.zones',
                 'ta.equities.candlestick', 
                 'ta.equities.pricerange', 
                 'ta.equities.slope',
                 'ta.indices.ma', 
                 'ta.indices.candlestick', 
                 'ta.indices.heikinAshiCandlestick', 
                 'ta.indices.adx',
                 'ta.indices.heikinAshiMA',
                 'ta.indices.oi',
                 'fa.quarterly', 
                 'fa.annualy', 
                 'breadth.market']
    parser.add_argument('-t', help="timeframe", choices=['1wk', '1d', '60m', '1m'], default='1d')
    parser.add_argument('-l', help="loop forever", default=False)

    args = parser.parse_args()
    print(args)

    level = 'logging.{}'.format(args.debug_level)
    # logging.basicConfig(filename='./logs.txt', format='%(asctime)s %(levelname)s > %(message)s', level=eval(level))
    logging.basicConfig(format='%(module)s : %(funcName)s> %(message)s', level=eval(level))

    symbols = []
    if args.symbolList is not None:
        symbols = args.symbolList.split(',')
    else:
        symbols = []

    ta = args.a.split(',')

    # convert args.l to boolean
    if args.l == 'true' or args.l == 'True':
        args.l = True
    else:
        args.l = False

    while True:
        print(f'_____ Running analyses: {ta} _____')
        processes = []
        for a in ta:
            run_analysis(a, ta_choices, args, symbols)

        if args.l == False:
            break
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            logging.info(f'completed analyses at {now}, sleeping until next signal...')

            long_pid = _pid("../instrumentStrategy/pid/app.long.pid")
            short_pid = _pid("../instrumentStrategy/pid/app.short.pid")

            if long_pid == None and short_pid == None:
                logging.error("Could not read PID(s) from file. Ensure that the strategy app is running and PID files are correctly created.")
            else:
                if long_pid != None:
                    logging.info(f"Sending SIGUSR2 to strategy app with PID: {long_pid}")
                    send_sigusr2(long_pid)
                else:
                    logging.warning("Long strategy PID is None. Skipping SIGUSR2 signal for long strategy.")

                if short_pid != None:
                    logging.info(f"Sending SIGUSR2 to strategy app with PID: {short_pid}")
                    send_sigusr2(short_pid)
                else:
                    logging.warning("Short strategy PID is None. Skipping SIGUSR2 signal for short strategy.")

            print('<< ______')
            wake_event.clear()
            wake_event.wait()  # Sleep until SIGUSR2 is received
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            logging.info(f'recieved signal to wake up at {now}, running analyses...')
