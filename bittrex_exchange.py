'''
'''

from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import wait_exponential

from bittrex.bittrex import API_V2_0
from bittrex.bittrex import Bittrex

from exchange import Exchange
from exchange import Order

# Settings for retry
MAX_DELAY = 30


class BittrexError(Exception):
    pass


class BittrexRetryableError(BittrexError):
    pass


def bittrex_retry():
    return retry(wait=wait_exponential(max=MAX_DELAY),
                 retry=retry_if_exception_type(BittrexRetryableError))


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

    @bittrex_retry()
    def sell_limit(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED')
        self._validate_req(req, 'Unable to pass limit order')
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    @bittrex_retry()
    def sell_market(self, pair, quantity):
        pass

    @bittrex_retry()
    def sell_stop(self, pair, quantity, value):
        req = self.conn.trade_sell(
            pair, 'LIMIT', quantity, value / 2,
            'GOOD_TIL_CANCELLED', 'LESS_THAN', value)
        self._validate_req(req, 'Unable to pass stop order')
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    @bittrex_retry()
    def buy_limit(self, pair, quantity, value):
        req = self.conn.trade_buy(
            pair, 'LIMIT', quantity, value,
            'GOOD_TIL_CANCELLED')
        self._validate_req(req, 'Unable to pass buy limit order')
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    @bittrex_retry()
    def buy_limit_range(self, pair, quantity, min_val, max_val):
        req = self.conn.trade_buy(
            pair, 'LIMIT', quantity, max_val,
            'GOOD_TIL_CANCELLED', 'GREATER_THAN', min_val)
        self._validate_req(req, 'Unable to pass buy range order')
        data = req['result']
        return BittrexOrder(data, id=data['OrderId'])

    @bittrex_retry()
    def get_tick(self, pair):
        req = self.conn.get_latest_candle(pair, 'oneMin')
        self._validate_req(req, 'Unable to get tick')
        return req['result'][0]

    @bittrex_retry()
    def get_open_orders(self, pair):
        req = self.conn.get_open_orders(pair)
        self._validate_req(req, 'Unable to get open orders')
        return [BittrexOrder(data, id=data['OrderUuid'])
                for data in req['result']]
    @bittrex_retry()
    def get_order_history(self, pair):
        req = self.conn.get_order_history(pair)
        self._validate_req(req, 'Unable to get order history')
        return [BittrexOrder(data, id=data['OrderUuid'])
                for data in req['result']]

    @bittrex_retry()
    def cancel_order(self, order):
        req = self.conn.cancel(order.id)
        self._validate_req(req, 'Unable to cancel order')
        return True

    @bittrex_retry()
    def get_balances(self):
        req = self.conn.get_balances()
        self._validate_req(req, 'Unable to get balances')
        return req['result']

    @bittrex_retry()
    def get_position(self, pair):
        req = self.conn.get_balance(pair)
        self._validate_req(req, 'Unable to get position')
        return req['result']

    @staticmethod
    def _validate_req(req, msg=None, do_raise=True):
        if 'success' in req and req['success'] is True:
            return True
        else:
            if msg:
                print('%s: %s' % (msg, req.get('message', '<no message>')))
            if do_raise:
                if req.get('message', None) in ('NO_API_RESPONSE',):
                    raise BittrexRetryableError(req['message'])
                else:
                    raise BittrexError(req.get('message', '<no message>'))
            else:
                return False


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
