import secrets
import codec
import api
import policy
from collections import defaultdict

class Lab2Server:
    """The server for the lab 2 autograder."""
    def __init__(self, database=None):
        self.name_rewrite = {}
        self.path_rewrite = {}
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

    def upload_contact_book(self, request):
        if not self._storage.check_token(request.username, request.token):
            return api.UploadContactBookResponse(api.Errcode.INVALID_TOKEN)
        contact_book = request.contact_book
        mapping = contact_book.keys()
        for name in mapping:
            info = mapping[name]
            self._storage.add_social_link(request.username, name, info)
        self._storage.set_contact_book(request.username, contact_book)
        return api.UploadContactBookResponse(None)

    def get_contact_book(self, request):
        book = self._storage.get_contact_book(request.username)
        if book is None:
            api.GetContactBookResponse(api.Errcode.CONTACT_BOOK_DOES_NOT_EXIST, None)
        return api.GetContactBookResponse(None, book)

    def get_trust_link(self, request):
        pair = (request.username, request.other_username)
        if pair in self.path_rewrite:
            return api.GetTrustLinkResponse(None, self.path_rewrite[pair])

        links = policy.friendship_policy(self._storage.social_graph, request.username, request.other_username)
        path = []
        for link in links:
            src = link[0]
            dest = link[1]
            if src in self.name_rewrite:
                src = self.name_rewrite[src]
            if dest in self.name_rewrite:
                dest = self.name_rewrite[dest]
            path.append(api.TrustLink(src, dest, link[2][0], codec.Encoding(link[2][1])))
        return api.GetTrustLinkResponse(None, path)

    def set_path_response(self, src, dest, path):
        self.path_rewrite[(src, dest)] = path

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

    def replace_name_raw(self, name1, name2):
        self.name_rewrite[name1] = name2

class UserData:
    def __init__(self, username, auth_secret, token):
        self.username = username
        self.public_profile = api.PublicProfile(username, {})
        self.auth_secret = auth_secret
        self.token = token
        self.photobase = {}
        self.history = []
        self.contact_book = None

class PhotoData:
    def __init__(self, username, photo_id, photo_blob):
        self.username = username
        self.photo_id = photo_id
        self.photo_blob = photo_blob

class DummyStorage:
    def __init__(self):
        self._userbase = {}
        self.social_graph = defaultdict(lambda: defaultdict(list))

    def check_user_registered(self, username):
        return (username in self._userbase)

    def check_token(self, username, token):
        return (username in self._userbase) and (self._userbase[username].token == token)

    def add_new_user(self, username, auth_secret, token):
        self._userbase[username] = UserData(username, auth_secret, token)

    def update_public_profile(self, username, new_public_profile):
        self._userbase[username].public_profile = new_public_profile

    def get_friend_public_profile(self, friend_username):
        return self._userbase[friend_username].public_profile

    def log_operation(self, username, log_entry):
        self._userbase[username].history.append(log_entry.data)

    def check_auth_secret(self, username, auth_secret):
        return self._userbase[username].auth_secret == auth_secret

    def update_user_token(self, username, token):
        self._userbase[username].token = token

    def store_photo(self, username, photo_id, photo_blob):
        self._userbase[username].photobase[photo_id] = PhotoData(username, photo_id, photo_blob)

    def load_photo(self, username, photo_id):
        if photo_id in self._userbase[username].photobase:
            return self._userbase[username].photobase[photo_id]
        else:
            return None

    def list_user_photos(self, username):
        return list(self._userbase[username].photobase.keys())

    def latest_user_version(self, username):
        # return self._userbase[username].history[-1].tag.version_number
        return len(self._userbase[username].history)-1

    def user_history(self, username, min_version_number):
        return self._userbase[username].history[min_version_number:]

    def add_social_link(self, start, end, info):
        if info[1] == None:
            data = None
        else:
            data = info[1].data
        entry = (bytes(info[0]), data)
        edge = [start, end, entry]
        self.social_graph[start][end] = edge

    def replace_public_key_raw(self, username, new_key):
        for start in self.social_graph:
            for end in self.social_graph[start]:
                edge = self.social_graph[start][end]
                if end != username:
                    continue
                edge[2] = (new_key, edge[2][1])
                self.social_graph[start][end] = edge

    def get_contact_book(self, username):
        if username not in self._userbase:
            return None
        if self._userbase[username].contact_book is None:
            return None
        return decode_contact_book(self._userbase[username].contact_book)

    def set_contact_book(self, username, book):
        if username not in self._userbase:
            return False
        self._userbase[username].contact_book = encode_contact_book(book)
        return True

def encode_contact_book(book):
    mappings = []
    keys = book.keys()
    for name in keys:
        pkey = bytes(keys[name][0])
        if keys[name][1] == None: # TODO clean up this switch
            data = None
        else:
            data = keys[name][1].data
        mappings.append((name, pkey, data))
    if book.metadata() is None:
        return (mappings, None)
    return (mappings, book.metadata().data)

def decode_contact_book(pair):
    if pair[1] is None:
        metadata = None
    else:
        metadata = codec.Encoding(pair[1]).items()
    book = api.ContactBook(metadata)
    for record in pair[0]:
        metadata = codec.Encoding(record[2])
        book.add_contact(record[0], record[1], metadata)
    return book

if __name__ == "__main__":
    import doctest
    doctest.testmod()
