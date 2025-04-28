import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from portfolio_pilot_backend.models import Base, User
from portfolio_pilot_backend.repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError

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
def user_repository(session):
    return UserRepository(session)

def test_get_user_by_id(user_repository, session):
    user1 = User(username="testuser1", email="test1@example.com", password_hash="hash1")
    user2 = User(username="testuser2", email="test2@example.com", password_hash="hash2")
    session.add_all([user1, user2])
    session.commit()

    retrieved_user = user_repository.get_by_id(user1.id)
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser1"

    non_existent_user = user_repository.get_by_id(999)
    assert non_existent_user is None

def test_get_user_by_username(user_repository, session):
    user1 = User(username="testuserA", email="testA@example.com", password_hash="hashA")
    user2 = User(username="testuserB", email="testB@example.com", password_hash="hashB")
    session.add_all([user1, user2])
    session.commit()

    retrieved_user = user_repository.get_by_username("testuserA")
    assert retrieved_user is not None
    assert retrieved_user.email == "testA@example.com"

    non_existent_user = user_repository.get_by_username("nonexistent")
    assert non_existent_user is None

def test_get_user_by_email(user_repository, session):
    user1 = User(username="testuserX", email="testX@example.com", password_hash="hashX")
    user2 = User(username="testuserY", email="testY@example.com", password_hash="hashY")
    session.add_all([user1, user2])
    session.commit()

    retrieved_user = user_repository.get_by_email("testX@example.com")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuserX"

    non_existent_user = user_repository.get_by_email("nonexistent@example.com")
    assert non_existent_user is None

def test_create_user(user_repository, session):
    new_user = User(username="newuser", email="new@example.com", password_hash="newhash")
    created_user = user_repository.create(new_user)
    session.commit()

    retrieved_user = session.query(User).filter_by(username="newuser").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "new@example.com"
    assert created_user.id is not None
    assert created_user.username == "newuser"

def test_update_user(user_repository, session):
    user_to_update = User(username="olduser", email="old@example.com", password_hash="oldhash")
    session.add(user_to_update)
    session.commit()
    original_id = user_to_update.id

    updated_user = user_to_update
    updated_user.username = "updateduser"
    updated_user.email="updated@example.com"
    updated_user.password_hash="new_secure_hash"
    updated_user = user_repository.update(updated_user)
    session.commit()

    retrieved_user = session.query(User).get(original_id)
    assert retrieved_user is not None
    assert retrieved_user.username == "updateduser"
    assert retrieved_user.email == "updated@example.com"
    assert retrieved_user.password_hash == "new_secure_hash"
    assert updated_user.id == original_id
    assert updated_user.username == "updateduser"

def test_delete_user(user_repository, session):
    user_to_delete = User(username="delsuer", email="del@example.com", password_hash="delhash")
    session.add(user_to_delete)
    session.commit()
    user_id_to_delete = user_to_delete.id

    user_repository.delete(user_to_delete)
    session.commit()

    retrieved_user = session.query(User).get(user_id_to_delete)
    assert retrieved_user is None

def test_list_all_users(user_repository, session):
    user1 = User(username="listuser1", email="list1@example.com", password_hash="listhash1")
    user2 = User(username="listuser2", email="list2@example.com", password_hash="listhash2")
    session.add_all([user1, user2])
    session.commit()

    all_users = user_repository.list_all()
    assert len(all_users) == 2
    assert any(user.username == "listuser1" for user in all_users)
    assert any(user.email == "list2@example.com" for user in all_users)

def test_create_user_with_duplicate_email(user_repository, session):
    # Ersten Benutzer mit einer bestimmten E-Mail-Adresse erstellen
    existing_user = User(username="user1", email="duplicate@example.com", password_hash="hash1")
    session.add(existing_user)
    session.commit()

    # Versuchen, einen zweiten Benutzer mit derselben E-Mail-Adresse zu erstellen
    duplicate_user = User(username="user2", email="duplicate@example.com", password_hash="hash2")

    # Wir erwarten, dass beim Hinzufügen und Committen des doppelten Benutzers eine IntegrityError ausgelöst wird
    with pytest.raises(IntegrityError) as excinfo:
        user_repository.create(duplicate_user)
        session.commit()
        session.rollback()
    # Code, der nach dem IntegrityError ausgeführt wird
    assert "UNIQUE constraint failed: users.email" in str(excinfo.value)
    session.close()

    new_session = SessionLocal()
    # Überprüfen, ob der erste Benutzer weiterhin existiert
    retrieved_user = new_session.query(User).filter_by(email="duplicate@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "user1"