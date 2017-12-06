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


def monitor_order_completion(exch, market):
    orders = exch.get_open_orders(market)
    if len(orders) == 0:
        print('order completed')
        return True
    else:
        print('order still in place')
        return False


if len(sys.argv) != 6:
    print('Usage: %s <market> <quantity> <stop> <entry> <exit>' % sys.argv[0])
    sys.exit(1)

market = sys.argv[1]
quantity = float(sys.argv[2])
stop = float(sys.argv[3])
entry = float(sys.argv[4])
exit = float(sys.argv[5])

exch = BittrexExchange(True)

# Do some sanity checks

currency = market.split('-')[1]

while True:
    position = exch.get_position(currency)
    if position and position['Balance'] >= quantity:
        break
    orders = exch.get_open_orders(market)
    if len(orders) == 0 or orders[0].data['OrderType'] != 'LIMIT_BUY':
        print('no buy order for %s' % market)
        sys.exit(1)
    tick = exch.get_tick(market)
    if tick and tick['L'] < stop:
        print('Trade invalidated (low price %f), cancelling order' %
              tick['L'])
        exch.cancel_order(orders[0])
        sys.exit(0)
    if position:
        print('Not the correct balance: %.2f instead of more than %.2f' %
              (position['Balance'], quantity))
    else:
        print(
            'Not the correct balance: no position instead of more than %.2f' %
            (quantity))
    time.sleep(60)

# Check if we have an open order

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
            if last < stop and monitor_order_completion(exch, market):
                break
            elif trend != 'down':
                print('down')
                order = send_order(order, exch, exch.sell_stop,
                                   market, quantity, stop)
                trend = 'down'
        else:
            if last > exit and monitor_order_completion(exch, market):
                break
            elif trend != 'up':
                print('up')
                order = send_order(order, exch, exch.sell_limit,
                                   market, quantity, exit)
                trend = 'up'
    time.sleep(60)
