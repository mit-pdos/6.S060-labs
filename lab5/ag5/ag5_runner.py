#!/usr/bin/env python3

from secure_server import VerySecureServer
from attacker import Client
import secrets

MAX_SCORE = 100

tests = []

def test_this(f):
    tests.append(f)
    return f

@test_this
def extract_8_bytes():
    pts = 50
    n_bytes = 8
    secret = secrets.token_hex(n_bytes)
    server = VerySecureServer(secret)
    attacker = Client(server)
    res = attacker.steal_secret_token(n_bytes)
    if res != secret:
        return 0
    else:
        return pts
@test_this
def extract_16_bytes():
    pts = 25
    n_bytes = 16
    secret = secrets.token_hex(n_bytes)
    server = VerySecureServer(secret)
    attacker = Client(server)
    res = attacker.steal_secret_token(n_bytes)
    if res != secret:
        return 0
    else:
        return pts

@test_this
def extract_32_bytes():
    pts = 15
    n_bytes = 32
    secret = secrets.token_hex(n_bytes)
    server = VerySecureServer(secret)
    attacker = Client(server)
    res = attacker.steal_secret_token(n_bytes)
    if res != secret:
        return 0
    else:
        return pts

@test_this
def extract_64_bytes():
    pts = 10
    n_bytes = 64
    secret = secrets.token_hex(n_bytes)
    server = VerySecureServer(secret)
    attacker = Client(server)
    res = attacker.steal_secret_token(n_bytes)
    if res != secret:
        return 0
    else:
        return pts

if __name__ == "__main__":
    total_pts = 0
    for test in tests:
        print(test.__name__)
        pts = test()
        print("{}: {} pt(s)".format(test.__name__, pts))
        total_pts += pts

    print("----------------------------------------------------------------")
    print("total: {} / {} pts".format(total_pts, MAX_SCORE))
