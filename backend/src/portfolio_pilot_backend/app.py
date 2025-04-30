from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importiere deine bestehenden Module
from AuthService import AuthService
from handle_request import RequestHandler
from portfolio_pilot_backend.repositories.user_repository import UserRepositoryFactory
from UserService import UserService
from portfolio_pilot_backend.models import Base

# Importiere die neue API-Klasse
from user_api import UserAPI

# Erstellung der Flask-Anwendungsinstanz
app = Flask(__name__)

# Konfiguration der Datenbank (kann auch aus einer separaten Datei oder Umgebungsvariablen kommen)
# Hier ist eine Standardkonfiguration für SQLite im Dateisystem
DATABASE_URL = "sqlite:///./app.db"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optionale Einstellung

# Erstellung des SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Erstellung einer SessionLocal-Klasse, um Datenbank-Sessions zu erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialisierung des RequestHandlers mit der SessionLocal
request_handler = RequestHandler(SessionLocal)

# Erstelle die Datenbanktabellen, falls sie noch nicht existieren
Base.metadata.create_all(bind=engine)

# Initialisierung von AuthService, UserRepositoryFactory und UserService
auth_service = AuthService()
user_repository_factory = UserRepositoryFactory()
user_service = UserService(user_repository_factory, auth_service)

# Initialisierung der UserAPI-Klasse und Registrierung der Routen
user_api = UserAPI(user_service, auth_service, request_handler)
user_api.register_routes(app)

# Die Methode test_client() ist Teil des Flask-Frameworks
# Sie wird an der Flask-Anwendungsinstanz (hier 'app') aufgerufen,
# um einen Test-Client zu erstellen.

if __name__ == "__main__":
    print("app run")
    app.run(debug=True)