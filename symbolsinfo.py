'''
retrieve and reorganize infos about symbol
min prize, min qty etc.
'''
import requests
import json
symbolsInfo = {}
def refresh_symbolsinfo():
    global symbolsInfo
    url = 'https://api.binance.com/api/v1/symbolsInfo'
    jsondata = requests.get(url).json()
    for eachsymbol in jsondata['symbols']:
        if not eachsymbol['symbol'] in symbolsInfo:
            symbolsInfo[eachsymbol['symbol']]={}
        for filter in eachsymbol['filters']:
            if 'minPrice' in filter:
                symbolsInfo[eachsymbol['symbol']]['minPrice'] = float(filter['minPrice'])
            if 'tickSize' in filter:
                symbolsInfo[eachsymbol['symbol']]['tickSize'] = float(filter['tickSize'])
            if 'minQty' in filter:
                symbolsInfo[eachsymbol['symbol']]['minQty'] = float(filter['minQty'])
            if 'stepSize' in filter:
                symbolsInfo[eachsymbol['symbol']]['stepSize'] = float(filter['stepSize'])
            if 'minNotional' in filter:
                symbolsInfo[eachsymbol['symbol']]['minNotional'] = float(filter['minNotional'])