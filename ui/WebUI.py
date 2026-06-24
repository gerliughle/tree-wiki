from flask import Flask, render_template, request, session, g, redirect, url_for
from flask_session import Session
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from ui.UserState import UserState
from bson import ObjectId

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
    @__app.before_request
    def login_admin():
        """ Auto-logins user0. To replace with real login. """
        if "user_id" not in session:
            all_users = WebUI.usermanager.get_all_users()
            if all_users:
                session["user_id"] = str(all_users[0].id)
                print(f"Auto logged in id: {session['user_id']}")
        current_user_id = session.get("user_id")
        if current_user_id:
            g.current_user = WebUI.usermanager.lookup_user(ObjectId(current_user_id))
        else:
            g.current_user = None

    @staticmethod
    @__app.context_processor
    def inject_user():
        return dict(current_user=getattr(g, "current_user", None))

    @staticmethod
    @__app.route('/show_branch', methods=["GET", "POST"])
    def show_branch():
        branch_id = ObjectId(request.args["branch"])
        print(f"{branch_id=}")
        branch = WebUI.engine.lookup_branch(branch_id)

        care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch_id)
        page_context = {
            "branch": branch,
            "care_guide": care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": category_list,
        }
        print(f"{branch.name=}")
        print(f"Care guide length: {len(care_guide)}")

        return render_template("index.html", **page_context)

    @staticmethod
    @__app.route('/index')
    @__app.route('/index.html')
    @__app.route('/index.php')
    @__app.route('/')
    def homepage():
        """ Sets Flask routes to homepage. """

        test_branch = "Japanese Maple"
        branch = WebUI.engine.lookup_branch_by_name(test_branch)
        care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch.id)
        page_context = {
            "branch": branch,
            "care_guide": care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": category_list,
        }
        print(f"{branch.name=}")
        print(f"Care guide length: {len(care_guide)}")

        return render_template("index.html", **page_context)

    @staticmethod
    @__app.route('/print_tree')
    def tree():
        """ Will eventually be replaced. For now, allows selection of any branch."""
        all_branches = WebUI.engine.get_branches()
        return render_template("print/print_tree.html", branches=all_branches)



    @classmethod
    def run(cls):
        cls.__app.config["SESSION_TYPE"] = "filesystem"
        Session(cls.__app)
        cls.__app.run(host="0.0.0.0")

if __name__ == "__main__":
    WebUI.init()
    WebUI.run()
