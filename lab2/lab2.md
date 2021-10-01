# 6.S060 Lab 2

In this lab you will design and implement decentralized public-key infrastructure.

## Scenario

Suppose that Alice wishes to share her contact information with her friends.  To make ensure that this contact information can be trusted, Alice signs the information with a private key `alice_private_key`.

```
(alice_public_key, alice_private_key) <- Gen()
signature <- Sign(alice_private_key, Contact(username="alice", email="alice@example.edu", ...))
```

Alice writes down `alice_public_key` on her business card.  When she meets her friend Bob, she hands him her card.  Now Bob can tie Alice's `Contact` signatures, received over our photo-sharing application, to her real-life identity. 

```
assert Verify(alice_public_key, signature, Contact(username="alice", email="alice@example.edu", ...))
```

In this way, anyone whom Alice gave her card to can verify her contact.  Unfortunately, this required her to physically meet the other person (which, perhaps you might imagine, could be inconvenient for some reason).  Is there a way to avoid doing this?

We'd like to allow strangers to verify Alice's contact information without having personally met her.  To do this, we will implement an idea borrowed from the ["web of trust"](https://en.wikipedia.org/wiki/Web_of_trust).  In particular, in our system, friends who verify each others' identity in person exchange public keys and sign a statement attesting to the keys' validity.  Chained signatures then form a "path of trust" which allows someone to verify the contact information of not just a friend, but also a friend of a friend, or of a friend of a friend of a friend, or ...

For instance, suppose that Cedric knows Bob and Bob knows Alice, but Cedric does not know Alice directly.  Since Cedric knows Bob's public key, Cedric might request from the server Bob's signature of Alice's public key in order to verify her contact information.

## More specifically

Suppose that _G_ represents a directed graph of user contacts.  Whenever a user _U1_ executes `add_contact` on some other user _U2_ and their public key _K2_, this adds an edge from _U1_ to _U2_ in _G_.

_U1_ might issue an `api.UploadContactBookRequest` to notify the server of this change.  If the server is functioning correctly, then on subsequent `api.GetTrustLinkRequest` calls by _U1_ for any other user _U3_, the server should return a path from _U1_ to _U3_ if one exists.

We assume the following.

 - All non-adversarial users _U_ have a unique key, denoted _K(U)_.
 - For all pairs of users _U1_ and _U2_, if _U1_ is not adversarial, then _U1_ will `add_contact` for _U2_ with key _K(U2)_ only if _U2_ is not adversarial.
 - If the server is functioning correctly and there exists at least one path from _U1_ to _U2_ in _G_, the server will respond to a `api.GetTrustLinkRequest` with one of these paths.

Given these assumptions, your implementation must do the following for any user _U1_ which `get_trusted_user_public_key` of another user _U2_.

 - _Security_: The procedure must return _K(U2)_ only if there exists a path from _U1_ to _U2_ in _G_.  Otherwise it must raise an `errors.InvalidTrustLinkError`.
 - _Correctness_: If the server is functioning correctly, and there exists such a path, then it must return _K(U2)_.

### Your job

is to modify `add_contact` and `get_trusted_user_public_key` so that users can indirectly verify the public keys of one another.

As with lab 1, _this is an open-ended assignment!_  Again, you may modify any code in `client.py` so long as you do not change the signatures of the public methods of `Client` (i.e., the `__init__` method or methods not beginning with an underscore `_`).  However, since your `Client` must still talk to our server, you will **not** be able to modify any other files given to you.

### To submit lab 2

upload a ZIP file containing `client.py` to [Gradescope](https://www.gradescope.com/courses/281655).
