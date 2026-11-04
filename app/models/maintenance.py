
from app.extensions import db
from app.models.base import TimestampMixin


class Maintenance(TimestampMixin, db.Model):
    __tablename__ = "maintenance"

    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    unit_id = db.Column(
        db.Integer,
        db.ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=True
    )

    reported_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )

    assigned_to_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(db.Text)

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="open"
    )

    reported_date = db.Column(
        db.Date,
        nullable=False
    )

    completed_date = db.Column(db.Date)

    estimated_cost = db.Column(db.Numeric(12, 2))
    actual_cost = db.Column(db.Numeric(12, 2))

    property = db.relationship(
        "Property",
        back_populates="maintenance_records"
    )

    unit = db.relationship(
        "Unit",
        back_populates="maintenance_records"
    )

    reported_by = db.relationship(
        "User",
        back_populates="reported_maintenance",
        foreign_keys=[reported_by_user_id]
    )

    assigned_to = db.relationship(
        "User",
        back_populates="assigned_maintenance",
        foreign_keys=[assigned_to_user_id]
    )

    def __repr__(self):
        return f"<Maintenance {self.title}>"
