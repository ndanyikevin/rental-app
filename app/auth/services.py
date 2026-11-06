
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User
from app.models.base import utc_now
from app.services.audit import record_audit


class AuthenticationError(Exception):
    """Raised when an authentication operation is invalid."""


def authenticate_user(identifier, password):
    identifier = identifier.strip().lower()

    user = db.session.query(User).filter(
        or_(
            func.lower(User.username) == identifier,
            func.lower(User.email) == identifier
        )
    ).first()

    if user is None or not user.is_active:
        return None

    if not user.check_password(password):
        return None

    try:
        user.last_login_at = utc_now()

        record_audit(
            actor=user,
            action="USER_LOGIN",
            entity_type="User",
            entity_id=user.id,
            description=f"{user.username} logged in.",
        )

        db.session.commit()

        return user

    except SQLAlchemyError:
        db.session.rollback()
        raise


def change_own_password(user, current_password, new_password):
    if not user.check_password(current_password):
        raise AuthenticationError("Your current password is incorrect.")

    if user.check_password(new_password):
        raise AuthenticationError(
            "Your new password must be different from your current password."
        )

    if len(new_password) < 12:
        raise AuthenticationError(
            "Your new password must contain at least 12 characters."
        )

    user.set_password(new_password)

    # Invalidate all previously issued sessions.
    user.session_version += 1

    try:
        record_audit(
            actor=user,
            action="USER_PASSWORD_CHANGED",
            entity_type="User",
            entity_id=user.id,
            description=f"{user.username} changed their password.",
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise
