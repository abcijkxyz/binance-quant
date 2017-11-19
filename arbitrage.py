'''
This strategy works by find arbitrage profit among 3 cycling trading pairs and execute
1. keep observing 3 trading paris depth
2. each time depth updates, calculate potential profit
3. As soon as it meets profit threshold, execute 3 market trades

However, it just doesn't profit
'''
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

isTrading = False

def process_any_depth(depth_cache):

    global isTrading
    if(isTrading):
        return

    global DCs
    global client
    BCPTBNB_bids = DCs['BCPTBNB'].get_bids()
    BCPTBNB_asks = DCs['BCPTBNB'].get_asks()
    BCPTETH_bids = DCs['BCPTETH'].get_bids()
    BCPTETH_asks = DCs['BCPTETH'].get_asks()
    BNBETH_bids = DCs['BNBETH'].get_bids()
    BNBETH_asks = DCs['BNBETH'].get_asks()

    if(len(BCPTBNB_bids)==0 or len(BCPTBNB_asks)==0 or len(BCPTETH_bids)==0 or len(BCPTETH_asks)==0 or len(BNBETH_bids)==0 or len(BNBETH_asks)==0 ):
        return

    BCPTBNB_bestbid = BCPTBNB_bids[0]
    BCPTBNB_bestask = BCPTBNB_asks[0]
    BCPTETH_bestbid = BCPTETH_bids[0]
    BCPTETH_bestask = BCPTETH_asks[0]
    BNBETH_bestbid = BNBETH_bids[0]
    BNBETH_bestask = BNBETH_asks[0]

    
    #BCPT->BNB->ETH->BCPT
    BEBRatio = float(BCPTBNB_bestbid[0]) * float(BNBETH_bestbid[0]) /float(BCPTETH_bestask[0]) - 1 - config.threshold['commission']
    BEBCapacity = int(min(float(BCPTBNB_bestbid[1]), float(BNBETH_bestbid[1]) / float(BCPTBNB_bestbid[0]),float(BCPTETH_bestask[1])))

    #BCPT->ETH->BNB->BCPT
    BBERatio = float(BCPTETH_bestbid[0])  /float(BNBETH_bestask[0]) /float(BCPTBNB_bestask[0]) - 1 - config.threshold['commission']
    BBECapacity = int(min(float(BCPTBNB_bestask[1]), float(BNBETH_bestask[1]) / float(BCPTBNB_bestask[0]),float(BCPTETH_bestbid[1])))

    #BCPT->BNB->ETH->BCPT
    if(BEBCapacity * BEBRatio>config.threshold['targetearn']):
        isTrading=True
        print("{}\tBCPT->BNB->ETH->BCPT Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio,BEBCapacity))
        
        #sell BCPT to BNB###########################################################
        '''
        bnb2ethorder = client.order_market_sell(
            symbol='BCPTBNB',
            quantity=BEBCapacity,
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(bnb2ethorder, indent=4, sort_keys=True))
        BNBAmount = float(0)
        for fill in bnb2ethorder['fills']:
            BNBAmount += (float(fill['qty']) * float(fill['price']))
            if fill['commissionAsset'] == "BNB":
                BNBAmount -= float(fill['commission'])
        print("Sell {} BCPT into {} BNB".format(BEBCapacity, BNBAmount))

        #sell BNB to ETH###########################################################
        eth2btcorder = client.order_market_sell(
            symbol='BNBETH',
            quantity=format(BNBAmount,".3f"),
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(eth2btcorder, indent=4, sort_keys=True))
        ETHAmount = float(0)
        for fill in eth2btcorder['fills']:
            ETHAmount+=(float(fill['qty']) * float(fill['price']))
            if fill['commissionAsset'] == "ETH":
                ETHAmount -= float(fill['commission'])
        print("Sell {} BNB into {} ETH".format(BNBAmount, ETHAmount))

        #buy ETH to BCPT

        #calculate proper buy amount###########################################################
        Buy_BCPTAmount = 0
        Sell_ETHAmount = ETHAmount
        asks = DCs['BCPTETH'].get_asks()
        for ask in asks:
            cost = float(ask[0]) * float(ask[1])
            if Sell_ETHAmount < cost:
                Buy_BCPTAmount += (Sell_ETHAmount/float(ask[0]))
                Sell_ETHAmount = 0
                break
            else:
                Sell_ETHAmount -=cost
                Buy_BCPTAmount += ask[1]
                

        btc2bnborder = client.order_market_buy(
            symbol='BCPTETH',
            quantity=int(Buy_BCPTAmount),
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(btc2bnborder, indent=4, sort_keys=True))
        BCPTAmount = float(0)
        for fill in btc2bnborder['fills']:
            BCPTAmount+=float(fill['qty'])
            if fill['commissionAsset'] == "BCPT" :
                BCPTAmount -= float(fill['commission'])
        print("Buy {} ETH into {} BCPT".format(ETHAmount, BCPTAmount))

        time.sleep(1)
        isTrading=False
        '''
    else:
        print("{}\tBCPT->BNB->ETH->BCPT Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BEBRatio))

    #BCPT->ETH->BNB->BCPT
    if(BBECapacity * BBERatio>config.threshold['targetearn']):
        isTrading=True
        print("{}\tBCPT->ETH->BNB->BCPT Ratio:{},\tQuantity:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio,BBECapacity))
        
        #sell BCPT to ETH###########################################################
        '''
        bnb2btcorder = client.order_market_sell(
            symbol='BCPTETH',
            quantity=BBECapacity,
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(bnb2btcorder, indent=4, sort_keys=True))
        ETHAmount = float(0)
        for fill in bnb2btcorder['fills']:
            ETHAmount += (float(fill['qty']) * float(fill['price']))
            if fill['commissionAsset'] == "ETH":
                ETHAmount -= float(fill['commission'])
        print("Sell {} BCPT into {} ETH".format(BBECapacity, ETHAmount))
        
        #buy ETH to BNB###########################################################

        #calculate proper buy amount
        Buy_BNBAmount = 0
        Sell_ETHAmount = ETHAmount
        asks = DCs['BNBETH'].get_asks()
        for ask in asks:
            cost = float(ask[0]) * float(ask[1])
            if Sell_ETHAmount < cost:
                Buy_BNBAmount += (Sell_ETHAmount/float(ask[0]))
                Sell_ETHAmount = 0
                break
            else:
                Sell_ETHAmount -=cost
                Buy_BNBAmount += ask[1]
                
        btc2ethorder = client.order_market_buy(
            symbol='BNBETH',
            quantity=format(Buy_BNBAmount,".3f"),
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(btc2ethorder, indent=4, sort_keys=True))
        BNBAmount = float(0)
        for fill in btc2ethorder['fills']:
            BNBAmount+=float(fill['qty'])
            if fill['commissionAsset'] == "BNB" :
                BNBAmount -= float(fill['commission'])
        print("Buy {} ETH into {} BNB".format(ETHAmount, BNBAmount))


        #buy BNB to BCPT###########################################################

        #calculate proper buy amount
        Buy_BCPTAmount = 0
        Sell_BNBAmount = BNBAmount
        asks = DCs['BCPTBNB'].get_asks()
        for ask in asks:
            cost = float(ask[0]) * float(ask[1])
            if Sell_BNBAmount < cost:
                Buy_BCPTAmount += (Sell_BNBAmount/float(ask[0]))
                Sell_BNBAmount = 0
                break
            else:
                Sell_BNBAmount -=cost
                Buy_BCPTAmount += ask[1]
                
        eth2bnborder = client.order_market_buy(
            symbol='BCPTBNB',
            quantity=int(Buy_BCPTAmount),
            disable_validation=True,
            newOrderRespType='FULL'
            )
        print(json.dumps(eth2bnborder, indent=4, sort_keys=True))
        BCPTAmount = float(0)
        for fill in eth2bnborder['fills']:
            BCPTAmount+=float(fill['qty'])
            if fill['commissionAsset'] == "BCPT" :
                BCPTAmount -= float(fill['commission'])
        print("Buy {} BNB into {} BCPT".format(BNBAmount, BCPTAmount))
        time.sleep(10)
        isTrading=False
        '''
    else:
        print("{}\tBCPT->ETH->BNB->BCPT Ratio:{},\tNot Good Enough".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , BBERatio))

# Set up watched depth cache
DCMs={}
DCMs['BCPTETH'] = DepthCacheManager(client,'BCPTETH',process_any_depth);
DCMs['BCPTBNB'] = DepthCacheManager(client,'BCPTBNB',process_any_depth);
DCMs['BNBETH'] = DepthCacheManager(client,'BNBETH',process_any_depth);

DCs={}
DCs['BCPTBNB'] = DCMs['BCPTBNB'].get_depth_cache();
DCs['BCPTETH'] = DCMs['BCPTETH'].get_depth_cache();
DCs['BNBETH'] = DCMs['BNBETH'].get_depth_cache();





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

