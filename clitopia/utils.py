import term as trm
import time as tm

def check_symbol_exchange(symbol, exchanges=None):
    symbol = str(symbol).replace('_', '/')
    exchange = str()

    if '/' in symbol:
        currency, exchange = symbol.split('/')

    if exchanges is None:
        exchanges = ['USDT', 'BTC']

    return exchange in exchanges

def check_symbol_minvol(quote_volume, minvol=.1):
    return quote_volume > minvol


class Cursor:
    save = trm.saveCursor
    restore = trm.restoreCursor()
    up = lambda self, n: trm.up(n)
    pos = lambda self, r, c: trm.pos(r, c)
    down = lambda self, n: trm.down(n)
    home = lambda self: trm.homePos()

# aliases
class BeautyCLI(Cursor):

    def __init__(self, clear=True):
        if clear:
            tm.sleep(.25)
            self.cls()


    cls = lambda self: trm.clear()
    cls_ln = lambda self: trm.clearLine()
    fmt = lambda self, *args, **kwargs: trm.format(*args, **kwargs)
    wrt = lambda self, *args, **kwargs: trm.write(*args, **kwargs)
    wln = lambda self, *args, **kwargs: trm.writeLine(*args, **kwargs)
    right = lambda self, t: trm.right(t)
    center = lambda self, t: trm.center(t)


    def echo(self, text, row=None, col=None, align='left', *args):
        formated_text = text

        if align in 'right':
            formated_text = self.right(formated_text)
        elif align in 'center':
            formated_text = self.center(formated_text)

        if row is not None and col is not None:
            self.pos(row, col)
        elif row is not None and row is None:
            self.pos(row, 1)
        elif col is not None and row is None:
            self.pos(1, col)

        self.wln(formated_text, *args)
