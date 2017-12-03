'''
This strategy works by place an profitable order against a just filled one
'''
from __future__ import print_function
import json
import threading
import time

from binance.client import Client
from binance.enums import *

import config 
from symbolsinfo import *

# Client Initialization
client = Client(config.account['key'], config.account['secret'])
refresh_symbolsinfo()

#handler of account update event
def process_usersocket_message(msg):
    # if a limite order is filled
    #print(json.dumps(msg, indent=4, sort_keys=True))

    if msg['e'] == "executionReport" and msg['o'] == "LIMIT":
        SYMBOL = msg['s']
        OLDSIDE = msg['S']
        OLDPRICE = float(msg['p'])
        OLDQUANTITY = float(msg['q'])
        print("{} An order {}:{} {} {}@{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),msg['X'],OLDSIDE,SYMBOL,OLDQUANTITY,OLDPRICE))
        if not msg['X'] == "FILLED":
            return
        else:
            time.sleep(1)

        if not SYMBOL in symbolsInfo:
            print("{} is not included, refresh".format(SYMBOL))
            refresh_symbolsinfo()

        if(OLDSIDE == "BUY"):
            NEWSIDE = "SELL"
            NEWPRICE = int(OLDPRICE/(1-config.better['margin'])/symbolsInfo[SYMBOL]['tickSize']) * symbolsInfo[SYMBOL]['tickSize']
            NEWQUANTITY = OLDQUANTITY
        else:
            NEWSIDE = "BUY"
            NEWPRICE = int(OLDPRICE*(1-config.better['margin'])/symbolsInfo[SYMBOL]['tickSize']) * symbolsInfo[SYMBOL]['tickSize']
            NEWQUANTITY = OLDQUANTITY

        print("Placing an order: {} {} {}@{}".format(NEWSIDE, SYMBOL, NEWQUANTITY,NEWPRICE))
        try:
            order = client.order_limit(
                symbol=SYMBOL,
                quantity=NEWQUANTITY,
                side=NEWSIDE,
                price=format(NEWPRICE,".8f")
                #newOrderRespType='FULL'
                )
            print("Placed")
        except ValueError:
            print("Something goes wrong")
        #print(json.dumps(order, indent=4, sort_keys=True))
from binance.websockets import BinanceSocketManager
bm1 = BinanceSocketManager(client)
bm1.start_user_socket(process_usersocket_message)
bm1.start()
