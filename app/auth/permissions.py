
from functools import wraps

from flask import abort
from flask_login import current_user


def has_permission(user, module, action):
    """
    Check whether a user has permission to perform an action
    within a particular application module.

    Permissions are inherited exclusively from the user's role.
    """

    if not user or not user.is_authenticated:
        return False

    role = user.role

    if role is None:
        return False

    permissions = role.permissions or {}

    if not isinstance(permissions, dict):
        return False

    # Global wildcard: full application access.
    if "*" in permissions:
        global_actions = permissions["*"]

        if isinstance(global_actions, list) and "*" in global_actions:
            return True

    # Module-specific permissions.
    allowed_actions = permissions.get(module, [])

    if not isinstance(allowed_actions, list):
        return False

    return "*" in allowed_actions or action in allowed_actions


def permission_required(module, action):
    """
    Protect a route using role-based permissions.

    Example:
        @login_required
        @permission_required("properties", "view")
        def index():
            ...
    """

    def decorator(view_function):

        @wraps(view_function)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            if not has_permission(current_user, module, action):
                abort(403)

            return view_function(*args, **kwargs)

        return decorated_view

    return decorator
