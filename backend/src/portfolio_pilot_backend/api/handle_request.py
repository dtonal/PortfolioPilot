from typing import Callable
from db import get_db_session
def handle_request(func: Callable, *args, **kwargs):
    """
    Helper-Methode, um das Session-Handling zu zentralisieren.
    """
    db = get_db_session()
    try:
        result = func(db, *args, **kwargs)  # Übergibt die Session an die eigentliche Funktion
        return result
    except Exception as e:
        db.rollback()
        raise e  # Re-raise, damit Flask es handhaben kann
    finally:
        db.close()