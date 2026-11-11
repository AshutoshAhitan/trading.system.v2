import logging, requests
from datetime import date

class EarningsCalender(object):

    def __init__(self, config) -> None:
        self.config = config
        self.session = requests.session()
        self.headers = config['headers']

    def fetch(self, symbol):

        calender = []

        self.session.get(self.config['host'], headers=self.headers)

        earningsCalenderUrl = f'{self.config["host"]}/{self.config["earnings.calender"]}'
        earningsCalenderUrl = earningsCalenderUrl.replace("{symbol}", symbol)
        logging.debug(f'Fetching earnings calendar for symbol: {symbol} with URL: {earningsCalenderUrl}')

        response = self.session.get(url=earningsCalenderUrl, headers=self.headers)
        if response.status_code == 200:
            results = response.json()
            for result in results:
                logging.debug(f'Processing result: {result}')
                if result['consolidated'].lower() == 'non-consolidated':
                    filtered_result = {k: v for k, v in result.items() if k in self.config['earnings.calender.desired_keys']}
                    calender.append(filtered_result)

            if len(calender) > 13:
                calender = calender[:13]
            logging.debug(f'Filtered earnings data for {symbol}: {calender}')
        else:
            logging.error(f'Failed to fetch earnings data for {symbol}: {response.status_code} - {response.text}')
            raise Exception(f'Failed to fetch earnings data for {symbol}: {response.status_code}')

        return calender
