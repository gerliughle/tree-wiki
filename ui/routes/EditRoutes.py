from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from bson import ObjectId
from markupsafe import Markup

from logic.Validate import Validate
from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager

class EditRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @login_required
    @UserManager.role_required("admin", "editor")
    @__app.route('/create_branch', methods=['POST', 'GET'])
    def create_branch():
        """ Sets up create branch page.

        The branch from the form or arg sets the default parent branch for
        the selector. Should error out gracefully. """

        branch = None
        all_branches = TreeEngine.get_branches()
        branch_id_form = Validate.make_objectid(request.form.get("select_branch_id"))
        branch_id_arg = Validate.make_objectid(request.args.get("branch"))
        if branch_id_form:
            branch = TreeEngine.lookup_branch(branch_id_form)
        elif branch_id_arg:
            branch = TreeEngine.lookup_branch(branch_id_arg)
        if branch:
            return render_template("edit/create_branch.html", branches=all_branches, branch=branch)
        else:
            flash("Error. No branch selected.", "warning")
            print("Edit_route: Create branch. Branch not found.")
            return redirect(url_for("homepage"))

    @staticmethod
    @login_required
    @UserManager.role_required("admin", "editor")
    @__app.route('/do_create_branch', methods=['POST'])
    def do_create_branch():
        """ Creates a new branch. Requires title,  description and parent branch.

         Auto generates image name (not very robust)
         Validates and cleans inputs.
         """

        # Setting up variables to reload page in case of errors.
        parent_branch_id = Validate.make_objectid(request.form.get("parent_branch_id"))
        parent_branch = TreeEngine.lookup_branch(parent_branch_id)
        all_branches = TreeEngine.get_branches()
        if not parent_branch:
            flash("Error. No parent branch selected.", "warning")
            return redirect(url_for("homepage"))

        branch_name = request.form.get("branch_name")
        valid, branch_name, error = Validate.validate_input(
            branch_name, "Branch Name", 3, 30, "title")
        if not valid:
            flash(error, "warning")
            return render_template("edit/create_branch.html", branches=all_branches, branch=parent_branch)

        duplicate_branch = TreeEngine.lookup_branch(branch_name)
        if duplicate_branch:
            print(f"Attempt to create branch {branch_name} failed. Already exists.")
            flash("Error, this branch already exists!", "warning")
            return render_template("edit/create_branch.html", branches=all_branches, branch=parent_branch)


        if not parent_branch_id:
            flash("Error. No parent branch selected.", "warning")
            return redirect(url_for("create_branch"))
        branch_image = str(branch_name.lower().replace(" ", "_") + ".jpg")
        branch_description = request.form.get("branch_description")
        valid, branch_description, error = Validate.validate_input(
            branch_description, "Branch Description", 10, 200, "text")
        if not valid:
            flash(error, "warning")
            return render_template("edit/create_branch.html", branches=all_branches, branch=parent_branch)
        branch_author = current_user.id

        branch_dict = {
            "author_id": branch_author,
            "is_active": True,
            "name": branch_name,
            "description": branch_description,
            "image": branch_image,
            "parent_id": parent_branch_id
        }
        branch = TreeEngine.save_branch(branch_dict, "create")
        flash(f"Successfully created branch {branch.name}", "success")
        return render_template("print/print_tree.html", branch=branch)

    @staticmethod
    @__app.route('/edit_branch', methods=['POST', 'GET'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_branch():
        """ Sets up edit branch page.  """

        branch_id_form = Validate.make_objectid(request.form.get("select_branch_id"))
        branch_id_arg = Validate.make_objectid(request.args.get("branch"))
        if branch_id_form:
            branch = TreeEngine.lookup_branch(branch_id_form)
        elif branch_id_arg:
            branch = TreeEngine.lookup_branch(branch_id_arg)
        else:
            branch = None
        if not branch:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage"))
        all_branches = TreeEngine.get_branches()
        return render_template("edit/edit_branch.html", edit_branch=branch, branches=all_branches)

    @staticmethod
    @__app.route('/do_edit_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_edit_branch():
        """ Edits an existing branch.

        Checks if form inputs exist, are not blank, and do not match the original.
         If so, it adds them to an update dict and passes requests an edit.
         """
        all_branches = TreeEngine.get_branches()
        branch_id = Validate.make_objectid(request.form.get("branch_id"))
        original_branch = TreeEngine.lookup_branch(branch_id)
        if not original_branch:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage")) # no branch, so can't redirect to edit

        branch_edits = {"_id": branch_id}
        branch_name = request.form.get("branch_name")
        if branch_name != original_branch.name and branch_name != "": # Skip if blank or unchanged.
            valid, branch_name, error = Validate.validate_input(branch_name, "Branch Name", 3, 30, "title")
            if not valid:
                flash(error, "warning")
                return redirect(url_for("edit_branch", branches=all_branches, branch=original_branch.id))
            duplicate_branch = TreeEngine.lookup_branch_by_name(branch_name)
            if duplicate_branch:
                print(f"Attempt to create branch {branch_name} failed. Already exists.")
                flash("Error, this branch already exists.", "warning")
                return redirect(url_for("edit_branch", branches=all_branches, branch=original_branch.id))
            branch_edits["name"] = branch_name
            branch_edits["image"] = str(branch_name.lower().replace(" ", "_") + ".jpg")

        branch_description = request.form.get("branch_description")
        if branch_description != original_branch.description and branch_description != "":  # Skip if blank or unchanged.
            valid, branch_description, error = Validate.validate_input(
                branch_description, "Branch Description", 10, 200, "text")
            if not valid:
                flash(error, "warning")
                return redirect(url_for("edit_branch", branches=all_branches, branch=original_branch.id))
            branch_edits["description"] = branch_description

        parent_id = Validate.make_objectid(request.form.get("select_parent_id"))
        if parent_id != "" and parent_id != original_branch.parent_id:
            branch_edits["parent_id"] = parent_id

        if len(branch_edits) == 1: # No edits made.
            flash("No changes made. No edits saved.", "warning")
            return redirect(url_for("show_branch", branch=original_branch.id))

        branch_author = current_user.id
        branch_edits["author_id"] = branch_author
        updated_branch = TreeEngine.save_branch(branch_edits, "edit")
        flash(f"'{updated_branch.name}' branch was successfully updated.", "success")
        return redirect(url_for("show_branch", branch=updated_branch.id))

    @staticmethod
    @__app.route('/check_delete_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_branch():
        """ FIXME """
        delete_branch = ""
        if "select_branch_id" in request.form:
            delete_branch = TreeEngine.lookup_branch(ObjectId(request.form["select_branch_id"]))
        print(f"Delete branch name: {delete_branch.name=}")
        return render_template("edit/check_delete_branch.html", delete_branch=delete_branch)

    @staticmethod
    @__app.route('/do_delete_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_branch():
        """ FIXME """
        delete_name = ""
        if "branch_id" in request.form:
            delete_branch_id = ObjectId(request.form["branch_id"])
            delete_name = TreeEngine.delete_branch(delete_branch_id)
            flash(f"Successfully deleted branch: {delete_name}")
            return redirect(url_for("homepage"))
        else:
            flash(f"No branch to delete.", "warning")
            return redirect(url_for("homepage"))

    @staticmethod
    @__app.route('/check_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_branch():
        """ FIXME """
        disable_branch = ""
        if "select_branch_id" in request.form:
            disable_branch = TreeEngine.lookup_branch(ObjectId(request.form["select_branch_id"]))
        print(f"Disable branch name: {disable_branch.name=}")
        return render_template("edit/check_disable_branch.html", disable_branch=disable_branch)

    @staticmethod
    @__app.route('/do_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_branch():
        """ FIXME"""
        if "branch_id" in request.form:
            disable_branch_id = ObjectId(request.form["branch_id"])
            branch_dict = {"_id": disable_branch_id,
                           "is_active": False}
            disable_branch = TreeEngine.save_branch(branch_dict, "disable")
        return render_template("edit/confirm_branch_disabled.html", disable_branch=disable_branch)

    @staticmethod
    @__app.route('/select_edit_leaf')
    @login_required
    @UserManager.role_required("admin", "editor")
    def select_edit_leaf():
        """ FIXME"""
        all_branches = TreeEngine.get_branches()
        return render_template("edit/select_edit_leaf.html", all_branches=all_branches)
    #
    # @staticmethod
    # @__app.route('/select_edit_leaf_type', methods=['POST'])
    # @login_required
    # @UserManager.role_required("admin", "editor")
    # def select_edit_leaf_type():
    #     branch_id = ""
    #     if "select_branch_id" in request.form:
    #         branch_id = ObjectId(request.form["select_branch_id"])
    #
    #     branch = TreeEngine.lookup_branch(branch_id)
    #     branch_leaves = TreeEngine.get_leaves_for_branch(branch_id)
    #     inherited_leaves = TreeEngine.get_inherited_leaves(branch_id)
    #     print(f"Branch_leaves count: {len(branch_leaves)}. Inherited_leaves count: {len(inherited_leaves)}")
    #
    #     page_context = {
    #         "branch": branch,
    #         "branch_leaves": branch_leaves,
    #         "inherited_leaves": inherited_leaves,
    #         "all_categories": TreeEngine.CATEGORIES
    #     }
    #     return render_template('edit/select_edit_leaf_type.html', **page_context)

    @staticmethod
    @__app.route('/edit_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_leaf():
        """ Leaf editing router FIXME

        Either clone, edit, or create new.
        leaf: clone source, edit source, or None
        source_branch: branch the leaf is sourced from, or being edited, or None.
        target_branch: branch_id for this leaf. this is selected in step 1. if this matches source, you're editing
        category_name: if creating a new subcat, this will exist. there will be no leaf_id or source branch.
        """

        leaf = None  # The branch I am cloning from
        target_branch = None  # The branch I am creating a leaf for
        source_branch = None
        category_name = None

        if "target_branch_id" in request.form:
            target_branch_id = ObjectId(request.form["target_branch_id"])
            target_branch = TreeEngine.lookup_branch(target_branch_id)

        if "leaf_id" in request.form:
            leaf_id = ObjectId(request.form["leaf_id"])
            leaf = TreeEngine.lookup_leaf(leaf_id)
            source_branch_id = leaf.branch_id
            source_branch = TreeEngine.lookup_branch(source_branch_id)

        if "category_name" in request.form:
            category_name = request.form["category_name"]

        return render_template("edit/edit_leaf.html", leaf=leaf, source_branch=source_branch,
                               target_branch=target_branch, category_name=category_name)

    @staticmethod
    @__app.route('/do_edit_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_edit_leaf():
        """ FIXME more validation

        leaf_id is added if it is existing. Then in save_leaf, it uses that to determine different approach.
        It seems like this could be improved to only send changed data instead of all of it, but needs form update."""

        branch_id = ""
        category = ""
        subcategory = ""
        leaf_id = None

        if request.form.get("leaf_id"):
            leaf_id = ObjectId(request.form.get("leaf_id"))

        if "branch_id" in request.form:
            branch_id = ObjectId(request.form["branch_id"])
        if "category" in request.form:
            category = request.form["category"]
        if "subcategory" in request.form:
            subcategory = request.form["subcategory"]
        author_id = current_user.id  # Eventually, a more robust editor tracking system could be used. Now, last editor rewrites creator.
        season_list = ['Spring', 'Summer', 'Fall', 'Winter']
        seasons = []
        if request.form.get("season"):
            print(request.form.get("season"))
            seasons = request.form.getlist("season")
            if request.form["season"] in [season_list]:
                seasons.append(request.form["season"])
            elif request.form["season"] == "all_seasons":
                seasons = season_list
        entries = []
        for i in range(1, 5):
            if 'entry_enabled_' + str(i) in request.form:
                phases = []
                if 'phase_1st_' + str(i) in request.form:
                    phases.append("1st")
                if 'phase_2nd_' + str(i) in request.form:
                    phases.append("2nd")
                if 'phase_3rd+_' + str(i) in request.form:
                    phases.append("3rd+")
                if len(phases) == 0:
                    return render_template("error.html")
                entry = {"text": request.form["entry_text_" + str(i)], "phases": phases}
                entries.append(entry)
        leaf_dict = {
            "author_id": author_id,
            "is_active": True,
            "branch_id": branch_id,
            "category": category,
            "subcategory": subcategory,
            "seasons": seasons,
            "entries": entries
        }
        if leaf_id:
            leaf_dict["_id"] = leaf_id
            save_type = "edit"
        else:
            save_type = "create"
        leaf = TreeEngine.save_leaf(leaf_dict, save_type)
        if leaf:
            print(f"leaf created. Id: {leaf.id}")
        else:
            print(f"No leaf created and returned.")
        branch = TreeEngine.lookup_branch(branch_id)
        return render_template("edit/confirm_leaf_created.html", leaf=leaf, branch=branch)

    @staticmethod
    @__app.route('/check_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_leaf():
        delete_leaf = ""
        if "leaf_id" in request.form:
            delete_leaf = TreeEngine.lookup_leaf(ObjectId(request.form["leaf_id"]))
        if delete_leaf:
            print("Delete leaf selected")
        else:
            print("No leaf found to delete.")
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        return render_template("edit/check_delete_leaf.html", delete_leaf=delete_leaf, branch=branch)

    @staticmethod
    @__app.route('/do_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_leaf():
        """ FIXME"""
        delete_leaf_id = ""
        if "leaf_id" in request.form:
            delete_leaf_id = ObjectId(request.form["leaf_id"])
        delete_leaf = TreeEngine.lookup_leaf(delete_leaf_id)
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        TreeEngine.delete_leaf(delete_leaf_id)

        return render_template("edit/confirm_leaf_deleted.html", branch=branch)

    @staticmethod
    @__app.route('/check_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_leaf():
        """ FIXME """
        disable_leaf = ""
        if "leaf_id" in request.form:
            disable_leaf = TreeEngine.lookup_leaf(ObjectId(request.form["leaf_id"]))
        if disable_leaf:
            print("Disable leaf selected")
        else:
            print("No leaf found to delete.")
        branch = TreeEngine.lookup_branch(disable_leaf.branch_id)
        return render_template("edit/check_disable_leaf.html", disable_leaf=disable_leaf, branch=branch)

    @staticmethod
    @__app.route('/do_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_leaf():
        """ FIXME"""
        disable_leaf_id = ObjectId(request.form.get("leaf_id"))
        branch = TreeEngine.lookup_branch(TreeEngine.lookup_leaf(disable_leaf_id).branch_id)
        leaf_dict = {
            "_id": disable_leaf_id,
            "is_active": False
        }
        TreeEngine.save_leaf(leaf_dict, "disable")
        return render_template("edit/confirm_leaf_disabled.html", branch=branch)
