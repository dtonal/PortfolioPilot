from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importiere deine bestehenden Module
from AuthService import AuthService  # Stelle sicher, dass der Pfad korrekt ist
from portfolio_pilot_backend.repositories.user_repository import UserRepositoryFactory
from UserService import UserService
from portfolio_pilot_backend.models import Base, User  # Importiere dein User-Modell

app = Flask(__name__)

# Konfiguration der Datenbank (passe dies an deine Bedürfnisse an)
DATABASE_URL = "sqlite:///./test.db"  # Beispiel für eine SQLite-Datenbank
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Erstelle die Datenbanktabellen, falls sie noch nicht existieren
Base.metadata.create_all(bind=engine)

# Initialisierung von AuthService und UserRepositoryFactory (angenommen, du hast diese bereits)
auth_service = AuthService()  # Erstelle eine Instanz deines AuthService
user_repository_factory = UserRepositoryFactory() # Erstelle eine Instanz deiner UserRepositoryFactory
user_service = UserService(user_repository_factory, auth_service)

# Funktion, um eine Datenbank-Session zu erstellen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpunkte ---

@app.route("/users", methods=["POST"])
def create_user():
    print("creater user")
    db = next(get_db())
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password_hash = data.get("password_hash") # Im echten Einsatz solltest du das Passwort hashen, bevor du es speicherst!

    if not all([username, email, password_hash]):
        return jsonify({"error": "Benutzername, E-Mail und Passwort sind erforderlich."}), 400


    new_user, error_msg = user_service.create_new_user(db, username, email, password_hash)

    if new_user:
        return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}), 201
    else:
        return jsonify({"error": error_msg}), 400

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    db = next(get_db())
    user = user_service.get_user_by_id(db, user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username, "email": user.email}), 200
    else:
        return jsonify({"error": "Benutzer nicht gefunden."}), 404

@app.route("/users", methods=["GET"])
def get_all_users():
    db = next(get_db())
    users = user_service.get_all_users(db)
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return jsonify(user_list), 200

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    db = next(get_db())
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password_hash = data.get("password_hash") # Auch hier: Hashen im echten Einsatz!
    updated_user, error_msg = user_service.update_user(db, user_id, username, email, password_hash)

    if updated_user:
        return jsonify({"id": updated_user.id, "username": updated_user.username, "email": updated_user.email}), 200
    else:
        return jsonify({"error": error_msg}), 404

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    db = next(get_db())
    if user_service.delete_user(db, user_id):
        return jsonify({"message": "Benutzer erfolgreich gelöscht."}), 200
    else:
        return jsonify({"error": "Benutzer nicht gefunden."}), 404

@app.route("/auth/login", methods=["POST"])
def login():
    db = next(get_db())
    data = request.get_json()
    username = data.get("username")
    password_hash = data.get("password_hash")

    if not all([username, password_hash]):
        return jsonify({"error": "Benutzername und Passwort sind erforderlich."}), 400

    user = user_service.get_user_by_username(db, username)
    if user and auth_service.authenticate(user, password_hash): # Nutze deine AuthService zum Passwort-Check
        return jsonify({"message": "Login erfolgreich.", "user_id": user.id, "username": user.username}), 200
    else:
        return jsonify({"error": "Ungültige Anmeldeinformationen."}), 401

if __name__ == "__main__":
    print("app run")
    app.run(debug=True)