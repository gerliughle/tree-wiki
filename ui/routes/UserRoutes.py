from logic.UserManager import UserManager
from ui.WebUI import WebUI
# from logic.UserManager import UserManager
from logic.User import User
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user


class UserRoutes:
    login_manager = LoginManager()
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/login')
    def login():
        return render_template("user/login.html")

    @staticmethod
    @__app.route('/login', methods=['POST'])
    def do_login():
        from data.Database import Database

        # FIXME will need to verify inputs using a function or bootstrap or something.

        username = request.form.get("username").strip().lower()
        password = request.form.get("password").strip()
        remember = True if request.form.get("remember_me") else False
        login_action = request.form.get("login_action")

        user = UserManager.lookup_user_name(username)

        if login_action == "login":
            print(f"Processing login request for {username}.")
            if user and user.verify_password(password):
                    print(f"Password verified. Logging in {user.username}")
                    print(f"{remember=}")
                    login_user(user, remember=remember)
            else:
                print("Login failed.")
                return render_template("error.html") # FIXME redirect back to login with error
        elif login_action == "register":
            print(f"Processing registration request for {username}.")
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
                return render_template("error.html") # FIXME redirect back to register with error
        return redirect(url_for("homepage"))


    # @staticmethod
    # @__app.route('/logout')
    # def logout():
    #     UserManager.logout()
    #     return redirect(url_for("homepage"))

    @staticmethod
    @__app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("homepage"))