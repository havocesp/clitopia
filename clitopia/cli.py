import os
import pandas as pd
import begin
import ccxt.cryptopia

from talib.abstract import Function
from tabulate import tabulate
import sys

# sys.argv.extend(['balance']) #, 'ZCL/BTC']) #, 'ROC,ADOSC,WILLR', '--timeframe', '15m', '--limit', '100'])  # , 'BTC/USDT,ETH/BTC,ZCL/BTC,ZEC/BTC'])
# sys.argv.extend(['ticker', 'ZCL/BTC']) #, 'ROC,ADOSC,WILLR', '--timeframe', '15m', '--limit', '100'])  # , 'BTC/USDT,ETH/BTC,ZCL/BTC,ZEC/BTC'])
# sys.argv.extend(['ticker', 'ZCL/BTC']) #, 'ROC,ADOSC,WILLR', '--timeframe', '15m', '--limit', '100'])  # , 'BTC/USDT,ETH/BTC,ZCL/BTC,ZEC/BTC'])

if not len(sys.argv[1:]):
    sys.argv.append('-h')

api = ccxt.cryptopia(
    config=dict(timeout=15000, apiKey=os.getenv('CRYPTOPIA_MAIN_KEY'), secret=os.getenv('CRYPTOPIA_MAIN_SECRET')))


@begin.subcommand
def ticker(symbols):
    ticker = api.fetch_tickers(symbols)

    data = list()
    droppable = ['info', 'previousClose', 'baseVolume', 'open', 'close', 'askVolume', 'bidVolume', 'change',
                 'timestamp',
                 'high', 'low']

    symbols = symbols.replace(' ', '').split(',') if ',' in symbols else [symbols]
    fields = list(ticker[symbols[0]].keys())
    for s in symbols:
        raw = ticker[s]
        for k in fields:
            if k in droppable:
                del raw[k]

        d = {k.title(): v for k, v in raw.items()}
        d['Date'] = d.pop('Datetime').split('.')[0].replace('T', ' ')
        d['Volume'] = round(d.pop('Quotevolume'), 2)
        d['Change'] = d.pop('Percentage')
        d['VWAP'] = d.pop('Vwap')

        data.append(d)
    print(tabulate(data,
                   headers='keys',
                   disable_numparse=[0, 5, 6, 7],
                   floatfmt='.8f',
                   stralign='center',
                   numalign='right',
                   tablefmt='fancy_grid'))


@begin.subcommand
def open(symbol):
    try:
        raw = api.fetch_open_orders(symbol)
        if len(raw):
            droppable = ['info', 'lastTradeTimestamp', 'fee', 'timestamp']
            data = [{k.title(): v for k, v in r.items() if k not in droppable} for r in raw]

            print(tabulate(data, headers='keys'))
        else:
            print('No orders found for symbol: {}'.format(symbol))

    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.subcommand
def close(id, symbol):
    try:
        raw = api.cancel_order(id, symbol)
        if len(raw):

            # data = {k.title(): v for k, v in raw.items() if k not in droppable}
            if raw and 'Success' in raw and raw.get('Sucess', False):
                print(' - [DONE] Cancellation success for order number {:d}.')
            else:
                print( '- [FAIL] Order cancellation has failed.\n - Echange Error: {}'.format(raw.get('Error')))
        else:
            print('Cancel task ends without success.')

    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.subcommand
@begin.convert(amount=float, price=float)
def buy(symbol, amount, price):
    try:
        raw = api.create_order(symbol, 'limit', 'buy', amount, price)
        if len(raw):
            droppable = ['info', 'lastTradeTimestamp', 'fee', 'timestamp']
            data = {k.title(): v for k, v in raw.items() if k not in droppable}

            print(tabulate([data], headers='keys'))
        else:
            print('Buy order ends without success.')

    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.subcommand
@begin.convert(amount=float, price=float)
def sell(symbol, amount, price):
    try:
        raw = api.create_order(symbol, 'limit', 'sell', amount, price)
        if len(raw):
            droppable = ['info', 'lastTradeTimestamp', 'fee', 'timestamp']
            data = {k.title(): v for k, v in raw.items() if k not in droppable}

            print(tabulate([data], headers='keys'))
        else:
            print('Sell order ends without success.')
    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.subcommand
def balance():
    try:
        raw = api.fetch_balance()
        del raw['used'], raw['free'], raw['total'], raw['info']
        balance = {k: v for k, v in raw.items() if v['total'] > 0.0}
        headers = ['Symbol'] + [f.title() for f in list(list(balance.values())[0].keys())]
        print(
            tabulate([[k, *v.values()] for k, v in balance.items()], headers=headers, floatfmt='.2f',
                     disable_numparse=[3]))
    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.subcommand
@begin.convert(limit=int)
def ta(symbol, indicators, timeframe='15m', limit=100, csv=False, params=''):
    args = []
    if len(params):
        args = params.split(',') if ',' in params else [params]
    args = map(lambda a: float(a) if '.' in a else int(a), args)

    df = ohlc(symbol, timeframe, limit, _raw=True)  # type: pd.DataFrame
    df.index = df.pop('date')
    table_data = list()
    for indicator in indicators.split(','):
        fn = Function(indicator.upper())
        d = fn(df, *args).bfill().round(8)
        if csv:
            df[indicator.lower()] = d
        else:
            table_data.append([indicator.upper(), d[-1], d.diff().round(8)[-1]])
    if csv:
        from io import StringIO
        str_io = StringIO()
        df.insert(0, 'date', [int(d.timestamp()) for d in df.index])
        df = df.reset_index(drop=True)
        df.to_csv(str_io, index=False, float_format='.8f')
        print(str_io.getvalue())

    else:
        print('    === {} ==='.format(symbol))
        print(tabulate(table_data,
                       headers=['Indicator', 'Value', 'Diff'],
                       stralign='center',
                       numalign='right',
                       tablefmt='fancy_grid'))


@begin.subcommand
@begin.convert(limit=int)
def ohlc(symbol, timeframe='15m', limit=100, csv=False, _raw=False):

    try:
        raw = api.fetch_ohlcv(symbol, timeframe, limit=limit)

        df = pd.DataFrame(raw, columns=['ts', 'open', 'high', 'low', 'close', 'volume']).round(8)
        df['volume'] = df['volume'].round(2)
        df.insert(0, 'date', value=pd.to_datetime(df.pop('ts'), unit='ms'))

        if _raw:
            return df
        elif csv:
            from io import StringIO
            str_io = StringIO()
            df.insert(0, 'date',  [int(d.timestamp()) for d in df.pop('date')])
            df = df.reset_index(drop=True)
            df.to_csv(str_io, index=False)
            print(str_io.getvalue())
        else:
            print(tabulate(df.values,
                           headers=map(str.title, ['date', 'open', 'high', 'low', 'close', 'volume']),
                           tablefmt='fancy_grid', floatfmt='.8f', numalign='right', stralign='center',
                           disable_numparse=[0, 5]))
    except ccxt.errors.ExchangeError as err:
        print(str(err).split(',')[1].replace('"', ' '))


@begin.start
def run():
    pass
