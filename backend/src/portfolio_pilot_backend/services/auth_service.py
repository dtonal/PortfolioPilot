from abc import ABC, abstractmethod
from portfolio_pilot_backend.models import User

class IAuthService(ABC):
    @abstractmethod
    def authenticate(self, user: User, password_hash: str) -> bool:
        pass

    @abstractmethod
    def hash_password(self, param: str) -> str:
        pass

class AuthService(IAuthService):
    def hash_password(self, param: str) -> str:
        return param

    def authenticate(self, user, password_hash: str) -> bool:
        return user.password_hash == password_hash

