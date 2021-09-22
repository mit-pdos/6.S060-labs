import secrets 
import api
from util import trace, auto_str

class Lab1Server:
    """The server for the lab 1 autograder."""
    def __init__(self, attack=None, database=None):
        self.attack = attack

        if database is None:
            self._storage = DummyStorage()
        else:
            self._storage = Storage(database)

    @trace
    def register_user(self, request):
        if not self._storage.check_user_registered(request.username):
            token = secrets.token_hex(64)
            self._storage.add_new_user(request.username, request.auth_secret, token)
            self._storage.log_operation(request.username, request.encoded_log_entry)
            return api.RegisterResponse(None, token)
        elif self._storage.check_user_registered(request.username) and self.attack == "double_register_1":
            self._storage.log_operation(request.username, request.encoded_log_entry)
            return api.RegisterResponse(api.Errcode.USER_ALREADY_EXISTS, None)
        elif self._storage.check_user_registered(request.username) and self.attack == "double_register_2":
            self._storage.log_operation(request.username, request.encoded_log_entry)
            token = secrets.token_hex(64)
            return api.RegisterResponse(None, token)
        elif self._storage.check_user_registered(request.username) and self.attack == "version_number_1":
            token = self._storage.get_user_token(request.username)
            return api.RegisterResponse(None, token)
        else:
            return api.RegisterResponse(api.Errcode.USER_ALREADY_EXISTS, None)

    @trace
    def login(self, request):
        if (self._storage.check_user_registered(request.username) and
            self._storage.check_auth_secret(request.username, request.auth_secret)):
            token = secrets.token_hex(64)
            self._storage.update_user_token(request.username, token)
            return api.LoginResponse(None, token)
        else:
            return api.LoginResponse(api.Errcode.LOGIN_FAILED, None)

    @trace
    def put_photo_user(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.PutPhotoResponse(api.Errcode.INVALID_TOKEN, None)

        # # Check version compatibility
        # # TODO REMOVED (derek): client is trusted to give correct info
        # server_version = self._storage.latest_user_version(request.username)
        # new_client_version = request.metadata.tag.version_number
        # if server_version+1 < new_client_version:
        #     return api.PutPhotoResponse(api.Errcode.VERSION_TOO_HIGH)
        # if server_version+1 > new_client_version:
        #     return api.PutPhotoResponse(api.Errcode.VERSION_TOO_LOW)

        else:
            self._storage.store_photo(request.username, request.photo_id, request.photo_blob)
        if self.attack == "change_photo_order_1" and request.photo_id == 2:
            self._storage.swap_photo_blobs(request.username, 1, 2)
        
        if self.attack == "replay_attack_1" and request.photo_id == 1:
            self._storage.log_operation(request.username, request.encoded_log_entry)
            self._storage.log_operation(request.username, request.encoded_log_entry)
        elif self.attack == "version_number_2" and request.photo_id == 2:
            log_entry = request.encoded_log_entry
            # Modify all potential version_numbers in the log_entry
            for i, item in enumerate(log_entry.data):
                if type(item) == int and item == 3:
                    log_entry.data[i] = 2
            self._storage.log_operation(request.username, log_entry)
        elif self.attack == "change_photo_id_1" and request.photo_id == 3:
            log_entry = request.encoded_log_entry
            # modify all potential photo_ids in log_entry
            for i, item in enumerate(log_entry.data):
                if type(item) == int and item == 3:
                    log_entry.data[i] = 2
            self._storage.log_operation(request.username, log_entry)
        elif self.attack == "change_photo_id_2" and request.photo_id == 3:
            log_entry = request.encoded_log_entry
            # modify all potential photo_ids in log_entry
            for i, item in enumerate(log_entry.data):
                if type(item) == int and item == 3:
                    log_entry.data[i] = 300
            self._storage.log_operation(request.username, log_entry)
        else:
            index = self._storage.log_operation(request.username, request.encoded_log_entry)
            self._storage._map_log(request.username, request.photo_id, index)
        return api.PutPhotoResponse(None)

    @trace
    def get_photo_user(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.GetPhotoResponse(api.Errcode.INVALID_TOKEN, None)

        photo = self._storage.load_photo(request.username, request.photo_id)
        #if self.attack == "change_photo_blob_1" and request.photo_id == 1 and photo == 'photo2':
        if self.attack == "change_photo_blob_1" and request.photo_id == 1:
            photo.photo_blob = b'photO2'
        
        if photo != None:
            return api.GetPhotoResponse(None, photo.photo_blob)
        else:
            return api.GetPhotoResponse(api.Errcode.PHOTO_DOES_NOT_EXIST, None)

    @trace
    def synchronize(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.SynchronizeResponse(api.Errcode.INVALID_TOKEN, None)

        # Check version compatibility
        server_version = self._storage.latest_user_version(request.username)

        if self.attack == "version_number_1" and request.min_version_number > 0:
            return api.SynchronizeResponse(None, [])

        # TODO delete because client is trusted?
        #if request.min_version_number > server_version+1:
        #    return api.SynchronizeResponse(api.Errcode.VERSION_TOO_HIGH, None)

        log = self._storage.user_history(request.username, request.min_version_number)
        return api.SynchronizeResponse(None, log)

@auto_str
class UserData:
    def __init__(self, username, auth_secret, token, photobase=None, history=None):
        self.username = username
        self.auth_secret = auth_secret
        self.token = token

        if photobase is None:
            photobase = {}
        if history is None:
            history = []
        self.photobase = photobase
        self.history = history

    # defined to help with debugging
    def __repr__(self):
        return self.__str__()

@auto_str
class PhotoData:
    def __init__(self, username, photo_id, photo_blob):
        self.username = username
        self.photo_id = photo_id
        self.photo_blob = photo_blob

    # defined to help with debugging
    def __repr__(self):
        return self.__str__()

class DummyStorage:
    def __init__(self):
        self.userbase = {}
        self.log_index_to_photo_id = {}
        self.photo_id_to_log_index = {}

    def check_user_registered(self, username):
        return (username in self.userbase)

    def check_token(self, username, token):
        return (username in self.userbase) and (self.userbase[username].token == token)

    def add_new_user(self, username, auth_secret, token):
        self.userbase[username] = UserData(username, auth_secret, token)
    
    def log_operation(self, username, log_entry):
        index = len(self.userbase[username].history)
        self.userbase[username].history.append(log_entry)
        return index

    def check_auth_secret(self, username, auth_secret):
        return self.userbase[username].auth_secret == auth_secret

    def update_user_token(self, username, token):
        self.userbase[username].token = token

    def get_user_token(self, username):
        return self.userbase[username].token

    def store_photo(self, username, photo_id, photo_blob):
        self.userbase[username].photobase[photo_id] = PhotoData(username, photo_id, photo_blob)

    def swap_photo_blobs(self, username, pid0, pid1):
        photo_blob0 = self.userbase[username].photobase[pid0].photo_blob
        photo_blob1 = self.userbase[username].photobase[pid1].photo_blob
        self.userbase[username].photobase[pid0] = PhotoData(username, pid0, photo_blob1)
        self.userbase[username].photobase[pid1] = PhotoData(username, pid1, photo_blob0)
    
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

    def _map_log(self, username, log_index, photo_id):
        self.log_index_to_photo_id[(username, log_index)] = photo_id
        self.photo_id_to_log_index[(username, photo_id)] = log_index

if __name__ == "__main__":
    import doctest
    doctest.testmod()
