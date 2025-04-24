from portfolio_pilot_backend.models import User

user = User("alice", "alice@example.com", "hashed_pw")
print(user.username)