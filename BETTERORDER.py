#!/usr/bin/python
'''
This strategy works by place an profitable order against a just filled one
'''
import apikey
from dudubinance.accountcache import AccountCache
from dudubinance.symbolsinfo import *
from binance.client import Client
#from __future__ import print_function
import json
import threading
import time

stepratio = 0.002
tradeamount = 100
orderamount = 20
baseasset = 'BNB'
quoteasset = 'BTC'
thesymbol = baseasset+quoteasset






client = Client(apikey.account['key'], apikey.account['secret'])
refresh_symbolsinfo()

ac = AccountCache(client, thesymbol)


def safePlaceLimitOrder(NEWSIDE, SYMBOL, NEWQUANTITY,NEWPRICE):
    print("Placing an order: {} {} {}@{}".format(NEWSIDE, SYMBOL, NEWQUANTITY,NEWPRICE))
    try:
        REALPRICE = format(round(int(NEWPRICE/symbolsInfo[SYMBOL]['tickSize']) * symbolsInfo[SYMBOL]['tickSize'] * 100000000 ) / 100000000,".8f")
        order = client.order_limit(
            symbol=SYMBOL,
            quantity=NEWQUANTITY,
            side=NEWSIDE,
            price=REALPRICE
            #newOrderRespType='FULL'
            )
        print("Placed")
    except ValueError:
        pass
    #print(json.dumps(order, indent=4, sort_keys=True))

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
            NEWPRICE = OLDPRICE/(1-stepratio)
        else:
            NEWSIDE = "BUY"
            NEWPRICE = OLDPRICE*(1-stepratio)

        safePlaceLimitOrder(NEWSIDE, msg['symbol'], msg['origQty'],NEWPRICE)




ac.registerOrderCallback(thesymbol,process_order_msg)

#fill 
depth = client.get_order_book(symbol=thesymbol)
askprice = float(depth['asks'][0][0])
i = 0
while i < orderamount and ac.getBalance(baseasset) >= tradeamount :
    safePlaceLimitOrder('SELL',thesymbol,tradeamount, askprice)
    time.sleep(1)
    askprice*=(1+stepratio)
    i+=1
