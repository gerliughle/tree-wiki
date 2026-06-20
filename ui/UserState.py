class UserState:
    __user_id = None
    __phase_filter = ["1st", "2nd", "3rd+"]
    __season_filter = ["Spring", "Summer", "Fall", "Winter"]

    # When asking filter data, store it here
    # When calling a care guide, app will get these filters, and branch target, then
    # call treeengine to get the care guide.
    # if needed, the page can be adjusted by calling the user's role. id get the id from UserState
    # then can call the ___ (database) class to get the user object.

    # might want to split usermanager from treeenginer. then readdata shouldnt return user list
    # wont need to do user stuff often. usermanaer is the same
    #