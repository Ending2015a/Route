class Route(dict):
    _sep = '.'

    @classmethod
    def set_sep(cls, sep='.'):
        cls._sep = sep

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

        if isinstance(it, dict):
            itr = iter(it.items())
        else:
            itr = iter(it)

        for k, v in itr:
            if isinstance(v, dict):
                self.__setitem__(k, Route(v))
            else:
                self.__setitem__(k, v)

    def __setitem__(self, key, item):
        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__setitem__(key, item)
        else:
            if not key in super(Route, self).keys():
                super(Route, self).__setitem__(key, Route())

            elif not isinstance(super(Route, self).__getitem__(key), Route):
                super(Route, self).__setitem__(key, Route())

            if isinstance(item, dict):
                super(Route, self).__getitem__(key).__setitem__(rem, Route(item))
            else:                
                super(Route, self).__getitem__(key).__setitem__(rem, item)

    def __getitem__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__getitem__(key)
        else:
            return super(Route, self).__getitem__(key).__getitem__(rem)

    def __delitem__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__delitem__(key)
        else:
            super(Route, self).__getitem__(key).__delitem__(rem)

    def __contains__(self, key):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__contains__(key)
        else:
            return (super(Route, self).__contains__(key) and   # contains key 
                    isinstance(super(Route, self).__getitem__(key), Route) and  # value is an instance of Route object
                    super(Route, self).__getitem__(key).__contains__(rem)) # remain keys are in the Route object

    def plain(self):
        d = {}
        for k, v in self.items():
            
            if isinstance(v, Route):
                for _k, _v in v.plain():
                    d[self._sep.join([k, _k])] = _v

            else:
                d[k] = v

        return d.items()

    def get(self, key, default=None):
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).get(key, default)
        else:
            tmp = super(Route, self).get(key, default)
            if tmp is not None:
                return tmp.get(rem, default)
            else:
                return tmp

def set_sep(sep='.'):
    Route._sep = sep

