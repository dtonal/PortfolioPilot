from typing import Callable

class RequestHandler():
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker

    def handle(self, func: Callable, *args, **kwargs):
        """
        Helper-Methode, um das Session-Handling zu zentralisieren.
        """
        db = self.sessionmaker()
        try:
            result = func(db, *args, **kwargs)  # Übergibt die Session an die eigentliche Funktion
            return result
        except Exception as e:
            db.rollback()
            raise e  # Re-raise, damit Flask es handhaben kann
        finally:
            db.close()