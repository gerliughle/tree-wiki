# class UserState:
#     __user_id = None
#     __user_map = {}
#
#     def __init__(self, user_id):
#         from data.Database import Database
#         self.__user_id = user_id
#         self.__class__.__user_map[user_id] = self
#
#     @classmethod
#     def logout(cls, user_id):
#         if user_id in cls.__user_map:
#             del cls.__user_map[user_id]



    # if needed, the page can be adjusted by calling the user's role. id get the id from UserState
    # then can call the ___ (database) class to get the user object.