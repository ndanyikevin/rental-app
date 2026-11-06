
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.property import Property
from app.models.unit import Unit
from app.services.audit import record_audit
from app.units.constants import COMMON_UNIT_TYPES


# ---------------------------------------------------------------------
# Constants and exceptions
# ---------------------------------------------------------------------

class UnitOperationError(Exception):
    """Raised when a unit operation violates a business rule."""


ALLOWED_STATUSES = {
    "available",
    "maintenance",
    "occupied",
}


# ---------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------

def get_unit(unit_id):
    """Retrieve a unit by its ID."""

    return db.session.get(Unit, unit_id)


def get_units(search=None, property_id=None, status=None):
    """Retrieve units with optional search and filters."""

    query = Unit.query.join(Property)

    if property_id:
        query = query.filter(
            Unit.property_id == property_id
        )

    if status:
        query = query.filter(
            Unit.status == status
        )

    if search and search.strip():
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Unit.unit_number.ilike(search_term),
                Unit.unit_type.ilike(search_term),
                Property.name.ilike(search_term),
                Property.property_code.ilike(search_term),
                Property.town.ilike(search_term),
            )
        )

    return query.order_by(
        Property.name.asc(),
        Unit.unit_number.asc(),
    ).all()


def get_active_properties():
    """Retrieve active properties for unit registration."""

    return Property.query.filter_by(
        is_active=True
    ).order_by(
        Property.name.asc()
    ).all()


# ---------------------------------------------------------------------
# Normalization and validation
# ---------------------------------------------------------------------

def _normalize_unit_number(unit_number):
    """Normalize unit numbers for consistent storage."""

    return (unit_number or "").strip().upper()


def _normalize_unit_type(data):
    """Resolve a predefined or custom unit type."""

    selected_type = (data.get("unit_type") or "").strip()
    custom_type = (data.get("custom_unit_type") or "").strip()

    if selected_type == "Other":
        if not custom_type:
            raise UnitOperationError(
                "Please specify the custom unit type."
            )

        if len(custom_type) > 50:
            raise UnitOperationError(
                "Custom unit type cannot exceed 50 characters."
            )

        return custom_type

    if selected_type not in COMMON_UNIT_TYPES:
        raise UnitOperationError(
            "Select a valid unit type."
        )

    return selected_type


def _normalize_integer(value, field_name):
    """Convert and validate a non-negative whole number."""

    try:
        number = int(value)

    except (TypeError, ValueError):
        raise UnitOperationError(
            f"{field_name} must be a valid whole number."
        )

    if number < 0:
        raise UnitOperationError(
            f"{field_name} cannot be negative."
        )

    return number


def _normalize_rent(value):
    """Convert rent to Decimal and validate its value."""

    try:
        rent = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError):
        raise UnitOperationError(
            "Enter a valid monthly rent."
        )

    if not rent.is_finite():
        raise UnitOperationError(
            "Monthly rent must be a finite number."
        )

    if rent < 0:
        raise UnitOperationError(
            "Monthly rent cannot be negative."
        )

    if rent.as_tuple().exponent < -2:
        raise UnitOperationError(
            "Monthly rent cannot have more than two decimal places."
        )

    return rent


def _get_property_id(data):
    """Validate the selected property ID."""

    try:
        property_id = int(data.get("property_id"))

    except (TypeError, ValueError):
        raise UnitOperationError(
            "Select a valid property."
        )

    if property_id <= 0:
        raise UnitOperationError(
            "Select a valid property."
        )

    return property_id


def _validate_unit_data(data):
    """Validate and normalize unit information."""

    unit_number = _normalize_unit_number(
        data.get("unit_number")
    )

    if not unit_number:
        raise UnitOperationError(
            "Unit number is required."
        )

    unit_type = _normalize_unit_type(data)

    bedrooms = _normalize_integer(
        data.get("bedrooms"),
        "Bedrooms",
    )

    bathrooms = _normalize_integer(
        data.get("bathrooms"),
        "Bathrooms",
    )

    default_rent = _normalize_rent(
        data.get("default_rent")
    )

    status = (
        data.get("status") or "available"
    ).strip()

    if status not in ALLOWED_STATUSES:
        raise UnitOperationError(
            "Invalid unit status."
        )

    description = (
        (data.get("description") or "").strip() or None
    )

    return {
        "unit_number": unit_number,
        "unit_type": unit_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "default_rent": default_rent,
        "status": status,
        "description": description,
    }


# ---------------------------------------------------------------------
# Business rule validation
# ---------------------------------------------------------------------

def _check_duplicate_unit_number(
    property_id,
    unit_number,
    exclude_id=None,
):
    """Ensure unit numbers are unique within a property."""

    query = Unit.query.filter(
        Unit.property_id == property_id,
        func.lower(Unit.unit_number) == unit_number.lower(),
    )

    if exclude_id is not None:
        query = query.filter(
            Unit.id != exclude_id
        )

    if query.first():
        raise UnitOperationError(
            "This unit number is already registered under this property."
        )


def _validate_status_transition(current_status, new_status):
    """Prevent manual changes to occupancy status."""

    if current_status == "occupied" and new_status != "occupied":
        raise UnitOperationError(
            "An occupied unit cannot have its status changed manually. "
            "Manage occupancy through lease records."
        )

    if current_status != "occupied" and new_status == "occupied":
        raise UnitOperationError(
            "A unit can only become occupied through a lease."
        )


# ---------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------

def _get_unit_snapshot(unit):
    """Capture unit values for audit comparison."""

    return {
        "unit_number": unit.unit_number,
        "unit_type": unit.unit_type,
        "bedrooms": unit.bedrooms,
        "bathrooms": unit.bathrooms,
        "default_rent": str(unit.default_rent),
        "status": unit.status,
        "description": unit.description,
    }


def _get_changes(old_values, new_values):
    """Return only values that have changed."""

    return {
        key: {
            "before": old_values[key],
            "after": new_values[key],
        }
        for key in old_values
        if old_values[key] != new_values[key]
    }


# ---------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------

def create_unit(data, acting_user):
    """Register a new unit under an active property."""

    property_id = _get_property_id(data)

    property_record = db.session.get(
        Property,
        property_id,
    )

    if property_record is None:
        raise UnitOperationError(
            "Selected property was not found."
        )

    if not property_record.is_active:
        raise UnitOperationError(
            "Units cannot be registered under an inactive property."
        )

    values = _validate_unit_data(data)

    if values["status"] == "occupied":
        raise UnitOperationError(
            "New units cannot be registered as occupied. "
            "Manage occupancy through lease records."
        )

    _check_duplicate_unit_number(
        property_id=property_id,
        unit_number=values["unit_number"],
    )

    unit = Unit(
        property_id=property_id,
        **values,
    )

    try:
        db.session.add(unit)
        db.session.flush()

        record_audit(
            actor=acting_user,
            action="UNIT_CREATED",
            entity_type="Unit",
            entity_id=unit.id,
            description=(
                f"Registered unit {unit.unit_number} "
                f"under property {property_record.name}."
            ),
            details={
                "property_id": property_record.id,
                "property_name": property_record.name,
                **_get_unit_snapshot(unit),
            },
        )

        db.session.commit()

        return unit

    except IntegrityError as error:
        db.session.rollback()

        raise UnitOperationError(
            "This unit number is already registered under this property."
        ) from error

    except SQLAlchemyError:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------

def update_unit(unit_id, data, acting_user):
    """Update the details of an existing unit."""

    unit = get_unit(unit_id)

    if unit is None:
        raise UnitOperationError(
            "Unit not found."
        )

    property_id = _get_property_id(data)

    if property_id != unit.property_id:
        raise UnitOperationError(
            "A unit cannot be moved to another property."
        )

    values = _validate_unit_data(data)

    _validate_status_transition(
        current_status=unit.status,
        new_status=values["status"],
    )

    _check_duplicate_unit_number(
        property_id=unit.property_id,
        unit_number=values["unit_number"],
        exclude_id=unit.id,
    )

    old_values = _get_unit_snapshot(unit)

    new_values = {
        **values,
        "default_rent": str(values["default_rent"]),
    }

    changes = _get_changes(
        old_values=old_values,
        new_values=new_values,
    )

    if not changes:
        return unit

    try:
        for key, value in values.items():
            setattr(unit, key, value)

        record_audit(
            actor=acting_user,
            action="UNIT_UPDATED",
            entity_type="Unit",
            entity_id=unit.id,
            description=(
                f"Updated unit {unit.unit_number}."
            ),
            details=changes,
        )

        db.session.commit()

        return unit

    except IntegrityError as error:
        db.session.rollback()

        raise UnitOperationError(
            "This unit number is already registered under this property."
        ) from error

    except SQLAlchemyError:
        db.session.rollback()
        raise
