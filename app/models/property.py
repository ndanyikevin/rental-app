
from app.extensions import db
from app.models.base import TimestampMixin


class Property(TimestampMixin, db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )

    property_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    address = db.Column(db.String(255))
    town = db.Column(db.String(100))
    description = db.Column(db.Text)

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    units = db.relationship(
        "Unit",
        back_populates="property"
    )

    expenses = db.relationship(
        "Expense",
        back_populates="property"
    )

    maintenance_records = db.relationship(
        "Maintenance",
        back_populates="property"
    )

    def __repr__(self):
        return f"<Property {self.name}>"
