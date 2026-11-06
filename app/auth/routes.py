
from urllib.parse import urlsplit

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)

from sqlalchemy.exc import SQLAlchemyError

from app.auth import auth_bp
from app.auth.forms import LoginForm, ChangePasswordForm
from app.auth.services import (
    authenticate_user,
    change_own_password,
    AuthenticationError,
)
from app.extensions import db
from app.services.audit import record_audit


def is_safe_redirect(target):
    if not target:
        return False

    parsed = urlsplit(target)

    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
        and "\\" not in target
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = authenticate_user(
                form.identifier.data,
                form.password.data,
            )

        except SQLAlchemyError:
            current_app.logger.exception(
                "Database error during authentication."
            )

            flash(
                "Unable to complete login. Please try again.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                form=form,
            ), 500

        if user is None:
            flash(
                "Invalid credentials or inactive account.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                form=form,
            )

        login_user(user, remember=False, fresh=True)

        flash(
            f"Welcome back, {user.username}.",
            "success",
        )

        next_page = request.args.get("next")

        if is_safe_redirect(next_page):
            return redirect(next_page)

        return redirect(url_for("dashboard.index"))

    return render_template(
        "auth/login.html",
        form=form,
    )


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = current_user._get_current_object()

        try:
            change_own_password(
                user=user,
                current_password=form.current_password.data,
                new_password=form.new_password.data,
            )

            logout_user()
            login_user(user, remember=False, fresh=True)

            flash("Your password has been changed successfully.", "success")
            return redirect(url_for("dashboard.index"))

        except AuthenticationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Password change failed.")
            flash("An unexpected error occurred. Please try again.", "danger")

    return render_template(
        "auth/change_password.html",
        form=form,
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    user = current_user._get_current_object()

    try:
        record_audit(
            actor=user,
            action="USER_LOGOUT",
            entity_type="User",
            entity_id=user.id,
            description=f"{user.username} logged out.",
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Unable to record logout audit event."
        )

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success",
    )

    return redirect(url_for("auth.login"))
