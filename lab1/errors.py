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

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
