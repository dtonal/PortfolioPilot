class AuthService():
    def authenticate(self, user, password_hash) -> bool:
        return user.password_hash == password_hash

    def hash_password(self, param):
        #TODO
        return param