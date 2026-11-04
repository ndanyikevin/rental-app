
from app.extensions import db
from app.models.base import TimestampMixin


class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    entity_type = db.Column(
        db.String(80),
        nullable=False
    )

    entity_id = db.Column(db.Integer)

    description = db.Column(db.Text)

    # Additional details about the action.
    details = db.Column(db.JSON)

    user = db.relationship(
        "User",
        back_populates="audit_logs"
    )

    def __repr__(self):
        return f"<AuditLog {self.action}: {self.entity_type}>"
