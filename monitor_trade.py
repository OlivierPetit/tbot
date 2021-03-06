#!/usr/bin/env python

import argparse
import time
import sys

from bittrex_exchange import BittrexExchange


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


def convert(s):
    if s[-1] == 's':
        val = float(s[:-1]) * 0.00000001
    elif s[-1] == 'S':
        val = float(s[:-1]) * 0.000001
    else:
        val = float(s)
    return val


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', "--buy", help='run a buy order',
                        action="store_true")
    parser.add_argument(
        '-r', "--range",
        help='floating number to compute buy range. Default 0.09.',
        type=float, default=0.09)
    parser.add_argument('market', help='name of the market like BTC-ETH')
    parser.add_argument('quantity', help='quantity of coins', type=float)
    parser.add_argument('stop', help='stop level')
    parser.add_argument('entry', help='entry level')
    parser.add_argument('exit', help='exit level')
    args = parser.parse_args()

    market = args.market
    quantity = args.quantity
    stop = convert(args.stop)
    entry = convert(args.entry)
    exit = convert(args.exit)

    exch = BittrexExchange(True)

    # Buy order if needed

    if args.buy:
        orders = exch.get_open_orders(market)
        if len(orders) != 0:
            for order in orders:
                if order.is_buy_order():
                    print('There is already a buy order. Aborting.')
                    print(order.data)
                    sys.exit(1)
        val_max = entry + (entry - stop) * args.range
        buy_order = exch.buy_limit_range(market, quantity, entry, val_max)
        print(buy_order.data)

    # Do some sanity checks

    currency = market.split('-')[1]

    while True:
        position = exch.get_position(currency)
        if position and position['Balance'] >= quantity:
            break
        orders = exch.get_open_orders(market)
        if len(orders) == 0 or not orders[0].is_buy_order():
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
                'Not the correct balance: no position '
                'instead of more than %.2f' %
                (quantity))
        time.sleep(60)

    # Check if we have an open order

    orders = exch.get_open_orders(market)

    if len(orders) > 0:
        print(orders[0].data)
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


if __name__ == "__main__":
    main()
