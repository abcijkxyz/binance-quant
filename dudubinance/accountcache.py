from binance.websockets import BinanceSocketManager
import time
import os
class AccountCache(object):
    def __init__(self, client, *symbols):
        '''
        client: python-binance client
        symbols: trades of which this cache should take care about
        '''
        self._client = client # the python-binance client

        #snapshot of account
        tempaccountinfo = self._client.get_account()

        #check restrictions, if any raise an error
        print("canTrade:{},canWithdraw:{},canDeposit:{}".format(tempaccountinfo['canTrade'],tempaccountinfo['canWithdraw'],tempaccountinfo['canDeposit']))
        if(not (tempaccountinfo['canTrade'] and tempaccountinfo['canWithdraw'] and tempaccountinfo['canDeposit'])):
            raise ValueError('Restriction detected')

        #initialize balances
        self._balances = {}
        for balance in tempaccountinfo['balances']:
            self._balances[balance['asset']] = {}
            self._balances[balance['asset']]['free'] = balance['free']
            if(float(balance['free']) > 0):
                print("FREE {}: {}".format(balance['asset'],balance['free']))
            self._balances[balance['asset']]['locked'] = balance['locked']
            if(float(balance['locked']) > 0):
                print("LOCK {}: {}".format(balance['asset'],balance['locked']))
        #initialize symbols
        self._orders = {}
        self._callbacks = {}
        for s in symbols:
            self._callbacks[s]=[]
            orders=self._client.get_open_orders(symbol=s)

            self._orders[s]={'BUY':[],'SELL':[]}
            for order in orders:
                self._orders[s][order['side']].append(order)
            self._sort_orders(s)
        #start the socketmanager
        self._bm = BinanceSocketManager(self._client)
        self._connkey = self._bm.start_user_socket(self.usersocketCallback)
        self._bm.start()

    def _sort_orders(self,s):
        self._orders[s]['BUY'].sort(key=lambda order:order['price'],reverse=True) 
        self._orders[s]['SELL'].sort(key=lambda order:order['price']) 
    def clear(self):
        #release thread
        self._bm.stop_socket(self._connkey)
        self._bm.close()
    def getOrders(self,symbol):
        return self._orders[symbol]
    def list_orders(self,thesymbol):
        if not self._ifHasSymbol(thesymbol):
            self.addSymbol(thesymbol)
        for order in self._orders[thesymbol]['BUY']:
            print("BUYING {}@{}".format(order['origQty'],order['price']))
        for order in self._orders[thesymbol]['SELL']:
            print("SELLING {}@{}".format(order['origQty'],order['price']))
    def _ifHasSymbol(self,s):
        return s in self._orders
    def addSymbol(self,s):
        #s:symbol
        self._callbacks[s]=[]
        orders=self._client.get_open_orders(symbol=s)
        self._orders[s]={'BUY':[],'SELL':[]}
        for order in orders:
            self._orders[s][order['side']].append(order)
        self._sort_orders(s)

    def registerOrderCallback(self, symbol, callback):
        if symbol not in self._callbacks:
            raise ValueError('contains no '+symbol)
        self._callbacks[symbol].append(callback)
    def getBalance(self,symbol):
        return self._balances[symbol]
    
    def usersocketCallback(self,msg):
        # callback for account websocket
        if(msg['e'] == "outboundAccountInfo"):
            if (not msg['T']):
                raise ValueError('Not tradable')
            for b in msg['B']:
                if not b['a'] in self._balances:
                    self._balances[b['a']]={'free':0,'locked':0}
                    #print('#########listing {}#####'.format(b['a']))
                    #os.system("bash alertlisting.sh "+b['a'])
                if b['f'] != self._balances[b['a']]['free']:
                    self._balances[b['a']]['free'] = b['f']
                    #print("FREE {}: {}".format(b['a'],b['f']))
                if b['l'] != self._balances[b['a']]['locked']:
                    self._balances[b['a']]['locked'] = b['l']
                    #print("LOCK {}: {}".format(b['a'],b['l']))
        if(msg['e'] == 'executionReport'):
            if(msg['s'] in self._orders):

                neworder = {
                "symbol": msg['s'],
                "orderId": msg['i'],
                "clientOrderId": msg['c'],
                "price": msg['p'],
                "origQty": msg['q'],
                "executedQty": msg['l'],
                "status": msg['X'],
                "timeInForce": msg['f'],
                "type": msg['o'],
                "side": msg['S'],
                "stopPrice": "0.0",
                "icebergQty": "0.0",
                "time": msg['E']
                }
                if(neworder['status']!="PARTIALLY_FILLED"):
                    print("{}:{} {} {} {}@{}".format(time.asctime( time.localtime(time.time()) ),neworder['status'],neworder['side'],neworder['symbol'],neworder['origQty'],neworder['price']))
                
                if(msg['X'] == "NEW"):
                    self._orders[neworder['symbol']][neworder['side']].append(neworder)
                    self._sort_orders(neworder['symbol'])
                if(msg['X'] == "FILLED" or msg['X'] == "CANCELED"):
                    for order in self._orders[neworder['symbol']][neworder['side']]:
                        if(order['orderId'] == neworder['orderId']):
                            self._orders[neworder['symbol']][neworder['side']].remove(order)
                            break
            #callback anyway
            for eachcb in self._callbacks[neworder['symbol']]:
                eachcb(neworder)
