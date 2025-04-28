import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient

from UserService import UserService
from AuthService import AuthService
from user_repository import UserRepositoryFactory
from portfolio_pilot_backend.models import Base, User

engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def user_service(session):
    auth_service = AuthService()
    user_repository_factory = UserRepositoryFactory()
    return UserService(user_repository_factory, auth_service)

def test_create_user(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", password_hash="hash", email="<EMAIL>")
    assert added_user.id is not None
    assert added_user.username == "Test"
    assert added_user.email == "<EMAIL>"
    assert msg is None

def test_create_user_same_email_creates_error_msg(user_service, session):
    first_user, msg = user_service.create_new_user(session, email="MEINE_EMAIL", username="Test1", password_hash="hash")
    assert first_user.id is not None
    assert msg is None
    second_user, msg = user_service.create_new_user(session, email="MEINE_EMAIL", username="Test2", password_hash="hash")
    assert second_user is None
    assert msg == "E-Mail bereits registriert."

def test_create_user_same_username_creates_error_msg(user_service, session):
    first_user, msg = user_service.create_new_user(session, email="MEINE_EMAIL1", username="Test1", password_hash="hash")
    assert first_user.id is not None
    assert msg is None
    second_user, msg = user_service.create_new_user(session, email="MEINE_EMAIL2", username="Test1", password_hash="hash")
    assert second_user is None
    assert msg == "Benutzername bereits vergeben."

def test_create_user_without_name_creates_error_msg(user_service, session):
    user_without_name, msg = user_service.create_new_user(session, email="MEINE_EMAIL1", username=None,
                                                   password_hash="hash")
    assert user_without_name is None
    assert msg is not None

def test_create_and_get_user_by_id(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    user_found = user_service.get_user_by_id(session, added_user.id)
    assert user_found is not None
    assert added_user.id == user_found.id
    assert added_user.username == user_found.username
    assert added_user.email == user_found.email

def test_create_and_get_user_by_username(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    user_found = user_service.get_user_by_username(session, added_user.username)
    assert user_found is not None
    assert added_user.id == user_found.id
    assert added_user.username == user_found.username
    assert added_user.email == user_found.email

def test_create_and_get_user_by_email(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    user_found = user_service.get_user_by_email(session, added_user.email)
    assert user_found is not None
    assert added_user.id == user_found.id
    assert added_user.username == user_found.username
    assert added_user.email == user_found.email

def test_create_user_and_try_to_find_it_with_other_data(user_service, session):
    user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    user_found = user_service.get_user_by_email(session, "email2")
    assert user_found is None
    user_found = user_service.get_user_by_username(session, "Test2")
    assert user_found is None
    user_found = user_service.get_user_by_id(session, "12")
    assert user_found is None

def test_create_and_delete_user(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    user_found = user_service.get_user_by_id(session, added_user.id)
    assert user_found is not None
    user_service.delete_user(session, user_found.id)
    session.commit()
    user_found = user_service.get_user_by_id(session, added_user.id)
    assert user_found is None

def test_update_user(user_service, session):
    added_user, msg = user_service.create_new_user(session, username="Test", email="email", password_hash="hash")
    session.commit()
    updated_user = user_service.update_user(session, added_user.id, username="Test2")
    session.commit()
    user_found = user_service.get_user_by_id(session, added_user.id)
    assert user_found.username == "Test2"

def test_get_all_users(user_service, session):
    user_service.create_new_user(session, username="Test1", email="email1", password_hash="hash")
    user_service.create_new_user(session, username="Test2", email="email2", password_hash="hash")
    session.commit()
    all_users = user_service.get_all_users(session)
    assert len(all_users) == 2
    assert any(user.username == "Test1" for user in all_users)
    assert any(user.username == "Test2" for user in all_users)
