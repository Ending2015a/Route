import json
import traceback
from map import Map


def pprint(d):
    print('=========================')
    print(json.dumps(d, indent=4))



a = Map()

# add item

a['www.google.com'] = 30
pprint(a)


# add items

a['1'] = 1
a['2'] = 2
a['3'] = 3
a['4.5'] = 45
a['6.7'] = 67
a['6.8'] = 68
a['6.9'] = 69
a['6.10.11'] = 61011

pprint(a)

print('* a[\'6.10.11\'] =', a['6.10.11'])
print('* len =', len(a))

# delete items

del a['1']
del a['6.7']
del a['6.8']
del a['6.10.11']
del a['www.google']


pprint(a)

print('* len =', len(a))


print('Exception!!')
try:
    print('key error a[\'6.10.11\']: ')
    print(a['6.10.11'])
except Exception as e:
    traceback.print_exc()


print('')
print('Not Exception')
print('not key error a[\'6.10.11\']: ')
print(a.get('6.10.11', 'Not Found'))




config = {
    'settings': {
        'gpu': {
            'number': 0,
            'memory': 1000
        },

        'cpu.number': 10,
        'cpu.memory': 2000
    }        
}


b = Map(config)
pprint(b)


b['settings.cpu.number'] = 20
b['hello'] = 'foobar'

pprint(b)

print('* contains settings.cpu.number:', 'settings.cpu.number' in b)
print('* contains settings.gpu.number:', 'settings.gpu.number' in b)
print('* contains settings.gpu.size:', 'settings.gpu.size' in b)
print('* contains settings.tpu.number:', 'settings.tpu.number' in b)
print('* contains settings.tpu:', 'settings.tpu' in b)