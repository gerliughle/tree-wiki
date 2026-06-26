from ui.WebUI import WebUI
from logic.UserManager import UserManager
from logic.User import User
from flask import render_template, request, redirect, url_for

class UserRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/login')
    def login():
        return render_template("user/login.html")

    @staticmethod
    @__app.route('/do_login', methods=['POST'])
    def do_login():
        from data.Database import Database

        # FIXME will need to verify inputs using a function or bootstrap.
        username = ""
        password = ""
        login_action = ""

        if "username" in request.form:
            username = request.form["username"].strip().lower()
        if "password" in request.form:
            password = request.form["password"].strip()
        if "login_action" in request.form:
            login_action = request.form["login_action"]

        user = UserManager.read_user(username)
        if login_action == "login":
            print(f"Processing login for {username}.")
            if user:
                if user.verify_password(password):
                    print(f"Password verified. Logging in {user.username}")
                    UserManager.login(user)
                else:
                    print("Invalid password.")
                    return render_template("error.html")
            else:
                print("No user found, error.")
                return render_template("error.html")
        elif login_action == "register":
            print("Processing registration.")
            if not user:
                pw_hash = User.hash_password(password)
                print("Password hashed.")
                user = UserManager.add_user(username, pw_hash)
                print("User added.")
                UserManager.login(user)
                print("User logged in.")
                # i need to make a dict, add to database, then i can pull from database and build.
            else:
                print("User already exists.")
                return render_template("error.html")
        return redirect(url_for("homepage"))


    @staticmethod
    @__app.route('/logout')
    def logout():
        UserManager.logout()
        return redirect(url_for("homepage"))