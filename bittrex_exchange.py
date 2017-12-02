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
        self.conn1 = Bittrex(api_key, api_secret)

    def sell_limit(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED')
        if not self._validate_req(req):
            print('Unable to pass limit order: %s' % req['message'])
        return req

    def sell_market(self, pair, quantity):
        pass

    def sell_stop(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED', 'LESS_THAN', value)
        if not self._validate_req(req):
            print('Unable to pass stop order: %s' % req['message'])
        return req

    def get_tick(self, pair):
        req = self.conn1.get_ticker(pair)
        if not self._validate_req(req):
            print('Unable to get tick: %s' % req['message'])
            return None
        return req['result']

    def get_open_orders(self, pair):
        req = self.conn.get_open_orders(pair)
        if self._validate_req(req):
            return [BittrexOrder(data, id=data['OrderUuid'])
                    for data in req['result']]
        else:
            return []

    def cancel_order(self, order):
        req = self.conn1.cancel(order.id)
        if not self._validate_req(req):
            print('Unable to cancel order: %s' % req['message'])
        return req

    @staticmethod
    def _validate_req(req):
        return ('success' in req and req['success'] is True)


class BittrexOrder(Order):
    # Called by the metaclass to update an existing order. Must have
    # the same signature as __init__. id is a mandatory kwarg.
    def update(self, data, id=None):
        self.data = data

# BittrexExchange.py ends here
