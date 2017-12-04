from binance.websockets import BinanceSocketManager
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
            self._orders[s]=self._client.get_open_orders(symbol=s)
            self._callbacks[s]={}

        #start the 
        self._bm = BinanceSocketManager(self._client)
        self._bm.start_user_socket(self.usersocketCallback)
        self._connkey = self._bm.start()

    def clear(self):
        #release thread
        self._bm.stop_socket(self._connkey)
        self._bm.close()

    def addSymbol(self,symbol):
        self._orders[symbol]=self._client.get_open_orders(symbol)
        self._callbacks[symbol]=[]
        # the cache should care about trades of the new symbol

    def registerOrderCallback(self, symbol, callback):
        if symbol not in self._callbacks:
            raise ValueError('contains no '+symbol)
        self._callbacks[symbol].append(callback)
    def usersocketCallback(self,msg):
        # callback for account websocket
        if(msg['e'] == "outboundAccountInfo"):
            if (not msg['T']):
                raise ValueError('Not tradable')
            for b in msg['B']:
                if b['f'] != self._balances[b['a']]['free']:
                    self._balances[b['a']]['free'] = b['f']
                    print("FREE {}: {}".format(b['a'],b['f']))
                if b['l'] != self._balances[b['a']]['locked']:
                    self._balances[b['a']]['locked'] = b['l']
                    print("LOCK {}: {}".format(b['a'],b['l']))
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
                print("{}: {} {} {}@{}".format(neworder['status'],neworder['side'],neworder['symbol'],neworder['origQty'],neworder['price']))
                
                if(msg['X'] == "NEW"):
                    self._orders[neworder['symbol']].append(neworder)
                if(msg['X'] == "FILLED"):
                    for order in self._orders[neworder['symbol']]:
                        if(order['orderId'] == neworder['orderId']):
                            self._orders[neworder['symbol']].remove(order)
                            break
                print("length of orders:{}".format(len(self._orders[neworder['symbol']])))
                
                for eachcb in self._callbacks[neworder['symbol']]:
                    eachcb(msg)
           
