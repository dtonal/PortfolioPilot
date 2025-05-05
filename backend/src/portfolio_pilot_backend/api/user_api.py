from flask import Flask, request, jsonify
from sqlalchemy.orm import Session

from auth_service import IAuthService
from handle_request import IRequestHandler
from interface_api import IApi
from user_service import UserService


class UserAPI(IApi):
    def __init__(self, user_service: UserService, auth_service: IAuthService, request_handler: IRequestHandler):
        """
        Initializes the UserAPI class.

        Args:
            user_service: The user service.
            auth_service: The authentication service.
            request_handler: The request handler for database session management.
        """
        self.user_service = user_service
        self.auth_service = auth_service
        self.request_handler = request_handler

    def register_routes(self, app: Flask) -> None:
        app.add_url_rule("/users", methods=["POST"], view_func=self.request_handler.handle(self.create_user))
        app.add_url_rule("/users/<int:user_id>", methods=["GET"], view_func=self.request_handler.handle(self.get_user))
        app.add_url_rule("/users", methods=["GET"], view_func=self.request_handler.handle(self.get_all_users))
        app.add_url_rule("/users/<int:user_id>", methods=["PUT"],
                         view_func=self.request_handler.handle(self.update_user))
        app.add_url_rule("/users/<int:user_id>", methods=["DELETE"],
                         view_func=self.request_handler.handle(self.delete_user))
        app.add_url_rule("/auth/login", methods=["POST"], view_func=self.request_handler.handle(self.login))


    def create_user(self, db: Session):
        """
        Creates a new user.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password_hash = data.get("password_hash")

        if not all([username, email, password_hash]):
            return jsonify({"error": "Username, email, and password are required."}), 400

        new_user, error_msg = self.user_service.create_new_user(db, username, email, password_hash)
        if new_user:
            user_data = {"id": new_user.id, "username": new_user.username, "email": new_user.email}
            return jsonify(user_data), 201
        else:
            return jsonify({"error": error_msg}), 400

    def get_user(self, db: Session, user_id: int):
        """
        Retrieves a single user by ID.
        """
        user = self.user_service.get_user_by_id(db, user_id)
        if user:
            user_data = {"id": user.id, "username": user.username, "email": user.email}
            return jsonify(user_data), 200
        else:
            return jsonify({"error": "User not found."}), 404

    def get_all_users(self, db: Session):
        """
        Retrieves all users.
        """
        users = self.user_service.get_all_users(db)
        user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
        return jsonify(user_list), 200

    def update_user(self, db: Session, user_id: int):
        """
        Updates an existing user.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password_hash = data.get("password_hash")

        updated_user, error_msg = self.user_service.update_user(db, user_id, username, email, password_hash)
        if updated_user:
            user_data = {"id": updated_user.id, "username": updated_user.username, "email": updated_user.email}
            return jsonify(user_data), 200
        else:
            return jsonify({"error": error_msg}), 404

    def delete_user(self, db: Session, user_id: int):
        """
        Deletes a user.
        """
        success = self.user_service.delete_user(db, user_id)
        if success:
            return jsonify({"message": "User deleted successfully."}), 200
        else:
            return jsonify({"error": "User not found."}), 404

    def login(self, db: Session):
        """
        Handles user login.
        """
        data = request.get_json()
        username = data.get("username")
        password_hash = data.get("password_hash")

        if not all([username, password_hash]):
            return jsonify({"error": "Username and password are required."}), 400

        user = self.user_service.get_user_by_username(db, username)
        if user and self.auth_service.authenticate(user, password_hash):
            user_data = {"message": "Login successful.", "user_id": user.id, "username": user.username}
            return jsonify(user_data), 200
        else:
            return jsonify({"error": "Invalid credentials."}), 401