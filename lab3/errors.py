#!/usr/bin/env python3

"""
errors contains a list of errors the client may report.
"""

class UserAlreadyExistsError(Exception):
    def __init__(self, username):
        self.username = username
    def __str__(self):
        return "{} already exists".format(self.username)

class LoginFailedError(Exception):
    def __init__(self, username):
        self.username = username
    def __str__(self):
        return "failed to log {} in".format(self.username)

class InvalidTokenError(Exception):
    def __str__(self):
        return "please login again: invalid API token provided"

class VersionTooHighError(Exception):
    def __str__(self):
        return "server is behind: client version higher than server's"

class VersionTooLowError(Exception):
    def __str__(self):
        return "please retry: client version lower than server's"

class InvalidAuthenticatorError(Exception):
    def __str__(self):
        return "could not validate authenticator"

class InvalidTrustLinkError(Exception):
    def __str__(self):
        return "could not validate trust link"

class InvalidHashError(Exception):
    def __str__(self):
        return "could not validate hash"

class InvalidOperationError(Exception):
    def __init__(self, version, code):
        self.version = version
        self.code = code
    def __str__(self):
        return "invalid operation code at version {}: {}".format(
            self.version, self.code
        )

class VersionMismatchError(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    def __str__(self):
        return "expected update version ({}) does not match received version ({})".format(
            expected, received
        )

class MissingRegistrationError(Exception):
    def __str__(self):
        return "server did not return valid registration"

class MalformedEncodingError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "provided encoding was malformed: {}".format(self.msg)

class SynchronizationError(Exception):
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return "synchronization failed: {}".format(self.error)

class PhotoDoesNotExistError(Exception):
    def __init__(self, photo_id):
        self.photo_id = photo_id
    def __str__(self):
        return "photo with ID {} does not exist".format(self.photo_id)

class InvalidPublicProfile(Exception):
    def __init__(self, name_friend):
        self.name_friend = name_friend
    def __str__(self):
        return "No valid public profile could be recovered for {}".format(self.name_friend)

class AlbumOwnerError(Exception):
    def __init__(self, name_album):
        self.name_album = name_album
    def __str__(self):
        return "Only the owner of {} can change the sharing preference".format(self.name_album) 

class AlbumPermissionError(Exception):
    def __init__(self, name_album):
        self.name_album = name_album
    def __str__(self):
        return "You don't have the permissions to access the album {}".format(self.name_album)

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
