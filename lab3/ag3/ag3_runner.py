#!/usr/bin/env python3

import traceback
import random

from client import *
from imp_client import *
from dummy_server import *
import api, errors
import codec
import crypto

MAX_SCORE = 100

tests = []

def test_this(f):
    tests.append(f)
    return f

### correctness

@test_this
def correctness_create_album():
    pts = 1
    try:
        server = DummyServer()
        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        alice.register()
        bob.register()
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"bob":bob_pp}
        alice.create_shared_album("my_album", photos, friends)
    except:
        traceback.print_exc()
        pts = 0
    return pts

@test_this
def correctness_get_album():
    pts = 1
    try:
        server = DummyServer()
        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        alice.register()
        bob.register()
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"bob":bob_pp}
        alice.create_shared_album("my_album", photos, friends)
        photos_received = bob.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            pts = 0
    except:
        traceback.print_exc()
        pts = 0
    return pts

@test_this
def correctness_add_friend():
    pts = 1
    try:
        server = DummyServer()
        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        alice.register()
        alice_pp = alice.public_profile
        bob.register()
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"alice":alice_pp}
        alice.create_shared_album("my_album", photos, friends)
        try:
            photos_received = bob.get_album("my_album", a_pk).photos
            pts = 0
        except errors.AlbumPermissionError:
            alice.add_friend_to_album("my_album", bob_pp)
            photos_received = bob.get_album("my_album", a_pk).photos
            if not photos_received == photos:
                pts = 0
    except:
        traceback.print_exc()
        pts = 0
    return pts

@test_this
def correctness_remove_friend():
    pts = 1
    try:
        server = DummyServer()
        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        alice.register()
        alice_pp = alice.public_profile
        bob.register()
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"alice":alice_pp, "bob":bob_pp}
        alice.create_shared_album("my_album", photos, friends)
        photos_received = bob.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            pts = 0
        alice.remove_friend_from_album("my_album", "bob")
        try:
            photos_received = bob.get_album("my_album", a_pk).photos
            pts = 0
        except errors.AlbumPermissionError:
            pass
    except:
        traceback.print_exc()
        pts = 0
    return pts

@test_this
def correctness_add_photo():
    pts = 1
    try:
        server = DummyServer()
        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        bob.register()
        cedric = Client("cedric", server)
        c_pk = cedric.signing_public_key
        cedric.register()
        alice.register()
        alice_pp = alice.public_profile
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"alice":alice_pp, "bob":bob_pp, "cedric":cedric_pp}
        alice.create_shared_album("my_album", photos, friends)
        photos_received = bob.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            pts = 0
        new_photo = b'PHOTOBOB'
        bob.add_photo_to_album("my_album", new_photo, a_pk)
        photos_received = cedric.get_album("my_album", a_pk).photos
        photos.append(new_photo)
        if not photos_received == photos:
            pts = 0
        photos_received = alice.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            pts = 0
    except:
        traceback.print_exc()
        pts = 0
    return pts

@test_this
def correctness_basic_workflow():
    if check_correctness_basic_workflow():
        return 5
    return 0

def check_correctness_basic_workflow():
    try:
        server = DummyServer()

        alice = Client("alice", server)
        a_pk = alice.signing_public_key
        bob = Client("bob", server)
        b_pk = bob.signing_public_key
        cedric = Client("cedric", server)
        c_pk = cedric.signing_public_key
        
        alice.register()
        bob.register()
        cedric.register()

        alice_pp = alice.public_profile
        bob_pp = alice.get_friend_public_profile("bob", b_pk)
        cedric_pp = alice.get_friend_public_profile("cedric", c_pk)

        photos = []
        photos.append(b'PHTOOOO')
        photos.append(b'PHOTOOO')
        photos.append(b'PHOOTOO')
        photos.append(b'PHOOOTO')
        photos.append(b'PHOOOOT')
        friends = {"alice":alice_pp, "bob":bob_pp}
        alice.create_shared_album("my_album", photos, friends)
        alice.get_album("my_album", a_pk)
        photos_received = bob.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            return False

        try:
            photos_received = cedric.get_album("my_album", a_pk).photos
            return False
        except errors.AlbumPermissionError:
            alice.add_friend_to_album("my_album", cedric_pp)
            photos_received = cedric.get_album("my_album", a_pk).photos
            if not photos_received == photos:
                return False

        photos_received = cedric.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            return False
        photos_received = alice.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            return False

        new_photo = b'PHOTOBOB'
        bob.add_photo_to_album("my_album", new_photo, a_pk)
        photos_received = cedric.get_album("my_album", a_pk).photos
        photos.append(new_photo)
        if not photos_received == photos:
            return False
        
        photos_received = alice.get_album("my_album", a_pk).photos
        if not photos_received == photos:
            return False

        alice.remove_friend_from_album("my_album", "cedric")
        try:
            photos_received = cedric.get_album("my_album", a_pk).photos
            return False
        except errors.AlbumPermissionError:
            pass

    except:
        traceback.print_exc()
        return False
    return True

### security

# confidentiality

class TestServer:
    def __init__(self):
        self.last_request = None
        self.last_response = None
        self.last_album_upload_request = None
        self.last_album_upload_response = None
        self.last_album_get_request = None
        self.last_album_get_response = None
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

    def upload_album(self, request):
        self.last_request = request
        self.last_album_upload_request = request
        response = self._real_server.upload_album(request)
        self.last_response = response
        self.last_album_upload_response = response
        return self.last_response

    def get_album(self, request):
        self.last_request = request
        self.last_album_get_request = request
        response = self._real_server.get_album(request)
        self.last_response = response
        self.last_album_get_response = response
        return self.last_response

class View:
    def __init__(self, available_keys=set()):
        self.available_keys = available_keys
        self.available_keys |= set(public_key_to_owner.keys())
        self.available_data = set()
        self.encryption_stack = []
    
    def add_obj(self, obj):
        self._walk_obj(obj)
        self._decrypt()

    def add_keys(self, keys):
        self.available_keys |= keys

    def _walk_obj(self, obj):
        if obj is None:
            return
        elif type(obj) is list:
            for o in obj:
                self._walk_obj(o)
        elif type(obj) is int:
            self.available_data.add(obj)
        elif type(obj) is dict:
            for k,v in obj.items():
                self._walk_obj(k)
                self._walk_obj(v)
        elif type(obj) is str:
            self.available_data.add(obj)
        elif type(obj) is bytes:
            self._open_bytes(obj)
        else:
            raise TypeError("type of obj ({}) is not encodable".format(type(obj)))
            
    def _open_bytes(self, b):
        assert(type(b) == bytes)
        if b in secret_key_to_owner or b in public_key_to_owner:
            self.available_keys.add(b)
        elif "Lab3".encode('utf-8') in b:
            enc = codec.Encoding(b).decode()
            self.encryption_stack.append(enc)
        else:
            self.available_data.add(b)

    def _decrypt(self):
        old_stack = self.encryption_stack
        self.encryption_stack = []
        for e in old_stack:
            obj = codec.Encoding(e["data"]).decode()
            if e["type"] == "Lab3Encryption":
                if e["sk"] in self.available_keys:
                    self._walk_obj(obj)
            elif e["type"] == "Lab3EncryptionAndAuthentication":
                if e["sk_enc"] in self.available_keys:
                    self._walk_obj(obj)
            elif e["type"] == "Lab3Signature":
                self._walk_obj(obj)
            else:
                raise TypeError("type of encoding is not supported")
        if len(self.encryption_stack) != 0:
            self.decrypt()

@test_this
def security_add_friend():
    if not correctness_basic_workflow():
        return 0

    crypto.current_owner = "None"
    pts = 10
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = Client("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create Album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Check that Bob cannot access the photos
    try:
        crypto.current_owner = "bob"
        photos_received = bob.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "bob":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        bob_view = View(owner_to_secret_key["bob"])
        bob_view.add_obj(server.last_album_get_response.album.metadata)
        bob_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in bob_view.available_data:
                return 0
    # Add Bob to the album
    crypto.current_owner = "alice"
    alice.add_friend_to_album("my_album", bob_pp)
    # Check that Bob can access all the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    # Check that Cedric cannot access any photos
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view = View(owner_to_secret_key["cedric"])
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    return pts

@test_this
def security_not_allowed_to_add_friend_1():
    if not correctness_basic_workflow():
        return 0

    crypto.current_owner = "None"
    pts = 10
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = ImpoliteClient("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create the Album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Check that Bob cannot access any photos
    try:
        crypto.current_owner = "bob"
        photos_received = bob.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "bob":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        bob_view = View(owner_to_secret_key["bob"])
        bob_view.add_obj(server.last_album_get_response.album.metadata)
        bob_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in bob_view.available_data:
                return 0
    
    # Cedric adds himself
    crypto.current_owner = "cedric"
    cedric.add_friend_to_album("my_album", cedric_pp)

    # Alice adds bob
    crypto.current_owner = "alice"
    alice.add_friend_to_album("my_album", bob_pp)

    # Check that Bob cannot access any photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    #Check that Cedric cannot access any photos
    cedric_view = View(owner_to_secret_key["cedric"])
    cedric_view.add_obj(server.last_album_get_response.album.metadata)
    cedric_view.add_obj(server.last_album_get_response.album.photos)

    for p in photos:
        if p in cedric_view.available_data:
            print("private photo is viewable to adversary {} in {}!".format(p, cedric_view.available_data))
            return 0
    #Check that Cedric cannot access any photos
    crypto.current_owner = "cedric"
    photos_received = cedric.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "cedric":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    cedric_view.add_keys(owner_to_secret_key["cedric"])
    cedric_view.add_obj(server.last_album_get_response.album.metadata)
    cedric_view.add_obj(server.last_album_get_response.album.photos)

    for p in photos:
        if p in cedric_view.available_data:
            print("private photo is viewable to adversary {} in {}!".format(p, cedric_view.available_data))
            return 0

    return pts

@test_this
def security_not_allowed_to_add_friend_2():
    if not correctness_basic_workflow():
        return 0

    crypto.current_owner = "None"
    pts = 15
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = ImpoliteClient("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create the album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Test that Bob cannot access any photos
    try:
        crypto.current_owner = "bob"
        photos_received = bob.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "bob":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        bob_view = View(owner_to_secret_key["bob"])
        bob_view.add_obj(server.last_album_get_response.album.metadata)
        bob_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in bob_view.available_data:
                return 0
    
    # Cedric tries to add himself
    crypto.current_owner = "cedric"
    cedric.add_friend_to_album("my_album", cedric_pp)

    # Alice adds Bob
    crypto.current_owner = "alice"
    alice.add_friend_to_album("my_album", bob_pp)

    # Check that Bob has access to the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    #Check that Cedric cannot access any photos
    cedric_view = View(owner_to_secret_key["cedric"])
    cedric_view.add_obj(server.last_album_get_response.album.metadata)
    cedric_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p in cedric_view.available_data:
            print("private photo is viewable to adversary! {} in {}".format(p, cedric_view.available_data))
            return 0

    # Bob adds a photo
    crypto.current_owner = "bob"
    new_photo = b'PHOTOBOB'
    bob.add_photo_to_album("my_album", new_photo, a_pk)
    photos.append(new_photo)

    # Check that Cedric cannot access any photos
    crypto.current_owner = "cedric"
    photos_received = cedric.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "cedric":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    cedric_view.add_keys(owner_to_secret_key["cedric"])
    cedric_view.add_obj(server.last_album_get_response.album.metadata)
    cedric_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p in cedric_view.available_data:
            print("private photo is viewable to adversary! {} in {}".format(p, cedric_view.available_data))
            return 0

    return pts

@test_this
def security_remove_friend():
    if not correctness_basic_workflow():
        return 0

    crypto.current_owner = "None"
    pts = 15
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = Client("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create the album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp, "bob":bob_pp, "cedric":cedric_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Test that Bob can access the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    # Remove Cedric
    crypto.current_owner = "alice"
    alice.remove_friend_from_album("my_album", "cedric")
    # Test that Cedric cannot access any photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view = View(owner_to_secret_key["cedric"])
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    # Test that Bob can access the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    return pts

@test_this
def security_remove_friend_2():
    pts = 20
    if not correctness_basic_workflow():
        return 0
    
    crypto.current_owner = "None"
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = Client("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create the album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp, "bob":bob_pp, "cedric":cedric_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Test that Bob can access the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    # Test that Cedric can access the photos
    crypto.current_owner = "cedric"
    cedric.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "cedric":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    cedric_view = View(owner_to_secret_key["cedric"])
    cedric_view.add_obj(server.last_album_get_response.album.metadata)
    cedric_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in cedric_view.available_data:
            return 0
    # Remove Cedric from the album
    crypto.current_owner = "alice"
    alice.remove_friend_from_album("my_album", "cedric")
    # Add a new photo
    crypto.current_owner = "bob"
    new_photo = b'PHOOBOB'
    bob.add_photo_to_album("my_album", new_photo, a_pk)
    # Test that Cedric cannot see the new photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_keys(owner_to_secret_key["cedric"])
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        if new_photo in cedric_view.available_data:
            return 0
    # Test Alice can see the new photo
    crypto.current_owner = "alice"
    alice.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "alice":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    alice_view = View(owner_to_secret_key["bob"])
    alice_view.add_obj(server.last_album_get_response.album.metadata)
    alice_view.add_obj(server.last_album_get_response.album.photos)
    if new_photo not in alice_view.available_data:
        return 0  
    # Add a new photo
    crypto.current_owner = "alice"
    new_photo = b'PHOOOOO'
    alice.add_photo_to_album("my_album", new_photo, a_pk)
    # Test that Cedric cannot see the new photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_keys(owner_to_secret_key["cedric"])
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        if new_photo in cedric_view.available_data:
            return 0
    # Test Bob can see the new photo
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if new_photo not in bob_view.available_data:
            return 0  

    return pts

@test_this
def security_add_photo():
    if not correctness_basic_workflow():
        return 0
    crypto.current_owner = "None"
    pts = 20
    server = TestServer()
    crypto.current_owner = "alice"
    alice = Client("alice", server)
    a_pk = alice.signing_public_key
    alice.register()
    alice_pp = alice.public_profile
    crypto.current_owner = "bob"
    bob = Client("bob", server)
    b_pk = bob.signing_public_key
    bob.register()
    bob_pp = alice.get_friend_public_profile("bob", b_pk)
    crypto.current_owner = "cedric"
    cedric = Client("cedric", server)
    c_pk = cedric.signing_public_key
    cedric.register()
    cedric_pp = alice.get_friend_public_profile("cedric", c_pk)
    # Create the album
    photos = []
    photos.append(b'PHTOOOO')
    photos.append(b'PHOTOOO')
    photos.append(b'PHOOTOO')
    photos.append(b'PHOOOTO')
    photos.append(b'PHOOOOT')
    friends = {"alice":alice_pp, "bob":bob_pp}
    crypto.current_owner = "alice"
    alice.create_shared_album("my_album", photos, friends)
    # Test that Bob can access the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0
    # Add a photo to the album
    crypto.current_owner = "bob"
    new_photo = b'PHOOBOB'
    photos.append(new_photo)
    bob.add_photo_to_album("my_album", new_photo, a_pk)
    # Test that Cedric cannot access any photo
    crypto.current_owner = "cedric"
    cedric_view = View(owner_to_secret_key["cedric"])
    try:
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    # Test that Bob can access the photos
    crypto.current_owner = "bob"
    bob.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "bob":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    bob_view = View(owner_to_secret_key["bob"])
    bob_view.add_obj(server.last_album_get_response.album.metadata)
    bob_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in bob_view.available_data:
            return 0  
    # Test that Cedric cannot access any photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    # Test that Alice can access the photos
    crypto.current_owner = "alice"
    alice.get_album("my_album", a_pk).photos
    request = server.last_album_get_request
    response = server.last_album_get_response
    if(type(request) != api.GetAlbumRequest):
        return 0
    if request.username != "alice":
        return 0
    if(type(response) != api.GetAlbumResponse):
        return 0
    alice_view = View(owner_to_secret_key["alice"])
    alice_view.add_obj(server.last_album_get_response.album.metadata)
    alice_view.add_obj(server.last_album_get_response.album.photos)
    for p in photos:
        if p not in alice_view.available_data:
            return 0  
    # Test that Cedric cannot access any photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    # Add a photo to the album
    crypto.current_owner = "alice"
    new_photo = b'PHOOOOO'
    photos.append(new_photo)
    alice.add_photo_to_album("my_album", new_photo, a_pk)
    # Test that Cedric cannot access any photo
    try:
        crypto.current_owner = "cedric"
        photos_received = cedric.get_album("my_album", a_pk).photos
        return 0
    except errors.AlbumPermissionError:
        request = server.last_album_get_request
        response = server.last_album_get_response
        if(type(request) != api.GetAlbumRequest):
            return 0
        if request.username != "cedric":
            return 0
        if(type(response) != api.GetAlbumResponse):
            return 0
        cedric_view.add_obj(server.last_album_get_response.album.metadata)
        cedric_view.add_obj(server.last_album_get_response.album.photos)
        for p in photos:
            if p in cedric_view.available_data:
                return 0
    return pts


total_pts = 0
for test in tests:
    pts = test()
    print("{}: {} pt(s)".format(test.__name__, pts))
    total_pts += pts

print("----------------------------------------------------------------")
print("total: {} / {} pts".format(total_pts, MAX_SCORE))
