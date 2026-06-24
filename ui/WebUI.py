from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from ui.UserState import UserState

class WebUI:
    __app = Flask(__name__)
    __all_branches = None
    __all_leaves = None
    APP_NAME = "bonsaitree"
    # ALLOWED_PATHS = [
    #     "/login",
    #     "/do_login",
    # ]

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()
        cls.usermanager = UserManager()

    @classmethod
    def get_app(cls):
        """ Ensures only one Flask app. """
        return cls.__app

    @classmethod
    def get_user(cls):
        """ Returns user if there is an active session. """
        if "user" in session:
            return session["user"]
        return None

    @classmethod
    def get_all_branches(cls):
        """ Returns all branches """
        return cls.engine.all_branches

    @classmethod
    def get_branch_map(cls):
        return cls.engine.branch_map

    @classmethod
    def get_all_leaves(cls):
        """ Returns all leaves """
        return cls.engine.all_leaves

    @classmethod
    def get_leaf_map(cls):
        return cls.engine.leaf_map


    @staticmethod
    @__app.route('/index')
    @__app.route('/index.html')
    @__app.route('/index.php')
    @__app.route('/')
    def homepage():
        """ Sets Flask routes to homepage. """
        users = WebUI.usermanager.get_all_users()
        user_id = users[0].id
        if "user" in session:
            session.clear()
        if "user" not in session:

            session["user"] = user_id
        print(f"{session['user']=}")
        current_user = WebUI.usermanager.lookup_user(user_id)
        current_username = current_user.username
        test_branch = "Japanese Maple"
        branch = WebUI.engine.lookup_branch_by_name(test_branch)
        care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch._id) # FIXME, prob should have better id getter.
        page_context = {
            "user": current_username,
            "branch": branch,
            "care_guide": care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": category_list,
        }
        print(f"{current_username=}")
        print(f"{branch.name=}")
        print(f"Care guide length: {len(care_guide)}")
        print(f"Care guide: {care_guide}")

        return render_template("index.html", **page_context)

    @classmethod
    def run(cls):
        cls.__app.config["SESSION_TYPE"] = "filesystem"
        Session(cls.__app)
        cls.__app.run(host="0.0.0.0")

if __name__ == "__main__":
    WebUI.init()
    WebUI.run()
