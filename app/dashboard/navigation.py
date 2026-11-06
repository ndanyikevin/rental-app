
from app.auth.permissions import has_permission


NAVIGATION = [
    {
        "group": "Overview",
        "items": [
            {
                "label": "Dashboard",
                "endpoint": "dashboard.index",
                "module": "dashboard",
                "action": "view",
                "icon": "dashboard",
            },
        ],
    },
    {
        "group": "Administration",
        "items": [
            {
                "label": "Staff Management",
                "endpoint": "staff.index",
                "module": "staff",
                "action": "view",
                "icon": "users",
            },
        ],
    },
    {
        "group": "Account",
        "items": [
            {
                "label": "Change Password",
                "endpoint": "auth.change_password",
                "module": None,
                "action": None,
                "icon": "lock",
            },
        ],
    },
]


def get_navigation(user):
    """
    Return navigation items accessible to the current user.

    Items without module permissions are available to every
    authenticated user. Other items require the specified permission.
    """

    visible_groups = []

    for group in NAVIGATION:
        visible_items = []

        for item in group["items"]:
            module = item["module"]
            action = item["action"]

            if module is None:
                visible_items.append(item)
                continue

            if has_permission(user, module, action):
                visible_items.append(item)

        if visible_items:
            visible_groups.append({
                "group": group["group"],
                "items": visible_items,
            })

    return visible_groups
