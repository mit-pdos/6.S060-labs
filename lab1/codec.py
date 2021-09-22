#!/usr/bin/env python3

"""
A simple codec for encoding arbitrary data as bytes.
"""

from typing import Iterator, Union

BIN_SEPARATOR = b'\x01'
INT_SEPARATOR = b'\x02'

class Encoding:
    def __init__(self, bytes_data: bytes=b"") -> None:
        """Holds the encoding for a sequence of data, which may
        contain raw bytes or unsigned 64-bit integers.

        >>> x = Encoding()
        >>> x.add_int(4)
        >>> x.add_bin("string".encode('utf-8'))
        >>> list(x.items())
        [4, b'string']

        """
        self.bytes_data = bytes_data

    def add_int(self, int_data: int) -> None:
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

    def add_bin(self, bin_data: bytes) -> None:
        if type(bin_data) != bytes:
            raise TypeError("bin_data must be bytes")
        self.bytes_data += BIN_SEPARATOR
        self.add_int(len(bin_data))
        self.bytes_data += bin_data


    def items(self) -> Iterator[Union[int, bytes]]:
        copy = Encoding(bytes(self.bytes_data))
        while len(copy.bytes_data) > 0:
            kind = copy.bytes_data[0:1]
            if kind == INT_SEPARATOR:
                yield copy._next_int()
            elif kind == BIN_SEPARATOR:
                yield copy._next_bin()
            else:
                raise Exception("Found unknown separator {} while decoding".format(kind))

    def _next_int(self) -> int:
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

    def _next_bin(self) -> bytes:
        assert(self.bytes_data[0:1] == BIN_SEPARATOR)
        self.bytes_data = self.bytes_data[1:]

        bin_len = self._next_int()

        data = self.bytes_data[:bin_len]
        self.bytes_data = self.bytes_data[bin_len:]

        return data

def encode_one_int(num: int) -> Encoding:
    """Convenience function for encoding a single int."""
    if type(num) != int:
        raise TypeError("argument must be int")
    enc = Encoding()
    enc.add_int(num)
    return enc
    
def encode_one_bin(num: int) -> Encoding:
    """Convenience function for encoding a single bytes object."""
    if type(num) != bytes:
        raise TypeError("argument must be bytes")
    enc = Encoding()
    enc.add_bin(num)
    return enc
    

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
