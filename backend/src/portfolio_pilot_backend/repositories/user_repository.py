from sqlalchemy.orm import Session
from portfolio_pilot_backend.models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def update(self, user: User) -> User:
        self.session.merge(user)
        self.session.flush()
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()

    def list_all(self) -> list[User]:
        return self.session.query(User).all()

class UserRepositoryFactory():
    def create(self, session) -> UserRepository:
        return UserRepository(session)