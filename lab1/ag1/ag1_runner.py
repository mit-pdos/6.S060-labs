#!/usr/bin/env python3

import traceback
import random

import client
from dummy_server import *
import api, errors

MAX_SCORE = 70

tests = []

def test_this(f):
    tests.append(f)
    return f

### standard tests

@test_this
def test_correct_behavior_1():
    pts = 2

    try:
        server = Lab1Server()
        alice = client.Client("alice", server)
        alice.register()
        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()
        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        photo_blob2 = b'photo2'
        if alice.put_photo(photo_blob2) != 1:
            pts -= 1

        alicebis.login()
        photo_blob3 = b'photo3'
        if alicebis.put_photo(photo_blob3) != 2:
            pts -= 1

        photos = [photo_blob1, photo_blob2, photo_blob3]
        photo_list = alicebis.list_photos()
        alicebis_photos = []
        for pid in photo_list:
            alicebis_photos.append(alicebis.get_photo(pid))

        if photos != alicebis_photos:
            pts -= 1

        if pts < 0:
            pts = 0
        return pts
    except:
        traceback.print_exc()
        return 0

@test_this
def test_replay_attack_1():
    pts = 2

    try:
        server = Lab1Server(attack="replay_attack_1")
        alice = client.Client("alice", server)
        alice.register()
        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()
        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        alicebis.login()
        photo_blob2 = b'photo2'
        if alicebis.put_photo(photo_blob2) != 1:
            pts -= 1

        photo_blob3 = b'photo3'
        try:
            alicebis.put_photo(photo_blob3)
            pts -= 1
        except errors.SynchronizationError: # TODO check the exact error
            pass

        if pts < 0:
            pts = 0
        return pts
    except:
        traceback.print_exc()
        return 0

# TODO technically, an implementation that fails this test might still be spec-compliant
# def test_double_register_attack_1():
#     pts = 2

#     try:
#         server = Lab1Server(attack="double_register_1")
#         alice = client.Client("alice", server)
#         alice.register()
#         alice.login()
#         photo_blob1 = b'photo1'
#         if alice.put_photo(photo_blob1) != 0:
#             pts -= 1
        
#         photo_blob2 = b'photo2'
#         if alice.put_photo(photo_blob2) != 1:
#             pts -= 1
#         try:
#             alice.register()
#         except errors.UserAlreadyExistsError:
#             pass
#         except:
#             traceback.print_exc()
#             return 0

#         user_secret = alice.user_secret
#         alicebis = client.Client("alice", server, user_secret)
#         alicebis.login()
#         photo_blob3 = b'photo3'
#         try:
#             alicebis.put_photo(photo_blob3)
#             pts = 0
#         except errors.SynchronizationError:
#             pass
#         except:
#             traceback.print_exc()
#             pts = 0

#         if pts < 0:
#             pts = 0
#         return pts
        
#     except:
#         traceback.print_exc()
#         return 0

@test_this
def test_double_register_attack_2():
    pts = 2

    try:
        server = Lab1Server(attack="double_register_2")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()
        
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1

        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()
        photo_blob2 = b'photo2'
        if alicebis.put_photo(photo_blob2) != 1:
            pts -= 1

        alice.register()

        alicebis.login()
        photo_blob3 = b'photo3'
        try:
            alicebis.put_photo(photo_blob3)
            pts = 0
        except errors.SynchronizationError: # TODO make check more precise
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_change_photo_id_attack_1():
    pts = 2

    try:
        server = Lab1Server(attack="change_photo_id_1")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()

        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        photo_blob2 = b'photo2'
        if alice.put_photo(photo_blob2) != 1:
            pts -= 1

        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()

        photo_blob3 = b'photo3'
        if alicebis.put_photo(photo_blob3) != 2:
            pts -= 1

        photo_blob4 = b'photo4'
        if alicebis.put_photo(photo_blob4) != 3:
            pts -= 1

        try:
            alice.login()
            photo_blob5 = b'photo5'
            alice.put_photo(photo_blob5)
            pts = 0
        except errors.SynchronizationError: # TODO make check more precise
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_change_photo_id_attack_2():
    pts = 2

    try:
        server = Lab1Server(attack="change_photo_id_2")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()

        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        photo_blob2 = b'photo2'
        if alice.put_photo(photo_blob2) != 1:
            pts -= 1

        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()

        photo_blob3 = b'photo3'
        if alicebis.put_photo(photo_blob3) != 2:
            pts -= 1

        photo_blob4 = b'photo4'
        if alicebis.put_photo(photo_blob4) != 3:
            pts -= 1

        try:
            alice.login()
            photo_blob5 = b'photo5'
            alice.put_photo(photo_blob5)
            pts = 0
        except errors.SynchronizationError: # TODO make check more precise
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_change_photo_order_attack_1():
    pts = 2

    try:
        server = Lab1Server(attack="change_photo_order_1")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()

        photo_blob2 = b'photo2'
        if alicebis.put_photo(photo_blob2) != 1:
            pts -= 1

        alice.login()
        photo_blob3 = b'photo3'
        if alice.put_photo(photo_blob3) != 2:
            pts -= 1
        
        alicebis.login()
        photo_blob4 = b'photo4'
        try:
            alicebis.put_photo(photo_blob4)
            pts = 0
        except errors.SynchronizationError: # TODO make check more exact
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_version_number_attack_1():
    pts = 2

    try:
        server = Lab1Server(attack="version_number_1")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()

        user_secret = alice.user_secret
        alicecheck = client.Client("alice", server, user_secret)
        alicecheck.login()
        if alicecheck.list_photos() != []:
            pts -= 1

        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        photo_blob2 = b'photo2'
        if alice.put_photo(photo_blob2) != 1:
            pts -= 1
        
        alice.register()
        
        photo_blob3 = b'photo3'
        if alice.put_photo(photo_blob3) != 2:
            pts -= 1
        
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()
        photo_blob4 = b'photo4'
        try:
            alicebis.put_photo(photo_blob4)
            pts = 0
        except errors.SynchronizationError: # TODO more precise check
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_version_number_attack_2():
    pts = 2

    try:
        server = Lab1Server(attack="version_number_2")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()

        photo_blob2 = b'photo2'
        if alicebis.put_photo(photo_blob2) != 1:
            pts -= 1

        alice.login()
        photo_blob3 = b'photo3'
        if alice.put_photo(photo_blob2) != 2:
            pts -= 1
        
        alicebis.login()
        photo_blob4 = b'photo4'
        try:
            alicebis.put_photo(photo_blob4)
            pts = 0
        except errors.SynchronizationError: # TODO more precise check
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

@test_this
def test_change_photo_blob_1():
    pts = 2

    try:
        server = Lab1Server(attack="change_photo_blob_1")
        alice = client.Client("alice", server)
        alice.register()
        alice.login()
        photo_blob1 = b'photo1'
        if alice.put_photo(photo_blob1) != 0:
            pts -= 1
        
        user_secret = alice.user_secret
        alicebis = client.Client("alice", server, user_secret)
        alicebis.login()

        photo_blob2 = b'photo2'
        if alicebis.put_photo(photo_blob2) != 1:
            pts -= 1

        alice.login()
        photo_blob3 = b'photo3'
        try:
            alice.put_photo(photo_blob3)
            pts = 0
        except errors.SynchronizationError: # TODO more precise check
            pass
        except:
            traceback.print_exc()
            pts = 0

        if pts < 0:
            pts = 0
        return pts
        
    except:
        traceback.print_exc()
        return 0

### trace tests

class StateTracer:
    def __init__(self, username, server):
        self.server = server
        self.write_client = client.Client(username, server)
        self.read_client = client.Client(username, server, self.write_client.user_secret)
        self.trace = []

    def register(self):
        self.write_client.register()
        self._save_snapshot()

    def put_photo(self, blob):
        self.write_client.put_photo(blob)
        self._save_snapshot()

    def _snapshot(self, client):
        snapshot = []
        id_list = client.list_photos()
        for photo_id in id_list:
            snapshot.append(client.get_photo(photo_id))
        return snapshot

    def _save_snapshot(self):
        self.trace.append(self._snapshot(self.write_client))

    def sanity_check(self):
        try:
            sanity_client = client.Client(self.write_client.username, self.server, self.write_client.user_secret)
            sanity_client.login()

            snapshot = self._snapshot(sanity_client)
            return snapshot == self.trace[-1]
        except Exception:
            traceback.print_exc()
            return False

    def test_sync(self):
        self.read_client.login()
        try:
            snapshot = self._snapshot(self.read_client)
        except errors.SynchronizationError:
            self.server.synchronize = lambda request: api.SynchronizeResponse(None, [])
            try:
                snapshot = self._snapshot(self.read_client)
            except errors.SynchronizationError:
                # occurs when registration was tampered with
                return True
            pass


        for t_snapshot in self.trace:
            if t_snapshot == snapshot:
                return True

        # print('snapshot prefix invalid: {} does not precede {}'.format(snapshot, self.trace[-1]))
        return False

from enum import IntEnum, auto, unique

@unique
class TamperOp(IntEnum):
    REPLAY_LOG = auto()
    DELETE_LOG = auto()
    OVERWRITE_LOG = auto()
    SWAP_LOGS = auto()
    
    TAMPER_BLOB = auto()
    ZERO_BLOB = auto()

    SWAP_BLOBS = auto()
    SWAP_IDS = auto()

    INCR_INT = auto()
    DECR_INT = auto()
    TAMPER_INT = auto()
    ZERO_INT = auto()
    SWAP_INTS_0 = auto()

@auto_str
class StorageMod:
    def __init__(self, op, log_index, log_index2, int_offset, int_offset2):
        self.op = op
        self.log_index = log_index
        self.log_index2 = log_index2
        self.int_offset = int_offset
        self.int_offset2 = int_offset2
    def apply(self, storage):
        pid = self.log_index
        if pid == 0:
            pid = 1
        pid2 = self.log_index2
        if pid2 == 0:
            pid2 = 1

        if self.op == TamperOp.REPLAY_LOG:
            for username in storage.userbase:
                udata = storage.userbase[username]
                storage.userbase[username] = replay_log(udata, self.log_index)
        elif self.op == TamperOp.DELETE_LOG:
            for username in storage.userbase:
                udata = storage.userbase[username]
                storage.userbase[username] = delete_log(udata, self.log_index)
        elif self.op == TamperOp.OVERWRITE_LOG:
            for username in storage.userbase:
                udata = storage.userbase[username]
                storage.userbase[username] = overwrite_log(udata, self.log_index, self.log_index2)
        elif self.op == TamperOp.SWAP_LOGS:
            for username in storage.userbase:
                udata = storage.userbase[username]
                storage.userbase[username] = swap_logs(udata, self.log_index, self.log_index2)
        elif self.op == TamperOp.TAMPER_BLOB:
            for username in storage.userbase:
                blob_tamper(storage, username, pid)
        elif self.op == TamperOp.ZERO_BLOB:
            for username in storage.userbase:
                blob_zero(storage, username, pid)

        elif self.op == TamperOp.SWAP_BLOBS:
            for username in storage.userbase:
                swap_blobs(storage, username, pid, pid2)
        elif self.op == TamperOp.SWAP_IDS:
            for username in storage.userbase:
                swap_ids(storage, username, pid, pid2)

        elif self.op == TamperOp.INCR_INT:
            for username in storage.userbase:
                udata = storage.userbase[username]
                xs = find_ints(udata.history[self.log_index])
                if len(xs) == 0:
                    return
                off = self.int_offset % len(xs)
                storage.userbase[username] = replace_int(udata, self.log_index, xs[off], xs[off]+1)
        elif self.op == TamperOp.DECR_INT:
            for username in storage.userbase:
                udata = storage.userbase[username]
                xs = find_ints(udata.history[self.log_index])
                if len(xs) == 0:
                    return
                off = self.int_offset % len(xs)

                # TODO should we sanitize this?
                result = xs[off]-1
                if result < 0:
                    result = 0

                storage.userbase[username] = replace_int(udata, self.log_index, xs[off], result)
        elif self.op == TamperOp.TAMPER_INT:
            for username in storage.userbase:
                udata = storage.userbase[username]
                xs = find_ints(udata.history[self.log_index])
                if len(xs) == 0:
                    return
                off = self.int_offset % len(xs)
                storage.userbase[username] = replace_int(udata, self.log_index, xs[off], self.int_offset2)
        elif self.op == TamperOp.ZERO_INT:
            for username in storage.userbase:
                udata = storage.userbase[username]
                xs = find_ints(udata.history[self.log_index])
                if len(xs) == 0:
                    return
                off = self.int_offset % len(xs)
                storage.userbase[username] = replace_int(udata, self.log_index, xs[off], 0)
        elif self.op == TamperOp.SWAP_INTS_0:
            for username in storage.userbase:
                udata = storage.userbase[username]
                xs = find_ints(udata.history[self.log_index])
                if len(xs) == 0:
                    return
                off = self.int_offset % len(xs)
                off2 = self.int_offset2 % len(xs)
                storage.userbase[username] = replace_int(udata, self.log_index, xs[off], xs[off2])

def gen_index(gen_int, log_size):
    if gen_int(4) == 0:
        return 0
    else:
        return gen_int(log_size)

def gen_storage_mod(gen_int, log_size):
    op = TamperOp(1+gen_int(len(TamperOp.__members__)-1))
    log_index = gen_index(gen_int, log_size)
    log_index2 = gen_index(gen_int, log_size)
    int_offset = gen_int(50)
    int_offset2 = gen_int(50)
    return StorageMod(op, log_index, log_index2, int_offset, int_offset2)

def find_ints(log_entry):
    xs = []
    for item in log_entry.data:
        if type(item) == int:
            xs.append(item)
    return xs

def blob_zero(storage, username, id1):
    blob1 = storage.userbase[username].photobase[id1].photo_blob
    blob_tamper = b''

    storage.userbase[username].photobase[id1] = PhotoData(username, id1, blob_tamper)

    index1 = storage.photo_id_to_log_index[(username, id1)]

    udata = storage.userbase[username]
    udata = replace_bytes(udata, index1, blob1, blob_tamper)
    storage.userbase[username] = udata

def blob_tamper(storage, username, id1):
    blob1 = storage.userbase[username].photobase[id1].photo_blob
    blob_tamper = b'TAMPER' + blob1 + b'TAMPER'

    storage.userbase[username].photobase[id1] = PhotoData(username, id1, blob_tamper)

    index1 = storage.photo_id_to_log_index[(username, id1)]

    udata = storage.userbase[username]
    udata = replace_bytes(udata, index1, blob1, blob_tamper)
    storage.userbase[username] = udata

def replace_int(userdata, index, a, b):
    history = userdata.history
    log_entry = history[index]
    
    for i, item in enumerate(log_entry.data):
        if type(item) == int and item == a:
            log_entry.data[i] = b

    history = history[:index] + [log_entry] + history[index+1:]
    userdata.history = history
    return userdata

def replace_bytes(userdata, index, a, b):
    history = userdata.history
    log_entry = history[index]
    
    for i, item in enumerate(log_entry.data):
        if type(item) == bytes and item == a:
            log_entry.data[i] = b

    history = history[:index] + [log_entry] + history[index+1:]
    userdata.history = history
    return userdata

def swap_blobs(storage, username, id1, id2):
    blob1 = storage.userbase[username].photobase[id1].photo_blob
    blob2 = storage.userbase[username].photobase[id2].photo_blob

    storage.userbase[username].photobase[id1] = PhotoData(username, id1, blob2)
    storage.userbase[username].photobase[id2] = PhotoData(username, id2, blob1)

    index1 = storage.photo_id_to_log_index[(username, id1)]
    index2 = storage.photo_id_to_log_index[(username, id2)]

    udata = storage.userbase[username]
    udata = replace_bytes(udata, index1, blob1, blob2)
    udata = replace_bytes(udata, index2, blob2, blob1)
    storage.userbase[username] = udata

def swap_ids(storage, username, id1, id2):
    blob1 = storage.userbase[username].photobase[id1].photo_blob
    blob2 = storage.userbase[username].photobase[id2].photo_blob

    storage.userbase[username].photobase[id1] = PhotoData(username, id2, blob1)
    storage.userbase[username].photobase[id2] = PhotoData(username, id1, blob2)

    index1 = storage.photo_id_to_log_index[(username, id1)]
    index2 = storage.photo_id_to_log_index[(username, id2)]

    udata = storage.userbase[username]
    udata = replace_int(udata, index1, id1, id2)
    udata = replace_int(udata, index2, id2, id1)
    storage.userbase[username] = udata

def replay_log(userdata, index):
    history = userdata.history
    history = history[:index] + [history[index]] + history[index:]
    userdata.history = history
    return userdata

def delete_log(userdata, index):
    history = userdata.history
    history = history[:index] + history[index+1:]
    userdata.history = history
    return userdata

def overwrite_log(userdata, index_remove, index_replace):
    history = userdata.history
    history = history[:index_remove] + [history[index_replace]] + history[index_remove+1:]
    userdata.history = history
    return userdata

def swap_logs(userdata, index1, index2):
    history = userdata.history
    log1 = history[index1]
    log2 = history[index2]
    history = history[:index1] + [log1] + history[index1+1:]
    history = history[:index2] + [log2] + history[index2+1:]
    userdata.history = history
    return userdata

@test_this
def test_correct_behavior_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        res = tracer.test_sync()
        if res:
            try:
                snap = tracer._snapshot(tracer.read_client)
                if snap != tracer.trace[-1]:
                    return 0
            except:
                traceback.print_exc()
                return 0
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0
    
@test_this
def test_replay_attack_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0
        
        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replay_log(udata, 5)
            
        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_double_register_attack_2t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0
        
        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replay_log(udata, 0)
            
        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_change_photo_id_attack_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replace_int(udata, 4, 3, 2)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0    

@test_this
def test_change_photo_id_attack_2t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replace_int(udata, 4, 3, 300)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0    

@test_this
def test_change_photo_order_attack_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            swap_blobs(server._storage, username, 4, 5)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_delete_log_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = delete_log(udata, 5)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_version_number_attack_2t_1():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replace_int(udata, 4, 4, 2)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0    

@test_this
def test_version_number_attack_2t_2():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replace_int(udata, 4, 4, 200)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0    

@test_this
def test_change_photo_blob_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            blob_tamper(server._storage, username, 1)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_censor_photo_1t():
    pts = 2

    try:
        server = Lab1Server()

        tracer = StateTracer("alice", server)
        tracer.register()

        for i in range(10):
            photo_blob = b'photo' + bytes(str(i), 'utf-8')
            tracer.put_photo(photo_blob)
        if not tracer.sanity_check():
            return 0

        for username in server._storage.userbase:
            udata = server._storage.userbase[username]
            server._storage.userbase[username] = replace_int(udata, 5, api.OperationCode.PUT_PHOTO, api.OperationCode.REGISTER)

        # for username in server._storage.userbase:
        #     udata = server._storage.userbase[username]
        #     server._storage.userbase[username] = overwrite_log(udata, 5, 0)

        res = tracer.test_sync()
        if res:
            return 2
        else:
            return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_search_for_attacks_1t():
    pts = 10
    wrong = search_for_attacks(pts=pts, seed=65060, iters=50, logsize=5, muts=1)
    if wrong > pts:
        return 0
    else:
        return pts - wrong

@test_this
def test_search_for_attacks_2t():
    pts = 10
    wrong = search_for_attacks(pts=pts, seed=65060, iters=50, logsize=5, muts=2)
    if wrong > pts:
        return 0
    else:
        return pts - wrong

@test_this
def test_search_for_attacks_3t():
    pts = 10
    wrong = search_for_attacks(pts=pts, seed=65060, iters=50, logsize=10, muts=5)
    if wrong > pts:
        return 0
    else:
        return pts - wrong

def search_for_attacks(pts, seed, iters, logsize, muts):
    rng = random.Random(seed)
    def rng_int(b):
        return rng.randrange(0, b)

    correct = 0
    for i in range(iters):
        try:
            server = Lab1Server()

            tracer = StateTracer("alice", server)
            tracer.register()

            for j in range(logsize):
                photo_blob = b'photo' + bytes(str(j), 'utf-8')
                tracer.put_photo(photo_blob)
            if not tracer.sanity_check():
                print("failed correct trace (length {})".format(logsize))
                if i-correct >= pts:
                    break
                continue

            attacks = []
            for j in range(muts):
                attacks.append(gen_storage_mod(rng_int, logsize))

            for attack in attacks:
                attack.apply(server._storage)

            try:
                res = tracer.test_sync()
            except:
                traceback.print_exc()
                res = False
            if res:
                correct += 1
            else:
                print('attack trace\n' + '\n'.join('  ' + str(smod) for smod in attacks))

            if i-correct >= pts:
                break

        except:
            traceback.print_exc()
            pass

    # return pts * (float(correct) / iters)
    return iters-correct


# TODO multiuser attack?

# TODO add timeouts to tests (to handle infinite loops)

total_pts = 0
for test in tests:
    pts = test()
    print("{}: {} pt(s)".format(test.__name__, pts))
    total_pts += pts

print("----------------------------------------------------------------")
print("total: {} / {} pts".format(total_pts, MAX_SCORE))
