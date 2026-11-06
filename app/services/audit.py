
from app.extensions import db
from app.models import AuditLog


def record_audit(
    actor,
    action,
    entity_type,
    entity_id=None,
    description=None,
    details=None,
):
    """
    Add an audit record to the current database transaction.

    This function deliberately does not commit. The calling
    service commits the audit record together with the operation.
    """

    log = AuditLog(
        user_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        details=details or {},
    )

    db.session.add(log)

    return log
