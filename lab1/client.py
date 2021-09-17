#!/usr/bin/env python3

"""
client holds the lab client.
"""

from dummy_server import *
from crypto import *
import api
import codec
import errors

class Client:
    """The client for the photo-sharing application.

    A client can query a remote server for the list of a user's photos
    as well as the photos themselves.  A client can also add photos on
    behalf of that user.

    A client retains data required to authenticate a user's device
    both to a remote server and to other devices.  To authenticate to
    the remote server, the client presents a username and auth_secret,
    while to authenticate to other devices, the client tags
    updates with an authenticator over the history of all updates.  To
    verify the authenticity of an update, clients check the
    authenticator using a shared symmetric key.
    """
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

        self._public_profile = api.PublicProfile(username)

        self._photos = [] # list of photos in put_photo order
        self._next_photo_id = 0
        self._last_log_number = 0

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
