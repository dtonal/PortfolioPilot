from sqlalchemy.orm import Session

from auth_service import IAuthService
from portfolio_pilot_backend.repositories.user_repository import UserRepository, UserRepositoryFactory
from portfolio_pilot_backend.models import User

class UserService:
    def __init__(self, user_repository_factory: UserRepositoryFactory, auth_service: IAuthService):
        self.user_repository_factory = user_repository_factory
        self.auth_service = auth_service

    def create_user_repository(self, session:Session) -> UserRepository:
        return self.user_repository_factory.create(session)

    def get_user_by_id(self, session: Session, user_id: int) -> User | None:
        user_repository = self.create_user_repository(session)
        return user_repository.get_by_id(user_id)

    def get_user_by_username(self, session: Session, username: str) -> User | None:
        user_repository = self.create_user_repository(session)
        return user_repository.get_by_username(username)

    def get_user_by_email(self, session: Session, email: str) -> User | None:
        user_repository = self.create_user_repository(session)
        return user_repository.get_by_email(email)

    def get_all_users(self, session: Session) -> list[User]:
        user_repository = self.create_user_repository(session)
        return user_repository.list_all()

    def validate_user_data(self, username: str, email: str, password_hash: str) -> str | None:
        if username is None:
            return  "Benutzername muss angegeben werden."
        if email is None:
            return  "E-Mail muss angegeben werden."
        if password_hash is None:
            return  "Password muss angegeben werden."
        return None

    def create_new_user(self, session: Session, username: str, email: str, password_hash: str) -> tuple[User | None, str | None]:
        validation_msg = self.validate_user_data(username, email, password_hash)
        if validation_msg:
            return None, validation_msg

        user_repository = self.create_user_repository(session)


        # Validierungen (Eindeutigkeit etc.)
        if user_repository.get_by_username(username):
            return None, "Benutzername bereits vergeben."
        if user_repository.get_by_email(email):
            return None, "E-Mail bereits registriert."


        new_user = User(username=username, email=email, password_hash=password_hash)
        try:
            created_user = user_repository.create(new_user)
            session.commit()
            return created_user, None
        except Exception as e:
            session.rollback()
            return None, f"Fehler beim Erstellen des Benutzers: {e}"

    def update_user(self, session: Session, user_id: int, username: str | None = None, email: str | None = None, password_hash: str | None = None) -> tuple[User | None, str | None]:
        user_repository = self.create_user_repository(session)
        user = user_repository.get_by_id(user_id)
        if not user:
            return None, "Benutzer nicht gefunden."

        if username and username != user.username and user_repository.get_by_username(username):
            return None, "Benutzername bereits vergeben."
        if email and email != user.email and user_repository.get_by_email(email):
            return None, "E-Mail bereits registriert."

        if username:
            user.username = username
        if email:
            user.email = email
        # Das gehashte Passwort wird direkt gesetzt
        if password_hash:
            user.password_hash = password_hash

        try:
            updated_user = user_repository.update(user)
            session.commit()
            return updated_user, None
        except Exception as e:
            session.rollback()
            return None, f"Fehler beim Aktualisieren des Benutzers: {e}"

    def delete_user(self, session: Session, user_id: int) -> bool:
        user_repository = self.create_user_repository(session)
        user = user_repository.get_by_id(user_id)
        if user:
            user_repository.delete(user)
            session.commit()
            return True
        return False

    def authenticate_user(self, session: Session, username: str, password_hash_from_frontend: str) -> User | None:
        user_repository = self.create_user_repository(session)
        user = user_repository.get_by_username(username)
        if user and self.auth_service.authenticate(user, password_hash_from_frontend):
            return user
        return None