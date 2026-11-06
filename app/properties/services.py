
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Property
from app.services.audit import record_audit


class PropertyOperationError(Exception):
    """Raised when a property operation is invalid."""


def normalize_property_code(code):
    return code.strip().upper()


def get_property(property_id):
    return db.session.get(Property, property_id)


def get_properties(search=None, active_only=False):
    query = Property.query

    if active_only:
        query = query.filter(Property.is_active.is_(True))

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            db.or_(
                Property.name.ilike(search_term),
                Property.property_code.ilike(search_term),
                Property.town.ilike(search_term),
            )
        )

    return query.order_by(Property.name.asc()).all()


def _check_duplicate_code(code, exclude_id=None):
    query = Property.query.filter(
        func.lower(Property.property_code) == code.lower()
    )

    if exclude_id is not None:
        query = query.filter(Property.id != exclude_id)

    if query.first():
        raise PropertyOperationError(
            "A property with this code already exists."
        )


def create_property(data, acting_user):
    name = data["name"].strip()
    code = normalize_property_code(data["property_code"])

    if not name:
        raise PropertyOperationError("Property name is required.")

    if not code:
        raise PropertyOperationError("Property code is required.")

    _check_duplicate_code(code)

    property_record = Property(
        name=name,
        property_code=code,
        address=(data.get("address") or "").strip() or None,
        town=(data.get("town") or "").strip() or None,
        description=(data.get("description") or "").strip() or None,
        is_active=True,
    )

    try:
        db.session.add(property_record)
        db.session.flush()

        record_audit(
            actor=acting_user,
            action="PROPERTY_CREATED",
            entity_type="Property",
            entity_id=property_record.id,
            description=f"Created property {property_record.name}.",
            details={
                "property_code": property_record.property_code,
                "name": property_record.name,
            },
        )

        db.session.commit()
        return property_record

    except IntegrityError as error:
        db.session.rollback()
        raise PropertyOperationError(
            "A property with this code already exists."
        ) from error

    except SQLAlchemyError:
        db.session.rollback()
        raise


def update_property(property_id, data, acting_user):
    property_record = get_property(property_id)

    if property_record is None:
        raise PropertyOperationError("Property not found.")

    name = data["name"].strip()
    code = normalize_property_code(data["property_code"])

    if not name:
        raise PropertyOperationError("Property name is required.")

    if not code:
        raise PropertyOperationError("Property code is required.")

    _check_duplicate_code(code, exclude_id=property_id)

    old_values = {
        "name": property_record.name,
        "property_code": property_record.property_code,
        "address": property_record.address,
        "town": property_record.town,
        "description": property_record.description,
    }

    new_values = {
        "name": name,
        "property_code": code,
        "address": (data.get("address") or "").strip() or None,
        "town": (data.get("town") or "").strip() or None,
        "description": (data.get("description") or "").strip() or None,
    }

    changes = {
        key: {
            "before": old_values[key],
            "after": new_values[key],
        }
        for key in old_values
        if old_values[key] != new_values[key]
    }

    if not changes:
        return property_record

    try:
        for key, value in new_values.items():
            setattr(property_record, key, value)

        record_audit(
            actor=acting_user,
            action="PROPERTY_UPDATED",
            entity_type="Property",
            entity_id=property_record.id,
            description=f"Updated property {property_record.name}.",
            details=changes,
        )

        db.session.commit()
        return property_record

    except IntegrityError as error:
        db.session.rollback()
        raise PropertyOperationError(
            "A property with this code already exists."
        ) from error

    except SQLAlchemyError:
        db.session.rollback()
        raise


def set_property_active_status(property_id, active, acting_user):
    property_record = get_property(property_id)

    if property_record is None:
        raise PropertyOperationError("Property not found.")

    if property_record.is_active == active:
        return property_record

    previous_status = property_record.is_active

    try:
        property_record.is_active = active

        action = (
            "PROPERTY_ACTIVATED"
            if active
            else "PROPERTY_DEACTIVATED"
        )

        status_text = "activated" if active else "deactivated"

        record_audit(
            actor=acting_user,
            action=action,
            entity_type="Property",
            entity_id=property_record.id,
            description=f"Property {property_record.name} was {status_text}.",
            details={
                "previous_status": previous_status,
                "new_status": active,
            },
        )

        db.session.commit()
        return property_record

    except SQLAlchemyError:
        db.session.rollback()
        raise
