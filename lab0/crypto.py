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
            self._secret = secrets.token_bytes(256)
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
        
class SymmetricSignature:
    """A wrapper for symmetric keys to perform cryptographic signature operations."""

    def __init__(self, symmetric_key=None):
        """Save the symmetric key.
        If none is provided, generate a new key.
        >>> prover = SymmetricSignature()
        """
        if symmetric_key == None:
            self._secret_key = secrets.token_bytes(256)
        else:
            self._secret_key = symmetric_key

    def auth(self, data):
        """Create a message authenticator over the data given the
        symmetric key.

        >>> prover = SymmetricSignature("fake_secret_key".encode('utf-8'))
        >>> payload = codec.Encoding()
        >>> payload.add_bin(b"Hello ")
        >>> payload.add_bin("Security!".encode('utf-8'))
        >>> payload.add_int(1)
        >>> prover.auth(payload).hex()
        'ef0314771da203ab984053b93559f28d47ffa9e134ea45d49f4e017707f2bb38'
        """
        if type(data) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        return hmac.new(self._secret_key, data.bytes_data, hash_function).digest()

    def compare_auth(self, data, signature):
        """Check the provided message authenticator against the given
        data and secret.

        >>> prover = SymmetricSignature("fake_secret_key".encode('utf-8'))

        >>> payload = codec.Encoding()
        >>> payload.add_bin(b"Hello ")
        >>> payload.add_bin("Security!".encode('utf-8'))
        >>> payload.add_int(1)
        >>> signature = prover.auth(payload)
        >>> prover.compare_auth(payload, signature)
        True
        """
        return hmac.compare_digest(hmac.new(self._secret_key, data.bytes_data, hash_function).digest(), signature)

class _HashChain:
    """Create a commitment given a list of hash digests.
    >>> enc = codec.encode_one_int
    >>> hlist0 = get_hlist([enc(9), enc(4), enc(4), enc(3), enc(2), enc(1)])
    >>> hchain0 = _HashChain(hlist0)
    >>> hchain0.get_commitment().hex()
    'd2a3f67087d74f00eebf1ae49665f76c9dfe9f8031c8614bedb8b9f73f4fb4d4'
    >>> hlist1 = get_hlist([enc(9), enc(4), enc(4)])
    >>> hlist2 = get_hlist([enc(3), enc(2), enc(1)])
    >>> hchain1 = _HashChain(hlist1)
    >>> commitment_half = hchain1.get_commitment()
    >>> hchain1.add_hashes(hlist2)
    >>> hchain2 = _HashChain([], commitment_half)
    >>> hchain2.add_hashes(hlist2)
    >>> hchain0.get_commitment() == hchain1.get_commitment()
    True
    >>> hchain0.get_commitment() == hchain2.get_commitment()
    True
    """
    def __init__(self, hlist, first_node=hash_function().digest()):
        self.nodes = []
        self.nodes.append(first_node)
        self.add_hashes(hlist)

    def add_hashes(self, hlist):
        """Add new hashes to the hash chain and compute the new coresponding nodes digests.
        """
        for h in hlist:
            h_ctxt = hash_function()
            h_ctxt.update(self.nodes[-1])
            h_ctxt.update(h)
            self.nodes.append(h_ctxt.digest())
        
    def get_commitment(self):
        return self.nodes[-1]

def get_hlist(data):
    hlist = []
    for d in data:
        if type(d) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        d = d.bytes_data
        h_ctxt = hash_function()
        h_ctxt.update(d)
        hlist.append(h_ctxt.digest())
    return hlist

def hash_list_commitment(hlist):
    """Create a commitment given a list of hash digests.
    """
    hchain = _HashChain(hlist)
    return hchain.get_commitment()

def data_list_commitment(data):
    """Create a commitment to the given data.
    >>> enc = codec.encode_one_int
    >>> data_list_commitment([enc(9), enc(4), enc(4), enc(3), enc(2), enc(1)]).hex()
    'd2a3f67087d74f00eebf1ae49665f76c9dfe9f8031c8614bedb8b9f73f4fb4d4'
    """
    hlist = get_hlist(data)
    return hash_list_commitment(hlist)

def verify_commitment(data, commitment):
    hlist = get_hlist(data)
    hchain = _HashChain(hlist)
    return hchain.get_commitment() == commitment

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
