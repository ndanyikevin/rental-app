
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
        "group": "Management",
        "items": [
            {
                "label": "Properties",
                "endpoint": "properties.index",
                "module": "properties",
                "action": "view",
                "icon": "building-2",
            },
            {
                "label": "Units",
                "endpoint": "units.index",
                "module": "units",
                "action": "view",
                "icon": "door-open",
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
    """Return navigation groups containing only accessible items."""

    visible_groups = []

    for group in NAVIGATION:
        visible_items = [
            item
            for item in group["items"]
            if item["module"] is None
            or has_permission(user, item["module"], item["action"])
        ]

        if visible_items:
            visible_groups.append({
                "group": group["group"],
                "items": visible_items,
            })

    return visible_groups
