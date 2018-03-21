from symbolsinfo import * 
import time
import sys
class Executor(object):
    def __init__(self, client):
        refresh_symbolsinfo()
        self._client = client
    def cancelOrders(self,*orders):
        for order in orders:
            print("{}:Canceling an order: {}{} {}@{}".format(time.asctime( time.localtime(time.time()) ),order['side'], order['symbol'], order['origQty'],order['price']))
            self._client.cancel_order(symbol=order['symbol'],orderId=order['orderId'])
        
    def safePlaceLimitOrder(self,NEWSIDE, SYMBOL, NEWQUANTITY,NEWPRICE):
        REALPRICE = format(round(NEWPRICE/symbolsInfo[SYMBOL]['tickSize']) * symbolsInfo[SYMBOL]['tickSize'],".8f")
        print("{}:Placing an order: {} {} {}@{}".format(time.asctime( time.localtime(time.time()) ),NEWSIDE, SYMBOL, NEWQUANTITY,REALPRICE))
        try:
            order = self._client.order_limit(
            symbol=SYMBOL,
            quantity=NEWQUANTITY,
            side=NEWSIDE,
            price=REALPRICE
            #newOrderRespType='FULL'
            )
        except:
            print "Unexpected error:", sys.exc_info()
        time.sleep(0.11)

    def placeOrderUntil(self,side,startprice,stopprice,thestepratio,targetsymbol,amount,assetbalance):
        #,maxorderamount):
        nextprice = startprice
        i = 0
        while True:
            if side=="SELL" and stopprice/nextprice <= (1+thestepratio):
                print("Wanted to place sell at {}, but the stopprice is {},stop".format(nextprice, stopprice))
                break;
            if side=="BUY" and nextprice/stopprice <= (1+thestepratio):
                print("Wanted to place buy at {}, but the stopprice is {},stop".format(nextprice, stopprice))
                break;
            if side=="SELL" and assetbalance < amount :
                break;
            if side=="BUY" and assetbalance < amount*nextprice:
                break;

            self.safePlaceLimitOrder(side,targetsymbol,amount, nextprice)

            if side=="SELL":
                assetbalance -= amount
                nextprice*=(1+thestepratio)
            if side=="BUY":
                assetbalance -= amount*nextprice
                nextprice/=(1+thestepratio)
            i+=1

            #if i >= maxorderamount:
            #    break;

