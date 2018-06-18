#!/usr/bin/python
'''
This script pingpong a BNBBTC order at 48 BTC to continuously trigger the orderbook update
'''
from binance.client import Client
from binance.depthcache import DepthCacheManager
from ACCOUNTS import accounts
from dudubinance.clientfactory import clientFactory

import json
import threading
import time
import os

interval = 180
# Client Initialization
client = clientFactory(accounts)
dcm = DepthCacheManager(client, 'BNBBTC')


print("{}:Placing an order".format(time.asctime( time.localtime(time.time()) )))
order = client.order_limit(
            symbol='BNBBTC',
            quantity='0.01',
            side='SELL',
            price='48'
            )
print('Done.')
time.sleep(1)
print("{}:Cancling an order".format(time.asctime( time.localtime(time.time()) )))
result = client.cancel_order( symbol='BNBBTC', orderId=order['orderId'])
time.sleep(1)

depth_cache = dcm.get_depth_cache()
oldamount=0
while True:
    if "48.00000000" in depth_cache._asks and depth_cache._asks["48.00000000"] != oldamount:
        oldamount=depth_cache._asks["48.00000000"]
        output={"amt":depth_cache._asks["48.00000000"]}
        file=open('/var/www/html/sell48test','w')
        file.write(json.dumps(output))
        file.flush()
        os.fsync(file.fileno())
        file.close()
        print(json.dumps(output))
    time.sleep(interval)

    

dcm.close()
