import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

# Importiere deine bestehenden Module
from auth_service import AuthService
from portfolio_pilot_backend.models import Base
from portfolio_pilot_backend.models import User  # Importiere das User-Modell

# Importiere die zu testende Klasse und die app-Definition
from user_api import UserAPI
from app import AppFactory

class UserAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up for each test."""
        # Konfiguration für die Testumgebung (In-Memory SQLite)
        self.temp_db_file, self.temp_db_path = tempfile.mkstemp()
        test_config = {
            'SQLALCHEMY_DATABASE_URI': f"sqlite:///{self.temp_db_path}",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }
        self.app_factory = AppFactory(config=test_config)
        self.app = self.app_factory.create_app()
        self.test_client = self.app.test_client()

        # Erstelle die Datenbanktabellen
        with self.app.app_context():
            SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=self.app_factory.engine)
            self.SessionLocalTest = SessionLocalTest

            # Initialisiere AuthService für das Erstellen des Testnutzers
            auth_service = AuthService()

            # Erstelle einen initialen Testnutzer in der Datenbank
            with self.SessionLocalTest() as db:
                test_user = User(username="testuser", email="test@example.com",
                                 password_hash=auth_service.hash_password("testpassword"))
                db.add(test_user)
                db.commit()
                self.test_user_id = test_user.id

        self.base_url = "http://127.0.0.1:5000"  # Wird jetzt vom Test-Client gehandhabt
        self.user_data = {"username": "newuser", "email": "new@example.com", "password_hash": "securepassword"}
        self.login_data = {"username": "testuser", "password_hash": "testpassword"}

    def tearDown(self):
        self.app_factory.engine.dispose()
        os.close(self.temp_db_file)
        os.remove(self.temp_db_path)

    def test_create_user(self):
        response = self.test_client.post("/users", json=self.user_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], self.user_data["username"])
        self.assertEqual(data["email"], self.user_data["email"])
        created_user_id = data["id"]
        # Überprüfe, ob der Nutzer wirklich in der DB ist
        with self.SessionLocalTest() as db:
            user = db.query(User).filter(User.id == created_user_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, self.user_data["username"])
            self.assertEqual(user.email, self.user_data["email"])

    def test_get_user(self):
        response = self.test_client.get(f"/users/{self.test_user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")

        response = self.test_client.get("/users/9999")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_get_all_users(self):
        # Erstelle einen weiteren Nutzer für diesen Test
        with self.SessionLocalTest() as db:
            another_user = User(username="anotheruser", email="another@example.com", password_hash="somehash")
            db.add(another_user)
            db.commit()

        response = self.test_client.get("/users")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1) # Mindestens der initial erstellte Nutzer sollte da sein
        usernames = {user["username"] for user in data}
        self.assertIn("testuser", usernames)
        self.assertIn("anotheruser", usernames)

    def test_update_user(self):
        updated_data = {"username": "updateduser", "email": "updated@example.com"}
        response = self.test_client.put(f"/users/{self.test_user_id}", json=updated_data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["username"], "updateduser")
        self.assertEqual(data["email"], "updated@example.com")

        # Überprüfe die Aktualisierung in der DB
        with self.SessionLocalTest() as db:
            updated_user = db.query(User).filter(User.id == self.test_user_id).first()
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user.username, "updateduser")
            self.assertEqual(updated_user.email, "updated@example.com")

        response = self.test_client.put("/users/9999", json=updated_data)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_delete_user(self):
        response = self.test_client.delete(f"/users/{self.test_user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)

        # Überprüfe, ob der Nutzer aus der DB gelöscht wurde
        with self.SessionLocalTest() as db:
            deleted_user = db.query(User).filter(User.id == self.test_user_id).first()
            self.assertIsNone(deleted_user)

        response = self.test_client.delete("/users/9999")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_login(self):
        response = self.test_client.post("/auth/login", json=self.login_data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertEqual(data["user_id"], self.test_user_id)
        self.assertEqual(data["username"], "testuser")

        invalid_login_data = {"username": "testuser", "password_hash": "wrongpassword"}
        response = self.test_client.post("/auth/login", json=invalid_login_data)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("error", data)

        missing_data = {"username": "testuser"}
        response = self.test_client.post("/auth/login", json=missing_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)



if __name__ == "__main__":
    unittest.main()