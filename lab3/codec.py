#!/usr/bin/env python3

"""
A simple codec for encoding arbitrary data as bytes.
"""

BIN_SEPARATOR = b'\x01'
INT_SEPARATOR = b'\x02'
PAIR_SEPARATOR = b'\x03'
DICT_SEPARATOR = b'\x04'
STR_SEPARATOR  = b'\x05'

def encode_one_int(num):
    """Convenience function for encoding a single int."""
    if type(num) != int:
        raise TypeError("argument must be int")
    enc = Encoding()
    enc.add_int(num)
    return enc
    
def encode_one_bin(bin_data):
    """Convenience function for encoding a single bytes object."""
    if type(bin_data) != bytes:
        raise TypeError("argument must be bytes")
    enc = Encoding()
    enc.add_bin(bin_data)
    return enc
    
class Encoding:
    def __init__(self, bytes_data=b""):
        """Holds the encoding for a sequence of data, which may
        contain raw bytes or unsigned 64-bit integers.

        >>> x = Encoding()
        >>> x.add_int(4)
        >>> x.add_bin("string".encode('utf-8'))
        >>> list(x.items())
        [4, b'string']

        """
        self.bytes_data = bytes_data

    def add_int(self, int_data):
        if type(int_data) != int:
            raise TypeError("int_data must be int")
        if int_data > 2**64 - 1:
            raise Exception("Integer is too large to encode {}".format(int_data))
        if int_data < 0:
            raise Exception("Integer cannot be negative {}".format(int_data))
        data = [
            (int_data >> (8 * 0)) & 0xFF,
            (int_data >> (8 * 1)) & 0xFF,
            (int_data >> (8 * 2)) & 0xFF,
            (int_data >> (8 * 3)) & 0xFF,
            (int_data >> (8 * 4)) & 0xFF,
            (int_data >> (8 * 5)) & 0xFF,
            (int_data >> (8 * 6)) & 0xFF,
            (int_data >> (8 * 7)) & 0xFF,
        ]
        self.bytes_data += INT_SEPARATOR
        self.bytes_data += bytes(data)

    def add_bin(self, bin_data):
        if type(bin_data) != bytes:
            raise TypeError("bin_data must be bytes")
        self.bytes_data += BIN_SEPARATOR
        self.add_int(len(bin_data))
        self.bytes_data += bin_data

    def add_pair(self, encoding_key, encoding_value):
        self.bytes_data += PAIR_SEPARATOR
        self.bytes_data += encoding_key.bytes_data
        self.bytes_data += encoding_value.bytes_data

    def add_dict(self, dict_data):
        self.bytes_data += DICT_SEPARATOR
        self.add_int(len(dict_data))
        for k,v in dict_data.items():
            enc_k = Encoding()
            enc_k.add_obj(k)
            enc_v = Encoding()
            enc_v.add_obj(v)
            self.add_pair(enc_k, enc_v)
    
    def add_string(self, string):
        self.bytes_data += STR_SEPARATOR
        self.add_bin(string.encode('utf-8'))

    def add_obj(self, obj):
        if obj is None:
            return
        elif type(obj) is list:
            for o in obj:
                self.add_obj(obj)
        elif type(obj) is int:
            self.add_int(obj)
        elif type(obj) is dict:
            self.add_dict(obj)
        elif type(obj) is str:
            self.add_string(obj)
        elif type(obj) is bytes:
            self.add_bin(obj)
        else:
            raise TypeError("type of obj is not encodable")

    def items(self):
        copy = Encoding(bytes(self.bytes_data))
        while len(copy.bytes_data) > 0:
            kind = copy.bytes_data[0:1]
            if kind == INT_SEPARATOR:
                yield copy._next_int()
            elif kind == BIN_SEPARATOR:
                yield copy._next_bin()
            elif kind == PAIR_SEPARATOR:
                yield copy._next_pair()
            elif kind == DICT_SEPARATOR:
                yield copy._next_dict()
            elif kind == STR_SEPARATOR:
                yield copy._next_str()
            else:
                raise Exception("Found unknown separator {} while decoding".format(kind))
    
    def decode(self):
        ret = list(self.items())
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    def _next_int(self):
        assert(self.bytes_data[0:1] == INT_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]

        data = self.bytes_data[0:8]
        self.bytes_data = self.bytes_data[8:]

        return (
            (data[0] << (8 * 0)) +
            (data[1] << (8 * 1)) +
            (data[2] << (8 * 2)) +
            (data[3] << (8 * 3)) +
            (data[4] << (8 * 4)) +
            (data[5] << (8 * 5)) +
            (data[6] << (8 * 6)) +
            (data[7] << (8 * 7)) +
        0)

    def _next_bin(self):
        assert(self.bytes_data[0:1] == BIN_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]

        bin_len = self._next_int()

        data = self.bytes_data[:bin_len]
        self.bytes_data = self.bytes_data[bin_len:]

        return data

    def _next_pair(self):
        assert(self.bytes_data[0:1] == PAIR_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]
        key_kind = self.bytes_data[0:1]
        if key_kind == INT_SEPARATOR:
            key = self._next_int()
        elif key_kind == STR_SEPARATOR:
            key = self._next_str()
        elif key_kind == BIN_SEPARATOR:
            key = self._next_bin()
        value_kind = self.bytes_data[0:1]
        if value_kind == INT_SEPARATOR:
            value = self._next_int()
        elif value_kind == STR_SEPARATOR:
            value = self._next_str()
        elif value_kind == BIN_SEPARATOR:
            value = self._next_bin()
        return (key, value)
        
    def _next_dict(self):
        assert(self.bytes_data[0:1] == DICT_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]
        ret = {}
        size = self._next_int()
        for _ in range(size):
            pair = self._next_pair()
            ret[pair[0]] = pair[1]
        return ret

    def _next_str(self):
        assert(self.bytes_data[0:1] == STR_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]
        enc = self._next_bin()
        return enc.decode('utf-8')

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
