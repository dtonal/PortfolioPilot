from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importiere deine bestehenden Module
from AuthService import AuthService
from portfolio_pilot_backend.repositories.user_repository import UserRepositoryFactory
from UserService import UserService
from portfolio_pilot_backend.models import Base

# Importiere die neue API-Klasse
from UserAPI import UserAPI

app = Flask(__name__)

# Konfiguration der Datenbank
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Erstelle die Datenbanktabellen, falls sie noch nicht existieren
Base.metadata.create_all(bind=engine)

# Initialisierung von AuthService, UserRepositoryFactory und UserService
auth_service = AuthService()
user_repository_factory = UserRepositoryFactory()
user_service = UserService(user_repository_factory, auth_service)

# Initialisierung der UserAPI-Klasse und Registrierung der Routen
user_api = UserAPI(user_service, auth_service)
user_api.register_routes(app)

if __name__ == "__main__":
    print("app run")
    app.run(debug=True)