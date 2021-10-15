#!/usr/bin/env python3

from dummy_server import *
from crypto import *
import api
import codec
import errors

class ImpoliteClient:
    """An impolite client that doesn't check before writing!"""
    def __init__(self, username, remote, user_secret=None):
        """Initialize a client given a username, a
        remote server, and a user secret.

        If no user secret is provided, this constructor generates a
        new one.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice1 = Client("alice", server, alice.user_secret)
        """
        self._remote = remote

        self._username = username
        self._server_session_token = None

        self._user_secret = UserSecret(user_secret)

        self._auth_secret = self._user_secret.get_auth_secret()
        self._symmetric_auth = MessageAuthenticationCode(self._user_secret.get_symmetric_key())

        # OLD VERSION FROM LAB < 3
        #self._public_profile = PublicProfile(username)
        
        self._public_key_signer = PublicKeySignature(self._user_secret.get_signing_secret_key())

        self._public_key_encrypt_and_auth = PublicKeyEncryptionAndAuthentication(self._user_secret.get_encrypt_and_auth_secret_key())
        self._public_profile = PublicProfile(username, infos={"encrypt_and_auth_public_key":self.encrypt_and_auth_public_key})
        self._sign_public_profile()
        self._photos = [] # list of photos in put_photo order
        self._next_photo_id = 0
        self._last_log_number = 0
        self._albums = {}


    @property
    def username(self):
        """Get the client's username.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.username == "alice"
        True
        """
        return self._username

    @property
    def user_secret(self):
        """Get the client's user secret.

        >>> server = DummyServer()
        >>> user_secret = UserSecret().get_secret()
        >>> alice = Client("alice", server, user_secret)
        >>> alice.user_secret == user_secret
        True
        """
        return self._user_secret.get_secret()

    @property
    def signing_public_key(self):
        """Get the client's public key.

        >>> server = DummyServer()
        >>> secret = UserSecret()
        >>> pubkey = secret.get_signing_public_key()
        >>> alice = Client("alice", server, secret.get_secret())
        >>> alice.signing_public_key == bytes(pubkey)
        True
        """
        return bytes(self._user_secret.get_signing_public_key())

    @property
    def encrypt_and_auth_public_key(self):
        """Get the client's public key.

        >>> server = DummyServer()
        >>> secret = UserSecret()
        >>> pubkey = secret.get_encrypt_and_auth_public_key()
        >>> alice = Client("alice", server, secret.get_secret())
        >>> alice.encrypt_and_auth_public_key == bytes(pubkey)
        True
        """
        return bytes(self._user_secret.get_encrypt_and_auth_public_key())

    @property
    def public_profile(self):
        return self._public_profile

    def register(self):
        """Register this client's username with the server,
        initializing the user's state on the server.

        If the client is already registered, raise a
        UserAlreadyExistsError.

        Otherwise, save the session token returned by the server for
        use in future requests.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)

        >>> alice.login()
        Traceback (most recent call last):
                ...
        errors.LoginFailedError: failed to log alice in

        >>> alice.register()
        >>> alice.login()

        >>> alice.register()
        Traceback (most recent call last):
                ...
        errors.UserAlreadyExistsError: alice already exists
        >>> alice.login()

        >>> alice2 = Client("alice", server, alice.user_secret)
        >>> alice2.login()
        >>> alice2.register()
        Traceback (most recent call last):
                ...
        errors.UserAlreadyExistsError: alice already exists

        >>> bob = Client("bob", server)
        >>> bob.login()
        Traceback (most recent call last):
                ...
        errors.LoginFailedError: failed to log bob in
        """
        log = LogEntry(api.OperationCode.REGISTER, 0)
        req  = api.RegisterRequest(self._username, self._auth_secret, encode_log_entry(codec.Encoding(), log))
        resp = self._remote.register_user(req)
        if resp.error is None:
            self._last_log_number += 1
            self._server_session_token = resp.token
        elif resp.error == api.Errcode.USER_ALREADY_EXISTS:
            raise errors.UserAlreadyExistsError(self._username)
        else:
            raise Exception(resp)
        self._upload_public_profile()

    # TODO login for multiple devices
    def login(self):
        """Try to login with to the server with the username and
        auth_secret.

        On success, save the new session token returned by the server
        for use in future requests.

        Otherwise, if the username and auth_secret combination is
        incorrect, raise a LoginFailedError.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)

        >>> alice.login()
        Traceback (most recent call last):
                ...
        errors.LoginFailedError: failed to log alice in

        >>> alice.register()
        >>> alice.login()

        >>> alice.login()

        >>> not_alice = Client("alice", server)
        >>> not_alice.login()
        Traceback (most recent call last):
                ...
        errors.LoginFailedError: failed to log alice in

        See also: register(self)
        """
        req  = api.LoginRequest(self._username, self._auth_secret)
        resp = self._remote.login(req)
        if resp.error is None:
            self._server_session_token = resp.token
        elif resp.error == api.Errcode.LOGIN_FAILED:
            raise errors.LoginFailedError(self._username)
        else:
            raise Exception(resp)

    def _sign_public_profile(self):
        encoding = self._public_profile.encode()
        signature = self._public_key_signer.sign(encoding)
        self._public_profile.add_metadata(signature)

    def update_public_profile_infos(self, infos):
        """Update user public profile with the given fields.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> public_prof = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        >>> alice.update_public_profile_infos(public_prof)
        """
        self._public_profile.infos.update(infos)
        self._sign_public_profile()
        self._upload_public_profile()

    def _upload_public_profile(self):
        """Uploads user public profile.
        """
        req = api.UpdatePublicProfileRequest(self._username, self._server_session_token, self._public_profile)
        resp = self._remote.update_public_profile(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error is not None:
            raise Exception(resp)

    def get_friend_public_profile(self, friend_username, friend_public_key=None):
        """Obtain the public profile of another user.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> alice_s_pk = alice.signing_public_key
        >>> infos = {'bio': 'I like computer security and cryptography', 'location': 'MIT', 'camera': 'mobile phone'}
        >>> alice.update_public_profile_infos(infos)
        >>> bob = Client("bob", server)
        >>> bob.register()
        >>> bob.get_friend_public_profile("alice", alice_s_pk).infos.items() >= infos.items()
        True
        """
        req = api.GetFriendPublicProfileRequest(self._username, self._server_session_token, friend_username)
        resp = self._remote.get_friend_public_profile(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error is not None:
            raise Exception(resp)
        if friend_public_key==None :
            friend_public_key = self.get_trusted_user_public_key(friend_username)
        if not resp.public_profile.verify(friend_public_key):
            raise errors.InvalidPublicProfile(friend_username)
        return resp.public_profile



    def list_photos(self):
        """Fetch a list containing the photo id of each photo stored
        by the user.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> photo_blob = b'PHOTOOO'
        >>> alice.put_photo(photo_blob)
        0
        >>> photo_blob = b'PHOOOTO'
        >>> alice.put_photo(photo_blob)
        1
        >>> photo_blob = b'PHOOT0O'
        >>> alice.put_photo(photo_blob)
        2
        >>> alice.list_photos()
        [0, 1, 2]
        """
        self._synchronize()

        return list(range(self._next_photo_id))

    def get_photo(self, photo_id):
        """Get a photo by ID.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> photo_blob = b'PHOTOOO'
        >>> photo_id = alice.put_photo(photo_blob)
        >>> photo_id
        0
        >>> alice._fetch_photo(photo_id)
        b'PHOTOOO'
        >>> alice._fetch_photo(1)
        Traceback (most recent call last):
                ...
        errors.PhotoDoesNotExistError: photo with ID 1 does not exist
        """
        self._synchronize()

        if photo_id < 0 or photo_id >= len(self._photos):
            raise errors.PhotoDoesNotExistError(photo_id)
        return self._photos[photo_id]

    def _fetch_photo(self, photo_id):
        """Get a photo from the server using the unique PhotoID
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> photo_blob = b'PHOTOOO'
        >>> photo_id = alice.put_photo(photo_blob)
        >>> photo_id
        0
        >>> alice._fetch_photo(photo_id)
        b'PHOTOOO'
        >>> alice._fetch_photo(1)
        Traceback (most recent call last):
                ...
        errors.PhotoDoesNotExistError: photo with ID 1 does not exist
        """
        req = api.GetPhotoRequest(self._username, self._server_session_token, photo_id)
        resp = self._remote.get_photo_user(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error == api.Errcode.PHOTO_DOES_NOT_EXIST:
            raise errors.PhotoDoesNotExistError(photo_id)
        elif resp.error is not None:
            raise Exception(resp)
        return resp.photo_blob

    def put_photo(self, photo_blob):
        """Append a photo_blob to the server's database.

        On success, this returns the unique photo_id associated with
        the newly-added photo.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> photo_blob = b'PHOTOOO'
        >>> alice.put_photo(photo_blob)
        0
        >>> photo_blob = b'PHOOOTO'
        >>> alice.put_photo(photo_blob)
        1
        >>> photo_blob = b'PHOOT0O'
        >>> alice.put_photo(photo_blob)
        2
        """
        self._synchronize()

        photo_id = self._next_photo_id

        log = LogEntry(api.OperationCode.PUT_PHOTO, photo_id)
        req = api.PutPhotoRequest(self._username, self._server_session_token, photo_blob, photo_id, encode_log_entry(codec.Encoding(), log))

        resp = self._remote.put_photo_user(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error is not None:
            raise Exception(resp)

        self._record_new_photo(photo_blob)
        return photo_id

    def _record_new_photo(self, photo_blob):
        """A convenience method to add a new photo to client records
        under a tag."""
        self._next_photo_id += 1
        self._photos.append(photo_blob)
        self._last_log_number += 1

    def _synchronize(self):
        """Synchronize the client's state against the server.

        On failure, this raises a SynchronizationError.

        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> alice.register()
        >>> user_secret = alice.user_secret
        >>> alicebis = Client("alice", server, user_secret)
        >>> alicebis.login()
        >>> alicebis._synchronize()
        >>> alice.login()
        >>> photo_blob = b'PHOTOOO'
        >>> alice._synchronize()
        >>> alice.put_photo(photo_blob)
        0
        >>> photo_blob = b'PHOOOTO'
        >>> alice.put_photo(photo_blob)
        1
        >>> alicebis.login()
        >>> photo_blob = b'PHOOT0O'
        >>> alicebis._synchronize()
        >>> photo_blob = b'PHOOT0O'
        >>> alicebis.put_photo(photo_blob)
        2
        """
        req = api.SynchronizeRequest(self._username,
                                     self._server_session_token,
                                     self._last_log_number)
        resp = self._remote.synchronize(req)

        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error == api.Errcode.VERSION_TOO_HIGH:
            raise errors.SynchronizationError(errors.VersionTooHighError())
        elif resp.error is not None:
            raise Exception(resp)

        for encoded in resp.encoded_log_entries:
            try:
                log = decode_log_entry(encoded.items())
            except errors.MalformedEncodingError as e:
                raise errors.SynchronizationError(e)
            if log.opcode == api.OperationCode.PUT_PHOTO:
                photo_id = log.photo_id
                photo_blob = self._fetch_photo(photo_id)
                self._record_new_photo(photo_blob)
            else:
                self._last_log_number += 1

        if self._last_log_number == 0:
            raise errors.SynchronizationError(errors.MissingRegistrationError())

        # From here everything has been checked

    def create_shared_album(self, name_album, photos, friends):
        ''' Create a new private album with name name_album photos in photos
        The album will be uploaded to the server.
        The photos should only be accessible to the users listed in friends.
        
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> a_s_pk = alice.signing_public_key
        >>> bob = Client("bob", server)
        >>> b_s_pk = bob.signing_public_key
        >>> alice.register()
        >>> bob.register()
        >>> bob_pp = alice.get_friend_public_profile("bob", b_s_pk)
        >>> photos = []
        >>> photos.append(b'PHTOOOO')
        >>> photos.append(b'PHOTOOO')
        >>> photos.append(b'PHOOTOO')
        >>> photos.append(b'PHOOOTO')
        >>> photos.append(b'PHOOOOT')
        >>> friends = {"bob":bob_pp}
        >>> alice.create_shared_album("my_album", photos, friends)
        '''
        self._albums[name_album] = api.PhotoAlbum(name_album, photos, self._username, friends)
        self._upload_album(name_album)
    
    def _upload_album(self, name_album):
        album = self._albums[name_album]
        req = api.UploadAlbumRequest(self._username, self._server_session_token, album)
        resp = self._remote.upload_album(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        elif resp.error is not None:
            raise Exception(resp)

    def get_album(self, name_album, owner_signing_pk):
        ''' Get an album from the server using its name and the public key of the owner of the album
        If the client is part of the friends given access to the album, it will have access to the photos.
        
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> a_s_pk = alice.signing_public_key
        >>> alice_pp = alice.public_profile
        >>> bob = Client("bob", server)
        >>> b_s_pk = bob.signing_public_key
        >>> alice.register()
        >>> bob.register()
        >>> bob_pp = alice.get_friend_public_profile("bob", b_s_pk)
        >>> photos = []
        >>> photos.append(b'PHTOOOO')
        >>> photos.append(b'PHOTOOO')
        >>> photos.append(b'PHOOTOO')
        >>> photos.append(b'PHOOOTO')
        >>> photos.append(b'PHOOOOT')
        >>> friends = {"alice":alice_pp, "bob":bob_pp}
        >>> alice.create_shared_album("my_album", photos, friends)
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        >>> photos_received == photos
        True
        '''
        req = api.GetAlbumRequest(self._username, self._server_session_token, name_album)
        resp = self._remote.get_album(req)
        if resp.error == api.Errcode.INVALID_TOKEN:
            raise errors.InvalidTokenError()
        if resp.error == api.Errcode.ALBUM_DOES_NOT_EXIST:
            raise errors.AlbumPermissionError(name_album)
        elif resp.error is not None:
            raise Exception(resp)
        # i refuse to check ._.
        # if self._username not in resp.album.friends:
        #     raise errors.AlbumPermissionError(name_album)
        self._albums[name_album] = resp.album
        return resp.album


    def add_friend_to_album(self, name_album, friend_public_profile):
        ''' Add a friend to an existing album with name album_name.
        Only the owner of the album can modify the list of friends.
        
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> a_s_pk = alice.signing_public_key
        >>> bob = Client("bob", server)
        >>> b_s_pk = bob.signing_public_key
        >>> alice.register()
        >>> alice_pp = alice.public_profile
        >>> bob.register()
        >>> bob_pp = alice.get_friend_public_profile("bob", b_s_pk)
        >>> photos = []
        >>> photos.append(b'PHTOOOO')
        >>> photos.append(b'PHOTOOO')
        >>> photos.append(b'PHOOTOO')
        >>> photos.append(b'PHOOOTO')
        >>> photos.append(b'PHOOOOT')
        >>> friends = {"alice":alice_pp}
        >>> alice.create_shared_album("my_album", photos, friends)
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        Traceback (most recent call last):
                ...
        errors.AlbumPermissionError: You don't have the permissions to access the album my_album
        >>> alice.add_friend_to_album("my_album", bob_pp)
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        >>> photos_received == photos
        True
        '''
        # i refuse to check ._.
        # if not self._albums[name_album].is_owner(self.username):
        #     return errors.AlbumOwnerError(name_album)
        self.get_album(name_album, self.signing_public_key)
        self._albums[name_album].add_friend(friend_public_profile)
        self._upload_album(name_album)

    def remove_friend_from_album(self, name_album, name_friend):
        ''' Add a friend to an existing album with name album_name.
        Only the owner of the album can modify the list of friends.
        
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> a_s_pk = alice.signing_public_key
        >>> bob = Client("bob", server)
        >>> b_s_pk = bob.signing_public_key
        >>> alice.register()
        >>> alice_pp = alice.public_profile
        >>> bob.register()
        >>> bob_pp = alice.get_friend_public_profile("bob", b_s_pk)
        >>> photos = []
        >>> photos.append(b'PHTOOOO')
        >>> photos.append(b'PHOTOOO')
        >>> photos.append(b'PHOOTOO')
        >>> photos.append(b'PHOOOTO')
        >>> photos.append(b'PHOOOOT')
        >>> friends = {"alice":alice_pp, "bob":bob_pp}
        >>> alice.create_shared_album("my_album", photos, friends)
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        >>> photos_received == photos
        True
        >>> alice.remove_friend_from_album("my_album", "bob")
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        Traceback (most recent call last):
                ...
        errors.AlbumPermissionError: You don't have the permissions to access the album my_album
        '''
        # i refuse to check ._.
        # if not self._albums[name_album].is_owner(self.username):
        #     return errors.AlbumOwnerError(name_album)
        self.get_album(name_album, self.signing_public_key)
        self._albums[name_album].remove_friend(name_friend)
        self._upload_album(name_album)

    def add_photo_to_album(self, name_album, photo, owner_signing_pk):
        ''' Add a photo to an existing album with name album_name.
        Only friends of the album can add photos.
        
        >>> server = DummyServer()
        >>> alice = Client("alice", server)
        >>> a_s_pk = alice.signing_public_key
        >>> bob = Client("bob", server)
        >>> b_s_pk = bob.signing_public_key
        >>> bob.register()
        >>> cedric = Client("cedric", server)
        >>> c_s_pk = cedric.signing_public_key
        >>> cedric.register()
        >>> alice.register()
        >>> alice_pp = alice.public_profile
        >>> bob_pp = alice.get_friend_public_profile("bob", b_s_pk)
        >>> cedric_pp = alice.get_friend_public_profile("cedric", c_s_pk)
        >>> photos = []
        >>> photos.append(b'PHTOOOO')
        >>> photos.append(b'PHOTOOO')
        >>> photos.append(b'PHOOTOO')
        >>> photos.append(b'PHOOOTO')
        >>> photos.append(b'PHOOOOT')
        >>> friends = {"alice":alice_pp, "bob":bob_pp, "cedric":cedric_pp}
        >>> alice.create_shared_album("my_album", photos, friends)
        >>> photos_received = bob.get_album("my_album", a_s_pk).photos
        >>> photos_received == photos
        True
        >>> new_photo = b'PHOTOBOB'
        >>> bob.add_photo_to_album("my_album", new_photo, a_s_pk)
        >>> photos_received = cedric.get_album("my_album", a_s_pk).photos
        >>> photos.append(new_photo)
        >>> photos_received == photos
        True
        '''
        self.get_album(name_album, owner_signing_pk)
        self._albums[name_album].add_photo(photo)
        self._upload_album(name_album)

class PublicProfile:
    def __init__(self, username, infos={}):
        self.username = username
        self.infos = infos
        self.metadata = None

    def add_metadata(self, metadata):
        self.metadata = metadata

    def encode(self):
        encoding = codec.Encoding()
        encoding.add_bin(self.username.encode('utf-8'))
        encoding.add_dict(self.infos)
        return encoding

    def verify(self, pk):
        return verify_sign(pk, self.encode(), self.metadata)
class LogEntry:
    def __init__(self, opcode, photo_id):
        self.opcode = opcode
        self.photo_id = photo_id

def encode_log_entry(encoding, log_entry):
    encoding.add_int(log_entry.opcode.value)
    encoding.add_int(log_entry.photo_id)
    return encoding

def decode_log_entry(items_iter):
    items = list(items_iter)
    if len(items) != 2:
        raise errors.MalformedEncodingError("expected 2 items but got {} items".format(len(items)))
    try:
        api.OperationCode(items[0])
    except ValueError:
        raise errors.MalformedEncodingError("item 0 is not valid opcode {}".format(items[0]))
    return LogEntry(api.OperationCode(items[0]), items[1])


if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
