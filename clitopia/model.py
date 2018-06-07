class BaseItem:

    def __init__(self, **data):
        self.__dict__.update(data)


    def __eq__(self, other):
        return self.__dict__


    def __setattr__(self, key, value):
        self.__dict__.update({key: value})


    def __str__(self):
        return str(self.__dict__)


    def __getitem__(self, item):
        return self.__dict__.get(item)


    def __getattr__(self, item):
        return self.__dict__.get(item)


    def __setitem__(self, key, value):
        self.__dict__.update({key: value})

class Balance(BaseItem):
    free, used, total = 0.0, 0.0, 0.0

