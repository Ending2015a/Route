import os
import sys
import time
import logging


class Route(dict):
    _sep = '/'
    _auto_convert_dict = True

    @classmethod
    def set_sep(cls, sep='/'):
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
            if self._auto_convert_dict and isinstance(v, dict):
                self.__setitem__(k, Route(v))
            else:
                self.__setitem__(k, v)

    def __setitem__(self, key, item):

        # terminate
        #if self.terminate:
        #    super(Route, self).__setitem__(key, item)
        #    return

        # no terminate

        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__setitem__(key, item)
        else:
            if not key in super(Route, self).keys():
                super(Route, self).__setitem__(key, Route())

            elif not isinstance(super(Route, self).__getitem__(key), Route):
                super(Route, self).__setitem__(key, Route())


            
            if self._auto_convert_dict and isinstance(item, dict):
                super(Route, self).__getitem__(key).__setitem__(rem, Route(item))
            else:                
                super(Route, self).__getitem__(key).__setitem__(rem, item)

    def __getitem__(self, key):

        # terminate
        #if self.terminate:
        #    return super(Route, self).__getitem__(key)


        # no terminate
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__getitem__(key)
        else:
            return super(Route, self).__getitem__(key).__getitem__(rem)

    def __delitem__(self, key):

        # terminate
        #if self.terminate:
        #    super(Route, self).__delitem__(key)
        #    return

        # no terminate
        key, rem = self.splitkey(key)

        if rem is None:
            super(Route, self).__delitem__(key)
        else:
            super(Route, self).__getitem__(key).__delitem__(rem)

    def __contains__(self, key):

        # terminate
        #if self.terminate:
        #    return super(Route, self).__contains__(key)

        # no terminate
        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).__contains__(key)
        else:
            return (super(Route, self).__contains__(key) and   # contains key 
                    isinstance(super(Route, self).__getitem__(key), Route) and  # value is an instance of Route object
                    super(Route, self).__getitem__(key).__contains__(rem)) # remain keys are in the Route object




    def get(self, key, default=None):

        # terminate
        #if self.terminate:
        #    return super(Route, self).get(key, default)

        # no terminate

        key, rem = self.splitkey(key)

        if rem is None:
            return super(Route, self).get(key, default)
        else:
            tmp = super(Route, self).get(key, default)
            if tmp is not None:
                return tmp.get(rem, default)
            else:
                return tmp


    # === custom function ===

    def plain(self, sep=None):

        if sep is None:
            sep = self._sep

        d = {}
        for k, v in self.items():
            
            if isinstance(v, Route):
                #if v.terminate: # convert to dict type
                #    v = dict(v)
                #    v.__term__ = True
                #    d[k] = dict(v)
                #else:
                for _k, _v in v.plain(sep=sep):
                    d[sep.join([k, _k])] = _v
            else:
                d[k] = v

        return d.items()

    #@property
    #def terminate(self):
    #    return self.__term__

    #@terminate.setter
    #def terminate(self, term: bool):
    #    self.__term__ = term

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
        if ext in cls._deserialize_ext:
            raise RuntimeError('The extension `{}` is already in use by class `{}`'.format(ext, cls._deserialize_ext[ext].__name__))

        cls._deserializer[class_type] = deserialize_func
        cls._deserialize_ext[ext] = class_type

    # decorator
    @classmethod
    def serializer(cls, class_type, ext, overwrite=False):
        '''
        example usage:

            @Route.serializer(MyClass, ext='.mcls', overwrite=True)
            def my_class_serializer(value):
            
                if isinstance(value, MyClass):
                    serialized_value = value.my_serializing_method()
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
        example usage:

            @Route.deserializer(MyClass, ext='.mcls', overwrite=True)
            def my_class_deserializer(serialized_value):

                value = MyClass.my_deserializing_method(serialized_value)

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
