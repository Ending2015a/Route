# --- built in ---
import os
import abc
import sys
import copy
import time
import logging

from typing import Any
from typing import Type
from typing import Tuple
from typing import Hashable
from typing import NoReturn
from typing import Optional

from builtins import dict as _dict

from collections import Iterable
from collections import Mapping
from collections import OrderedDict


# --- 3rd party ---

# --- my module ---


__all__ = [
    'set_base_dict_type',
    'set_sep',
    'enable_auto_convert',
    'disable_auto_convert',
    'Route',
    'OrderedRoute',
    '_Route'
]

_BASE_DICT = _dict
_ROUTE_LIST = []
_DEFAULT_SEP = '.'

def set_base_dict_type(DICT=_dict) -> NoReturn:
    '''
    Set base dict type for Route

    DICT can be any mapping
    '''
    global _BASE_DICT
    _BASE_DICT = DICT

def set_sep(sep: str =_DEFAULT_SEP) -> NoReturn:
    '''
    Set seperator
    '''
    global _ROUTE_LIST

    for routeclass in _ROUTE_LIST:
        routeclass.set_sep(sep)

def enable_auto_convert() -> NoReturn:
    '''
    Enable dict auto convertion
    '''
    global _ROUTE_LIST

    for routeclass in _ROUTE_LIST:
        routeclass.enable_auto_convert()

def disable_auto_convert() -> NoReturn:
    '''
    Disable dict auto convertion
    '''
    global _ROUTE_LIST

    for routeclass in _ROUTE_LIST:
        routeclass.disable_auto_convert()


def _Route(_base_dict: Type[_BASE_DICT] =_BASE_DICT, 
           _base_meta: Type[abc.ABCMeta] =abc.ABCMeta, 
           sep: str =_DEFAULT_SEP, 
           auto_cvt: bool =True) -> 'Route':
    '''
    Create Route class
    '''
    global _ROUTE_LIST

    # --- class def start

    class Route(_base_dict, metaclass=_base_meta):
        
        # === Attributes ===

        _sep = '.'
        _auto_convert_dict = True

        # === Main interfaces ===

        @classmethod
        def set_sep(cls, sep: str =_DEFAULT_SEP) -> NoReturn:
            cls._sep = sep or cls._sep
        
        @classmethod
        def enable_auto_convert(cls) -> NoReturn:
            cls._auto_convert_dict = True

        @classmethod
        def disable_auto_convert(cls) -> NoReturn:
            cls._auto_convert_dict = False

        @classmethod
        def splitkey(cls, key: str, sep: str =None) -> Tuple[str, Optional[str]]:
            sep = sep or cls._sep

            # only str can be splitted
            if isinstance(key, str):
                keys = key.split(sep, 1)
                if len(keys) == 2:
                    return tuple(keys)
            
            return key, None

        # === Override dict ===

        def __init__(self, *args, **kwargs) -> NoReturn:
            
            self.update(*args, **kwargs)

        def update(self, *args, **kwargs) -> NoReturn:

            if len(args) > 1:
                raise TypeError('dict expected at most 1 arguments, got {}'.format(len(args)))
            elif len(args) == 1:

                it = args[0]
                if isinstance(args[0], Mapping):
                    itr = iter(args[0].items())
                else:
                    itr = iter(args[0])
                
                for k, v in itr:
                    # convert dict object to Route (if auto_convert_dict is enabled)
                    if self._auto_convert_dict and isinstance(v, Mapping):
                        self.__setitem__(k, Route(v))
                    else:
                        self.__setitem__(k, v)

            if len(kwargs) > 0:
                self.update(kwargs)
        
        def __setitem__(self, keys: str, item: Any) -> NoReturn:

            key, rem = self.splitkey(keys)

            if rem is None:
                if self._auto_convert_dict and isinstance(item, Mapping):
                    super(Route, self).__setitem__(key, Route(item))
                else:
                    super(Route, self).__setitem__(key, item)
            else:
                # --- handle key ---
                # key does not exist, create new
                if key not in super(Route, self).keys():
                    super(Route, self).__setitem__(key, Route())

                # key exists, but value is not an instance of Route. Overwrite if self._auto_convert_dict == True
                elif self._auto_convert_dict and (not isinstance(super(Route, self).__getitem__(key), type(self))):
                    # if it is an instance of Mapping, convert to Route
                    if isinstance(super(Route, self).__getitem__(key), Mapping):
                        super(Route, self).__setitem__(key, type(self)(super(Route, self).__getitem__(key)))
                    # if not, replace it by Route()
                    else:
                        super(Route, self).__setitem__(key, type(self)())

                # --- handle rem ---
                # convert dict object to Route (if auto_convert_dict is enabled)
                super(Route, self).__getitem__(key).__setitem__(rem, item)

        def __getitem__(self, keys: Hashable) -> Any:
            
            key, rem = self.splitkey(keys)

            if rem is None:
                return super(Route, self).__getitem__(key)
            else:
                return super(Route, self).__getitem__(key)[rem]

        def __delitem__(self, keys: Hashable) -> NoReturn:

            key, rem = self.splitkey(keys)

            if rem is None:
                super(Route, self).__delitem__(key)
            else:
                del super(Route, self).__getitem__(key)[rem]


        def __contains__(self, keys: Hashable) -> bool:

            key, rem = self.splitkey(keys)

            if rem is None:
                return super(Route, self).__contains__(key)
            else:
                return (super(Route, self).__contains__(key) and
                        hasattr(super(Route, self).__getitem__(key), '__contains__') and
                        super(Route, self).__getitem__(key).__contains__(rem))

        def get(self, keys: Hashable, default: Any =None) -> Any:

            if self.__contains__(keys):
                return self.__getitem__(keys)
            else:
                return default

        def pop(self, keys: Hashable, default: Any =None) -> Any:

            if self.__contains__(keys):
                item = self.__getitem__(keys)
                self.__delitem__(keys)
                return item
            else:
                return default

        def __copy__(self) -> __qualname__:

            ndict = type(self)()

            for k, v in self.items():
                super(Route, ndict).__setitem__(k, v)

            return ndict

        def __deepcopy__(self, memo) -> __qualname__:

            ndict = type(self)()

            for k, v in self.items():
                super(Route, ndict).__setitem__(k, copy.deepcopy(v, memo))

            return ndict


        # === custim function ===

        def plain(self, sep: str =None) -> _base_dict:
            
            sep = sep or self._sep

            d = _base_dict()

            for k, v in self.items():

                if isinstance(v, type(self)):
                    # recursive call
                    for _k, _v in v.plain(sep=sep).items():
                        d[sep.join([k, _k])] = _v
                else:
                    d[k] = v

            return d

        def to_base(self) -> _base_dict:

            return _base_dict((k, v.to_base()) if isinstance(v, type(self)) else (k, v) for k, v in self.items())

    # --- class def end

    Route.__copy__.__annotations__['return'] = Route
    Route.__copy__.__annotations__['return'] = Route


    _ROUTE_LIST.append(Route)

    return Route


Route = _Route()
OrderedRoute = _Route(OrderedDict)

# update qualname
Route.__qualname__ = 'Route'
OrderedRoute.__qualname__ = 'OrderedRoute'