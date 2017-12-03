#!/usr/bin/env python

from bittrex_exchange import BittrexExchange
import time
import sys


def get_orders(conn, market):
    return conn.get_open_orders(market)


def send_order(order, exch, func, *args, **kwargs):
    if order and exch.cancel_order(order):
        order = None
    new_order = func(*args, **kwargs)
    if new_order:
        print(new_order.data)
        order = new_order
    return order


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
        print(market, tick)
        # TODO(fl): need to abstract tick
        last = tick['C']
        if last < entry:
            if trend != 'down':
                print('down')
                order = send_order(order, exch, exch.sell_stop,
                                   market, quantity, stop)
                trend = 'down'
        else:
            if trend != 'up':
                print('up')
                order = send_order(order, exch, exch.sell_limit,
                                   market, quantity, exit)
                trend = 'up'
    time.sleep(60)
