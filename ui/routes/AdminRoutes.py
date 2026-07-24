from ui.WebUI import WebUI
from flask import render_template, request, redirect, url_for

class AdminRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/admin_dashboard')
    def admin_dashboard():
        return render_template("admin/admin_dashboard.html")
