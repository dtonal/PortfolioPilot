import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.portfolio_pilot_backend.models import Base, User, Stock, HistoricalData, Watchlist


@pytest.fixture(scope="function")
def session():
    """Erstellt eine neue Datenbank-Session für jeden Test."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # Hier wird die Session dem Test bereitgestellt
    session.close()
    Base.metadata.drop_all(engine)

def test_can_create_and_retrieve_users(session):
    new_user = User(username="Torben", email="<EMAIL>", password_hash="<PASSWORD>")
    session.add(new_user)
    session.commit()

    retrieved_user = session.query(User).filter_by(username="Torben").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "<EMAIL>"
    assert retrieved_user.username == "Torben"
    assert retrieved_user.password_hash == "<PASSWORD>"

def test_can_delete_user(session):
    new_user = User(username="Torben", email="<EMAIL>", password_hash="<PASSWORD>")
    session.add(new_user)
    session.commit()
    user_id = new_user.id
    assert user_id is not None
    print(user_id)

    retrieved_user = session.query(User).filter_by(id=user_id).first()
    assert retrieved_user is not None

    session.delete(retrieved_user)
    session.commit()

    retrieved_user = session.query(User).filter_by(id=user_id).first()
    assert retrieved_user is None

def test_can_create_stock(session):
    new_stock = Stock(symbol="AAPL", name="Apple Inc.", isin="US0378331005")
    session.add(new_stock)
    session.commit()
    retrieved_stock = session.query(Stock).filter_by(symbol="AAPL").first()
    assert retrieved_stock is not None
    assert retrieved_stock.name == "Apple Inc."
    assert retrieved_stock.isin == "US0378331005"

def test_can_create_historical_data(session):
    stock = Stock(symbol="GOOGL", name="Alphabet Inc.")
    session.add(stock)
    session.commit()
    historical_entry = HistoricalData(
        stock_id=stock.id,
        date=datetime(2025, 4, 24),
        open=150.0,
        high=152.5,
        low=149.0,
        close=152.0,
        adj_close=151.5,
        volume=1000000
    )
    session.add(historical_entry)
    session.commit()
    retrieved_data = session.query(HistoricalData).filter_by(stock_id=stock.id).first()
    assert retrieved_data is not None
    assert retrieved_data.open == 150.0
    assert retrieved_data.stock.symbol == "GOOGL" # Test der Beziehung

def test_can_create_watchlist_entry(session):
    user = User(username="watcher", email="watch@example.com", password_hash="secure")
    stock = Stock(symbol="MSFT", name="Microsoft Corp.")
    session.add_all([user, stock])
    session.commit()
    watchlist_entry = Watchlist(user_id=user.id, stock_id=stock.id)
    session.add(watchlist_entry)
    session.commit()
    retrieved_entry = session.query(Watchlist).filter_by(user_id=user.id, stock_id=stock.id).first()
    assert retrieved_entry is not None
    assert retrieved_entry.added_at is not None
    assert retrieved_entry.user.username == "watcher" # Test der Beziehung
    assert retrieved_entry.stock.name == "Microsoft Corp." # Test der Beziehung

def test_user_has_watchlist_relationship(session):
    user1 = User(username="user1", email="user1@example.com", password_hash="pass1")
    stock1 = Stock(symbol="AMZN", name="Amazon.com Inc.")
    stock2 = Stock(symbol="TSLA", name="Tesla, Inc.")
    session.add_all([user1, stock1, stock2])
    session.commit()  # Stelle sicher, dass User und Stocks eine ID haben

    watchlist_entry1 = Watchlist(user_id=user1.id, stock_id=stock1.id)
    watchlist_entry2 = Watchlist(user_id=user1.id, stock_id=stock2.id)
    session.add_all([watchlist_entry1, watchlist_entry2])
    session.commit()
    retrieved_user = session.query(User).filter_by(username="user1").first()
    assert len(retrieved_user.watchlists) == 2
    assert retrieved_user.watchlists[0].stock.symbol in ["AMZN", "TSLA"]
    assert retrieved_user.watchlists[1].stock.symbol in ["AMZN", "TSLA"]

def test_stock_has_watchlist_relationship(session):
    user1 = User(username="userA", email="userA@example.com", password_hash="pwA")
    user2 = User(username="userB", email="userB@example.com", password_hash="pwB")
    stock = Stock(symbol="NVDA", name="NVIDIA Corporation")
    session.add_all([user1, user2, stock])
    session.commit()
    watchlist_entry1 = Watchlist(user_id=user1.id, stock_id=stock.id)
    watchlist_entry2 = Watchlist(user_id=user2.id, stock_id=stock.id)
    session.add_all([watchlist_entry1, watchlist_entry2])
    session.commit()
    retrieved_stock = session.query(Stock).filter_by(symbol="NVDA").first()
    assert len(retrieved_stock.watchlists) == 2
    assert retrieved_stock.watchlists[0].user.username in ["userA", "userB"]
    assert retrieved_stock.watchlists[1].user.username in ["userA", "userB"]

def test_stock_has_historical_data_relationship(session):
    stock = Stock(symbol="FB", name="Meta Platforms, Inc.")
    session.add(stock)
    session.commit()
    historical_data1 = HistoricalData(stock_id=stock.id, date=datetime(2025, 4, 22), open=160.0, high=161.5, low=159.0, close=161.0, adj_close=160.5, volume=1500000)
    historical_data2 = HistoricalData(stock_id=stock.id, date=datetime(2025, 4, 23), open=161.0, high=162.0, low=160.5, close=161.8, adj_close=161.3, volume=1200000)
    session.add_all([historical_data1, historical_data2])
    session.commit()
    retrieved_stock = session.query(Stock).filter_by(symbol="FB").first()
    assert len(retrieved_stock.historical_data) == 2
    assert retrieved_stock.historical_data[0].open in [160.0, 161.0]
    assert retrieved_stock.historical_data[1].volume in [1500000, 1200000]