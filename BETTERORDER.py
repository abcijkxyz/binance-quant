#!/usr/bin/python
'''
This strategy works by place an profitable order against a just filled one
'''
import apikey
from dudubinance.accountcache import AccountCache
from dudubinance.executor import Executor
from binance.client import Client
import json
import threading
import time

STEPRATIO = 0.002
TRADEQUANTITY = 100
ORDERAMOUNT = 20
BASEASSET = 'BNB'
QUOTEASSET = 'BTC'
THESYMBOL = BASEASSET+QUOTEASSET

client = Client(apikey.account['key'], apikey.account['secret'])

ac = AccountCache(client, THESYMBOL)
executor = Executor(client)



def process_order_msg(msg):
    # if a limite order is filled
    #print(json.dumps(msg, indent=4, sort_keys=True))

    if msg['type'] == "LIMIT" and msg['status'] == "FILLED":
        OLDPRICE = float(msg['price'])
        '''
        if not SYMBOL in symbolsInfo:
            print("{} is not included, refresh".format(SYMBOL))
            refresh_symbolsinfo()
        '''

        if(msg['side'] == "BUY"):
            NEWSIDE = "SELL"
            NEWPRICE = OLDPRICE/(1-STEPRATIO)
        else:
            NEWSIDE = "BUY"
            NEWPRICE = OLDPRICE*(1-STEPRATIO)

        executor.safePlaceLimitOrder(NEWSIDE, msg['symbol'], msg['origQty'],NEWPRICE)
        orders = ac.getOrders(msg['symbol'])
        if len(orders[msg['side']]) == 0:
            depth = client.get_order_book(symbol=msg['symbol'])
            if msg['side'] == "SELL":
                basebalance = float(ac.getBalance(BASEASSET)['free'])
                executor.placeOrderUntil("SELL",float(depth['asks'][0][0]),float(depth['asks'][0][0]) * 2,STEPRATIO,msg['symbol'],TRADEQUANTITY,basebalance,ORDERAMOUNT)
            if msg['side'] == "BUY":
                quotebalance = float(ac.getBalance(QUOTEASSET)['free'])
                executor.placeOrderUntil("BUY",float(depth['bids'][0][0]),float(depth['bids'][0][0]) / 2,STEPRATIO,msg['symbol'],TRADEQUANTITY,quotebalance,ORDERAMOUNT)


ac.registerOrderCallback(THESYMBOL,process_order_msg)
#fill 
depth = client.get_order_book(symbol=THESYMBOL)
orders = ac.getOrders(THESYMBOL)


askprice = float(depth['asks'][0][0])
myaskprice = askprice * 2

if len(orders['SELL']) > 0:
    myaskprice = float(orders['SELL'][0]['price'])
    print("my lowest ask price: {}".format(myaskprice))
basebalance = float(ac.getBalance(BASEASSET)['free'])
print("my free {}: {}".format(BASEASSET,basebalance))

executor.placeOrderUntil("SELL",askprice,myaskprice,STEPRATIO,THESYMBOL,TRADEQUANTITY,basebalance,ORDERAMOUNT)

bidprice = float(depth['bids'][0][0])
mybidprice = bidprice/2
if len(orders['BUY']) > 0:
    mybidprice = float(orders['BUY'][0]['price'])
    print("my highest bidprice is {}".format(mybidprice))
quotebalance =  float(ac.getBalance(QUOTEASSET)['free'])
print("my free {}: {}".format(QUOTEASSET,quotebalance))

executor.placeOrderUntil("BUY",bidprice,mybidprice,STEPRATIO,THESYMBOL,TRADEQUANTITY,quotebalance,ORDERAMOUNT)
