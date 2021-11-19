#!/usr/bin/env python3
from enum import IntEnum, auto, unique

"""
A common API between the client and the server.
"""

class VerifyTokenRequest():
    def __init__(self, token):
        self.token = token

class VerifyTokenResponse():
    def __init__(self, ret):
        self.ret = ret
