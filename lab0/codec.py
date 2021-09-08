#!/usr/bin/env python3

"""
A simple codec for encoding arbitrary data as bytes.
"""

BIN_SEPARATOR = b'\x01'
INT_SEPARATOR = b'\x02'
PAIR_SEPARATOR = b'\x03'
DICT_SEPARATOR = b'\x04'

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
    
class Encoding:
    def __init__(self, bytes_data=b""):
        """Holds the encoding for a sequence of data, which may
        contain raw bytes or unsigned 64-bit integers.

        >>> x = Encoding()
        >>> x.add_int(4)
        >>> x.add_bin("string".encode('utf-8'))
        >>> list(x.items())
        [4, b'string']

        >>> D = {"Key1":"Value1", "Key2":2, 3:"Value3"}
        >>> x.add_dict(D)
        >>> x.bytes_data.hex()
        '02040000000000000001020600000000000000737472696e670402030000000000000003010204000000000000004b6579310102060000000000000056616c75653103010204000000000000004b657932020200000000000000030203000000000000000102060000000000000056616c756533'
        >>> list(x.items())
        [4, b'string', {'Key1': 'Value1', 'Key2': 2, 3: 'Value3'}]

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
            if type(k) == int:
                enc_k.add_int(k)
            else:
                enc_k.add_bin(k.encode('utf-8'))
            enc_v = Encoding()
            if type(v) == int:
                enc_v.add_int(v)
            else:
                enc_v.add_bin(v.encode('utf-8'))
            self.add_pair(enc_k, enc_v)

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
            else:
                raise Exception("Found unknown separator {} while decoding".format(kind))

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
        elif key_kind == BIN_SEPARATOR:
            key = self._next_bin().decode('utf-8')
        value_kind = self.bytes_data[0:1]
        if value_kind == INT_SEPARATOR:
            value = self._next_int()
        elif value_kind == BIN_SEPARATOR:
            value = self._next_bin().decode('utf-8')
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

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
