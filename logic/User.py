import bcrypt
from flask_login import UserMixin

class User(UserMixin):
    __username = ""
    __pw_hash = ""
    __role = ""
    __is_active = True

    def __init__(self, _id, username, pw_hash, role, is_active):
        self._id = _id
        self.__username = username
        self.__pw_hash = pw_hash
        self.__role = role
        self.__is_active = is_active

    @staticmethod
    def build(user_dict):
        return User(
            user_dict["_id"],
            user_dict["username"],
            user_dict["pw_hash"],
            user_dict["role"],
            user_dict.get("is_active") # hopefully this only pulls if it is set and false?
        )

    def to_dict(self):
        return {
            "username": self.__username,
            "pw_hash": self.__pw_hash,
            "role": self.__role,
            "is_active": self.__is_active
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

    @property
    def is_active(self):
        return self.__is_active