from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Beziehung zur Watchlist (One-to-many über die Watchlist-Tabelle)
    watchlists = relationship("Watchlist", back_populates="user")

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    isin = Column(String, unique=True, nullable=True)  # Optional, kann auch Null sein
    wkn = Column(String, unique=True, nullable=True)   # Optional, kann auch Null sein
    exchange = Column(String, nullable=True)  # Optional
    industry = Column(String, nullable=True)  # Optional

    # Beziehung zu Kursdaten (One-to-many)
    historical_data = relationship("HistoricalData", back_populates="stock")

     # Beziehung zur Watchlist (One-to-many über die Watchlist-Tabelle)
    watchlists = relationship("Watchlist", back_populates="stock")

    def __init__(self, symbol, name, isin=None, wkn=None, exchange=None, industry=None):
        self.symbol = symbol
        self.name = name
        self.isin = isin
        self.wkn = wkn
        self.exchange = exchange
        self.industry = industry

class HistoricalData(Base):
    __tablename__ = 'historical_data'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    # Beziehung zur Aktie (Many-to-one)
    stock = relationship("Stock", back_populates="historical_data")

    def __init__(self, stock_id, date, open, high, low, close, adj_close, volume):
        self.stock_id = stock_id
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume

class Watchlist(Base):
    __tablename__ = 'watchlists'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), primary_key=True, nullable=False)
    added_at = Column(DateTime, default=func.now())

    # Beziehungen zu User und Aktie (Many-to-One)
    user = relationship("User", back_populates="watchlists")
    stock = relationship("Stock", back_populates="watchlists")

    def __init__(self, user_id, stock_id):
        self.user_id = user_id
        self.stock_id = stock_id