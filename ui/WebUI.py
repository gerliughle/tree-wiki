from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, current_user
from flask_session import Session
import os
from configparser import ConfigParser

from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from logic.Validate import Validate


class WebUI:
    __app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(__app)
    APP_NAME = "bonsaitree"

    MAX_IMAGE_SIZE_MB = 5
    USER_IMAGES_PATH = "ui/static/assets/USER_IMAGES/branch_images"
    MIN_HD_SPACE_GB = 10
    MAX_CAROUSEL_SIZE = 5

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()
        cls.usermanager = UserManager()

        from ui.routes.EditRoutes import EditRoutes
        from ui.routes.UserRoutes import UserRoutes
        from ui.routes.AdminRoutes import AdminRoutes

        home_path = os.environ['HOME']
        path = os.path.join(home_path, cls.APP_NAME)
        file = os.path.join(path, f"{cls.APP_NAME}.ini")
        if not os.path.exists(file):
            raise FileNotFoundError(f'{file} not found.')

        config_parser = ConfigParser()
        config_parser.read(file)
        secret_key = config_parser.get("App", "secret_key")
        env = config_parser.get("App", "environment", fallback="development")

        cls.__app.config["SESSION_TYPE"] = "mongodb"
        cls.__app.config["SESSION_MONGODB"] = TreeEngine.get_client()
        cls.__app.config["SESSION_MONGODB_DB"] = "BonsaiTree"
        cls.__app.config["SESSION_MONGODB_COLLECT"] = "sessions"
        cls.__app.secret_key = secret_key
        Session(cls.__app)

        cls.__app.config["SESSION_COOKIE_SECURE"] = env == "production"
        cls.__app.config["SESSION_COOKIE_HTTPONLY"] = True
        cls.__app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

        cls.__app.config["UPLOAD_FOLDER"] = cls.USER_IMAGES_PATH
        cls.__app.config["MAX_CONTENT_LENGTH"] = cls.MAX_IMAGE_SIZE_MB * 1024**2

        return cls.__app

    @classmethod
    def get_app(cls):
        """ Ensures only one Flask app. """
        return cls.__app

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        """ Flask-login required. Uses Str id, returns either User obj or None. """
        return UserManager.lookup_user_id(user_id)

    @staticmethod
    @__app.route('/show_branch', methods=["GET", "POST"])
    def show_branch():
        branch_id = Validate.make_objectid(request.args.get("branch"))
        branch = TreeEngine.lookup_branch(branch_id)
        if not branch:
            branch_id = None
        if request.args.get("branch") is not None and branch is None:
            flash(f"Error, branch not found.", "warning")
        if (branch_id is not None and branch is None) or branch_id is None: # lmao
            branch_name = "Japanese Maple"
            branch = WebUI.engine.lookup_branch_by_name(branch_name)
            branch_id = branch.id

        care_guide, breadcrumbs, category_list = WebUI.engine.get_care_guide(branch_id)

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
                    "entries": filtered_entries,
                    "branch_name": leaf.branch_name,
                    "end_chain": leaf.end_chain,
                }
                filtered_care_guide.append(filtered_leaf)

        # branch_has_image = branch.has_image

        # PROCESS IMAGE UPLOADS
        if request.method == 'POST':
            uploaded_branch_img = request.files["branch_img"]
            if uploaded_branch_img.filename != '':
                valid, image_ext, error = Validate.validate_image(uploaded_branch_img)
                if not valid:
                    flash(error, "warning")
                    return redirect(url_for("show_branch"))

                caption = request.form.get("image_caption")
                valid, caption, error = Validate.validate_input(
                    caption, "Image Caption", 0, 100, "text")
                if not valid:
                    flash(error, "warning")
                    return redirect(url_for("show_branch"))

                image_dict = {
                    "is_active": True,
                    "author_id": current_user.id,
                    "branch_id": branch_id,
                    "ext": image_ext,
                    "is_approved": False,
                    "quality": 3,
                    "caption": caption,
                    "name": str(f"'{branch.name}' Image by {current_user.username}"),
                }
                os.makedirs(WebUI.USER_IMAGES_PATH, exist_ok=True)
                user_image = TreeEngine.save_image(image_dict, "create")
                print(f"Image saved: {user_image.name}")
                uploaded_branch_img.save(os.path.join(WebUI.USER_IMAGES_PATH, str(user_image.id) + image_ext))
                flash(f"{user_image.name} uploaded. Awaiting moderation approval.", "success")

        branch_images = TreeEngine.get_branch_images(branch.id) # returns list of top 5 images (by qual) filenames

        children = TreeEngine.get_children_of_branch(branch.id)
        all_seasons = ["Spring", "Summer", "Fall", "Winter"]
        page_context = {
            "branch": branch,
            "care_guide": filtered_care_guide,
            "breadcrumbs": breadcrumbs,
            "category_list": TreeEngine.CATEGORIES,
            "phases": phases,
            "children": children,
            "all_seasons": all_seasons,
            "branch_images": branch_images
        }
        if current_user.is_authenticated:
            print(f"View: '{branch.name}' by '{current_user.username}'. Guide: {len(filtered_care_guide)} leaves.")
        else:
            print(f"View: '{branch.name}' by anon. Guide: {len(filtered_care_guide)} leaves.")

        # Sets or removes edit mode for session
        if request.args.get("mode") == "exit":
            session["mode"] = None
        if request.args.get("mode") == "edit" or session.get("mode") == "edit":
            if current_user.is_authenticated and current_user.role in ["admin", "editor"]:
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

    @classmethod
    def run(cls):
        cls.__app.run(host="0.0.0.0")
