#!/usr/bin/env python3

import secrets 
import hmac
import hashlib

import codec

hash_function = hashlib.sha3_256

class UserSecret:
    """A user secret used for key generation."""

    def __init__(self, secret=None):
        """Wrap secret bytes to generate different user keys.
        If none is provided, generate new secret bytes.
        >>> secret = UserSecret()
        """
        if secret == None:
            self._secret = secrets.token_bytes(32)
        else:
            self._secret = secret
        self._auth_secret = self._generate_auth_secret()
        self._symmetric_key = self._generate_symmetric_key()

    def _generate_auth_secret(self):
        h_ctxt = hash_function()
        h_ctxt.update("auth_secret".encode('utf-8'))
        h_ctxt.update(self._secret)
        return h_ctxt.digest()

    def _generate_symmetric_key(self):
        h_ctxt = hash_function()
        h_ctxt.update("symmetric_key".encode('utf-8'))
        h_ctxt.update(self._secret)
        return h_ctxt.digest()

    def get_secret(self):
        return self._secret

    def get_auth_secret(self):
        return self._auth_secret

    def get_symmetric_key(self):
        return self._symmetric_key

class MessageAuthenticationCode:
    """A wrapper for symmetric keys to produce message authentication codes."""

    def __init__(self, symmetric_key=None):
        """Wrap the given symmetric key.

        If none is provided, generate a new key.

        >>> prover = MessageAuthenticationCode()
        """
        if symmetric_key == None:
            self._secret_key = secrets.token_bytes(256)
        else:
            self._secret_key = symmetric_key

    def gen_mac(self, data):
        """Create a message authenticator over the data given the
        symmetric key.

        >>> prover = MessageAuthenticationCode("fake_secret_key".encode('utf-8'))
        >>> payload = codec.Encoding()
        >>> payload.add_bin(b"Hello ")
        >>> payload.add_bin("Security!".encode('utf-8'))
        >>> payload.add_int(1)
        >>> prover.gen_mac(payload).hex()
        'ef0314771da203ab984053b93559f28d47ffa9e134ea45d49f4e017707f2bb38'
        """
        if type(data) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        return hmac.new(self._secret_key, data.bytes_data, hash_function).digest()

    def compare_mac(self, data, auth):
        """Check the provided message authenticator against the given
        data and secret.

        >>> prover = MessageAuthenticationCode("fake_secret_key".encode('utf-8'))

        >>> payload = codec.Encoding()
        >>> payload.add_bin(b"Hello ")
        >>> payload.add_bin("Security!".encode('utf-8'))
        >>> payload.add_int(1)
        >>> mac = prover.gen_mac(payload)
        >>> prover.compare_mac(payload, mac)
        True
        """
        return hmac.compare_digest(hmac.new(self._secret_key, data.bytes_data, hash_function).digest(), auth)

class _HashChain:
    """Create a hash chain given a list of hash outputs.
    >>> enc = codec.encode_one_int
    >>> hlist0 = to_hlist([enc(9), enc(4), enc(4), enc(3), enc(2), enc(1)])
    >>> hchain0 = _HashChain(hlist0)
    >>> hchain0.hash().hex()
    'd2a3f67087d74f00eebf1ae49665f76c9dfe9f8031c8614bedb8b9f73f4fb4d4'
    >>> hlist1 = to_hlist([enc(9), enc(4), enc(4)])
    >>> hlist2 = to_hlist([enc(3), enc(2), enc(1)])
    >>> hchain1 = _HashChain(hlist1)
    >>> hash_half = hchain1.hash()
    >>> hchain1.add_hashes(hlist2)
    >>> hchain2 = _HashChain([], hash_half)
    >>> hchain2.add_hashes(hlist2)
    >>> hchain0.hash() == hchain1.hash()
    True
    >>> hchain0.hash() == hchain2.hash()
    True
    """
    def __init__(self, hlist, first_node=hash_function().digest()):
        self.nodes = []
        self.nodes.append(first_node)
        self.add_hashes(hlist)

    def add_hashes(self, hlist):
        """Add new hashes to the hash chain and compute the new corresponding item hashes.
        """
        for h in hlist:
            h_ctxt = hash_function()
            h_ctxt.update(self.nodes[-1])
            h_ctxt.update(h)
            self.nodes.append(h_ctxt.digest())
        
    def hash(self):
        return self.nodes[-1]

def to_hlist(data):
    """Convert a list of codec.Encoding to a list of hashes."""
    hlist = []
    for d in data:
        if type(d) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        d = d.bytes_data
        h_ctxt = hash_function()
        h_ctxt.update(d)
        hlist.append(h_ctxt.digest())
    return hlist

def _hash_list(hlist):
    """Get the hash of a list of hashes."""
    hchain = _HashChain(hlist)
    return hchain.hash()

def list_data_hash(data):
    """Hash the given list of codec.Encoding data.

    >>> enc = codec.encode_one_int
    >>> list_data_hash([enc(9), enc(4), enc(4), enc(3), enc(2), enc(1)]).hex()
    'd2a3f67087d74f00eebf1ae49665f76c9dfe9f8031c8614bedb8b9f73f4fb4d4'
    """
    hlist = to_hlist(data)
    return _hash_list(hlist)

def verify_list_data_hash(data, output):
    """Verify that the given list of codec.Encoding data corresponds
    to the given hash output.

    >>> enc = codec.encode_one_int
    >>> hex = 'd2a3f67087d74f00eebf1ae49665f76c9dfe9f8031c8614bedb8b9f73f4fb4d4'
    >>> expect = bytes.fromhex(hex)
    >>> verify_list_data_hash([enc(9), enc(4), enc(4), enc(3), enc(2), enc(1)], expect)
    True
    """
    hlist = to_hlist(data)
    hchain = _HashChain(hlist)
    return hchain.hash() == output


if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
