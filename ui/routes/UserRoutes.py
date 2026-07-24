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
                    "pw_hash": pw_hash
                }
                new_user = UserManager.save_user(user_dict)
                # FIXME
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

    @staticmethod
    @__app.route("/manage_users")
    @login_required
    @UserManager.role_required("admin")
    def manage_users():
        users = UserManager.get_users()
        josh = UserManager.lookup_user_name("josh")
        if josh in users:
            users.remove(josh)
        return render_template("user/manage_users.html", users=users)


    @staticmethod
    @__app.route("/edit_user", methods=["POST"])
    @login_required
    @UserManager.role_required("admin")
    def edit_user():
        username = request.form.get("user_selection")
        user = UserManager.lookup_user_name(username)
        if user and user.username != "josh":
            return render_template("user/edit_user.html", user=user)
        else:
            print("User does not exist.")
            return redirect(url_for("do_login"))

    @staticmethod
    @__app.route("/do_edit_user", methods=["POST"])
    @login_required
    @UserManager.role_required("admin")
    def do_edit_user():
        user_id = request.form.get("user_id")
        user = UserManager.lookup_user_id(user_id)
        print(f"Debug. {user.is_active=}")
        role_change = request.form.get("role_change")
        disable_account = request.form.get("disable_account")
        enable_account = request.form.get("enable_account")
        delete_account = request.form.get("delete_account")
        if user and user.username != "josh":
            user_edits = {"_id": user.id}
            if role_change and role_change != "":
                user_edits["role_change"] = role_change
            elif disable_account:
                user_edits["is_active"] = False
            elif enable_account:
                user_edits["is_active"] = True
            elif delete_account:
                UserManager.delete_user(user_id)
                return redirect(url_for("homepage"))
            updated_user = UserManager.save_user(user_edits)
            print(f"Updated user: {updated_user}")
            return redirect(url_for("homepage"))
        return render_template("error.html")



