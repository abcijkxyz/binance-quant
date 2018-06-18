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

STEPRATIO = 0.001


class MarketMaker(object):
    def __init__(self, baseasset, quoteasset, tradeqty):
        self._BASEASSET = baseasset
        self._QUOTEASSET = quoteasset
        self._TRADEQUANTITY = tradeqty
        self._THESYMBOL = self._BASEASSET+self._QUOTEASSET

#list
marketmakers = {
#'GTOBNB':MarketMaker('GTO','BNB',150),
#'RDNBNB':MarketMaker('RDN','BNB',30),
#'LOOMBNB':MarketMaker('LOOM','BNB',100),
'SKYBNB':MarketMaker('SKY','BNB',100),
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
        #Auto fill
        '''
        if(msg['side'] == 'BUY' and len(orders['BUY']) == 0):
            if(marketmakers[msg['symbol']]._BASEASSET == 'BNB'):
                executor.safePlaceLimitOrder('SELL', msg['symbol'], msg['origQty'],OLDPRICE)
            else:
                executor.safePlaceLimitOrder('BUY', msg['symbol'], msg['origQty'],OLDPRICE/(1+STEPRATIO))
        elif(msg['side'] == 'SELL' and len(orders['SELL']) == 0):
            if(marketmakers[msg['symbol']]._QUOTEASSET == 'BNB'):
                executor.safePlaceLimitOrder('BUY', msg['symbol'], msg['origQty'],OLDPRICE)
            else:
                executor.safePlaceLimitOrder('SELL', msg['symbol'], msg['origQty'],OLDPRICE*(1+STEPRATIO))
        '''
        #Auto fill
            


def fill(marketmaker):
    #fill 
    depth = client.get_order_book(symbol=marketmaker._THESYMBOL)
    orders = ac.getOrders(marketmaker._THESYMBOL)
    averageprice = (float(depth['asks'][0][0]) + float(depth['bids'][0][0]))/2



    askprice = averageprice * (1 + STEPRATIO)
    stopaskprice = askprice * 1.05
    if len(orders['SELL']) > 0:
        stopaskprice = float(orders['SELL'][0]['price'])
        print("my lowest ask price: {}".format(stopaskprice))
    basebalance = float(ac.getBalance(marketmaker._BASEASSET)['free'])
    print("my free {}: {}".format(marketmaker._BASEASSET,basebalance))
    executor.placeOrderUntil("SELL",askprice,stopaskprice,STEPRATIO,marketmaker._THESYMBOL,marketmaker._TRADEQUANTITY,basebalance)

    bidprice =  averageprice / (1 + STEPRATIO)
    stopbidprice = bidprice * 0.8
    if len(orders['BUY']) > 0:
        stopbidprice = float(orders['BUY'][0]['price'])
        print("my highest bidprice is {}".format(stopbidprice))
    quotebalance =  float(ac.getBalance(marketmaker._QUOTEASSET)['free'])
    print("my free {}: {}".format(marketmaker._QUOTEASSET,quotebalance))
    executor.placeOrderUntil("BUY",bidprice,stopbidprice,STEPRATIO,marketmaker._THESYMBOL,marketmaker._TRADEQUANTITY,quotebalance)
    #end of fill
    time.sleep(1)


for symbol in marketmakers:
    ac.registerOrderCallback(symbol,process_order_msg)

print("help/fill/exit/status/fill [symbol]/cancel [symbol]")

while True:
    try:
        something = raw_input()
        if(something == "exit"):
            raise NameError("exit")
        elif(something == "help"):
            print("help/fill/exit")
        elif(something == "fill"):
            for symbol in marketmakers:
                fill(marketmakers[symbol])
        elif(something == "status"):
            for symbol in marketmakers:
                print(symbol)
                orders = ac.getOrders(symbol)
                print(len(orders['BUY']))
                print(len(orders['SELL']))
        else:
            commands=something.split(" ")
            if(commands[0]=="fill"):
                fill(marketmakers[commands[1]])
            elif(commands[0]=="cancel"):
                orders = ac.getOrders(commands[1])
                executor.cancelOrders(orders['BUY'])
                executor.cancelOrders(orders['SELL'])
                
    except:
        ac.clear()
        reactor.stop()
        break
