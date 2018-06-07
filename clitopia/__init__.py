import requests.exceptions as reqex
from ccxt import cryptopia
from datetime import datetime as dt
import time as tm
import pandas as pd
import term as trm
from tabulate import tabulate


get_time = lambda: dt.now().isoformat().split('T')[1]

depth_table_options = dict(numalign='right',
                           disable_numparse=True,
                           # floatfmt='25.8f',
                           headers=['Ord.', 'Ask', 'Ask Amount', 'Bid', 'Bid Amount'],
                           stralign='right',
                           showindex=True)

market_trades_table_options = dict(numalign='right',
                                   disable_numparse=True,
                                   # floatfmt='25.8f',
                                   headers=['Ord.', 'Amount', 'BTC Total', 'Date', 'Price', 'Side'],
                                   stralign='right',
                                   showindex=True)

cols = ['price', 'amount']



pd.options.display.precision = 8

exchange = 'BTC'
coin = 'ETN'

symbol = '{}/{}'.format(coin, exchange)

# book = api.fetch_order_book(symbol, limit=10)
#
# asks, bids = book['asks'], book['bids']
# df_asks = pd.DataFrame(asks, columns=cols)
# df_bids = pd.DataFrame(bids, columns=cols)

tm.sleep(.25), trm.clear(), trm.pos(1, 1)
api = cryptopia()
while True:
    try:
        sep = lambda: trm.writeLine(trm.center('-' * 80), trm.dim, trm.cyan)
        book = api.fetch_order_book(symbol, limit=5)

        asks, bids = book['asks'], book['bids']
        df_asks = pd.DataFrame(asks, columns=cols)
        df_bids = pd.DataFrame(bids, columns=cols)
        df_asks['amount'] = df_asks['amount'].apply(lambda v: '{: >16.2f}'.format(v))
        df_asks['price'] = df_asks['price'].apply(lambda v: '{: >16.8f}'.format(v))
        df_bids['amount'] = df_bids['amount'].apply(lambda v: '{: >16.2f}'.format(v))
        df_bids['price'] = df_bids['price'].apply(lambda v: '{: >16.8f}'.format(v))
        book_join = [[*ask, *bid] for ask, bid in zip(df_bids.values, df_asks.values)]

        trm.pos(1, 1), sep(), [trm.clearLine() for x in range(13)]
        trm.writeLine(trm.center(' === {} === '.format(symbol)), trm.bold, trm.cyan)
        sep()

        table_string = tabulate(book_join[:5], **depth_table_options)
        trm.writeLine(trm.center('DEPTH'.format(symbol)))
        trm.writeLine('\n'.join([trm.center(ln) for ln in table_string.split('\n')]) + '\n')

        sep(), tm.sleep(1.25)
        trades = api.fetch_trades(symbol, limit=5)
        trades = pd.DataFrame(trades).drop(['info', 'timestamp', 'symbol', 'fee', 'id', 'order', 'type'], axis=1)
        trades['amount'] = trades['amount'].apply(lambda v: '{: >16.3f}'.format(v))
        trades['cost'] = trades['cost'].apply(lambda v: '{: >16.8f}'.format(v))
        # print(trades.columns)
        trades['price'] = trades['price'].apply(lambda v: '{: >16.8f}'.format(v))

        trades['datetime'] = trades['datetime'].apply(lambda v: v.replace('T', ' ').replace('.000Z', ''))

        # print(trades.columns)
        trm.saveCursor(), [trm.clearLine() for x in range(13)], trm.restoreCursor()
        trm.writeLine(trm.center('LAST TRADES'.format(symbol)))
        table_string = tabulate(trades, **market_trades_table_options)
        trm.writeLine('\n'.join([trm.center(ln) for ln in table_string.split('\n')]))
        trm.writeLine(trm.center('\n - {} -'.format(get_time()[:-3])), trm.dim)

        tm.sleep(1.25)
    except (reqex.RequestException, reqex.ConnectionError) as err:
        trm.writeLine(str(err))
        tm.sleep(3)
    except KeyboardInterrupt:
        print('EXIT')
        break
