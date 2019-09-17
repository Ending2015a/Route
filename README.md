# Map

## Example
```python
a = Map(h=10, foo=20, bar={'nnn':{'sd':30}, 'mmm':40})

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
