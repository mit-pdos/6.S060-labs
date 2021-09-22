#!/usr/bin/env python3

from enum import IntEnum, auto, unique
from typing import List

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

@unique
class OperationCode(IntEnum):
    REGISTER  = auto()
    PUT_PHOTO = auto()

@auto_str
class PublicProfile:
    def __init__(self, username: str, infos: dict={}):
        self.username: str = username
        self.infos: dict = infos


@auto_str
class RequestError:
    """An error returned by a request, identified with an error code and extra information."""
    def __init__(self, error_code: Errcode, info: any) -> None:
        self.error_code = int(error_code)
        self.info = info

@auto_str
class Request:
    def __init__(self, username: str, token: bytes) -> None:
        self.username = username
        self.token = token

@auto_str
class PushRequest(Request):
    def __init__(self, username: str, token: str, encoded_log_entry: codec.Encoding) -> None:
        if type(encoded_log_entry) is not codec.Encoding:
            raise TypeError("encoded_log_entry must be Encoding")
        Request.__init__(self, username, token)
        self.encoded_log_entry = encoded_log_entry

@auto_str
class RegisterRequest():
    def __init__(self, username: str, auth_secret: bytes, encoded_log_entry: codec.Encoding) -> None:
        if type(encoded_log_entry) is not codec.Encoding:
            raise TypeError("encoded_log_entry must be Encoding")
        self.username = username
        self.auth_secret = auth_secret
        self.encoded_log_entry = encoded_log_entry

@auto_str
class RegisterResponse:
    """The register response is composed of an error code (indicating if the registration was successful and a session token"""
    def __init__(self, error: Errcode, token: str) -> None:
        self.token: str = token
        self.error: Errcode = error

@auto_str
class LoginRequest:
    def __init__(self, username: str, auth_secret: bytes):
        self.username: str = username
        self.auth_secret: bytes = auth_secret

@auto_str
class LoginResponse:
    """The login response is composed of an error code (indicating if the registration was successful and a session token"""
    def __init__(self, error: Errcode, token: str):
        self.token: str = token
        self.error: Errcode = error

@auto_str
class UpdatePublicProfileRequest(Request):
    def __init__(self, username: str, token: str, public_profile: PublicProfile) -> None:
        super().__init__(username, token)
        self.public_profile: PublicProfile = public_profile

@auto_str
class UpdatePublicProfileResponse():
    def __init__(self, error: Errcode) -> None:
        self.error: Errcode = error

@auto_str
class GetFriendPublicProfileRequest(Request):
    def __init__(self, username: str, token: str, friend_username: str) -> None:
        super().__init__(username, token)
        self.friend_username: str = friend_username

@auto_str
class GetFriendPublicProfileResponse():
    def __init__(self, error, public_profile) -> None:
        self.error: Errcode = error
        self.public_profile: PublicProfile = public_profile


@auto_str
class PutPhotoRequest(PushRequest):
    def __init__(self, 
        username: str,
        token: str,
        photo_blob: bytes,
        photo_id: int,
        encoded_log_entry: codec.Encoding
    ) -> None:
        super().__init__(username, token, encoded_log_entry)
        self.photo_blob: bytes = photo_blob
        self.photo_id: int = photo_id

@auto_str
class PutPhotoResponse:
    def __init__(self, error: Errcode) -> None:
        self.error: Errcode = error

@auto_str
class GetPhotoRequest(Request):
    def __init__(self, username: str, token: str, photo_id: int) -> None:
        super().__init__(username, token)
        self.photo_id: int = photo_id

@auto_str
class GetPhotoResponse:
    def __init__(self, error: Errcode, photo_blob: bytes) -> None:
        self.error: Errcode = error
        self.photo_blob: bytes = photo_blob

@auto_str
class SynchronizeRequest(Request):
    def __init__(self, username: str, token: str, min_version_number: int) -> None:
        super().__init__(username, token)
        self.min_version_number: int = min_version_number

@auto_str
class SynchronizeResponse():
    def __init__(self, error: Errcode, encoded_log_entries: List[codec.Encoding]):
        self.error: Errcode = error
        self.encoded_log_entries: List[codec.Encoding] = encoded_log_entries
