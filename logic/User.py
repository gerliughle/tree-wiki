class User:
    __username = ""
    __hash = ""
    __role = ""
    __email = ""

    def __init__(self, _id, username, hash, role, email):
        self._id = _id
        self.__username = username
        self.__hase = hash
        self.__role = role
        self.__email = email

    @staticmethod
    def build(user_dict):
        return User(
            user_dict["_id"],
            user_dict["username"],
            user_dict["hash"],
            user_dict["role"],
            user_dict["email"]
        )

    @property
    def username(self):
        return self.__username

    @property
    def id(self):
        return self._id