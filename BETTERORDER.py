#!/usr/bin/python
'''
This strategy works by place an profitable order against a just filled one
'''
from binance.client import Client
from ACCOUNTS import accounts
from dudubinance.clientfactory import clientFactory
from dudubinance.accountcache import AccountCache
from dudubinance.executor import Executor
from twisted.internet import reactor

import json
import threading
import time

STEPRATIO = 0.002


class MarketMaker(object):
    def __init__(self, baseasset, quoteasset, tradeqty):
        self._BASEASSET = baseasset
        self._QUOTEASSET = quoteasset
        self._TRADEQUANTITY = tradeqty
        self._THESYMBOL = self._BASEASSET+self._QUOTEASSET

#list
marketmakers = {
'GTOBNB':MarketMaker('GTO','BNB',500),
'QTUMBNB':MarketMaker('QTUM','BNB',15)
}

# Client Initialization
client = clientFactory(accounts)

ac = AccountCache(client)
for symbol in marketmakers:
    print('addSymbol:'+symbol)
    ac.addSymbol(symbol)

executor = Executor(client)



def process_order_msg(msg):
    # if a limite order is filled
    #print(json.dumps(msg, indent=4, sort_keys=True))
    if msg['type'] == "LIMIT" and msg['status'] == "FILLED":
        # and int(float(msg['origQty'])) == marketmakers[msg['symbol']]._TRADEQUANTITY:
        # msg['symbol'] == THESYMBOL and 
        OLDPRICE = float(msg['price'])
        '''
        if not SYMBOL in symbolsInfo:
            print("{} is not included, refresh".format(SYMBOL))
            refresh_symbolsinfo()
        '''

        if(msg['side'] == "BUY"):
            NEWSIDE = "SELL"
            NEWPRICE = OLDPRICE*(1+STEPRATIO)
        else:
            NEWSIDE = "BUY"
            NEWPRICE = OLDPRICE/(1+STEPRATIO)

        executor.safePlaceLimitOrder(NEWSIDE, msg['symbol'], msg['origQty'],NEWPRICE)
        orders = ac.getOrders(msg['symbol'])
        #Auto place new
        if(len(orders['BUY']) == 0):
            executor.safePlaceLimitOrder('BUY', msg['symbol'], msg['origQty'],float(orders['SELL'][0]['price'])/(1+STEPRATIO)/(1+STEPRATIO))
        elif(len(orders['SELL']) == 0):
            executor.safePlaceLimitOrder('SELL', msg['symbol'], msg['origQty'],float(orders['BUY'][0]['price'])*(1+STEPRATIO)*(1+STEPRATIO))
            


def fill(marketmaker):
    #fill 
    depth = client.get_order_book(symbol=marketmaker._THESYMBOL)
    orders = ac.getOrders(marketmaker._THESYMBOL)
    averageprice = (float(depth['asks'][0][0]) + float(depth['bids'][0][0]))/2

    askprice = averageprice * (1 + STEPRATIO)
    myaskprice = askprice * 2

    if len(orders['SELL']) > 0:
        myaskprice = float(orders['SELL'][0]['price'])
        print("my lowest ask price: {}".format(myaskprice))
    basebalance = float(ac.getBalance(marketmaker._BASEASSET)['free'])
    print("my free {}: {}".format(marketmaker._BASEASSET,basebalance))
    executor.placeOrderUntil("SELL",askprice,myaskprice,STEPRATIO,marketmaker._THESYMBOL,marketmaker._TRADEQUANTITY,basebalance,3)

    bidprice =  averageprice / (1 + STEPRATIO)
    mybidprice = bidprice/2
    if len(orders['BUY']) > 0:
        mybidprice = float(orders['BUY'][0]['price'])
        print("my highest bidprice is {}".format(mybidprice))
    quotebalance =  float(ac.getBalance(marketmaker._QUOTEASSET)['free'])
    print("my free {}: {}".format(marketmaker._QUOTEASSET,quotebalance))
    executor.placeOrderUntil("BUY",bidprice,mybidprice,STEPRATIO,marketmaker._THESYMBOL,marketmaker._TRADEQUANTITY,quotebalance,3)
    #end of fill


for symbol in marketmakers:
    ac.registerOrderCallback(symbol,process_order_msg)

print("help/fill/exit")

while True:
    try:
        something = raw_input()
        if(something == "exit"):
            raise NameError("random")
        if(something == "help"):
            print("help/fill/exit")
        if(something == "fill"):

            for symbol in marketmakers:
                fill(marketmakers[symbol])
    except:
        ac.clear()
        reactor.stop()
        break
