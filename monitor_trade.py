#!/usr/bin/env python

from bittrex_exchange import BittrexExchange
import time
import sys


def get_orders(conn, market):
    return conn.get_open_orders(market)


if len(sys.argv) != 6:
    print('Usage: %s <market> <quantity> <stop> <entry> <exit>' % sys.argv[0])
    sys.exit(1)

market = sys.argv[1]
quantity = float(sys.argv[2])
stop = float(sys.argv[3])
entry = float(sys.argv[4])
exit = float(sys.argv[5])

exch = BittrexExchange(True)

orders = exch.get_open_orders(market)

if len(orders) > 0:
    order = orders[0]

    # TODO(fl): need to abstract
    if order.data['IsConditional']:
        trend = 'down'
    else:
        trend = 'up'
else:
    trend = 'none'
    order = None

print(trend)

while True:
    tick = exch.get_tick(market)
    if tick:
        print(tick)
        # TODO(fl): need to abstract tick
        if tick['Last'] < entry:
            if trend != 'down':
                print('down')
                if order:
                    req = exch.cancel_order(order)
                    print(req)
                    time.sleep(15)
                req = exch.sell_stop(market, quantity, stop)
                print(req)
                time.sleep(15)
                order = exch.get_open_orders(market)[0]
                trend = 'down'
        else:
            if trend != 'up':
                print('up')
                if order:
                    req = exch.cancel_order(order)
                    print(req)
                    time.sleep(15)
                req = exch.sell_limit(market, quantity, exit)
                print(req)
                time.sleep(15)
                order = exch.get_open_orders(market)[0]
                trend = 'up'
    time.sleep(60)
