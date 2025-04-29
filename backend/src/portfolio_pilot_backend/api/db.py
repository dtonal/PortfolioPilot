from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from portfolio_pilot_backend.models import Base

def get_db_session():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_local()