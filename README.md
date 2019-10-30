# Route

## Example 1
```python
a = Route(h=10, foo=20, bar={'nnn':{'sd':30}, 'mmm':40})

print(a['h'])
# 10

print(a['foo'])
# 20

print(a['bar'])
# {'nnn':{'sd':30}, 'mmm':40}

print(a['bar.nnn'])
# {'sd':30}

print(a['bar.nnn.sd'])
# 30

print(a['bar.mmm'])
# 40

print('bar.mmm' in a)
# True

print('bar.fff' in a)
# False

print(a.get('bar.mmm', default='NotFound'))
# 40

print(a.get('bar.fff', defualt='NotFound'))
# NotFound

```


#### Example 2
* safely get `d['settings']['hello']['world']['world2']['world3']` which might not exist
* using python dict:
```python


def get_value(d, path, default=None):
    v = d
    for p in path:
        v = v.get(p, None)

        if (v is None) or (not isinstance(v, dict)):
            return default
    return v

path = ['settings', 'hello', 'world', 'world2', 'world3']
print(get_value(d, path, default=None)) 
```

* using Route
```python
print(d.get('settings.hello.world.world2.world3', None))
```


#### Example 3
* Nested dict
* using python dict:
```python
d = dict({
    'LayerA': {
        'LayerB': {
            'LayerC': {
                'LayerD-1': {
                    'LayerE': {
                        'item1': 10,
                        'item2': 20
                    }
                },
                'LayerD-2': {
                    'LayerE': {
                        'LayerF': {
                            'item3': 30,
                            'item4': 40
                        }
                    }
                }
            }   
        }
    }
})
```

* using Route
```python
d = Map({
    'LayerA.LayerB.LayerC.LayerD-1.LayerE': {
        'item1': 10,
        'item2': 20,
    },
    'LayerA.LayerB.LayerC.LayerD-2.LayerE.LayerF': {
        'item3': 30,
        'item4': 40,
    },
})
```
