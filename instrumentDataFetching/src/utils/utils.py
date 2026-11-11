import dateparser, sys, os, json
from typing import Optional
from datetime import timedelta, timezone, datetime
import ntplib, logging

def getStartDateEndDate(period: str):

	startDate = dateparser.parse(period)
	startDate = startDate.date()
	endDate = dateparser.parse('today')
	endDate = endDate.date()

	return startDate, endDate


def read_config_files(filepath):
    configurations = {}

    for root, _, file_list in os.walk(filepath):

        for file in file_list:
            filename = file.split('.')[0]
            if file.endswith('json') is False: continue

            try:
                with open(root + '/' + file) as fd:
                    content = fd.read()
                    content = json.loads( content )
                    configurations[filename] = content
            except:
                print('UNEXPECTED ERROR IN CONFIG FILE :: ', sys.exc_info()[0])
                print('FILENAME :: {}'.format(file))
                sys.exit()

    # print(json.dumps(configurations, indent=4))
    return configurations


def get_configurations(filepath):
    return read_config_files(filepath)


def readConfigFile(configPath: str):

    configurations: Optional[dict] = None
    with open(configPath) as file:
        content = file.read()
        configurations = json.loads(content)
        assert configurations != None

    return configurations


def secondsToNextMinute(offset):
    IST = timezone(timedelta(hours=5, minutes=30))
    ntp_client = ntplib.NTPClient()
    while True:
        try:
            response = ntp_client.request('time.google.com', version=3)
            now_utc = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            now = now_utc.astimezone(IST)
        except Exception as e:
            logging.warning(f"NTP sync failed: {e}, using local time.")
            continue

        seconds_to_next_minute = 60 - now.second + offset
        return seconds_to_next_minute
