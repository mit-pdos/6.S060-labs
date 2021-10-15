# 6.S060 Lab 3

In this lab you will design and implement a private album feature.

This coding lab is closely related to the theory lab.
In particular, we ask you to implement a functionnality very close to what you designed in the part (c) of the first problem.
Note that there is no bandwith restriction here.
If you haven't looked at the theory part first, we advise you to read it to get hints on how to proceed.

## Scenario

Suppose that Alice has taken some photos which she wishes to share _privately_ with some of her friends.
Right now, all the photos she uploads through our application are public.

In order to allow Alice to control who has access to these picture, we would like to introduce the notion of _private albums_.
A private album has an _owner_ (`"Alice"`), a list of _photos_ (`[secret_party_invite.jpg, buried_treasure_coordinates.jpg]`), and a list of _friends_ who can add photos to and view photos in the album (`["Alice", "Bob", "Cedric", "Danielle"]`).
In this scenario, once Alice has created the album, she wishes for the following to be true.
  1. All of the friends should be able to view all of the photos, and
  2. No one else should be able to view any of the photos.

## More specifically

Assume that you have access to a PKI (for instance, one provided by a correct implementation for lab2).
As a result, tests will assume that you've already received the "correct" public _signing_ keys (i.e., for digital signatures) of other users.

Assume that the public profiles from lab0 are implemented.
We've added new public public keys for new primitives to the profiles and also signed them with each user's signing key. 
This way, any user can retreive these public keys in a trusted manner.

Assume that operations between the clients and the server happen sequentially and atomically.
In particular, a client will always have the latest version of the server state when the client tries to modifying the state.

As described in the theory portion of lab 3, assume the following.
 - The server is functioning correctly and will not tamper with the integrity of messages.  However, the server might not authenticate users before performing operations on their behalf.
 - Malicious clients will try to access photos that they are not supposed to see.  (Currently, a correctly-function `Client` will politely refuse to access photos it is not authorized to view.  A malicious client will not...)

Given these assumptions, our albums feature should support the following **correctness** properties.
1. Any client is able to create a private album and upload it to the server using `create_shared_album(album_name, photos, list_friends)`.  The client who does this is the album's _owner_.
2. Any client which is part of an album's `friends` is able to view photos within the album by calling `get_album(album_name, owner_signing_public_key)`.
3. Any client which is part of an album's `friends` is able to add photos to the album by calling `add_photo_to_album(album_name, photo, owner_signing_public_key)`.
4. An album's owner can `add_friend_to_album(album_name, friend_public_profile)`.  Once a friend is added to an album, it should be able to access all photos which were already added.

In addition, we should also support the following **confidentiality** property: clients (identified by their public signing key) which are _not_ part of an album should not be able to see any photo within the album.  In particular, an album's owner can remove a client from an album with `remove_friend_from_album(album_name, friend_name)`.  After a client is removed, it should not be able to see any new photos that are added to the album.

### Your Job

is to modify `client.py` to implement _secure_ private albums.

To do so, you can use the PKI, the public profile feature and the two new cryptographic primitives we added to your library: authenticated symmetric-key encryption and authenticated public-key encryption.  For a precise specification of these primitives, refer to the theory portion of lab 3.

As with previous labs, _this is an open-ended assignment!_  Again, you may modify any code in `client.py` so long as you do not change the signatures of the public methods of `Client` (i.e., the `__init__` method or methods not beginning with an underscore `_`).
However, since your `Client` must still talk to our server, you will **not** be able to modify any other files given to you.

### To submit lab 3

upload a ZIP file containing `client.py` to [Gradescope](https://www.gradescope.com/courses/281655).
