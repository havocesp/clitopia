#!/usr/bin/env python
# -*- coding: utf-8 -*-
from finta import TA
import pandas as pd
from blessed import Terminal
from api import ApiClient
import os

def main():
    term = Terminal()
    term.stream.write(term.clear())
    term.stream.write(term.move(0, 0))
    key, secret = os.getenv('CRYPTOPIA_MAIN_KEY'), os.getenv('CRYPTOPIA_MAIN_SECRET')

    api = ApiClient(key, secret)
    symbols = api.get_ticker()
    print(symbols.keys())
    with term.cbreak():

        val = ''

        while val.lower() != 'q':
            val = term.inkey(timeout=5)
            if not val:
                # timeout
                print("It sure is quiet in here ...")
            elif val.is_sequence:
                print("got sequence: {0}.".format(
                        (str(val), val.name, val.code)))
            elif val:
                if val == 'r':
                    roc = TA.ROC(pd.DataFrame(), period=3)[-1]
                    print(roc)


if __name__ == '__main__':
    main()

# if __name__ == '__main__':
#     pairs = ['DGB/BTC', 'HXX/BTC', 'ZCL/BTC', 'BTC/USDT']
#
#     max_book_rows = 5
#
#     for pair in pairs:
#         book = api.fetch_order_book(pair, limit=max_book_rows)
#         asks, bids = book['asks'], book['bids']
#
#         nums_template = '{: >12.8f} - {: >9.3f}'
#         if '/USDT' in pair:
#             nums_template = '{: >9.3f} - {: >12.8f}'
#
#         print(' \n==================== {} =================='.format(pair))
#         print('  - Bids: ')
#         for row_num in range(max_book_rows):
#             print(nums_template.format(*bids[row_num]))
#         print('\n  - Asks: ')
#         for row_num in range(max_book_rows):
#             print(nums_template.format(*asks[row_num]))
#         print(' ==============================================')
