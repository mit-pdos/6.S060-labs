def trace(f):
    def g(*args):
        # print(f.__name__, ','.join(str(x) for x in args[1:]))
        res = f(*args)
        # print(' -> ', res)
        return res
    return g

# see: https://stackoverflow.com/a/33800620
def auto_str(cls):
    def __str__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join('{}={}'.format(item[0], item[1]) for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls
