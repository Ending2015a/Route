import os
import sys
import time
import logging


class Route(dict):
    _sep = '.'
    _auto_convert_dict = True

    @classmethod
    def set_sep(cls, sep='.'):
        cls._sep = sep

    # === Override dict ===

    def __init__(self, it=None, **kwargs):

        if it is not None:
            self.update(it)
        if not kwargs:
            self.update(kwargs)

    def splitkey(self, key, sep=None):
        if sep is None:
            sep = self._sep
        if isinstance(key, str):
            keys = key.split(sep, 1)
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
            # convert dict object to Route (if auto_convert_dict is enabled)
            if self._auto_convert_dict and isinstance(v, dict):
                self.__setitem__(k, Route(v))
            else:
                self.__setitem__(k, v)

    def __setitem__(self, key, item):

        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__setitem__(key, item)
        else:
            # --- handle keys ---
            # key does not exist, create new
            if not key in super(Route, self).keys():
                super(Route, self).__setitem__(key, Route())

            # key exists, but value is not an instance of Route. Overwrite if self._auto_convert_dict == True
            elif self._auto_convert_dict and (not isinstance(super(Route, self).__getitem__(key), Route)):
                # if it is an instance of dict, convert to Route
                if isinstance(super(Route, self).__getitem__(key), dict):
                    super(Route, self).__setitem__(key, Route(super(Route, self).__getitem__(key)))

            # --- handle items ---
            # not subscriptable
            # for example, key conflict: 'AAA/BBB/CCC' is not a dict, but 'AAA/BBB/CCC/DDD' assigned
            if not hasattr(super(Route, self).__getitem__(key), '__setitem__'):
                raise TypeError('\'{}\' object for key \'{}\' does not support item assignment'.format(type(super(Route, self).__getitem__(key)).__name__, key))

            # convert dict object to Route (if auto_convert_dict is enabled)
            if self._auto_convert_dict and isinstance(item, dict):
                super(Route, self).__getitem__(key).__setitem__(rem, Route(item))
            else:
                super(Route, self).__getitem__(key).__setitem__(rem, item)

    def __getitem__(self, key):

        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__getitem__(key)
        else:
            if not hasattr(super(Route, self).__getitem__(key), '__getitem__'):
                raise TypeError('\'{}\' object for key \'{}\' is not subscriptable'.format(type(super(Route, self).__getitem__(key)).__name__, key))
            return super(Route, self).__getitem__(key).__getitem__(rem)

    def __delitem__(self, key):

        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__delitem__(key)
        else:
            if not hasattr(super(Route, self).__getitem__(key), '__delitem__'):
                raise TypeError('\'{}\' object for key \'{}\' does not support item deletion'.format(type(super(Route, self).__getitem__(key)).__name__, key))
            super(Route, self).__getitem__(key).__delitem__(rem)

    def __contains__(self, key):

        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__contains__(key)
        else:
            return (super(Route, self).__contains__(key) and   # contains key in current layer
                    isinstance(super(Route, self).__getitem__(key), dict) and  # value is an instance of dict
                    super(Route, self).__getitem__(key).__contains__(rem)) # remain keys exist in the next layer of dict object

    def get(self, key, default=None):

        key, rem = self.splitkey(key)

        # end of Route
        if rem is None:
            return super(Route, self).get(key, default)
        else:
            # not end of Route, check if the key exists
            tmp = super(Route, self).get(key, None)
            # if not exists, return default
            if tmp is None:
                return default
            # if exists
            else:
                # if next Route exists
                if isinstance(tmp, Route):
                    return tmp.get(rem, default)
                else:
                    return default

        return default

    def pop(self, key, default=None):

        key, rem = self.splitkey(key)

        # end of Route
        if rem is None:
            return super(Route, self).pop(key, default)
        else:
            tmp = super(Route, self).pop(key, None)
            if tmp is None:
                return default
            else:
                if isinstance(tmp, Route):
                    return tmp.pop(rem, default)
                else:
                    return default

        return default

    # === custom function ===

    def plain(self, sep=None):
        '''
        Plain dict using given sep

        d = Route({
            'AAA': {
                'BBB': {
                    'CCC': {
                        'item1': 10,
                        'item2': 20,
                    },
                    'DDD': {
                        'item3': 30,
                        'item4': 40,
                    }
                }
            }
        })

        print(type(d.plain()))

        for k, v in d.plain(sep='.'):
            print('{}: {}'.format(k, v))

        # This will print out:
        # <class 'dict'>
        # AAA.BBB.CCC.item1: 10
        # AAA.BBB.CCC.item2: 20
        # AAA.BBB.DDD.item3: 30
        # AAA.BBB.DDD.item4: 40
        '''

        if sep is None:
            sep = self._sep

        d = {}
        for k, v in self.items():
            
            if isinstance(v, Route):
                # recursive call
                for _k, _v in v.plain(sep=sep):
                    d[sep.join([k, _k])] = _v
            else:
                d[k] = v

        return d.items()

    # === archive/restore ===

    def archive_zip(self, filename, mode='w', **kwargs):
        
        # === import ===
        import zipfile

        _, ext = os.path.splitext(filename)

        if not ext:
            filename += '.zip'

        
        with zipfile.ZipFile(filename, mode, **kwargs) as zf:
            for k, v in self.plain('/'):

                # retrieve serializer and ext
                serializer, ext = self._get_serializer_with_ext(type(v))

                # serialize value
                serialized_v = serializer(v)

                # write serialized value to zip file
                zf.writestr(k+ext, serialized_v)

    def archive(self, filename, _type=None, **kwargs):
        '''
        Archive Route object to the given zip type

        :param filename: the name of the archive file
        :param _type: archive type, must be one of ['zip']
        '''

        if _type is None:
            _, _type = os.path.splitext(filename)

            if not _type:
                _type = '.zip'
        else:
            if not _type.startswith('.'):
                _type = '.' + _type
            

        if _type == '.zip':
            self.archive_zip(filename, **kwargs)
        else:
            raise NotImplementedError('Method not implemented for archiving `{}` file'.format(_type))

    @classmethod
    def restore_zip(self, filename, mode='r', **kwargs):
        
        # === import ===
        import zipfile

        route = self()

        with zipfile.ZipFile(filename, mode) as zf:
            for name in zf.namelist():
                if name.endswith('/'):
                    continue

                serialized_v = zf.open(name).read()

                k, ext = os.path.splitext(name)
                k = k.replace('/', self._sep)

                deserializer = self._get_deserializer(ext)

                v = deserializer(serialized_v)

                route[k] = v

        return route

    @classmethod
    def restore(self, filename, _type=None, **kwargs):
        '''
        Restore Route object from archive file

        :param filename: the name of the archive file
        :param _type: archive type.
        '''

        if _type is None:
            _, _type = os.path.splitext(filename)

            if not _type:
                _type = '.zip'

        else:
            if not _type.startswith('.'):
                _type = '.' + _type

        if _type == '.zip':
            return self.restore_zip(filename, **kwargs)
        else:
            raise NotImplementedError('Method not implemented for restoring `{}` file'.format(_type))


    # === serializer/deserializer ===

    _serializer = {}
    _deserializer = {}
    _serialize_ext = {}
    _deserialize_ext = {}

    @classmethod
    def serialize(self, value):
        serializer, _ = self._get_serializer_with_ext(type(value))

        return serializer(value)


    @classmethod
    def deserialize(self, class_type, value):
        deserializer = self._deserializer.get(class_type, None)

        if deserializer is None:
            deserializer = self._deserializer[Route]

        return deserializer(value)

    @classmethod
    def _get_serializer_with_ext(self, class_type):
        # retrieve serializer and ext
        serializer = self._serializer.get(class_type, None)
        ext = self._serialize_ext.get(class_type, None)

        # if serialize is None, then retrieve default serielizer and ext
        if serializer is None:
            serializer = self._serializer[Route]
            ext = self._serialize_ext[Route]

        return serializer, ext

    @classmethod
    def _get_deserializer(self, ext):
        # retrieve class type by ext
        class_type = self._deserialize_ext.get(ext, None)
        # retrieve deserialize by class type
        deserializer = self._deserializer.get(class_type, None)

        # if deserializer is None, then use default deserializer
        if deserializer is None:
            deserializer = self._deserializer[Route]

        return deserializer


    @classmethod
    def set_serializer(cls, class_type, serialize_func, ext, overwrite=False):

        # check redefine
        if (class_type in cls._serializer) and (not overwrite):
            raise RuntimeError('The serializer of class `{}` is already defined. Please set overwrite=True to ignore this error'.format(class_type.__name__))

        # formalize ext
        if not ext.startswith('.'):
            ext = '.' + ext

        cls._serializer[class_type] = serialize_func
        cls._serialize_ext[class_type] = ext

    @classmethod
    def set_deserializer(cls, class_type, deserialize_func, ext, overwrite=False):

        # check redefine
        if (class_type in cls._deserializer) and (not overwrite):
            raise RuntimeError('The deserializer of class `{}` is already defined. Please set overwrite=True to ignore this error'.format(class_type.__name__))

        # formalize ext
        if not ext.startswith('.'):
            ext = '.' + ext

        # check whether ext is in use by other class
        if (ext in cls._deserialize_ext) and (not overwrite):
            raise RuntimeError('The extension `{}` is already in use by class `{}`'.format(ext, cls._deserialize_ext[ext].__name__))

        cls._deserializer[class_type] = deserialize_func
        cls._deserialize_ext[ext] = class_type


    @classmethod
    def serializable(cls, ext, overwrite=False):
        '''

        Class decorator

        example usage:

            @Route.serializable(ext='.my_list')
            class MyList():
                def __init__(self):
                    ...
                # your
                # class
                # definition
                
            @MyList.serializer(overwrite=True)
            def my_serializer(value):
                ...

                return serialized_value  # either str or bytes

            @MyList.deserializer(overwrite=True)
            def my_deserializer(serialied_value):
                ...

                return MyList(value)
        '''
        def _cls_serializable(class_type):
            @staticmethod
            def set_serializer(overwrite=overwrite):
                def _serializer(func):
                    cls.set_serializer(class_type, func, ext, overwrite)
                    class_type.serialize = staticmethod(func)
                    return func
                return _serializer

            @staticmethod
            def set_deserializer(overwrite=overwrite):
                def _deserializer(func):
                    cls.set_deserializer(class_type, func, ext, overwrite)
                    class_type.deserialize = staticmethod(func)
                    return func
                return _deserializer

            class_type.set_serializer = set_serializer
            class_type.set_deserializer = set_deserializer

            return class_type

        return _cls_serializable
            

    # decorator
    @classmethod
    def serializer(cls, class_type, ext, overwrite=False):
        '''
        Function decorator

        example usage:

            @Route.serializer(MyList, ext='.my_list', overwrite=True)
            def my_list_serializer(my_list):
            
                if isinstance(my_list, MyList):
                    serialized_value = my_list.my_serializing_method()
                else:
                    raise Exception('Error')

                return serialized_value
        '''
        def _set_serializer(func):
            cls.set_serializer(class_type, func, ext, overwrite)

        return _set_serializer

    # decorator
    @classmethod
    def deserializer(cls, class_type, ext, overwrite=False):
        '''
        Function decorator

        example usage:

            @Route.deserializer(MyList, ext='.my_list', overwrite=True)
            def my_list_deserializer(serialized_value):

                value = MyList.my_deserializing_method(serialized_value)

                return value
        '''
        def _set_deserializer(func):
            cls.set_deserializer(class_type, func, ext, overwrite)

        return _set_deserializer


# === global ===

def set_sep(sep='.'):
    Route._sep = sep

def set_default_serializer(serialize_func, ext, overwrite=False):

    Route.set_serializer(Route, serialize_func, ext, overwrite)

def set_default_deserializer(deserialize_func, ext, overwrite=False):
    
    Route.set_deserializer(Route, deserialize_func, ext, overwrite)



'''
Some pre-defined serializer/deserializer
'''

# === default ===

try:
    import dill
    pickle = dill
except:
    try:
        import cloudpickle
        pickle = cloudpickle
    except:
        import pickle

set_default_serializer(pickle.dumps, '.pkl', overwrite=True)
set_default_deserializer(pickle.loads, '.pkl', overwrite=True)

# === str ===

@Route.serializer(str, ext='.txt', overwrite=True)
def str_serializer(string):
    return string

@Route.deserializer(str, ext='.txt', overwrite=True)
def str_deserializer(serialized_string):
    return serialized_string

# === bytes ===

@Route.serializer(bytes, ext='.bytes', overwrite=True)
def bytes_serializer(byte_string):
    return byte_string

@Route.deserializer(bytes, ext='.bytes', overwrite=True)
def bytes_deserializer(serialized_byte_string):
    return serialized_byte_string


# === numpy array ===

try:
    import numpy as np
    import io

    @Route.serializer(np.ndarray, ext='.npy', overwrite=True)
    def np_serializer(array):
        byte_fp = io.BytesIO()
        np.save(byte_fp, array)
        return byte_fp.getvalue()


    @Route.deserializer(np.ndarray, ext='.npy', overwrite=True)
    def np_deserializer(serialized_array):
        byte_fp = io.BytesIO(serialized_array)
        contents = np.load(byte_fp)
        return contents

except:
    pass
