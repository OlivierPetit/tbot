'''
'''

from bittrex.bittrex import API_V2_0
from bittrex.bittrex import Bittrex

from exchange import Exchange
from exchange import Order


class BittrexExchange(Exchange):
    def __init__(self, auth=False):
        if auth:
            with open('bittrex.key') as kfile:
                api_key = kfile.readline().strip()
                api_secret = kfile.readline().strip()
        else:
            api_key = None
            api_secret = None
        self.conn = Bittrex(api_key, api_secret, api_version=API_V2_0)

    def sell_limit(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED')
        if not self._validate_req(req):
            print('Unable to pass limit order: %s' % req['message'])
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    def sell_market(self, pair, quantity):
        pass

    def sell_stop(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED', 'LESS_THAN', value)
        if not self._validate_req(req):
            print('Unable to pass stop order: %s' % req['message'])
            return None
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    def buy_limit(self, pair, quantity, value):
        req = self.conn.trade_buy(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED')
        if not self._validate_req(req):
            print('Unable to pass buy limit order: %s' % req['message'])
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    def buy_limit_range(self, pair, quantity, min_val, max_val):
        req = self.conn.trade_buy(
            pair, 'LIMIT', quantity, max_val,
            'GOOD_TIL_CANCELLED', 'GREATER_THAN', min_val)
        if not self._validate_req(req):
            print('Unable to pass buy range order: %s' % req['message'])
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    def get_tick(self, pair):
        req = self.conn.get_latest_candle(pair, 'oneMin')
        if not self._validate_req(req):
            print('Unable to get tick: %s' % req['message'])
            return None
        return req['result'][0]

    def get_open_orders(self, pair):
        req = self.conn.get_open_orders(pair)
        if self._validate_req(req):
            return [BittrexOrder(data, id=data['OrderUuid'])
                    for data in req['result']]
        else:
            return []

    def cancel_order(self, order):
        req = self.conn.cancel(order.id)
        if not self._validate_req(req):
            print('Unable to cancel order: %s' % req['message'])
            return False
        return True

    def get_position(self, pair):
        req = self.conn.get_balance(pair)
        if not self._validate_req(req):
            print('Unable to get position: %s' % req['message'])
            return None
        return req['result']

    @staticmethod
    def _validate_req(req):
        return ('success' in req and req['success'] is True)


class BittrexOrder(Order):
    # Called by the metaclass to update an existing order. Must have
    # the same signature as __init__. id is a mandatory kwarg.
    def update(self, data, id=None):
        self.data = data

    def is_sell_order(self):
        return self.data['OrderType'] == 'LIMIT_SELL'

    def is_buy_order(self):
        return self.data['OrderType'] == 'LIMIT_BUY'

# BittrexExchange.py ends here
