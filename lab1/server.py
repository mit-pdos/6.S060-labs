from abc import ABC, abstractmethod
import api

class Server(ABC):
    """
    The interface for any server.
    """
    @abstractmethod
    def __init__(self, database=None) -> None:
        ...

    @abstractmethod
    def register_user(self, request: api.RegisterRequest) -> api.RegisterResponse:
        ...

    @abstractmethod
    def login(self, request: api.LoginRequest) -> api.LoginResponse:
        ...
    
    @abstractmethod
    def update_public_profile(self, request: api.UpdatePublicProfileRequest) -> api.UpdatePublicProfileResponse:
        ...

    @abstractmethod
    def get_friend_public_profile(self, request: api.GetFriendPublicProfileRequest) -> api.GetFriendPublicProfileResponse:
        ...
    
    @abstractmethod
    def put_photo_user(self, request: api.PutPhotoRequest) -> api.PutPhotoResponse:
        ...

    @abstractmethod
    def get_photo_user(self, request: api.GetPhotoRequest) -> api.GetPhotoResponse:
        ...

    @abstractmethod
    def synchronize(self, request: api.SynchronizeRequest) -> api.SynchronizeResponse:
        ...
