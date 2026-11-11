from bs4 import BeautifulSoup
import re

def parseScreenerTableHeaders(tableHeadersHtml):

    headers = tableHeadersHtml.find_all('th')
    headers = [header.text for header in headers if len(header.text) != 0]

    return headers


def parseScreenerTableBody(tableBodyHtml):

    rows = tableBodyHtml.find_all('tr')
    data = []
    for row in rows:
        tableData = row.find_all('td')
        tableData = [data.text.strip() for data in tableData]
        tableData = [re.sub(r'\xa0\+', '', data) for data in tableData]
        data.append(tableData)

    return data

def parseScreenerTable(tableHeadersHtml, tableBodyHtml):
    table = {}

    headers = parseScreenerTableHeaders(tableHeadersHtml)
    dates = [' '.join(date.split()) for date in headers]

    tdata = parseScreenerTableBody(tableBodyHtml)

    topics = [row[0] for row in tdata]

    for idx, aTopic in enumerate(topics):
        table[aTopic] = {
            'Date' : dates,
            'data' : tdata[idx][1:]
        }

    return table
