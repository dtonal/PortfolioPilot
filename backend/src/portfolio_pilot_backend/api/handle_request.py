from flask import request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from abc import ABC, abstractmethod
from typing import Callable

class IRequestHandler(ABC):
    @abstractmethod
    def handle(self, api_method: Callable):
        """
        Should wrap the given API method with any processing logic.
        """
        pass

class RequestHandler(IRequestHandler):
    def __init__(self, session_factory):
        """
        Initializes the RequestHandler with a session factory.

        Args:
            session_factory: A callable that returns a new SQLAlchemy Session.
        """
        self.session_factory = session_factory

    def handle(self, api_method):
        """
        A decorator that handles database session management and error handling
        for API methods.

        Args:
            api_method: The API method to be wrapped.

        Returns:
            The wrapped function.
        """

        @wraps(api_method)
        def wrapper(*args, **kwargs):
            db: Session = self.session_factory()
            try:
                # Call the API method, passing the database session as the first argument
                result = api_method(db, *args, **kwargs)
                db.commit()
                return result
            except SQLAlchemyError as e:
                db.rollback()
                return jsonify({"error": f"Database error: {str(e)}"}), 500
            except Exception as e:
                db.rollback()
                return jsonify({"error": str(e)}), 500
            finally:
                db.close()
        return wrapper