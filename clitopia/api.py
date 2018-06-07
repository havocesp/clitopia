from pprint import pprint
import pandas as pd
import ccxt

from model import Balance


class ApiClient(ccxt.cryptopia):

    def __init__(self, apikey=None, secret=None, **config):
        super().__init__(config)

        if apikey is not None and secret is not None:
            self.apiKey = apikey
            self.secret = secret

        self.enableRateLimit = True


    def get_balance(self, currency=None):
        balance = self.fetch_balance()
        del balance['info'], balance['used'], balance['free'], balance['total']

        result = {k: v for k, v in balance.items() if v['total'] > 0.0}
        if currency is not None:
            result = Balance(**balance.get(currency, {}))
        return result


    def get_ticker(self, symbol=None, hours=24):
        params = dict(params={'hours': hours})
        result = dict()
        if symbol is None:
            data = self.fetch_tickers(params=params)

            for k, v in data.items():
                base, quote = k.split('/')
                if quote in ['BTC', 'USDT']:
                    min_volume = 25000 if 'USDT' in quote else 0.1
                    if v['quoteVolume'] > min_volume:
                        del v['info'], v['askVolume'], v['bidVolume'], v['previousClose']
                        result.update({k: v})
        else:
            data = self.fetch_ticker(symbol, params=params)
            del data['info']

        return pd.DataFrame(result)

    def get_market_history(self, symbol=None, limit=100):
        params = dict(params={'limit': limit})
        result = dict()
        if symbol is None:
            data = self.fetch_tickers(params=params)

            for k, v in data.items():
                base, quote = k.split('/')
                if quote in ['BTC', 'USDT']:
                    min_volume = 25000 if 'USDT' in quote else 0.1
                    if v['quoteVolume'] > min_volume:
                        del v['info'], v['askVolume'], v['bidVolume'], v['previousClose']
                        result.update({k: v})
        else:
            data = self.fetch_ticker(symbol, params=params)
            del data['info']

        return pd.DataFrame(result)


if __name__ == '__main__':
    pd.set_option('precision', 8)
    api = ApiClient()
    ticker = api.get_ticker()
    # btc_exchange = ticker.query('')
    print(ticker.sort_values(by='baseVolume', axis=1, ascending=False).first_valid_index())
    # api.get_ticker('DGB/BTC')
