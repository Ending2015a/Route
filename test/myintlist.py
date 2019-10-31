from route import Route
Route.set_sep('/')    # the default separator is '.'

# custom type
@Route.serializable(ext='.my_list')
class MyIntList:
    def __init__(self, *integers):
        self.integers = integers


@MyIntList.set_serializer()
def my_serializer(my_list):
    int_string = ','.join([str(x) for x in my_list.integers])

    return int_string  # return value must be either 'str' or 'bytes'


@MyIntList.set_deserializer()
def my_deserializer(int_string):
    integers = [int(x) for x in int_string.split(',')]

    return MyIntList(*integers)




ints = MyIntList(5, 6, 7, 8, 9)

print('* My Int List: {}'.format(ints.integers))

print('======================================')
print('* define serializer/deserializer')

serialized = MyIntList.serialize(ints)
print('  serialized MyIntList:   {}'.format(serialized))
print('  deserialized MyIntList: {}'.format(MyIntList.deserialize(serialized).integers))


# If you want to re-define the (de)serialization method, you should set overwrite=True

@MyIntList.set_serializer(overwrite=True)
def redef_my_serializer(my_list):
    int_string = '\n'.join( [ str(x) for x in my_list.integers ] )

    return int_string

@MyIntList.set_deserializer(overwrite=True)
def redef_my_deserializer(int_string):
    integers = [int(x) for x in int_string.split('\n')]

    return MyIntList(*integers)


print('======================================')
print('* re-define serializer/deserializer')

serialized = MyIntList.serialize(ints)
print('  serialized MyIntList: \n{}'.format(serialized))
print('  deserialized MyIntList: {}'.format(MyIntList.deserialize(serialized).integers))

print('======================================')
print('* using Route.serialize/deserialize')

serialized = Route.serialize(ints)
print('  serialized MyIntList: \n{}'.format(serialized))
print('  deserialized MyIntList: {}'.format(Route.deserialize(MyIntList, serialized).integers))



print('======================================')
print('* test archive')
print('  save to my_archive.zip')
d = Route({
    'My/Int/List': ints
})

d.archive('my_archive.zip')
