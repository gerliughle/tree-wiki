from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user

from ui.WebUI import WebUI
from logic.User import User
from logic.UserManager import UserManager
from logic.Validate import Validate

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
        """ Manages login/register requests.

        Does several validations. If login fails, allows retries.
        If registering, checks for duplicate names, and profanity, before saving.
        Also checks CloudlFlare turnstile token"""

        # CloudFlare Token check
        token = request.form.get("cf-turnstile-response")
        ip = request.headers.get("CF-Connecting-IP", request.remote_addr)
        if not token or not UserManager.verify_turnstile(token, ip):
            print("Cloudflare Turnstile error.")
            flash("Error with verification. Please try again.", "danger")
            return redirect(url_for("do_login"))

        # Process inputs
        username = request.form.get("username")
        valid, username, error = Validate.validate_input(username, "username", 4, 25, "username")
        if not valid:
            flash(error, "warning")
            return redirect(url_for("do_login"))

        password = request.form.get("password")
        valid, password, error = Validate.validate_input(password, "password", 8, 30, "password", check_profanity=False)
        if not valid:
            flash(error, "warning")
            return redirect(url_for("do_login"))

        remember = True if request.form.get("remember_me") else False
        login_action = request.form.get("login_action")
        user = UserManager.lookup_user_name(username)

        # Process login or registration
        if login_action == "login":
            print(f"Processing login request for '{username}'.")
            if user and user.verify_password(password) and user.is_active:
                    print(f"Login verified. Logging in {user.username}")
                    login_user(user, remember=remember)
            else:
                print(f"Login attempt for '{username}' failed.")
                flash("Login failed, please check your username or password.", "warning")
                return redirect(url_for("do_login"))
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
                flash("Registration successful. Welcome to bonsaitree.wiki!", "success")
                print(f"New User '{username}'registered and logged in.")
            else:
                print("User already exists.")
                flash("Username already exists. Please try again.", "warning")
                return redirect(url_for("do_login"))
        return redirect(url_for("homepage"))

    @staticmethod
    @__app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("homepage"))
