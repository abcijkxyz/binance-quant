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
        #initialize orders
        self._orders = {}
        for s in symbols:
            self._orders[s]=self._client.get_open_orders(symbol=s)

        #start the 
        self._bm = BinanceSocketManager(self._client)
        self._bm.start_user_socket(self.usersocketCallback)
        self._connkey = self._bm.start()
    def clear(self):
        self._bm.stop_socket(self._connkey)
        self._bm.close()
    def addSymbol(self,symbol):
        self._orders[symbol]=self._client.get_open_orders(symbol)
        # the cache should care about trades of the new symbol
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
                print(msg)
           
