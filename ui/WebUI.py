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
    def assign_user():
        """ Assigns user on page click """
        current_user_id = session.get("user_id")

        if current_user_id:
            print("Current user found in session.")
            g.current_user = WebUI.usermanager.lookup_user(ObjectId(current_user_id))
        else:
            print("No user found in session.")
            g.current_user = None

    @staticmethod
    @__app.context_processor
    def inject_user():
        return dict(current_user=getattr(g, "current_user", None))

    @staticmethod
    @__app.route('/show_branch', methods=["GET", "POST"])
    def show_branch():
        if "branch" in request.args:
            try:
                branch_id = ObjectId(request.args["branch"])
            except:
                return render_template("error.html")
        else:
            return render_template("error.html")
        print(f"{branch_id=}")
        branch = WebUI.engine.lookup_branch(branch_id)
        if branch:
            care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch_id)
        else:
            return render_template("error.html")
        phases = []
        if "1st" in request.args:
            phases.append("1st")
        if "2nd" in request.args:
            phases.append("2nd")
        if "3rd+" in request.args:
            phases.append("3rd+")
        if len(phases) == 0:
            phases = ["1st", "2nd", "3rd+"]

        filtered_care_guide = WebUI.engine.filter_care_guide(care_guide,"phases", phases)
        children = TreeEngine.get_children_of_branch(branch.id)

        page_context = {
            "branch": branch,
            "care_guide": filtered_care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": category_list,
            "phases": phases,
            "children": children
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

        default_branch = "Japanese Maple"
        branch = WebUI.engine.lookup_branch_by_name(default_branch)
        care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch.id)
        phases = ["1st", "2nd", "3rd+"]
        children = TreeEngine.get_children_of_branch(branch.id)
        page_context = {
            "branch": branch,
            "care_guide": care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": category_list,
            "phases": phases,
            "children": children
        }
        print(f"{branch.name=}")
        print(f"Care guide length: {len(care_guide)}")

        return render_template("index.html", **page_context)

    @staticmethod
    @__app.route('/print_tree')
    def print_tree():
        """ Will eventually be replaced. For now, allows selection of any branch."""
        all_branches = WebUI.engine.get_branches()
        return render_template("print/print_tree.html", branches=all_branches)

    @classmethod
    def run(cls):
        from ui.routes.EditRoutes import EditRoutes
        from ui.routes.UserRoutes import UserRoutes

        cls.__app.config["SESSION_TYPE"] = "filesystem"
        cls.__app.secret_key = "my_secret_key"
        Session(cls.__app)
        cls.__app.run(host="0.0.0.0")
