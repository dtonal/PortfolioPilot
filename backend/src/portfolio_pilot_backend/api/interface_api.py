from abc import ABC, abstractmethod

from flask import Flask


class IApi(ABC):
    @abstractmethod
    def register_routes(self, app: Flask):
        pass