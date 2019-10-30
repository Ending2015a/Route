import json
import traceback
from route import Route


def pprint(d):
    print('=========================')
    print(json.dumps(d, indent=4))


Route.set_sep('.')

a = Route()

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


b = Route(config)
pprint(b)

print('print plain:')
for k, v in b.plain('/'):
    print('{}: {}'.format(k, v))


b['settings.cpu.number'] = 20
b['hello'] = 'foobar'

pprint(b)

print('* contains settings.cpu.number:', 'settings.cpu.number' in b)
print('* contains settings.gpu.number:', 'settings.gpu.number' in b)
print('* contains settings.gpu.size:', 'settings.gpu.size' in b)
print('* contains settings.tpu.number:', 'settings.tpu.number' in b)
print('* contains settings.tpu:', 'settings.tpu' in b)



# === test archive ===

print('=======================')


import numpy as np

val = np.array([1.5, 2.5, 3.5], dtype=np.float32)
val2 = np.array([1, 2, 3], dtype=np.int32)

Route.set_sep('/')

d = Route()

class HelloMyClass:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def print(self):
        print('args: {}'.format(self.args))
        print('kwargs: {}'.format(self.kwargs))

cc = HelloMyClass('abc', 'zz', 445, name='dfsA', _type='hhhhh')


d['model/policy/val'] = val
d['model/val'] = val2
d['train/settings'] = cc


print('\nThe structure of `d`:')
print('    {}'.format(d))

print('\nArchive d to `my_test.zip`')
d.archive('my_test.zip')


print('\nRestore `my_test.zip` and save to `a`')
a = Route.restore('my_test.zip')

print('\nThe structure of `a`: ')
print('    {}'.format(a))
