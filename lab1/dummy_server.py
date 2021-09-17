import secrets 
import codec
import api

class DummyServer:
    """A dummy server.  Useful for testing."""
    def __init__(self, database=None):
        self._files = {}
        self._history = []

        if database is None:
            self._storage = DummyStorage()
        else:
            self._storage = Storage(database)

    def register_user(self, request):
        if not self._storage.check_user_registered(request.username):
            token = secrets.token_hex(64)
            self._storage.add_new_user(request.username, request.auth_secret, token)
            self._storage.log_operation(request.username, request.encoded_log_entry)
            return api.RegisterResponse(None, token)
        else:
            return api.RegisterResponse(api.Errcode.USER_ALREADY_EXISTS, None)

    def login(self, request):
        if (self._storage.check_user_registered(request.username) and
            self._storage.check_auth_secret(request.username, request.auth_secret)):
            token = secrets.token_hex(64)
            self._storage.update_user_token(request.username, token)
            return api.LoginResponse(None, token)
        else:
            return api.LoginResponse(api.Errcode.LOGIN_FAILED, None)
    
    def update_public_profile(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.UpdatePublicProfileResponse(api.Errcode.INVALID_TOKEN)
        self._storage.update_public_profile(request.username, request.public_profile)
        return api.UpdatePublicProfileResponse(None)

    def get_friend_public_profile(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.GetFriendPublicProfileResponse(api.Errcode.INVALID_TOKEN, None)
        public_profile = self._storage.get_friend_public_profile(request.friend_username)
        return api.GetFriendPublicProfileResponse(None, public_profile)
    
    def put_photo_user(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.PutPhotoResponse(api.Errcode.INVALID_TOKEN, None)

        self._storage.store_photo(request.username, request.photo_id, request.photo_blob)
        self._storage.log_operation(request.username, request.encoded_log_entry)
        return api.PutPhotoResponse(None)

    def get_photo_user(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.GetPhotoResponse(api.Errcode.INVALID_TOKEN, None)

        photo = self._storage.load_photo(request.username, request.photo_id)
        if photo != None:
            return api.GetPhotoResponse(None, photo.photo_blob)
        else:
            return api.GetPhotoResponse(api.Errcode.PHOTO_DOES_NOT_EXIST, None)

    def synchronize(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.SynchronizeResponse(api.Errcode.INVALID_TOKEN, None)

        # Check version compatibility
        server_version = self._storage.latest_user_version(request.username)
        if request.min_version_number > server_version+1:
            return api.SynchronizeResponse(api.Errcode.VERSION_TOO_HIGH, None)

        log = self._storage.user_history(request.username, request.min_version_number)
        log = [codec.Encoding(entry) for entry in log]
        return api.SynchronizeResponse(None, log)

class UserData:
    def __init__(self, username, auth_secret, token):
        self.username = username
        self.public_profile = api.PublicProfile(username, {})
        self.auth_secret = auth_secret
        self.token = token
        self.photobase = {}
        self.history = []

class PhotoData:
    def __init__(self, username, photo_id, photo_blob):
        self.username = username
        self.photo_id = photo_id
        self.photo_blob = photo_blob

class DummyStorage:
    def __init__(self):
        self.userbase = {}

    def check_user_registered(self, username):
        return (username in self.userbase)

    def check_token(self, username, token):
        return (username in self.userbase) and (self.userbase[username].token == token)

    def add_new_user(self, username, auth_secret, token):
        self.userbase[username] = UserData(username, auth_secret, token)
   
    def update_public_profile(self, username, new_public_profile):
        self.userbase[username].public_profile = new_public_profile

    def get_friend_public_profile(self, friend_username):
        return self.userbase[friend_username].public_profile

    def log_operation(self, username, log_entry):
        self.userbase[username].history.append(log_entry.bytes_data)

    def check_auth_secret(self, username, auth_secret):
        return self.userbase[username].auth_secret == auth_secret

    def update_user_token(self, username, token):
        self.userbase[username].token = token

    def store_photo(self, username, photo_id, photo_blob):
        self.userbase[username].photobase[photo_id] = PhotoData(username, photo_id, photo_blob)

    def load_photo(self, username, photo_id):
        if photo_id in self.userbase[username].photobase:
            return self.userbase[username].photobase[photo_id]
        else:
            return None
   
    def list_user_photos(self, username):
        return list(self.userbase[username].photobase.keys())

    def latest_user_version(self, username):
        # return self.userbase[username].history[-1].tag.version_number
        return len(self.userbase[username].history)-1

    def user_history(self, username, min_version_number):
        return self.userbase[username].history[min_version_number:]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
