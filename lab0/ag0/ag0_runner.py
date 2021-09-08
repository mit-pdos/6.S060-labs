#!/usr/bin/env python3

import traceback

import client
from dummy_server import *
from crypto import *
import api, errors

tests = []

def test_this(f):
    tests.append(f)
    return f

class TestServer:
    def __init__(self):
        self.last_request = None
        self.last_response = None
        self._real_server = DummyServer()

    def register_user(self, request):
        self.last_request = request
        self.last_response = self._real_server.register_user(request)
        return self.last_response

    def update_public_profile(self, request):
        self.last_request = request
        self.last_response = self._real_server.update_public_profile(request)
        return self.last_response

    def get_friend_public_profile(self, request):
        self.last_request = request
        self.last_response = self._real_server.get_friend_public_profile(request)
        return self.last_response

class ErrorServer_0:
    def __init__(self):
        self._real_server = DummyServer()

    def register_user(self, request):
        return self._real_server.register_user(request)

    def update_public_profile(self, request):
        return api.UpdatePublicProfileResponse(api.Errcode.INVALID_TOKEN)

class ErrorServer_1:
    def __init__(self):
        self._real_server = DummyServer()

    def register_user(self, request):
        return self._real_server.register_user(request)

    def update_public_profile(self, request):
        return api.UpdatePublicProfileResponse(api.Errcode.UNKNOWN)

class ErrorServer_2:
    def __init__(self):
        self._real_server = DummyServer()

    def register_user(self, request):
        return self._real_server.register_user(request)

    def update_public_profile(self, request):
        return self._real_server.update_public_profile(request)

    def get_friend_public_profile(self, request):
        return api.GetFriendPublicProfileResponse(api.Errcode.INVALID_TOKEN, None)

class ErrorServer_3:
    def __init__(self):
        self._real_server = DummyServer()

    def register_user(self, request):
        return self._real_server.register_user(request)

    def update_public_profile(self, request):
        return self._real_server.update_public_profile(request)

    def get_friend_public_profile(self, request):
        return api.GetFriendPublicProfileResponse(api.Errcode.UNKNOWN, None)

@test_this
def test_correct_behavior_1():
    pts = 1
    try:
        server = DummyServer()
        alice = client.Client("alice", server)
        alice.register()
        infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        alice.update_public_profile_infos(infos)
    except:
        return 0
    return pts

@test_this
def test_correct_behavior_2():
    pts = 0
    try:
        server = TestServer()
        alice = client.Client("alice", server)
        alice.register()
        token = server.last_response.token
        infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        alice.update_public_profile_infos(infos)
        request = server.last_request
        if type(request) == api.UpdatePublicProfileRequest:
            pts += 1
        else:
            return pts
        if request.username == "alice":
            pts += 1
        else:
            return pts
        if request.token == token:
            pts += 1
        else:
            return pts
        if request.public_profile.username == "alice":
            pts += 1
        else:
            return pts
        if request.public_profile.infos == infos:
            pts += 2
        else:
            return pts
    except Exception as e:
        traceback.print_exc()
        return 0
    return pts

@test_this
def test_correct_behavior_3():
    pts = 2
    try:
        server = TestServer()
        alice = client.Client("alice", server)
        alice.register()
        token = server.last_response.token
        infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        alice.update_public_profile_infos(infos)
        received_pp = server.get_friend_public_profile(api.GetFriendPublicProfileRequest("alice", token, "alice")).public_profile
        new_infos = received_pp.infos
        if new_infos != infos:
            pts = 0
    except Exception as e:
        traceback.print_exc()
        return 0
    return pts

@test_this
def test_correct_behavior_4():
    pts = 0
    try:
        server = TestServer()
        alice = client.Client("alice", server)
        alice.register()
        infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        alice.update_public_profile_infos(infos)
        bob = client.Client("bob", server)
        bob.register()
        token = server.last_response.token
        bob.get_friend_public_profile("alice")
        request = server.last_request
        if type(request) == api.GetFriendPublicProfileRequest:
            pts += 1
        else:
            return pts
        if request.username == "bob":
            pts += 1
        else:
            return pts
        if request.token == token:
            pts += 1
        else:
            return pts
        if request.friend_username == "alice":
            pts += 1
        else:
            return pts
    except Exception as e:
        traceback.print_exc()
        return 0
    return pts

@test_this
def test_correct_behavior_5():
    pts = 2
    try:
        server = DummyServer()
        alice = client.Client("alice", server)
        alice.register()
        infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        alice.update_public_profile_infos(infos)
        bob = client.Client("bob", server)
        bob.register()
        received_pp = bob.get_friend_public_profile("alice")
        new_infos = received_pp.infos
        if new_infos != infos:
            pts = 0
    except Exception as e:
        traceback.print_exc()
        return 0
    return pts

# TODO add timeouts to tests (to handle infinite loops)

total_pts = 0
for test in tests:
    pts = test()
    print("{}: {} pt(s)".format(test.__name__, pts))
    total_pts += pts

print("----------------------------------------------------------------")
print("total: {} pt(s)".format(total_pts))
