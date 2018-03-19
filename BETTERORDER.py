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
TRADEQUANTITY = 500
ORDERAMOUNT = 50
BASEASSET = 'GTO'
QUOTEASSET = 'BNB'
THESYMBOL = BASEASSET+QUOTEASSET

# Client Initialization
client = clientFactory(accounts)

ac = AccountCache(client, THESYMBOL)
executor = Executor(client)



def process_order_msg(msg):
    # if a limite order is filled
    #print(json.dumps(msg, indent=4, sort_keys=True))

    if msg['symbol'] == THESYMBOL and msg['type'] == "LIMIT" and msg['status'] == "FILLED" and int(float(msg['origQty'])) == TRADEQUANTITY:
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


def fill():
    #fill 
    depth = client.get_order_book(symbol=THESYMBOL)
    orders = ac.getOrders(THESYMBOL)
    averageprice = (float(depth['asks'][0][0]) + float(depth['bids'][0][0]))/2

    askprice = averageprice * (1 + STEPRATIO)
    myaskprice = askprice * 2

    if len(orders['SELL']) > 0:
        myaskprice = float(orders['SELL'][0]['price'])
        print("my lowest ask price: {}".format(myaskprice))
    basebalance = float(ac.getBalance(BASEASSET)['free'])
    print("my free {}: {}".format(BASEASSET,basebalance))
    executor.placeOrderUntil("SELL",askprice,myaskprice,STEPRATIO,THESYMBOL,TRADEQUANTITY,basebalance,ORDERAMOUNT)

    bidprice =  averageprice / (1 + STEPRATIO)
    mybidprice = bidprice/2
    if len(orders['BUY']) > 0:
        mybidprice = float(orders['BUY'][0]['price'])
        print("my highest bidprice is {}".format(mybidprice))
    quotebalance =  float(ac.getBalance(QUOTEASSET)['free'])
    print("my free {}: {}".format(QUOTEASSET,quotebalance))
    executor.placeOrderUntil("BUY",bidprice,mybidprice,STEPRATIO,THESYMBOL,TRADEQUANTITY,quotebalance,ORDERAMOUNT)
    #end of fill


ac.registerOrderCallback(THESYMBOL,process_order_msg)
print("help/fill/exit")

while True:
    try:
        something = raw_input()
        if(something == "exit"):
            raise NameError("random")
        if(something == "help"):
            print("help/fill/exit")
        if(something == "fill"):
            fill()
    except:
        ac.clear()
        reactor.stop()
        break
