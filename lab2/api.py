#!/usr/bin/env python3

from enum import IntEnum, auto, unique

import codec
from util import auto_str

"""
A common API between the client and the server.
"""

@unique
class Errcode(IntEnum):
    UNKNOWN = auto()
    USER_ALREADY_EXISTS = auto()
    LOGIN_FAILED = auto()
    INVALID_TOKEN = auto()
    VERSION_TOO_LOW = auto()
    VERSION_TOO_HIGH = auto()
    PHOTO_DOES_NOT_EXIST = auto()
    CONTACT_BOOK_DOES_NOT_EXIST = auto()

@unique
class OperationCode(IntEnum):
    REGISTER  = auto()
    PUT_PHOTO = auto()

@auto_str
class PublicProfile:
    def __init__(self, username, infos={}):
        self.username = username
        self.infos = infos

class ContactBook:
    """A set of contacts belonging to a given user.

    A ContactBook maps usernames to public keys.  It may also contain
    additional authenticating metadata.
    """
    def __init__(self, book_metadata=None):
        if book_metadata is not None and type(book_metadata) is not codec.Encoding:
            raise TypeError("book_metadata must be Encoding")
        self._mapping = {}
        self._metadata = book_metadata

    def add_contact(self, username, public_key, contact_metadata=None):
        if contact_metadata is not None and type(contact_metadata) is not codec.Encoding:
            raise TypeError("contact_metadata must be Encoding")
        self._mapping[username] = (public_key, contact_metadata)

    def keys(self):
        return self._mapping

    def metadata(self):
        return self._metadata

@auto_str
class RequestError:
    """An error returned by a request, identified with an error code and extra information."""
    def __init__(self, error_code, info):
        self.error_code = int(error_code)
        self.info = info

@auto_str
class Request:
    def __init__(self, username, token):
        self.username = username
        self.token = token

@auto_str
class PushRequest(Request):
    def __init__(self, username, token, encoded_log_entry):
        if type(encoded_log_entry) is not codec.Encoding:
            raise TypeError("encoded_log_entry must be Encoding")
        Request.__init__(self, username, token)
        self.encoded_log_entry = encoded_log_entry

@auto_str
class RegisterRequest():
    def __init__(self, username, auth_secret, encoded_log_entry):
        if type(encoded_log_entry) is not codec.Encoding:
            raise TypeError("encoded_log_entry must be Encoding")
        self.username = username
        self.auth_secret = auth_secret
        self.encoded_log_entry = encoded_log_entry

@auto_str
class RegisterResponse:
    """The register response is composed of an error code (indicating if the registration was successful and a session token"""
    def __init__(self, error, token):
        self.token = token
        self.error = error

@auto_str
class LoginRequest:
    def __init__(self, username, auth_secret):
        self.username = username
        self.auth_secret = auth_secret

@auto_str
class LoginResponse:
    """The login response is composed of an error code (indicating if the registration was successful and a session token"""
    def __init__(self, error, token):
        self.token = token
        self.error = error

@auto_str
class UpdatePublicProfileRequest(Request):
    def __init__(self, username, token, public_profile):
        super().__init__(username, token)
        self.public_profile = public_profile

@auto_str
class UpdatePublicProfileResponse():
    def __init__(self, error):
        self.error = error

@auto_str
class GetFriendPublicProfileRequest(Request):
    def __init__(self, username, token, friend_username):
        super().__init__(username, token)
        self.friend_username = friend_username

@auto_str
class GetFriendPublicProfileResponse():
    def __init__(self, error, public_profile):
        self.error = error
        self.public_profile = public_profile

@auto_str
class UploadContactBookRequest(Request):
    """Ask the server to replace the user's currect ContactBook with a
    new one."""
    def __init__(self, username, token, contact_book):
        if type(contact_book) is not ContactBook:
            raise TypeError("contact_book must be ContactBook")
        super().__init__(username, token)
        self.contact_book = contact_book

@auto_str
class UploadContactBookResponse():
    def __init__(self, error):
        self.error = error

@auto_str
class GetContactBookRequest():
    """Get a user's ContactBook."""
    def __init__(self, username):
        self.username = username

@auto_str
class GetContactBookResponse():
    def __init__(self, error, book):
        self.error = error
        self.book = book

@auto_str
class GetTrustLinkRequest():
    """Try to get a path of TrustLinks from one user to another.

    A correctly-functioning server is guaranteed to give a path if one
    exists.
    """
    def __init__(self, username, other_username):
        self.username = username
        self.other_username = other_username

@auto_str
class TrustLink:
    """A single edge in a path within a GetTrustLinkResponse.

    In a TrustLink, the user_src trusts that user_dest holds
    public_key.

    A TrustLink may also hold additional authenticating metadata (in
    the form of the Encoding given to an uploaded contact book).
    """
    def __init__(self, user_src, user_dest, pub_key, metadata):
        self.user_src = user_src
        self.user_dest = user_dest
        self.public_key = pub_key
        self.metadata = metadata

    # for debugging
    def __repr__(self):
        return str(self)

@auto_str
class GetTrustLinkResponse():
    def __init__(self, error, path):
        self.error = error
        self.path = path

@auto_str
class PutPhotoRequest(PushRequest):
    def __init__(self, username, token, photo_blob, photo_id, encoded_log_entry):
        super().__init__(username, token, encoded_log_entry)
        self.photo_blob = photo_blob
        self.photo_id = photo_id

@auto_str
class PutPhotoResponse:
    def __init__(self, error):
        self.error = error

@auto_str
class GetPhotoRequest(Request):
    def __init__(self, username, token, photo_id):
        super().__init__(username, token)
        self.photo_id = photo_id

@auto_str
class GetPhotoResponse:
    def __init__(self, error, photo_blob):
        self.error = error
        self.photo_blob = photo_blob

@auto_str
class SynchronizeRequest(Request):
    def __init__(self, username, token, min_version_number):
        super().__init__(username, token)
        self.min_version_number = min_version_number

@auto_str
class SynchronizeResponse():
    def __init__(self, error, encoded_log_entries):
        self.error = error
        self.encoded_log_entries = encoded_log_entries
