from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from handle_request import handle_request


class UserAPI:
    def __init__(self, user_service, auth_service):
        """
        Initializes the UserAPI class.

        Args:
            user_service: The user service.
            auth_service: The authentication service.
            get_db: A function that returns a database session.  This is a dependency.
        """
        self.user_service = user_service
        self.auth_service = auth_service


    def register_routes(self, app: Flask):
        app.add_url_rule("/users", methods=["POST"], view_func=self.create_user)
        app.add_url_rule("/users/<int:user_id>", methods=["GET"], view_func=self.get_user)
        app.add_url_rule("/users", methods=["GET"], view_func=self.get_all_users)
        app.add_url_rule("/users/<int:user_id>", methods=["PUT"], view_func=self.update_user)
        app.add_url_rule("/users/<int:user_id>", methods=["DELETE"], view_func=self.delete_user)
        app.add_url_rule("/auth/login", methods=["POST"], view_func=self.login)

    def create_user(self):
        """
        Creates a new user.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password_hash = data.get("password_hash")

        if not all([username, email, password_hash]):
            return jsonify({"error": "Username, email, and password are required."}), 400

        def _create_user(db: Session):
            new_user, error_msg = self.user_service.create_new_user(db, username, email, password_hash)
            if new_user:
                user_data = {"id": new_user.id, "username": new_user.username, "email": new_user.email}
                return jsonify(user_data), 201
            else:
                return jsonify({"error": error_msg}), 400

        return handle_request(_create_user)


    def get_user(self, user_id: int):
        """
        Retrieves a single user by ID.
        """
        def _get_user(db: Session):
            user = self.user_service.get_user_by_id(db, user_id)
            if user:
                user_data = {"id": user.id, "username": user.username, "email": user.email}
                return jsonify(user_data), 200
            else:
                return jsonify({"error": "User not found."}), 404
        return handle_request(_get_user)

    def get_all_users(self):
        """
        Retrieves all users.
        """
        def _get_all_users(db: Session):
            users = self.user_service.get_all_users(db)
            user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
            return jsonify(user_list), 200

        return handle_request(_get_all_users)

    def update_user(self, user_id: int):
        """
        Updates an existing user.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password_hash = data.get("password_hash")

        def _update_user(db: Session):
            updated_user, error_msg = self.user_service.update_user(db, user_id, username, email, password_hash)
            if updated_user:
                user_data = {"id": updated_user.id, "username": updated_user.username, "email": updated_user.email}
                return jsonify(user_data), 200
            else:
                return jsonify({"error": error_msg}), 404

        return handle_request(_update_user)

    def delete_user(self, user_id: int):
        """
        Deletes a user.
        """
        def _delete_user(db: Session):
            success = self.user_service.delete_user(db, user_id)
            if success:
                return jsonify({"message": "User deleted successfully."}), 200
            else:
                return jsonify({"error": "User not found."}), 404
        return handle_request(_delete_user)

    def login(self):
        """
        Handles user login.
        """
        data = request.get_json()
        username = data.get("username")
        password_hash = data.get("password_hash")

        if not all([username, password_hash]):
            return jsonify({"error": "Username and password are required."}), 400

        def _login(db: Session):
            user = self.user_service.get_user_by_username(db, username)
            if user and self.auth_service.authenticate(user, password_hash):
                user_data = {"message": "Login successful.", "user_id": user.id, "username": user.username}
                return jsonify(user_data), 200
            else:
                return jsonify({"error": "Invalid credentials."}), 401

        return handle_request(_login)
