
from flask import render_template
from flask_login import login_required, current_user

from app.dashboard import dashboard_bp
from app.dashboard.navigation import get_navigation
from app.auth.permissions import permission_required


def get_dashboard_content(user):
    role_name = user.role.name if user.role else ""

    dashboards = {
        "Administrator": {
            "title": "Administrator Dashboard",
            "description": "Monitor the entire rental management operation and manage system users and activities.",
            "welcome": "Here's an overview of your business.",
        },
        "Manager": {
            "title": "Management Dashboard",
            "description": "Monitor properties, occupancy, tenants, leases and day-to-day property operations.",
            "welcome": "Here's your operational overview.",
        },
        "Accountant": {
            "title": "Finance Dashboard",
            "description": "Manage rent collections, payments, expenses and financial reporting.",
            "welcome": "Here's your financial workspace.",
        },
        "Caretaker": {
            "title": "Maintenance Dashboard",
            "description": "View property information and manage your assigned maintenance responsibilities.",
            "welcome": "Here are your maintenance activities.",
        },
    }

    return dashboards.get(role_name, {
        "title": "Dashboard",
        "description": "Welcome to your RentalHub workspace.",
        "welcome": "Here's your workspace overview.",
    })


@dashboard_bp.route("/")
@login_required
@permission_required("dashboard", "view")
def index():
    user = current_user._get_current_object()

    return render_template(
        "dashboard/index.html",
        user=user,
        navigation=get_navigation(user),
        dashboard=get_dashboard_content(user),
    )
