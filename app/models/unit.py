
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin


class Unit(TimestampMixin, db.Model):
    __tablename__ = "units"

    __table_args__ = (
        db.UniqueConstraint(
            "property_id",
            "unit_number",
            name="uq_property_unit_number"
        ),
        CheckConstraint(
            "default_rent >= 0",
            name="ck_unit_default_rent_nonnegative"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    unit_number = db.Column(
        db.String(50),
        nullable=False
    )

    unit_type = db.Column(db.String(50))

    bedrooms = db.Column(db.Integer, default=1)
    bathrooms = db.Column(db.Integer, default=1)

    default_rent = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="available"
    )

    description = db.Column(db.Text)

    property = db.relationship(
        "Property",
        back_populates="units"
    )

    leases = db.relationship(
        "Lease",
        back_populates="unit"
    )

    maintenance_records = db.relationship(
        "Maintenance",
        back_populates="unit"
    )

    def __repr__(self):
        return f"<Unit {self.unit_number}>"
