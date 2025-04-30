import unittest
import requests
import json
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Thread
import time

# Importiere deine bestehenden Module
from AuthService import AuthService
from handle_request import RequestHandler
from portfolio_pilot_backend.repositories.user_repository import UserRepositoryFactory
from UserService import UserService
from portfolio_pilot_backend.models import Base
from portfolio_pilot_backend.models import User  # Importiere das User-Modell

# Importiere die zu testende Klasse und die app-Definition
from user_api import UserAPI
from app import app as flask_app

class UserAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up for each test."""
        self.app = flask_app
        self.client = self.app.test_client()
        self.base_url = "http://127.0.0.1:5000"  # Standard Flask-Adresse

        # Konfiguration der Testdatenbank (verwende eine In-Memory SQLite DB für Tests)
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Überschreibe die SessionLocal in der app für die Tests
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        global request_handler
        request_handler = RequestHandler(self.SessionLocalTest)

        # Initialisierung der Services mit der Test-DB-Session-Factory
        auth_service = AuthService()
        user_repository_factory = UserRepositoryFactory()
        user_service = UserService(user_repository_factory, auth_service)

        # Initialisierung der UserAPI mit den echten Services und dem Test-RequestHandler
        self.user_api = UserAPI(user_service, auth_service, request_handler)

        # Erstelle eine neue Flask-App für den Test und registriere die Routen der UserAPI
        self.test_app = Flask(__name__)
        self.user_api.register_routes(self.test_app)
        self.test_client = self.test_app.test_client()

        self.user_data = {"username": "newuser", "email": "new@example.com", "password_hash": "securepassword"}
        self.login_data = {"username": "testuser", "password_hash": "testpassword"}

        # Erstelle einen initialen Testnutzer in der Datenbank
        with self.SessionLocalTest() as db:
            test_user = User(username="testuser", email="test@example.com", password_hash=auth_service.hash_password("testpassword"))
            db.add(test_user)
            db.commit()
            self.test_user_id = test_user.id

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