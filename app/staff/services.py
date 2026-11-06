
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User, Role
from app.services.audit import record_audit


class StaffOperationError(Exception):
    """Raised when a staff management operation is not allowed."""


def get_role(role_id):
    role = db.session.get(Role, role_id)

    if role is None:
        raise StaffOperationError("Selected role does not exist.")

    return role


def get_staff(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        raise StaffOperationError("Staff account not found.")

    return user


def is_administrator(user):
    return user.role is not None and user.role.name == "Administrator"


def active_administrator_count():
    admin_role = Role.query.filter_by(
        name="Administrator"
    ).first()

    if admin_role is None:
        return 0

    return User.query.filter_by(
        role_id=admin_role.id,
        is_active=True
    ).count()


def ensure_administrator_remains(user, new_role=None, deactivate=False):
    if not user.is_active or not is_administrator(user):
        return

    losing_admin_access = (
        deactivate
        or (
            new_role is not None
            and new_role.name != "Administrator"
        )
    )

    if losing_admin_access and active_administrator_count() <= 1:
        raise StaffOperationError(
            "You cannot remove the last active Administrator."
        )


def create_staff(username, email, password, role_id, acting_user):
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email:
        raise StaffOperationError(
            "Username and email are required."
        )

    if len(password) < 12:
        raise StaffOperationError(
            "Password must contain at least 12 characters."
        )

    if User.query.filter_by(username=username).first():
        raise StaffOperationError("Username already exists.")

    if User.query.filter_by(email=email).first():
        raise StaffOperationError("Email already exists.")

    role = get_role(role_id)

    user = User(
        username=username,
        email=email,
        role=role,
        is_active=True,
    )

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()

        record_audit(
            actor=acting_user,
            action="STAFF_CREATED",
            entity_type="User",
            entity_id=user.id,
            description=f"Created staff account {username}.",
            details={
                "username": username,
                "email": email,
                "role": role.name,
            },
        )

        db.session.commit()
        return user

    except SQLAlchemyError:
        db.session.rollback()
        raise


def update_staff(user_id, username, email, role_id, acting_user):
    user = get_staff(user_id)

    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email:
        raise StaffOperationError(
            "Username and email are required."
        )

    existing_username = User.query.filter(
        User.username == username,
        User.id != user.id
    ).first()

    if existing_username:
        raise StaffOperationError("Username already exists.")

    existing_email = User.query.filter(
        User.email == email,
        User.id != user.id
    ).first()

    if existing_email:
        raise StaffOperationError("Email already exists.")

    new_role = get_role(role_id)

    if user.id == acting_user.id and user.role_id != new_role.id:
        raise StaffOperationError(
            "You cannot change your own role."
        )

    ensure_administrator_remains(user, new_role=new_role)

    old_values = {
        "username": user.username,
        "email": user.email,
        "role": user.role.name if user.role else None,
    }

    new_values = {
        "username": username,
        "email": email,
        "role": new_role.name,
    }

    changed_fields = [
        field
        for field in old_values
        if old_values[field] != new_values[field]
    ]

    user.username = username
    user.email = email
    user.role = new_role

    try:
        if changed_fields:
            record_audit(
                actor=acting_user,
                action="STAFF_UPDATED",
                entity_type="User",
                entity_id=user.id,
                description=f"Updated staff account {username}.",
                details={
                    "changed_fields": changed_fields,
                    "before": {
                        field: old_values[field]
                        for field in changed_fields
                    },
                    "after": {
                        field: new_values[field]
                        for field in changed_fields
                    },
                },
            )

        db.session.commit()
        return user

    except SQLAlchemyError:
        db.session.rollback()
        raise


def set_staff_active_status(user_id, active, acting_user):
    user = get_staff(user_id)

    if user.id == acting_user.id and not active:
        raise StaffOperationError(
            "You cannot deactivate your own account."
        )

    if not active:
        ensure_administrator_remains(
            user,
            deactivate=True
        )

    if user.is_active == active:
        return

    user.is_active = active

    # Invalidate all existing sessions for this account.
    user.session_version += 1

    action = "STAFF_ACTIVATED" if active else "STAFF_DEACTIVATED"

    try:
        record_audit(
            actor=acting_user,
            action=action,
            entity_type="User",
            entity_id=user.id,
            description=(
                f"{'Activated' if active else 'Deactivated'} "
                f"staff account {user.username}."
            ),
            details={
                "username": user.username,
                "is_active": active,
            },
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise


def reset_staff_password(user_id, new_password, acting_user):
    user = get_staff(user_id)

    if len(new_password) < 12:
        raise StaffOperationError(
            "Password must contain at least 12 characters."
        )

    user.set_password(new_password)

    # Invalidate all sessions for the affected account.
    user.session_version += 1

    try:
        record_audit(
            actor=acting_user,
            action="STAFF_PASSWORD_RESET",
            entity_type="User",
            entity_id=user.id,
            description=(
                f"Reset password for staff account {user.username}."
            ),
            details={
                "username": user.username,
            },
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise
