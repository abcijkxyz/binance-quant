
from __future__ import print_function
import json
import threading
import time

from binance.client import Client
from binance.depthcache import DepthCacheManager
from binance.enums import *

mylock = threading.Lock()

import config 
# Client Initialization
client = Client(config.account['key'], config.account['secret'])

def process_any_depth(depth_cache):
    global BDCs
    global client

    BNBETH_dc = DCMs['BNBETH'].get_depth_cache();
    BNBBTC_dc = DCMs['BNBBTC'].get_depth_cache();
    ETHBTC_dc = DCMs['ETHBTC'].get_depth_cache();

    BNBETH_bestbid = BNBETH_dc.get_bids()[0]
    BNBETH_bestask = BNBETH_dc.get_asks()[0]
    BNBBTC_bestbid = BNBBTC_dc.get_bids()[0]
    BNBBTC_bestask = BNBBTC_dc.get_asks()[0]
    ETHBTC_bestbid = ETHBTC_dc.get_bids()[0]
    ETHBTC_bestask = ETHBTC_dc.get_asks()[0]

    
    #BNB->ETH->BTC->BNB
    BEBRatio = BNBETH_bestbid[0] * ETHBTC_bestbid[0] /BNBBTC_bestask[0] - 1.0015
    BEBCapacity = int(min(BNBETH_bestbid[1], int(ETHBTC_bestbid[1]/BNBETH_bestbid[0]),BNBBTC_bestask[1]))
    if(BEBCapacity * BEBRatio>0.1):
        print("{}\tBNB->ETH->BTC->BNB Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio,BEBCapacity))
    else:
        print("{}\tBNB->ETH->BTC->BNB Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio))

        
    #BNB->BTC->ETH->BNB
    BBERatio = BNBBTC_bestbid[0]  /ETHBTC_bestask[0] /BNBETH_bestask[0] - 1.0015
    BBECapacity = int(min(BNBETH_bestask[1], int(ETHBTC_bestask[1]/BNBETH_bestask[0]),BNBBTC_bestbid[1]))
    if(BBECapacity * BBERatio>0.1):
        print("{}\tBNB->BTC->ETH->BNB Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio,BBECapacity))
    else:
        print("{}\tBNB->BTC->ETH->BNB Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio))

# Set up watched depth cache
DCMs={}
DCMs['BNBBTC'] = DepthCacheManager(client,'BNBBTC',process_any_depth);
DCMs['BNBETH'] = DepthCacheManager(client,'BNBETH',process_any_depth);
DCMs['ETHBTC'] = DepthCacheManager(client,'ETHBTC',process_any_depth);






#something about user socket
'''
#handler of account update event
def process_usersocket_message(msg):
    if(msg['e'] == "outboundAccountInfo"):
        #print("message type:" + msg['e'])
        #print(msg)
        print(json.dumps(msg, indent=4, sort_keys=True))
    
    
from binance.websockets import BinanceSocketManager
bm1 = BinanceSocketManager(client)
bm1.start_user_socket()
bm1.start()
'''

