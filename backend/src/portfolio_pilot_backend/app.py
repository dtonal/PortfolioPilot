from flask import Flask
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from auth_service import AuthService
from handle_request import RequestHandler
from interface_api import IApi
from portfolio_pilot_backend.repositories.user_repository import UserRepositoryFactory
from user_service import UserService
from portfolio_pilot_backend.models import Base
from user_api import UserAPI

class AppFactory:
    def __init__(self, config: dict = None):
        self.config = config if config is not None else self._load_default_config()
        self.app = self._create_app(config)
        self.engine = create_engine(self.config['SQLALCHEMY_DATABASE_URI'])
        session_factory = self._create_session_factory(self.engine)
        request_handler = self._create_request_handler(session_factory)
        apis = self._create_apis(request_handler)
        for api in apis:
            api.register_routes(self.app)

    def _create_session_factory(self, engine: Engine):
        Base.metadata.create_all(bind=self.engine)
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_apis(self, request_handler: RequestHandler) -> list[IApi]:
        apis = []
        apis.append(self._create_user_api(request_handler))
        return apis

    def _create_user_api(self, request_handler: RequestHandler) -> UserAPI:
        auth_service = self._create_auth_service()
        user_repository_factory = self._create_user_repository_factory()
        user_service = self._create_user_service(user_repository_factory, auth_service)
        return UserAPI(user_service, auth_service, request_handler)

    def _load_default_config(self):
        return {
            'SQLALCHEMY_DATABASE_URI': "sqlite:///./app.db",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }

    def _create_app(self, config: dict) -> Flask:
        app = Flask(__name__)
        app.config.update(self.config)
        return app

    def _create_request_handler(self, session_local):
        return RequestHandler(session_local)

    def _create_auth_service(self):
        return AuthService()

    def _create_user_repository_factory(self):
        return UserRepositoryFactory()

    def _create_user_service(self, user_repository_factory, auth_service):
        return UserService(user_repository_factory, auth_service)

    def create_app(self) -> Flask:
        return self.app

if __name__ == "__main__":
    app_factory = AppFactory()
    app = app_factory.create_app()
    app.run(debug=True)

