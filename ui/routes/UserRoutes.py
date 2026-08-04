from logic.UserManager import UserManager
from ui.WebUI import WebUI
from logic.User import User
from logic.UserManager import UserManager
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
        password = request.form.get("password")
        remember = True if request.form.get("remember_me") else False
        login_action = request.form.get("login_action")

        user = UserManager.lookup_user_name(username)

        if login_action == "login":
            print(f"Processing login request for {username}.")
            if user and user.verify_password(password) and user.is_active:
                    print(f"Password verified. Logging in {user.username}")
                    login_user(user, remember=remember)
            else:
                print("Login failed.")
                return redirect(url_for("do_login")) # FIXME redirect back to login with error
        elif login_action == "register":
            print(f"Processing registration request for {username}.")
            if not user:
                pw_hash = User.hash_password(password)
                print("Password hashed.")
                user_dict = {
                    "username": username,
                    "pw_hash": pw_hash,
                    "role": "user",
                    "is_active": True
                }
                new_user = UserManager.save_user(user_dict, "create")
                login_user(new_user)
                print("New User registered and logged in.")
            else:
                print("User already exists.")
                return redirect(url_for("do_login")) # FIXME redirect back to register with error
        return redirect(url_for("homepage"))

    @staticmethod
    @__app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("homepage"))