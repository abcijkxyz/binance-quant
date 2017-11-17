
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
    with mylock:
        global DCs
        global client

        BNBETH_bestbid = float(DCs['BNBETH'].get_bids()[0])
        BNBETH_bestask = float(DCs['BNBETH'].get_asks()[0])
        BNBBTC_bestbid = float(DCs['BNBBTC'].get_bids()[0])
        BNBBTC_bestask = float(DCs['BNBBTC'].get_asks()[0])
        ETHBTC_bestbid = float(DCs['ETHBTC'].get_bids()[0])
        ETHBTC_bestask = float(DCs['ETHBTC'].get_asks()[0])

        
        #BNB->ETH->BTC->BNB
        BEBRatio = BNBETH_bestbid[0] * ETHBTC_bestbid[0] /BNBBTC_bestask[0] - 1.0015
        BEBCapacity = int(min(BNBETH_bestbid[1], int(ETHBTC_bestbid[1]/BNBETH_bestbid[0]),BNBBTC_bestask[1]))

        if(BEBCapacity * BEBRatio>0.1):
            #attemp to arbitrade
            print("{}\tBNB->ETH->BTC->BNB Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio,BEBCapacity))
            
            #sell BNB to ETH
            bnb2ethorder = client.order_market_sell(
                symbol='BNBETH',
                quantity=BEBCapacity,
                disable_validation=True,
                newOrderRespType='FULL'
                )
            print(json.dumps(bnb2ethorder, indent=4, sort_keys=True))
            ETHAmount = float(0)
            for fill in bnb2ethorder['fills']:
                ETHAmount += (float(fill['qty']) * float(fill['price']))
                if fill['commissionAsset'] == "ETH":
                    ETHAmount -= float(fill['commission'])
            print("Sell {} BNB into {} ETH".format(BEBCapacity, ETHAmount))

            #sell ETH to BTC
            eth2btcorder = client.order_market_sell(
                symbol='ETHBTC',
                quantity=format(ETHAmount,".3f"),
                disable_validation=True,
                newOrderRespType='FULL'
                )
            print(json.dumps(eth2btcorder, indent=4, sort_keys=True))
            BTCAmount = float(0)
            for fill in eth2btcorder['fills']:
                BTCAmount+=(float(fill['qty']) * float(fill['price']))
                if fill['commissionAsset'] == "BTC":
                    BTCAmount -= float(fill['commission'])
            print("Sell {} ETH into {} BTC".format(ETHAmount, BTCAmount))

            #buy BTC to BNB
            Buy_BNBAmount = 0
            Sell_BTCAmount = BTCAmount
            asks = DCs['BNBBTC'].get_asks()
            for ask in asks:
                cost = float(ask[0]) * float(ask[1])
                if Sell_BTCAmount < cost:
                    Buy_BNBAmount += (Sell_BTCAmount/float(ask[0]))
                    Sell_BTCAmount = 0
                    break
                else:
                    Sell_BTCAmount -=cost
                    Buy_BNBAmount += ask[1]
                    

            btc2bnborder = client.order_market_buy(
                symbol='BNBBTC',
                quantity=int(Buy_BNBAmount),
                disable_validation=True,
                newOrderRespType='FULL'
                )
			print(json.dumps(btc2bnborder, indent=4, sort_keys=True))
            BNBAmount = float(0)
            for fill in btc2bnborder['fills']:
                BNBAmount+=float(fill['qty'])
                if fill['commissionAsset'] == "BNB" :
                    BNBAmount -= float(fill['commission'])
            print("Buy {} BTC into {} BNB".format(BTCAmount, BNBAmount))

        else:
            print("{}\tBNB->ETH->BTC->BNB Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio))

        
    #BNB->BTC->ETH->BNB
    '''
    BBERatio = BNBBTC_bestbid[0]  /ETHBTC_bestask[0] /BNBETH_bestask[0] - 1.0015
    BBECapacity = int(min(BNBETH_bestask[1], int(ETHBTC_bestask[1]/BNBETH_bestask[0]),BNBBTC_bestbid[1]))
    if(BBECapacity * BBERatio>0.1):
        print("{}\tBNB->BTC->ETH->BNB Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio,BBECapacity))
    else:
        print("{}\tBNB->BTC->ETH->BNB Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio))
    '''

# Set up watched depth cache
DCMs={}
DCMs['BNBBTC'] = DepthCacheManager(client,'BNBBTC',process_any_depth);
DCMs['BNBETH'] = DepthCacheManager(client,'BNBETH',process_any_depth);
DCMs['ETHBTC'] = DepthCacheManager(client,'ETHBTC',process_any_depth);

DCs={}
DCs['BNBETH'] = DCMs['BNBETH'].get_depth_cache();
DCs['BNBBTC'] = DCMs['BNBBTC'].get_depth_cache();
DCs['ETHBTC'] = DCMs['ETHBTC'].get_depth_cache();





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

