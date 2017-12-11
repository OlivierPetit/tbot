#!/usr/bin/env python

from bittrex_exchange import BittrexExchange

exch = BittrexExchange(True)

balances = exch.get_balances()

for b in balances:
    bb = b['Balance']
    if bb['Balance'] > 0 or bb['Available'] > 0:
        print('[%s] balance: %2.8f available %2.8f' %
              (bb['Currency'], bb['Balance'], bb['Available']))
