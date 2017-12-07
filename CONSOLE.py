import consoleapikey
from dudubinance.accountcache import AccountCache
from dudubinance.symbolsinfo import *
from binance.client import Client
#from __future__ import print_function
import json
import threading
import time

client = Client(consoleapikey.account['key'], consoleapikey.account['secret'])
refresh_symbolsinfo()

ac = AccountCache(client,'BNBBTC')

while (1):
    command = raw_input().split()
    if(command[0] == "help"):
        print("list symbol|balance")
    if(command[0] == "list"):
        ac.list_orders(command[1])
    if(command[0] == "balance"):
        balances = ac.getBalance(command[1])
        print("free:{}, locked:{}".format(balances['free'],balances['locked']))
    if(command[0] == "exit"):
        ac.clear()
