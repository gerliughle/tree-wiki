import bcrypt
from flask_login import UserMixin

class User(UserMixin):
    __username = ""
    __pw_hash = ""
    __role = ""

    def __init__(self, _id, username, pw_hash, role):
        self._id = _id
        self.__username = username
        self.__pw_hash = pw_hash
        self.__role = role

    @staticmethod
    def build(user_dict):
        return User(
            user_dict["_id"],
            user_dict["username"],
            user_dict["pw_hash"],
            user_dict["role"]
        )

    def to_dict(self):
        return {
            "username": self.__username,
            "pw_hash": self.__pw_hash,
            "role": self.__role
        }

    @property
    def username(self):
        return self.__username

    @property
    def id(self):
        return self._id

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt(13)
        pw_hash = bcrypt.hashpw(password.encode(), salt)
        return pw_hash

    def verify_password(self, password):
        result = bcrypt.checkpw(password.encode(), self.__pw_hash)
        return result

    @property
    def role(self):
        return self.__role

