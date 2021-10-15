#!/usr/bin/env python3

import json
import secrets 
import hmac
import hashlib
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.utils import random
from collections import defaultdict
import nacl

import codec

"""Special Cryptographic Library for Auto Grading"""

hash_function = hashlib.sha3_256

""" Global Data"""
global current_owner
current_owner = "None"
global public_key_to_owner
public_key_to_owner = {}
global secret_key_to_owner
secret_key_to_owner = {}
global owner_to_secret_key
owner_to_secret_key = defaultdict(set)
global key_mapping
key_mapping = {}

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
        (self._s_sk, self._s_pk) = self._generate_signing_key_pair()
        (self._e_sk, self._e_pk) = self._generate_encrypt_and_auth_key_pair()

    def _generate_auth_secret(self):
        h_ctxt = hash_function()
        h_ctxt.update("auth_secret".encode('utf-8'))
        h_ctxt.update(self._secret)
        sk = h_ctxt.digest()
        secret_key_to_owner[bytes(sk)] = current_owner
        owner_to_secret_key[current_owner].add(bytes(sk))
        return sk

    def _generate_symmetric_key(self):
        h_ctxt = hash_function()
        h_ctxt.update("symmetric_key".encode('utf-8'))
        h_ctxt.update(self._secret)
        sk = h_ctxt.digest()
        secret_key_to_owner[bytes(sk)] = current_owner
        owner_to_secret_key[current_owner].add(bytes(sk))
        return sk

    def _generate_signing_key_pair(self):
        h_ctxt = hash_function()
        h_ctxt.update("signing_key_pair".encode('utf-8'))
        h_ctxt.update(self._secret)
        seed_sk = h_ctxt.digest()
        sk = SigningKey(seed_sk)
        pk = sk.verify_key
        public_key_to_owner[bytes(pk)] = current_owner
        secret_key_to_owner[bytes(sk)] = current_owner
        owner_to_secret_key[current_owner].add(bytes(sk))
        key_mapping[bytes(sk)] = bytes(pk)
        key_mapping[bytes(pk)] = bytes(sk)
        return (sk, pk)

    def _generate_encrypt_and_auth_key_pair(self):
        h_ctxt = hash_function()
        h_ctxt.update("encrypt_and_auth_key_pair".encode('utf-8'))
        h_ctxt.update(self._secret)
        seed_sk = h_ctxt.digest()
        sk = PrivateKey(seed_sk) #TODO this might be insecure
        pk = sk.public_key
        public_key_to_owner[bytes(pk)] = current_owner
        secret_key_to_owner[bytes(sk)] = current_owner
        owner_to_secret_key[current_owner].add(bytes(sk))
        key_mapping[bytes(sk)] = bytes(pk)
        key_mapping[bytes(pk)] = bytes(sk)
        return (sk, pk)

    def get_secret(self):
        return self._secret

    def get_auth_secret(self):
        return self._auth_secret

    def get_symmetric_key(self):
        return self._symmetric_key

    def get_signing_public_key(self):
        return self._s_pk

    def get_signing_secret_key(self):
        return self._s_sk

    def get_encrypt_and_auth_public_key(self):
        return self._e_pk

    def get_encrypt_and_auth_secret_key(self):
        return self._e_sk

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

def Lab3Sign(data, sk):
        owner = secret_key_to_owner[sk]
        pk = key_mapping[sk]
        signature = {"type":"Lab3Signature", "data":data, "sk":sk, "pk":pk, "owner":owner}
        enc = codec.Encoding()
        enc.add_obj(signature)
        return enc.bytes_data

def Lab3Ver(data, pk, sig):
    signature = codec.Encoding(sig).decode()
    if type(signature) is not dict:
        return False
    if signature["type"] != "Lab3Signature":
        return False
    if signature["pk"] == pk and signature["data"] == data:
        return True
    return False

class PublicKeySignature:
    def __init__(self, secret_key=None):
        """Save the key pair.
        If none is provided, generate a new key pair.

        >>> prover = PublicKeySignature()
        """
        if secret_key == None:
            sk = SigningKey.generate()
            self._sk = sk
            secret_key_to_owner[bytes(sk)] = current_owner
            owner_to_secret_key[current_owner].add(bytes(sk))
            pk = sk.verify_key
            self._pk = pk
            public_key_to_owner[bytes(pk)] = secret_key_to_owner[bytes(sk)]
            key_mapping[bytes(sk)] = bytes(pk)
            key_mapping[bytes(pk)] = bytes(sk)
        else:
            self._sk = secret_key
            self._pk = secret_key.verify_key
   
    def get_public_key(self):
        return self._pk.encode()

    def sign(self, data):
        """Create a digital signature over the data given the
        signing key.
       
        >>> fake_secret_key = bytes.fromhex('55fd88856b82d2b3149e8a872e7aeda485e5a2eca1ad3daca52f716472201dee')
        >>> sk = SigningKey(fake_secret_key)
        >>> secret_key_to_owner[bytes(sk)] = current_owner
        >>> owner_to_secret_key[current_owner].add(bytes(sk))
        >>> pk = sk.verify_key
        >>> public_key_to_owner[bytes(pk)] = secret_key_to_owner[bytes(sk)]
        >>> key_mapping[bytes(sk)] = bytes(pk)
        >>> key_mapping[bytes(pk)] = bytes(sk)
        >>> prover = PublicKeySignature(sk)
        >>> payload = codec.Encoding()
        >>> payload.add_bin(b"Hello ")
        >>> payload.add_bin("Security!".encode('utf-8'))
        >>> payload.add_int(1)
        >>> sign = prover.sign(payload).hex()
        """
        if type(data) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        if bytes(self._sk) not in secret_key_to_owner:
            print("Error this key was not tainted")
        return Lab3Sign(data.bytes_data, bytes(self._sk))

def verify_sign(pk, data, signature):
    """Check the provided message authenticator against the given
    data and secret.
    
    >>> sk = SigningKey.generate()
    >>> secret_key_to_owner[bytes(sk)] = current_owner
    >>> owner_to_secret_key[current_owner].add(bytes(sk))
    >>> pk = sk.verify_key
    >>> public_key_to_owner[bytes(pk)] = secret_key_to_owner[bytes(sk)]
    >>> key_mapping[bytes(sk)] = bytes(pk)
    >>> key_mapping[bytes(pk)] = bytes(sk)
    >>> prover = PublicKeySignature(sk)
    >>> payload = codec.Encoding()
    >>> payload.add_bin(b"Hello ")
    >>> payload.add_bin("Security!".encode('utf-8'))
    >>> payload.add_int(1)
    >>> signature = prover.sign(payload)
    >>> pk = prover.get_public_key()
    >>> verify_sign(pk, payload, signature)
    True
    """
    return Lab3Ver(data.bytes_data, bytes(pk), signature)

def generate_symmetric_secret_key():
    sk = random(SecretBox.KEY_SIZE)
    secret_key_to_owner[bytes(sk)] = current_owner
    owner_to_secret_key[current_owner].add(bytes(sk))
    return sk

def Lab3SymEnc(sk, data):
        owner = secret_key_to_owner[sk]
        cyphertext = {"type":"Lab3Encryption", "data":data, "sk":sk, "owner":owner}
        enc = codec.Encoding()
        enc.add_obj(cyphertext)
        return enc.bytes_data

def Lab3SymDec(sk, ctxt):
    enc = codec.Encoding(ctxt).decode()
    if type(enc) is not dict:
        return None
    if enc["type"] != "Lab3Encryption":
        return None
    if enc["sk"] != sk:
        return None
    return enc["data"]

class SymmetricKeyEncryption: 
    def __init__(self, secret_key=None):
        """Save the secret encryption key.
        If none is provided, generate a new secret key.

        >>> prover = SymmetricKeyEncryption()
        >>> data = codec.Encoding()
        >>> data.add_bin("hello".encode('utf-8'))
        >>> cyphertxt = prover.encrypt(data)
        >>> plain = prover.decrypt(cyphertxt)
        >>> codec.Encoding(plain).decode()
        b'hello'
        """
        if secret_key == None:
            self._sk = generate_symmetric_secret_key()
            secret_key_to_owner[bytes(self._sk)] = current_owner
            owner_to_secret_key[current_owner].add(bytes(self._sk))
        else:
            self._sk = secret_key
        self.box = SecretBox(self._sk)
  
    def encrypt(self, data):
        if type(data) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        return Lab3SymEnc(bytes(self._sk), data.bytes_data)

    def decrypt(self, cypher_text):
        return Lab3SymDec(bytes(self._sk), cypher_text)

def Lab3EncAndAuth(pk_enc, sk_auth, data):
        if pk_enc not in key_mapping or sk_auth not in key_mapping:
            raise KeyError("This private key doesn't match any public key")
        pk_auth = key_mapping[sk_auth]
        sk_enc = key_mapping[pk_enc]
        owner_auth = secret_key_to_owner[sk_auth]
        owner_enc = secret_key_to_owner[sk_enc]
        cyphertext = {"type":"Lab3EncryptionAndAuthentication", "data":data, "sk_auth":sk_auth, "pk_auth":pk_auth, "sk_enc":sk_enc, "pk_enc":pk_enc, "owner_auth":owner_auth, "owner_enc":owner_enc}
        enc = codec.Encoding()
        enc.add_obj(cyphertext)
        return enc.bytes_data

def Lab3DecAndVer(sk_enc, pk_auth, ctxt):
    enc = codec.Encoding(ctxt).decode()
    if type(enc) is not dict:
        return None
    if enc["type"] != "Lab3EncryptionAndAuthentication":
        return None
    if enc["sk_enc"] != sk_enc or enc["pk_auth"] != pk_auth:
        return None
    return enc["data"]

class PublicKeyEncryptionAndAuthentication:
    def __init__(self, secret_key=None):
        """Save the secret encryption key.
        If none is provided, generate a new secret key.

        >>> sender = PublicKeyEncryptionAndAuthentication()
        >>> receiver = PublicKeyEncryptionAndAuthentication()
        >>> data = codec.Encoding()
        >>> data.add_bin("hello".encode('utf-8'))
        >>> r_pk = bytes(receiver.get_public_key())
        >>> s_pk = bytes(sender.get_public_key())
        >>> cyphertxt = sender.encrypt_and_auth(data, r_pk)
        >>> plain = receiver.decrypt_and_verify(cyphertxt, s_pk)
        >>> list(codec.Encoding(plain).items())[0]
        b'hello'
        """
        if secret_key == None:
            sk = PrivateKey.generate()
            self._sk = sk
            secret_key_to_owner[bytes(sk)] = current_owner
            owner_to_secret_key[current_owner].add(bytes(sk))
            pk = sk.public_key
            public_key_to_owner[bytes(pk)] = secret_key_to_owner[bytes(sk)]
            key_mapping[bytes(sk)] = bytes(pk)
            key_mapping[bytes(pk)] = bytes(sk)
        else:
            self._sk = secret_key
        
    def get_public_key(self):
        pk = self._sk.public_key
        return pk
    
    def encrypt_and_auth(self, data, friend_pk):
        if type(data) is not codec.Encoding:
            raise TypeError("data must be Encoding")
        friend_pk = PublicKey(friend_pk)
        return Lab3EncAndAuth(bytes(friend_pk), bytes(self._sk), data.bytes_data)

    def decrypt_and_verify(self, cypher_text, friend_pk):
        return codec.Encoding(Lab3DecAndVer(bytes(self._sk), bytes(friend_pk), cypher_text))

if __name__ == "__main__":
    sender = PublicKeyEncryptionAndAuthentication()
    receiver = PublicKeyEncryptionAndAuthentication()
    data = codec.Encoding()
    data.add_bin("hello".encode('utf-8'))
    r_pk = bytes(receiver.get_public_key())
    s_pk = bytes(sender.get_public_key())
    cyphertxt = sender.encrypt_and_auth(data, r_pk)
    plain = receiver.decrypt_and_verify(cyphertxt, s_pk)
    list(codec.Encoding(plain).items())[0]
    import doctest
    exit(doctest.testmod()[0])
