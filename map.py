
class Map(dict):
    _sep = '.'

    def __init__(self, it=None, **kwargs):

        if it is not None:
            self.update(it)
        if kwargs is not None:
            self.update(kwargs)

    def splitkey(self, key):
        if isinstance(key, str):
            keys = key.split(self._sep, 1)
            if len(keys) == 2:
                return keys[0], keys[1] #key, remain
            else:
                return keys[0], None
        else:
            return key, None
        
    def update(self, it):
        for k, v in it.items():
            if isinstance(v, dict):
                self.__setitem__(k, Map(v))
            else:
                self.__setitem__(k, v)

    def __setitem__(self, key, item):
        key, rem = self.splitkey(key)

        if rem is None:
            super(Map, self).__setitem__(key, item)
        else:
            if not key in super(Map, self).keys():
                super(Map, self).__setitem__(key, Map())

            elif not isinstance(super(Map, self).__getitem__(key), Map):
                super(Map, self).__setitem__(key, Map())

            super(Map, self).__getitem__(key).__setitem__(rem, item)

    def __getitem__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Map, self).__getitem__(key)
        else:
            return super(Map, self).__getitem__(key).__getitem__(rem)

    def __delitem__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            super(Map, self).__delitem__(key)
        else:
            super(Map, self).__getitem__(key).__delitem__(rem)

    def __contains__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Map, self).__contains__(key)
        else:
            return (super(Map, self).__contains__(key) and   # contains key 
                    isinstance(super(Map, self).__getitem__(key), Map) and  # value is an instance of Map object
                    super(Map, self).__getitem__(key).__contains__(rem)) # remain keys are in the Map object

    def get(self, key, default=None):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Map, self).get(key, default)
        else:
            tmp = super(Map, self).get(key, default)
            if tmp is not None:
                return tmp.get(rem, default)
            else:
                return tmp


