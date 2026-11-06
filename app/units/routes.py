
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

from app.units import units_bp
from app.units.forms import UnitForm
from app.units.constants import COMMON_UNIT_TYPES
from app.units.services import (
    UnitOperationError,
    get_unit,
    get_units,
    get_active_properties,
    create_unit,
    update_unit,
)
from app.auth.permissions import permission_required
from app.models.property import Property


@units_bp.route("/")
@login_required
@permission_required("units", "view")
def index():
    search = request.args.get("q", "").strip()
    property_filter = request.args.get("property_id", "").strip()
    status_filter = request.args.get("status", "").strip()

    try:
        property_id = int(property_filter) if property_filter else None
    except ValueError:
        property_id = None
        property_filter = ""

    allowed_statuses = {"available", "occupied", "maintenance"}

    if status_filter not in allowed_statuses:
        status_filter = ""

    units = get_units(
        search=search,
        property_id=property_id,
        status=status_filter or None,
    )

    properties = get_active_properties()

    return render_template(
        "units/index.html",
        units=units,
        properties=properties,
        search=search,
        selected_property=property_filter,
        selected_status=status_filter,
    )


@units_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("units", "create")
def create():
    form = UnitForm()

    properties = get_active_properties()

    form.property_id.choices = [
        (0, "Select a property")
    ] + [
        (property_record.id, (
            f"{property_record.name} "
            f"({property_record.property_code})"
        ))
        for property_record in properties
    ]

    if not properties:
        flash(
            "There are no active properties available. "
            "Register or activate a property first.",
            "warning",
        )
        return redirect(url_for("properties.index"))

    if form.validate_on_submit():
        try:
            unit = create_unit(
                data=form.data,
                acting_user=current_user._get_current_object(),
            )

            flash(
                f"Unit {unit.unit_number} was registered successfully.",
                "success",
            )

            return redirect(
                url_for("units.detail", unit_id=unit.id)
            )

        except UnitOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            current_app.logger.exception("Unit creation failed.")
            flash(
                "An unexpected error occurred while registering the unit.",
                "danger",
            )

    return render_template(
        "units/form.html",
        form=form,
        page_title="Register Unit",
    )


@units_bp.route("/<int:unit_id>")
@login_required
@permission_required("units", "view")
def detail(unit_id):
    unit = get_unit(unit_id)

    if unit is None:
        flash("Unit not found.", "danger")
        return redirect(url_for("units.index"))

    return render_template(
        "units/detail.html",
        unit=unit,
    )


@units_bp.route("/<int:unit_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("units", "edit")
def edit(unit_id):
    unit = get_unit(unit_id)

    if unit is None:
        flash("Unit not found.", "danger")
        return redirect(url_for("units.index"))

    form = UnitForm(obj=unit)
    # Support editing unit types that were previously entered as custom types.
    if request.method == "GET" and unit.unit_type not in COMMON_UNIT_TYPES:
        form.unit_type.data = "Other"
        form.custom_unit_type.data = unit.unit_type or ""

    properties = get_active_properties()

    # Include the current property even if it has since been deactivated.
    if not unit.property.is_active:
        properties.append(unit.property)

    form.property_id.choices = [
        (property_record.id, (
            f"{property_record.name} "
            f"({property_record.property_code})"
        ))
        for property_record in properties
    ]

    # Occupied units must retain their existing status while being edited.
    if unit.status == "occupied":
        form.status.choices = [
            ("available", "Available"),
            ("maintenance", "Under maintenance"),
            ("occupied", "Occupied"),
        ]

    if form.validate_on_submit():
        try:
            update_unit(
                unit_id=unit_id,
                data=form.data,
                acting_user=current_user._get_current_object(),
            )

            flash(
                f"Unit {unit.unit_number} was updated successfully.",
                "success",
            )

            return redirect(
                url_for("units.detail", unit_id=unit_id)
            )

        except UnitOperationError as error:
            flash(str(error), "danger")

        except SQLAlchemyError:
            current_app.logger.exception("Unit update failed.")
            flash(
                "An unexpected error occurred while updating the unit.",
                "danger",
            )

    return render_template(
        "units/form.html",
        form=form,
        page_title="Edit Unit",
        unit=unit,
    )
