#!/usr/bin/env python3

import traceback
import random

import client
from dummy_server import *
import api, errors

from util import trace, auto_str

MAX_SCORE = 140

tests = []

def test_this(f):
    tests.append(f)
    return f

### correctness

@test_this
def test_one_hop_correct():
    try:
        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        alice.add_contact("bob", bob.public_key)
        if alice.get_trusted_user_public_key("bob") == bob.public_key:
            return 1
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_correct():
    try:
        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        if alice.get_trusted_user_public_key("cedric") == cedric.public_key:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_three_hops_correct():
    try:
        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        cedric.add_contact("danielle", danielle.public_key)
        if alice.get_trusted_user_public_key("danielle") == danielle.public_key:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_correct():
    try:
        N = 7
        if line_correct_check(N):
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

def line_correct_check(N):
    server = Lab2Server()
    names = []
    clients = []
    for i in range(N):
        name = "client"+str(i)
        ci = client.Client(name, server)
        names.append(name)
        clients.append(ci)
        ci.register()

    for i in range(N-1):
        clients[i].add_contact(names[i+1], clients[i+1].public_key)

    for i in range(1, N):
        if clients[0].get_trusted_user_public_key(names[i]) != clients[i].public_key:
            return False
    return True

@test_this
def test_two_way_signing_correct():
    try:
        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("alice", alice.public_key)

        pts = 0
        if alice.get_trusted_user_public_key("bob") == bob.public_key:
            pts += 1
        if bob.get_trusted_user_public_key("alice") == alice.public_key:
            pts += 1
        return pts
    except:
        traceback.print_exc()
        return 0

### security; honest server

@test_this
def test_island_secure():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        try:
            alice.get_trusted_user_public_key("bob")
        except errors.InvalidTrustLinkError:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_one_hop_secure():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        alice.add_contact("bob", bob.public_key)
        try:
            bob.get_trusted_user_public_key("alice")
        except errors.InvalidTrustLinkError:
            return 1
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_secure():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        try:
            cedric.get_trusted_user_public_key("alice")
        except errors.InvalidTrustLinkError:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_secure():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        for i in range(N-1, 0, -1):
            try:
                clients[i].get_trusted_user_public_key(names[0])
            except errors.InvalidTrustLinkError:
                pass
            else:
                return 0
        return 2
    except:
        traceback.print_exc()
        return 0

### security, adversarial server

@test_this
def test_zero_hops_secure_self():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        server._storage.replace_public_key_raw("alice", bob.public_key)
        try:
            alice.get_trusted_user_public_key("alice")
        except errors.InvalidTrustLinkError:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_zero_hops_secure_self_contact():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        alice.add_contact("bob", bob.public_key)
        server._storage.replace_public_key_raw("alice", bob.public_key)
        try:
            alice.get_trusted_user_public_key("alice")
        except errors.InvalidTrustLinkError:
            return 2
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_path_with_cycle_secure_self():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        cedric.add_contact("alice", alice.public_key)

        alice_to_bob = server.get_trust_link(api.GetTrustLinkRequest("alice", "bob"))
        bob_to_alice = server.get_trust_link(api.GetTrustLinkRequest("bob", "alice"))
        spliced_path = alice_to_bob.path + bob_to_alice.path
        server.set_path_response("alice", "alice", spliced_path)

        try:
            if alice.get_trusted_user_public_key("alice") == alice.public_key:
                return 4
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_path_with_cycle_secure_self_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        cedric.add_contact("alice", alice.public_key)

        server._storage.replace_public_key_raw("alice", bob.public_key)

        alice_to_bob = server.get_trust_link(api.GetTrustLinkRequest("alice", "bob"))
        bob_to_alice = server.get_trust_link(api.GetTrustLinkRequest("bob", "alice"))
        spliced_path = alice_to_bob.path + bob_to_alice.path
        server.set_path_response("alice", "alice", spliced_path)

        try:
            alice.get_trusted_user_public_key("alice")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_one_hop_secure_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()

        alice.add_contact("bob", bob.public_key)
        server._storage.replace_public_key_raw("bob", cedric.public_key)
        try:
            alice.get_trusted_user_public_key("bob")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_one_hop_secure_name():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()

        alice.add_contact("bob", bob.public_key)
        server.replace_name_raw("bob", "cedric")
        try:
            alice.get_trusted_user_public_key("cedric")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_secure_key_end():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()

        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", bob.public_key)
        server._storage.replace_public_key_raw("cedric", danielle.public_key)
        try:
            alice.get_trusted_user_public_key("cedric")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_secure_key_mid():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()

        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", bob.public_key)
        server._storage.replace_public_key_raw("bob", danielle.public_key)
        try:
            alice.get_trusted_user_public_key("cedric")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_secure_name_end():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()

        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", bob.public_key)
        server.replace_name_raw("cedric", "danielle")
        try:
            alice.get_trusted_user_public_key("cedric")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_two_hops_secure_name_mid():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()

        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", bob.public_key)
        server.replace_name_raw("bob", "danielle")
        try:
            alice.get_trusted_user_public_key("cedric")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_head_secure_1():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[1:])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_head_secure_2():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[4:])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_mid_secure_1():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[:3] + res.path[4:])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_mid_secure_2():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[:1] + res.path[-1:])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_tail_secure_1():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[:-1])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_missing_tail_secure_2():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        res = server.get_trust_link(api.GetTrustLinkRequest(names[0], names[-1]))
        server.set_path_response(names[0], names[-1], res.path[:-4])

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

# A -> B -> C -> B -> D
@test_this
def test_path_with_cycle_secure():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        cedric.add_contact("bob", bob.public_key)
        bob.add_contact("danielle", danielle.public_key)

        alice_to_cedric = server.get_trust_link(api.GetTrustLinkRequest("alice", "cedric"))
        cedric_to_danielle = server.get_trust_link(api.GetTrustLinkRequest("cedric", "danielle"))
        spliced_path = alice_to_cedric.path + cedric_to_danielle.path
        server.set_path_response("alice", "danielle", spliced_path)

        try:
            if alice.get_trusted_user_public_key("danielle") == danielle.public_key:
                return 4
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

# A -> B -> C -> B -> D
@test_this
def test_path_with_cycle_secure_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        alice = client.Client("alice", server)
        alice.register()
        bob = client.Client("bob", server)
        bob.register()
        cedric = client.Client("cedric", server)
        cedric.register()
        danielle = client.Client("danielle", server)
        danielle.register()
        elaine = client.Client("elaine", server)
        elaine.register()
        alice.add_contact("bob", bob.public_key)
        bob.add_contact("cedric", cedric.public_key)
        cedric.add_contact("bob", bob.public_key)
        bob.add_contact("danielle", danielle.public_key)
        server._storage.replace_public_key_raw("danielle", elaine.public_key)

        alice_to_cedric = server.get_trust_link(api.GetTrustLinkRequest("alice", "cedric"))
        cedric_to_danielle = server.get_trust_link(api.GetTrustLinkRequest("cedric", "danielle"))
        spliced_path = alice_to_cedric.path + cedric_to_danielle.path
        server.set_path_response("alice", "danielle", spliced_path)

        try:
            alice.get_trusted_user_public_key("danielle")
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_secure_head_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        for i in range(N-1):
            server._storage.replace_public_key_raw(names[i], clients[0].public_key)

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_secure_mid_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        for i in range(N-1):
            server._storage.replace_public_key_raw(names[i], clients[1].public_key)

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_line_graph_secure_end_key():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7
        names = []
        clients = []
        for i in range(N):
            name = "client"+str(i)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        for i in range(N-1):
            clients[i].add_contact(names[i+1], clients[i+1].public_key)

        for i in range(N-1):
            server._storage.replace_public_key_raw(names[i], clients[-1].public_key)

        try:
            clients[0].get_trusted_user_public_key(names[-1])
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_bogus_path_secure_1():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7

        alice = client.Client("alice", server)
        alice.register()

        prev = "alice"
        bogus = []
        names = []
        clients = []
        for i in range(N):
            name0 = "bogus-client0-"+str(i)
            name1 = "bogus-client1-"+str(i)
            ci0 = client.Client(name0, server)
            ci1 = client.Client(name1, server)

            names.append(name0)
            names.append(name1)
            clients.append(ci0)
            ci0.register()
            clients.append(ci1)
            ci1.register()

            ci0.add_contact(name1, ci1.public_key)
            hop = server.get_trust_link(api.GetTrustLinkRequest(name0, name1))
            hop.path[0].user_src = prev
            prev = name1
            bogus += hop.path

        server.set_path_response("alice", prev, bogus)
        try:
            alice.get_trusted_user_public_key(prev)
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

@test_this
def test_bogus_path_secure_2():
    try:
        if not line_correct_check(10):
            return 0

        server = Lab2Server()
        N = 7

        alice = client.Client("alice", server)
        alice.register()

        prev = "alice"
        bogus = []
        names = []
        clients = []
        for i in range(N):
            name0 = "bogus-client0-"+str(i)
            name1 = "bogus-client1-"+str(i)
            ci0 = client.Client(name0, server)
            ci1 = client.Client(name1, server, ci0.user_secret)

            names.append(name0)
            names.append(name1)
            clients.append(ci0)
            ci0.register()
            clients.append(ci1)
            ci1.register()

            ci0.add_contact(name1, ci1.public_key)
            hop = server.get_trust_link(api.GetTrustLinkRequest(name0, name1))
            hop.path[0].user_src = prev
            prev = name1
            bogus += hop.path

        server.set_path_response("alice", prev, bogus)
        try:
            alice.get_trusted_user_public_key(prev)
        except errors.InvalidTrustLinkError:
            return 4
        return 0
    except:
        traceback.print_exc()
        return 0

# randomized tests

@test_this
def test_part_of_path_signed_by_wrong_key_secure():
    pts = 6
    try:
        if not line_correct_check(10):
            return 0

        N = 5
        keys = [0, N-1, random.randint(0, N-1)]
        linkses = [[1], [N-1], [random.randint(1, N-1)], [link for link in range(N)]]
        gained_pts = 0.0
        total_pts = 0.0
        for key in keys:
            for links in linkses:
                if len(links) != 1 or links[0] != key:
                    total_pts += 1
                    if path_signed_by_key_secure_check(N, key, links):
                        gained_pts += 1
        return round(gained_pts / total_pts * pts)
    except:
        traceback.print_exc()
        return 0

def path_signed_by_key_secure_check(N, key=0, links=[0]):
    server = Lab2Server()
    names = []
    clients = []
    for i in range(N):
        name = "client"+str(i)
        ci = client.Client(name, server)
        names.append(name)
        clients.append(ci)
        ci.register()

    for i in range(N-1):
        clients[i].add_contact(names[i+1], clients[i+1].public_key)

    for link in links:
        server._storage.replace_public_key_raw(names[link], clients[key].public_key)

    try:
        clients[0].get_trusted_user_public_key(names[N-1])
    except errors.InvalidTrustLinkError:
        return True
    return False

from enum import IntEnum, auto, unique

@unique
class PathProp(IntEnum):
    DISCONNECTED = auto()
    TRUNCATE_BEFORE = auto()
    TRUNCATE_AFTER = auto()

    OVERWRITE_KEY = auto()
    OVERWRITE_NAME = auto()
    SWAP_KEYS = auto()
    SWAP_NAMES = auto()

    BOGUS_LINK = auto()

@auto_str
class PathAttr:
    def __init__(self, prop, index1, index2):
        self.prop = prop
        self.index1 = index1
        self.index2 = index2

    def __repr__(self):
        return str(self)

@auto_str
class PathSpec:
    def __init__(self, size, attrs):
        self.size = size
        self.attrs = attrs

    def __repr__(self):
        return str(self)

    def to_path(self, server, root, root_name, name_offset):
        prev = root
        names = []
        clients = []
        for i in range(self.size):
            name = "client-"+str(i)+"-offset-"+str(name_offset)
            ci = client.Client(name, server)
            names.append(name)
            clients.append(ci)
            ci.register()

        expect_no_raise = True

        bogus = {}
        for i in range(self.size):
            if self._bogus_index(i):
                expect_no_raise = False
                bogus[i] = True
            elif self._index_connected(i):
                prev.add_contact(names[i], clients[i].public_key)
            else:
                expect_no_raise = False

            prev = clients[i]

        for attr in self.attrs:
            expect_no_raise = False
            if attr.prop == PathProp.OVERWRITE_KEY:
                server._storage.replace_public_key_raw(names[attr.index1], clients[attr.index2].public_key)
            if attr.prop == PathProp.OVERWRITE_NAME:
                server.replace_name_raw(names[attr.index1], names[attr.index2])
            if attr.prop == PathProp.SWAP_KEYS:
                server._storage.replace_public_key_raw(names[attr.index1], clients[attr.index2].public_key)
                server._storage.replace_public_key_raw(names[attr.index2], clients[attr.index1].public_key)
            if attr.prop == PathProp.SWAP_NAMES:
                server.replace_name_raw(names[attr.index1], names[attr.index2])
                server.replace_name_raw(names[attr.index2], names[attr.index1])

        path = []
        prev = root_name
        for i in range(self.size):
            if i in bogus:
                corrupt = "corrupt-client-"+str(i)+"-offset-"+str(name_offset)
                ci_ = client.Client(corrupt, server, clients[i].user_secret)
                ci_.register()
                ci_.add_contact(names[i], clients[i].public_key)
                hop = server.get_trust_link(api.GetTrustLinkRequest(corrupt, names[i]))
                hop.path[0].user_src = prev
                path += hop.path
            else:
                resp = server.get_trust_link(api.GetTrustLinkRequest(prev, names[i]))
                path += resp.path
            prev = names[i]

        server.set_path_response("alice", names[-1], path)
        if len(path) == 0:
            expect_no_raise = False

        return clients, names, expect_no_raise

    def _index_connected(self, index):
        for attr in self.attrs:
            if attr.prop == PathProp.DISCONNECTED and attr.index1 == index:
                return False
            if attr.prop == PathProp.TRUNCATE_BEFORE and attr.index1 > index:
                return False
            if attr.prop == PathProp.TRUNCATE_AFTER and attr.index1 < index:
                return False
        return True

    def _bogus_index(self, index):
        for attr in self.attrs:
            if attr.prop == PathProp.BOGUS_LINK and attr.index1 == index:
                return True
        return False

def gen_path_attr(gen_int, max_size):
    op = PathProp(1+gen_int(len(PathProp.__members__)))
    index1 = gen_int(max_size)
    index2 = gen_int(max_size)
    return PathAttr(op, index1, index2)

def gen_path_spec(gen_int, max_size, max_muts):
    size = 1 + gen_int(max_size-1)
    num_muts = gen_int(max_muts+1)
    attrs = []
    for i in range(num_muts):
        attrs.append(gen_path_attr(gen_int, size))
    return PathSpec(size, attrs)

def search_for_attacks(seed, iters, max_path_length, num_muts):
    successes = 0

    rng = random.Random(seed)
    def rng_int(b):
        return rng.randrange(0, b)

    server = Lab2Server()

    alice = client.Client("alice", server)
    alice.register()

    try:
        for i in range(iters):
            spec = gen_path_spec(rng_int, max_path_length, num_muts)
            clients, names, expect_no_raise = spec.to_path(server, alice, "alice", i)

            if expect_no_raise:
                try:
                    key = alice.get_trusted_user_public_key(names[-1])
                    if key == clients[-1].public_key:
                        successes += 1
                    else:
                        print("accepted wrong public key")
                except errors.InvalidTrustLinkError:
                    print("failed to accept correct public key")
            else:
                try:
                    key = alice.get_trusted_user_public_key(names[-1])
                    if key == clients[-1].public_key:
                        successes += 1
                    else:
                        print("accepted attacker's public key from server. failure case:", spec)
                except errors.InvalidTrustLinkError:
                    successes += 1

    except:
        traceback.print_exc()

    finally:
        return successes
        
@test_this
def test_search_for_attacks_1():
    pts = 10
    total = 50
    correct = search_for_attacks(seed=65060, iters=total, max_path_length=5, num_muts=1)
    wrong = total - correct
    if wrong > pts:
        return 0
    else:
        return pts - wrong

@test_this
def test_search_for_attacks_2():
    pts = 10
    total = 100
    correct = search_for_attacks(seed=65060, iters=total, max_path_length=5, num_muts=2)
    wrong = total - correct
    if wrong > pts:
        return 0
    else:
        return pts - wrong

@test_this
def test_search_for_attacks_3():
    pts = 10
    total = 200
    correct = search_for_attacks(seed=65060, iters=total, max_path_length=5, num_muts=5)
    wrong = total - correct
    if wrong > pts:
        return 0
    else:
        return pts - wrong
        
total_pts = 0
for test in tests:
    pts = test()
    print("{}: {} pt(s)".format(test.__name__, pts))
    total_pts += pts

print("----------------------------------------------------------------")
print("total: {} / {} pts".format(total_pts, MAX_SCORE))
