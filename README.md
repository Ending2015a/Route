# Route

A new generation of python dict.

## Examples

### 1. Set/Retrieve values

```python
from route import Route
Route.set_sep(sep='/')  # the default seperator is '.'

# initialize
a = Route({'a': 10, 'b': 20})

print(a['a'])     # 10
print(a['foo'])   # 20

# set item
a['AAA/BBB/CCC'] = 30
print(a)     # {'a': 10, 'b': 20, 'AAA': {'BBB': {'CCC': 30}}}

# set item
a['AAA/BBB/DDD'] = 40
print(a)     # {'a': 10, 'b': 20, 'AAA': {'BBB': {'CCC': 30, 'DDD': 40}}}

# get item
print(a['AAA/BBB'])  # {'CCC': 30, 'DDD': 40}

# get item or default value
print(a.get('AAA/BBB/DDD', 'NotFound'))   # 40

# get item or default value
print(a.get('AAA/BBB/EEE', 'NotFound'))   # NotFound
```

### 2. Contains
```python
from route import Route

a = Route({'A.B.C.D.E': 30})

print(a)    # {'A': {'B': {'C': {'D': {'E': 30}}}}}

print('C' in a['A.B'])       # True
print('C.E' in a['A.B'])     # False
print('C.D' in a['A.B'])     # True
print('C.D.E' in a['A.B'])   # True
print('D.E' in a['A.B.C'])   # True
```

## Compare with python dict

### 1. Create nested dict
* python dict:
```python
d = {
    'AAA': {
        'BBB': {
            'CCC': {
                'DDD-1': {
                    'EEE': {
                        'FFF': {
                            'GGG': {
                                'item1': 10,
                                'item2': 20,
                            }
                        }
                    }
                },
                'DDD-2': {
                    'EEE': {
                        'FFF': {
                            'GGG': {
                                'item3': 30,
                                'item4': 40
                            }
                        }
                    }
                }
            }
        }
    }
}


print(d['AAA']['BBB']['CCC']['DDD-1']['EEE']['FFF']['GGG']['item1'])  # 10
print(d['AAA']['BBB']['CCC']['DDD-2']['EEE']['FFF']['GGG']['item3'])  # 30
```

* Route
```python
from route import Route
Route.set_sep('/')    # the default separator is '.'

d = Route()
d['AAA/BBB/CCC/DDD-1/EEE/FFF/GGG'] = {'item1': 10, 'item2': 20}
d['AAA/BBB/CCC/DDD-2/EEE/FFF/GGG'] = {'item3': 30, 'item4': 40}

print(d['AAA/BBB/CCC/DDD-1/EEE/FFF/GGG/item1'])  # 10
print(d['AAA/BBB/CCC/DDD-2/EEE/FFF/GGG/item3'])  # 30
```

or 
```python
from route import Route
Route.set_sep('/')    # the default separator is '.'

d = Route({
    'AAA/BBB/CCC': {
        'DDD-1/EEE/FFF/GGG': {'item1': 10, 'item2': 20},
        'DDD-2/EEE/FFF/GGG': {'item3': 30, 'item4': 40},
    }
})

print(d['AAA/BBB/CCC/DDD-1/EEE/FFF/GGG/item1'])  # 10
print(d['AAA/BBB/CCC/DDD-2/EEE/FFF/GGG/item3'])  # 30
```


### 2. Safely retrieve items that might not exist
* python dict:
```python

# create nested dict
d = {
    'AAA': {
        'BBB': {
            'CCC': {
                'DDD': {
                    'XXX': 10
                }
            }
        }
    }
}

def get_value(d, path, default=None):
    v = d
    for p in path:
        v = v.get(p, None)

        if (v is None) or (not isinstance(v, dict)):
            return default
    return v


path = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE']

print(get_value(d, path, default='NotFound'))   # NotFound
```

* Route
```python
from route import Route
Route.set_sep(sep='/')    # the default seperator is '.'

# create nested dict
d = Route({'AAA/BBB/CCC/DDD/XXX': 10})

print(d.get('AAA/BBB/CCC/DDD/EEE', 'NotFound'))   # NotFound
```


## Advance features

### 1. Auto conversion
When you assign a dict instance to the Route object, the dict will be automatically converted into a Route object:
```python
from route import Route
Route.set_sep('/')   # the default separator is '.'

d = Route({
    
    'AAA/BBB/CCC-1': {
        # this dict will be converted into Route, if Route._auto_covert_dict == Ture
        'DDD/EEE/FFF': {
            'item1': 10
        }
    }
})

d['AAA/BBB/CCC-2'] = {
    # this dict will be converted into Route, if Route._auto_convert_dict == Ture
    'DDD/EEE/FFF/item2': 20
}

```

If you want to disable this feature, you can set `Route._auto_convert_dict = False`.


```python
from route import Route
from collections import OrderedDict

# OrderedDict will be converted into Route
d = Route({'unordered': OrderedDict()})

print(type(d['unordered']))   # route.Route

# set to False
Route._auto_convert_dict = False


d = Route({'ordered': OrderedDict()})

print(type(d['ordered']))     # collections.OrderedDict

d['ordered.aaa'] = 1
d['ordered.bbb'] = 2
d['ordered.ccc'] = 3

print(d)   # {'ordered': OrderedDict([('aaa', 1), ('bbb', 2), ('ccc', 3)])}
```



### 2. Archive
This feature can compress Route object into a zip file

```python
from route import Route
Route.set_sep('/')   # the default separator is '.'

d = Route({'AAA/BBB': 10, 'AAA/CCC': 20, 'AAA/DDD/EEE': 30})
print(d)   # {'AAA': {'BBB': 10, 'CCC': 20, 'DDD': {'EEE': 30}}}


d.archive('my_route.zip')

a = Route.restore('my_route.zip')
print(a)   # {'AAA': {'BBB': 10, 'CCC': 20, 'DDD': {'EEE': 30}}}
```

The serialization methods for below types have already been implemented:
* `np.ndarray` (save as .npy)
* `str` (.txt)
* `bytes` (.bytes)

By default, one of the libs, [dill](https://github.com/uqfoundation/dill.git), [cloudpickle](https://github.com/cloudpipe/cloudpickle.git), or build-in pickle lib is chosen as the default serialization method for other types. But, you can also implement your own serialization method for your classes.


### 2. Customize serializer/deserializer
There are mainly two ways to design your own serialization method:

1. Class decorator
```python
from route import Route
Route.set_sep('/')    # the default separator is '.'

# custom type
@Route.serializable(ext='.my_list')     # Mark your class as serializable, and set the extension.
class MyIntList:
    def __init__(self, *integers):
        self.integers = integers

    # your class definitions


@MyIntList.set_serializer()  # define your serializer for your serializable class
def my_serializer(my_list):
    int_string = ', '.join( [ str(x) for x in my_list.integers ] )

    return int_string  # return value must be either 'str' or 'bytes'


@MyIntList.set_deserializer()  # define your deserializer for your serializable class
def my_deserializer(int_string):
    integers = [int(x) for x in int_string.split(',')]

    return MyIntList(*integers)


# If you want to re-define the de/serialization methods, you can set overwrite=True

@MyIntList.set_serializer(overwrite=True)
def redef_my_serializer(my_list):
    int_string = '\n'.join( [ str(x) for x in my_list.integers ] )

    return int_string

@MyIntList.set_deserializer(overwrite=True)
def redef_my_deserializer(int_string):
    integers = [int(x) for x in int_string.split('\n')]

    return MyIntList(*integers)


ints = MyIntList(5, 6, 7, 8, 9)

d = Route({
    'My/Int/List': ints
})

d.archive('my_archive.zip')
```

Re-use the serialization methods:
```python
ints = MyIntList(5, 6, 7, 8, 9)
serialized = MyIntList.serialize(ints)

print(serialized)
print(MyIntList.deserialize(serialized))
```

2. Function decorator
```python
from route import Route
Route.set_sep('/')    # the default separator is '.'

# custom type
class MyIntList:
    def __init__(self, *integers):
        self.integers = integers

    # your class definitions


@Route.serializer(MyIntList, ext='.my_list')  # define your serializer for your serializable class
def my_serializer(my_list):
    int_string = ', '.join( [ str(x) for x in my_list.integers ] )

    return int_string  # return value must be either 'str' or 'bytes'


@Route.deserializer(MyIntList, ext='.my_list')  # define your deserializer for your serializable class
def my_deserializer(int_string):
    integers = [int(x) for x in int_string.split(',')]

    return MyIntList(*integers)


# If you want to re-define the de/serialization methods, you can set overwrite=True

@Route.serializer(MyIntList, ext='.my_list', overwrite=True)
def redef_my_serializer(my_list):
    int_string = '\n'.join( [ str(x) for x in my_list.integers ] )

    return int_string

@Route.deserializer(MyIntList, ext='.my_list', overwrite=True)
def redef_my_deserializer(int_string):
    integers = [int(x) for x in int_string.split('\n')]

    return MyIntList(*integers)


ints = MyIntList(5, 6, 7, 8, 9)

d = Route({
    'My/Int/List': ints
})

d.archive('my_archive.zip')
```

* Re-use the serialization methods:
```python
ints = MyIntList(5, 6, 7, 8, 9)
serialized = Route.serialize(ints)

print(serialized)
print(Route.deserialize(MyIntList, serialized))
```
