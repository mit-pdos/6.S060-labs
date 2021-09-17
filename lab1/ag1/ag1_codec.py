#!/usr/bin/env python3

"""
The "codec" for the lab1 autograder.

Instead of doing any real encoding, it just stores the data directly
(so that further manipulation is easier).
"""

BIN_SEPARATOR = b'\x01'
INT_SEPARATOR = b'\x02'

def encode_one_int(num):
    """Convenience function for encoding a single int."""
    if type(num) != int:
        raise TypeError("argument must be int")
    enc = Encoding()
    enc.add_int(num)
    return enc

def encode_one_bin(num):
    """Convenience function for encoding a single bytes object."""
    if type(num) != bytes:
        raise TypeError("argument must be bytes")
    enc = Encoding()
    enc.add_bin(num)
    return enc

class Lab1Authenticator:
    def __init__(self, key, data):
        self.key = key
        self.data = data
    def equals(self, other_auth):
        if type(other_auth) != Lab1Authenticator:
            return False
        if self.key != other_auth.key:
            return False
        return self.data == other_auth.data
    def __str__(self):
        return 'Lab1Authenticator(key={}, data={})'.format(self.key, self.data)

    # defined to help with debugging
    def __repr__(self):
        return self.__str__()

class Encoding:
    def __init__(self):
        """TODO doctest here

        >>> x = Encoding()
        """
        self.data = []

    def add_int(self, int_data):
        if type(int_data) != int:
            raise TypeError("int_data must be int")
        if int_data > 2**64 - 1:
            raise Exception("Integer is too large to encode {}".format(int_data))
        self.data.append(int_data)

    def add_bin(self, bin_data):
        if type(bin_data) != bytes and type(bin_data) != Lab1Authenticator:
            raise TypeError("bin_data must be bytes")
        if type(bin_data) == bytes and len(bin_data) > 2**64 - 1:
            raise Exception("Integer is too large to encode {}".format(int_data))
        self.data.append(bin_data)

    def items(self):
        return list(self.data)

    def __str__(self):
        return 'Encoding({})'.format(self.items())

    # defined to help with debugging
    def __repr__(self):
        return '<{}>'.format(self.__str__())
