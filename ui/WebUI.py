from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, current_user
from flask_session import Session # FIXME why is this red
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from bson import ObjectId

class WebUI:
    __app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(__app)
    __all_branches = None
    __all_leaves = None
    APP_NAME = "bonsaitree"

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()
        cls.usermanager = UserManager()

    @classmethod
    def get_app(cls):
        """ Ensures only one Flask app. """
        return cls.__app

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        """ Flask-login required. Uses Str id, returns either User obj or None. """
        return UserManager.lookup_user_id(user_id)

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
    @__app.route('/show_branch', methods=["GET", "POST"])
    def show_branch():
        if "branch" in request.args:
            branch_id = ObjectId(request.args["branch"])
            branch = WebUI.engine.lookup_branch(branch_id)
            branch_id = branch.id
        else:
            branch_name = "Japanese Maple"
            branch = WebUI.engine.lookup_branch_by_name(branch_name)
            branch_id = branch.id

        if branch:
            care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch_id)
        else:
            return render_template("error.html") #FIXME no error routing

        phases = []
        if "1st" in request.args:
            phases.append("1st")
        if "2nd" in request.args:
            phases.append("2nd")
        if "3rd+" in request.args:
            phases.append("3rd+")
        if len(phases) == 0:
            phases = ["1st", "2nd", "3rd+"]

        filtered_care_guide = []

        for leaf in care_guide:
            filtered_entries = []
            for entry in leaf.entries:
                if any(item in entry["phases"] for item in phases):
                    filtered_entries.append(entry)
            if len(filtered_entries) > 0:
                filtered_leaf = {
                    "id": leaf.id,
                    "branch_id": leaf.branch_id,
                    "category": leaf.category,
                    "subcategory": leaf.subcategory,
                    "seasons": leaf.seasons,
                    "entries": filtered_entries
                }

                filtered_care_guide.append(filtered_leaf)

        children = TreeEngine.get_children_of_branch(branch.id)
        all_seasons = ["Spring", "Summer", "Fall", "Winter"]
        page_context = {
            "branch": branch,
            "care_guide": filtered_care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": TreeEngine.CATEGORIES,
            "phases": phases,
            "children": children,
            "all_seasons": all_seasons
        }
        print(f"{branch.name=}")
        print(f"Filtered care guide length: {len(filtered_care_guide)}")

        # Sets or removes edit mode for session
        if request.args.get("mode") == "exit":
            session["mode"] = None
        if request.args.get("mode") == "edit" or session.get("mode") == "edit":
            if current_user.is_authenticated and current_user.role == "admin":
                page_context["is_edit_mode"] = True
                session["mode"] = "edit"

        return render_template("index.html", **page_context)

    @staticmethod
    @__app.route('/index')
    @__app.route('/index.html')
    @__app.route('/index.php')
    @__app.route('/')
    def homepage():
        """ Redirects to show branch. Can replace with a home page one day. """
        return redirect(url_for('show_branch'))



    @staticmethod
    @__app.route('/tree_view')
    def tree_view():
        tree_dict = TreeEngine.get_tree()
        return render_template("print/tree_view.html", tree_dict=tree_dict)

    @staticmethod
    @__app.route('/print_tree')
    def print_tree():
        """ Will eventually be replaced. For now, allows selection of any branch."""
        all_branches = WebUI.engine.get_branches()

        #should i send list for each depth?

        return render_template("print/print_tree.html", branches=all_branches)

    @classmethod
    def run(cls):
        from ui.routes.EditRoutes import EditRoutes
        from ui.routes.UserRoutes import UserRoutes

        cls.__app.config["SESSION_TYPE"] = "filesystem"
        cls.__app.secret_key = "my_secret_key"
        Session(cls.__app)
        cls.__app.run(host="0.0.0.0")

