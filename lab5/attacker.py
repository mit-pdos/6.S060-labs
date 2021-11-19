#!/usr/bin/env python3

from secure_server import *
import api

import secrets

class Client:
    def __init__(self, remote):
        self._remote = remote

    def steal_secret_token(self, l):
        secret_token = secrets.token_hex(l)
        req = api.VerifyTokenRequest(secret_token)
        if (self._remote.verify_token(req).ret):
            return secret_token
        else:
            return None

if __name__ == "__main__":
    server = VerySecureServer('37a4e5bf847630173da7e6d19991bb8d')
    alice = Client(server)
    print(alice.steal_secret_token(16))
