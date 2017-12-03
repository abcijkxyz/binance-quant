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
                print("Amount of free {}: {}".format(balance['asset'],balance['free']))
            self._balances[balance['asset']]['locked'] = balance['locked']
            if(float(balance['locked']) > 0):
                print("Amount of locked {}: {}".format(balance['asset'],balance['locked']))
        #initialize orders
        self._orders = {}
        for symbol in symbols:
            self._orders[symbol]=self._client.get_open_orders(symbol)

        #start the 
        self._bm = BinanceSocketManager(self._client)
        self._bm.start_user_socket(self.usersocketCallback)
        self._bm.start()
    def addSymbol(self,symbol):
        self._orders[symbol]=self._client.get_open_orders(symbol)
        # the cache should care about trades of the new symbol
    def usersocketCallback(self,msg):
        # callback for account websocket
        if(msg['e'] == "outboundAccountInfo"):
            if (not msg['T']):
                raise ValueError('Not tradable')
            for balance in msg['B']:
                if balance['f'] != self._balances[balance['asset']['free']]:
                    self._balances[balance['asset']['free']] = balance['f']
                    print("Amount of free {}: {}".format(balance['a'],balance['f']))
                if balance['l'] != self._balances[balance['asset']['locked']]:
                    self._balances[balance['asset']['locked']] = balance['l']
                    print("Amount of locked {}: {}".format(balance['a'],balance['l']))
        if(msg['e'] == 'executionReport'):
            if(msg['s'] in self._orders):
                print(msg)
           