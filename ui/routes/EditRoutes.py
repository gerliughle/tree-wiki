from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

from logic.Validate import Validate
from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager

class EditRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/create_branch', methods=['POST', 'GET'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def create_branch():
        """ Sets up create branch page.

        The branch from the form or arg sets the default parent branch for
        the selector. Should error out gracefully. """

        all_branches = TreeEngine.get_branches()
        branch_id = Validate.make_objectid(request.form.get("select_branch_id"))
        branch = TreeEngine.lookup_branch(branch_id)

        if not branch:
            flash("Error. No branch selected.", "warning")
            print("Edit_route: Create branch. Branch not found.")
            return redirect(url_for("homepage"))
        else:
            return render_template("edit/create_branch.html", branches=all_branches, branch=branch)

    @staticmethod
    @__app.route('/do_create_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
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
        return redirect(url_for("show_branch", branch=branch.id))

    @staticmethod
    @__app.route('/edit_branch', methods=['POST', 'GET'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_branch():
        """ Sets up edit branch page.  """

        branch_id = Validate.make_objectid(request.form.get("select_branch_id"))
        branch = TreeEngine.lookup_branch(branch_id)
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
                return render_template("edit/edit_branch.html", edit_branch=original_branch, branches=all_branches)
            duplicate_branch = TreeEngine.lookup_branch_by_name(branch_name)
            if duplicate_branch:
                print(f"Attempt to create branch {branch_name} failed. Already exists.")
                flash("Error, this branch already exists.", "warning")
                return render_template("edit/edit_branch.html", edit_branch=original_branch, branches=all_branches)
            branch_edits["name"] = branch_name
            branch_edits["image"] = str(branch_name.lower().replace(" ", "_") + ".jpg")

        branch_description = request.form.get("branch_description")
        if branch_description != original_branch.description and branch_description != "":  # Skip if blank or unchanged.
            valid, branch_description, error = Validate.validate_input(
                branch_description, "Branch Description", 10, 200, "text")
            if not valid:
                flash(error, "warning")
                return render_template("edit/edit_branch.html", edit_branch=original_branch, branches=all_branches)
            branch_edits["description"] = branch_description

        parent_id = Validate.make_objectid(request.form.get("select_parent_id"))
        if parent_id is not None and parent_id != original_branch.parent_id:
            print("Parent id updated")
            branch_edits["parent_id"] = parent_id
        else:
            print("Parent id not updated")

        if len(branch_edits) == 1: # No edits made.
            flash("No changes made. No edits saved.", "warning")
            return render_template("edit/edit_branch.html", edit_branch=original_branch, branches=all_branches)

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
        """ Confirms that you want to delete a branch """
        delete_branch_id = Validate.make_objectid(request.form.get("select_branch_id"))
        delete_branch = TreeEngine.lookup_branch(delete_branch_id)
        if not delete_branch:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage"))
        return render_template("edit/check_delete_branch.html", delete_branch=delete_branch)

    @staticmethod
    @__app.route('/do_delete_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_branch():
        """ Permanently deletes a branch. """

        delete_branch_id = Validate.make_objectid(request.form.get("branch_id"))
        delete_branch = TreeEngine.lookup_branch(delete_branch_id)
        if not delete_branch:
            flash("Error. No branch selected.", "warning")
        delete_name = TreeEngine.delete_branch(delete_branch.id)
        flash(f"'{delete_name}' branch was successfully deleted.", "success")
        return redirect(url_for("homepage"))

    @staticmethod
    @__app.route('/check_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_branch():
        """ Sets up disable branch confirmation page. """
        disable_branch_id = Validate.make_objectid(request.form.get("select_branch_id"))
        disable_branch = TreeEngine.lookup_branch(disable_branch_id)
        if not disable_branch:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage"))
        return render_template("edit/check_disable_branch.html", disable_branch=disable_branch)

    @staticmethod
    @__app.route('/do_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_branch():
        """ Disables branch."""
        branch_id = Validate.make_objectid(request.form.get("branch_id"))
        if not branch_id:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage"))
        branch_dict = {"_id": branch_id,
                       "is_active": False}
        disable_branch = TreeEngine.save_branch(branch_dict, "disable")
        flash(f"'{disable_branch.name}' branch was successfully disabled.", "success")
        return redirect(url_for("homepage"))

    @staticmethod
    @__app.route('/edit_leaf', methods=['POST', 'GET'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_leaf():
        """ Sets up leaf edit page.

        Either clone, edit, or create new.

        leaf: clone source, edit source, or None.
        source_branch: branch the leaf is sourced from, or being edited, or None.
        target_branch: branch_id for this leaf. this is selected in step 1. if this matches source, you're editing
        category_name: if creating a new subcat, this will exist. there will be no leaf_id or source branch.

        from leaf.html in edit mode:
         <input type="hidden" name="target_branch_id" value="{{ branch.id }}">
         <input type="hidden" name="branch_id" value="{{ branch.id }}">
         <input type="hidden" name="leaf_id" value="{{ leaf.id }}">
        """

        target_branch_id = Validate.make_objectid(request.form.get("target_branch_id"))
        target_branch = TreeEngine.lookup_branch(target_branch_id)
        if not target_branch:
            flash("Error. No target branch selected.", "warning")
            return redirect(url_for("homepage"))

        leaf_id = Validate.make_objectid(request.form.get("leaf_id"))
        leaf = TreeEngine.lookup_leaf(leaf_id)
        if leaf:
            source_branch_id = leaf.branch_id
            source_branch = TreeEngine.lookup_branch(source_branch_id)
        else:
            source_branch = None
        category_name = request.form.get("category_name") # If this is detected on the edit_leaf page, it goes into subcat creation mode.

        return render_template("edit/edit_leaf.html", leaf=leaf, source_branch=source_branch,
                               target_branch=target_branch, category_name=category_name)

    @staticmethod
    @__app.route('/do_edit_leaf', methods=['POST', 'GET'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_edit_leaf():
        """

        Leaf editor.
        leaf_id is added if it is existing. Then in save_leaf, it uses that to determine different approach.
        It seems like this could be improved to only send changed data instead of all of it, but needs form update.

        Season can either be one season or all of them.
        There are four possible entries, each one is checked for phases and text is validated. """

        leaf_id = Validate.make_objectid(request.form.get("leaf_id"))
        leaf = TreeEngine.lookup_leaf(leaf_id)

        branch_id = Validate.make_objectid(request.form.get("branch_id")) # target branch?
        branch = TreeEngine.lookup_branch(branch_id)

        source_branch_id = Validate.make_objectid(request.form.get("source_branch_id"))
        source_branch = TreeEngine.lookup_branch(source_branch_id)

        if not branch_id:
            flash("Error. No branch selected.", "warning")
            return redirect(url_for("homepage"))

        category = request.form.get("category")
        category_arg = request.form.get("category_arg") # This is used to reset redirect. It is complicated, but
        # when a category is sent it makes the leaf go into new subcategory mode, so I only want to send one when
        # one was originally sent.
        subcategory = request.form.get("subcategory")
        print(f"{subcategory=}")
        if subcategory:
            valid, subcategory, error = Validate.validate_input(subcategory, "Subcategory", 5, 30, "title" )
            if not valid:
                flash(error, "warning")
                return render_template("edit/edit_leaf.html",
                                       leaf=leaf,
                                       source_branch=source_branch,
                                       target_branch=branch,
                                       category_name=category_arg)

        if not (category or subcategory):
            flash("Error, missing necessary category/subcategory.", "warning")
            return redirect(url_for("show_branch", branch=branch_id))

        author_id = current_user.id  # Eventually, a more robust editor tracking system could be used. Now, last editor rewrites creator.
        season= request.form.get("season")

        if season == "all_seasons":
            seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        elif season is None:
            flash("Error, select either one season or All Seasons.", "warning")
            return render_template("edit/edit_leaf.html",
                                   leaf=leaf,
                                   source_branch=source_branch,
                                   target_branch=branch,
                                   category_name=category_arg)
        else:
            seasons = [season]

        end_chain = False if request.form.get("allow_inherit") == False else True

        # Entry loop. Each leaf can have up to 4 entries for different phases.

        entries = []
        for i in range(1, 5):
            if request.form.get(f"entry_enabled_{i}"):
                phases = []
                for phase in ["1st", "2nd", "3rd+"]:
                    if request.form.get(f"phase_{phase}_{i}"):
                        phases.append(phase)
                print(f"Phases {i}: {phases}")
                if len(phases) == 0:
                    flash(f"Error in Entry {i}. Must select at least one phase.", "warning")
                    return render_template("edit/edit_leaf.html",
                                           leaf=leaf,
                                           source_branch=source_branch,
                                           target_branch=branch,
                                           category_name=category_arg)
                entry_text = request.form.get("entry_text_" + str(i))
                valid, entry, error = Validate.validate_input(entry_text, "Entry " + str(i),
                                                              0, 400, kind="text")
                if not valid:
                    flash(error, "warning")
                    return render_template("edit/edit_leaf.html",
                                           leaf=leaf,
                                           source_branch=source_branch,
                                           target_branch=branch,
                                           category_name=category_arg)
                entry = {"text": entry_text, "phases": phases}
                entries.append(entry)

        leaf_dict = {
            "author_id": author_id,
            "is_active": True,
            "branch_id": branch_id,
            "category": category,
            "subcategory": subcategory,
            "seasons": seasons,
            "entries": entries,
            "end_chain": end_chain,
        }
        if leaf_id:
            leaf_dict["_id"] = leaf_id
            save_type = "edit"
        else:
            save_type = "create"
        leaf = TreeEngine.save_leaf(leaf_dict, save_type)
        if leaf and save_type == "edit":
            print(f"leaf edited. Id: {leaf.id}")
            flash("Successfully edited leaf.", "success")
        elif leaf and save_type == "create":
            print(f"leaf created. Id: {leaf.id}")
            flash("Successfully created leaf.", "success")
        else:
            print(f"Error. No leaf created.")
            flash("Error creating leaf.", "warning")
        return redirect(url_for("show_branch", branch=leaf.branch_id))


    @staticmethod
    def verify_leaf():
        """ Used multiple times. """
        leaf_id = Validate.make_objectid(request.form.get("leaf_id"))
        leaf = TreeEngine.lookup_leaf(leaf_id)
        branch = TreeEngine.lookup_branch(leaf.branch_id)
        if not branch:
            flash("Error, no branch selected.", "warning")
            return redirect(url_for("homepage"))
        if not leaf:
            flash("Error. No leaf selected.")
            return redirect(url_for("show_branch", branch=branch.id))
        return leaf_id, leaf, branch

    @staticmethod
    @__app.route('/check_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_leaf():
        """ Select leaf to delete. """
        leaf_id, leaf, branch = EditRoutes.verify_leaf()

        return render_template("edit/check_delete_leaf.html", delete_leaf=leaf, branch=branch)


    @staticmethod
    @__app.route('/do_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_leaf():
        """ Delete leaf"""
        leaf_id, leaf, branch = EditRoutes.verify_leaf()
        TreeEngine.delete_leaf(leaf_id)
        return redirect(url_for("show_branch", branch=branch.id))

    @staticmethod
    @__app.route('/check_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_leaf():
        """ Select leaf to disable """
        leaf_id, leaf, branch = EditRoutes.verify_leaf()
        return render_template("edit/check_disable_leaf.html", disable_leaf=leaf, branch=branch)

    @staticmethod
    @__app.route('/do_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_leaf():
        """ Disables leaf by changing is_active status. """
        leaf_id, leaf, branch = EditRoutes.verify_leaf()
        leaf_dict = {
            "_id": leaf_id,
            "is_active": False
        }
        TreeEngine.save_leaf(leaf_dict, "disable")
        return redirect(url_for("show_branch", branch=branch.id))
