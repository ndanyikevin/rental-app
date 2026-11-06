
import logging

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User, Role
from app.auth.permissions import permission_required

from app.staff import staff_bp
from app.staff.forms import (
    StaffForm,
    CreateStaffForm,
    ResetStaffPasswordForm,
)
from app.staff.services import (
    StaffOperationError,
    create_staff,
    update_staff,
    set_staff_active_status,
    reset_staff_password,
)


def role_choices():
    return [
        (role.id, role.name)
        for role in Role.query.order_by(Role.name).all()
    ]


def handle_database_error(message):
    db.session.rollback()
    current_app.logger.exception(message)
    flash(
        "The operation could not be completed because of a database error.",
        "danger",
    )


@staff_bp.route("/")
@login_required
@permission_required("staff", "view")
def index():
    staff_members = User.query.order_by(User.username).all()

    return render_template(
        "staff/index.html",
        staff_members=staff_members,
    )


@staff_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("staff", "create")
def create():
    form = CreateStaffForm()
    form.role_id.choices = role_choices()

    if form.validate_on_submit():
        try:
            create_staff(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role_id=form.role_id.data,
                acting_user=current_user,
            )

            flash("Staff account created successfully.", "success")
            return redirect(url_for("staff.index"))

        except StaffOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            handle_database_error("Database error while creating staff.")

    return render_template(
        "staff/form.html",
        form=form,
        page_title="Add staff member",
        button_label="Create staff member",
    )


@staff_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("staff", "edit")
def edit(user_id):
    member = db.session.get(User, user_id)

    if member is None:
        flash("Staff account not found.", "danger")
        return redirect(url_for("staff.index"))

    form = StaffForm(obj=member)
    form.role_id.choices = role_choices()

    if request.method == "GET":
        form.role_id.data = member.role_id

    if form.validate_on_submit():
        try:
            update_staff(
                user_id=member.id,
                username=form.username.data,
                email=form.email.data,
                role_id=form.role_id.data,
                acting_user=current_user,
            )

            flash("Staff details updated successfully.", "success")
            return redirect(url_for("staff.index"))

        except StaffOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            handle_database_error("Database error while updating staff.")

    return render_template(
        "staff/form.html",
        form=form,
        page_title="Edit staff member",
        button_label="Save changes",
    )


@staff_bp.route("/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@permission_required("staff", "edit")
def toggle_status(user_id):
    member = db.session.get(User, user_id)

    if member is None:
        flash("Staff account not found.", "danger")
        return redirect(url_for("staff.index"))

    try:
        set_staff_active_status(
            user_id=member.id,
            active=not member.is_active,
            acting_user=current_user,
        )

        status = "activated" if member.is_active else "deactivated"
        flash(f"Staff account {status} successfully.", "success")

    except StaffOperationError as error:
        flash(str(error), "danger")

    except SQLAlchemyError:
        handle_database_error("Database error while changing staff status.")

    return redirect(url_for("staff.index"))


@staff_bp.route(
    "/<int:user_id>/reset-password",
    methods=["GET", "POST"],
)
@login_required
@permission_required("staff", "edit")
def reset_password(user_id):
    member = db.session.get(User, user_id)

    if member is None:
        flash("Staff account not found.", "danger")
        return redirect(url_for("staff.index"))

    form = ResetStaffPasswordForm()

    if form.validate_on_submit():
        try:
            reset_staff_password(
                user_id=member.id,
                new_password=form.password.data,
                acting_user=current_user,
            )

            flash(
                f"Password reset successfully for {member.username}.",
                "success",
            )
            return redirect(url_for("staff.index"))

        except StaffOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            handle_database_error("Database error while resetting password.")

    return render_template(
        "staff/reset_password.html",
        form=form,
        member=member,
    )
