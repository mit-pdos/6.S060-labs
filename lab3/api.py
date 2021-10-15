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
    ALBUM_DOES_NOT_EXIST = auto()

@unique
class OperationCode(IntEnum):
    REGISTER  = auto()
    PUT_PHOTO = auto()


@auto_str
class PhotoAlbum:
    def __init__(self, name, photos, owner, friends, metadata=None):
        self.name = name
        self.photos = photos
        self.owner = owner
        self.friends = friends
        try:
            encoder = codec.Encoding()
            encoder.add_obj(metadata)
        except TypeError:
            raise TypeError("Album's metadata should be encodable")
        self.metadata = metadata
    
    def add_photo(self, photo):
        self.photos.append(photo)

    def add_friend(self, friend):
        self.friends[friend.username] = friend

    def remove_friend(self, name_friend):
        del self.friends[name_friend]

    def is_owner(self, username):
        return username == self.owner

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

@auto_str
class UploadAlbumRequest(Request):
    def __init__(self, username, token, album):
        super().__init__(username, token)
        self.album = album

@auto_str
class UploadAlbumResponse():
    def __init__(self, error):
        self.error = error

@auto_str
class GetAlbumRequest(Request):
    def __init__(self, username, token, name_album):
        super().__init__(username, token)
        self.name_album = name_album

@auto_str
class GetAlbumResponse():
    def __init__(self, error, album):
        self.error = error
        self.album = album
