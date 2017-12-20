from __future__ import print_function

from binance.client import Client

def clientFactory(accounts):
    print("Which account do you want to proceed with:")
    for account in accounts:
        print("[{}]".format(account))
    name = "somethingdefinitelynotexist"
    while not name in accounts:
        print(">",end="")
        name = raw_input()
    return Client(accounts[name]['key'], accounts[name]['secret'])
