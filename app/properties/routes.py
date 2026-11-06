
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

from app.properties import properties_bp
from app.properties.forms import (
    PropertyForm,
    TogglePropertyStatusForm,
)
from app.properties.services import (
    PropertyOperationError,
    get_properties,
    get_property,
    create_property,
    update_property,
    set_property_active_status,
)
from app.auth.permissions import permission_required


@properties_bp.route("/")
@login_required
@permission_required("properties", "view")
def index():
    search = request.args.get("q", "").strip()

    properties = get_properties(search=search)

    return render_template(
        "properties/index.html",
        properties=properties,
        search=search,
    )


@properties_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("properties", "create")
def create():
    form = PropertyForm()

    if form.validate_on_submit():
        try:
            property_record = create_property(
                data=form.data,
                acting_user=current_user._get_current_object(),
            )

            flash(
                f"Property '{property_record.name}' was created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "properties.detail",
                    property_id=property_record.id,
                )
            )

        except PropertyOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            current_app.logger.exception("Property creation failed.")
            flash(
                "An unexpected error occurred while creating the property.",
                "danger",
            )

    return render_template(
        "properties/form.html",
        form=form,
        page_title="Register Property",
    )


@properties_bp.route("/<int:property_id>")
@login_required
@permission_required("properties", "view")
def detail(property_id):
    property_record = get_property(property_id)

    if property_record is None:
        flash("Property not found.", "danger")
        return redirect(url_for("properties.index"))

    status_form = TogglePropertyStatusForm()

    return render_template(
        "properties/detail.html",
        property=property_record,
        status_form=status_form,
    )


@properties_bp.route(
    "/<int:property_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@permission_required("properties", "edit")
def edit(property_id):
    property_record = get_property(property_id)

    if property_record is None:
        flash("Property not found.", "danger")
        return redirect(url_for("properties.index"))

    form = PropertyForm(obj=property_record)

    if form.validate_on_submit():
        try:
            update_property(
                property_id=property_id,
                data=form.data,
                acting_user=current_user._get_current_object(),
            )

            flash(
                "Property details updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "properties.detail",
                    property_id=property_id,
                )
            )

        except PropertyOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            current_app.logger.exception("Property update failed.")
            flash(
                "An unexpected error occurred while updating the property.",
                "danger",
            )

    return render_template(
        "properties/form.html",
        form=form,
        page_title="Edit Property",
        property=property_record,
    )


@properties_bp.route(
    "/<int:property_id>/toggle-status",
    methods=["POST"],
)
@login_required
@permission_required("properties", "edit")
def toggle_status(property_id):
    form = TogglePropertyStatusForm()

    if not form.validate_on_submit():
        flash("Invalid request. Please try again.", "danger")
        return redirect(
            url_for("properties.detail", property_id=property_id)
        )

    property_record = get_property(property_id)

    if property_record is None:
        flash("Property not found.", "danger")
        return redirect(url_for("properties.index"))

    try:
        new_status = not property_record.is_active

        set_property_active_status(
            property_id=property_id,
            active=new_status,
            acting_user=current_user._get_current_object(),
        )

        message = (
            "Property activated successfully."
            if new_status
            else "Property deactivated successfully."
        )

        flash(message, "success")

    except SQLAlchemyError:
        current_app.logger.exception("Property status update failed.")
        flash(
            "An unexpected error occurred while changing property status.",
            "danger",
        )

    return redirect(
        url_for("properties.detail", property_id=property_id)
    )
