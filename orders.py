#!/usr/bin/env python

from bittrex_exchange import BittrexExchange
import sys

from monitor_trade import convert


# for fun and others param
if len(sys.argv) != 2:
    print('Usage: %s <market>' % sys.argv[0])
    sys.exit(1)

market = sys.argv[1]
exch = BittrexExchange(True)
orders = exch.get_open_orders(market)
for order in orders:
    print('%s > [%s] %s(%d) %s(%2.8f) %s(%2.8f)' % (market, order.data['Opened'], order.data['Exchange'], order.data['Quantity'], order.data['OrderType'], order.data['Limit'], order.data['Condition'], order.data['ConditionTarget']))
    