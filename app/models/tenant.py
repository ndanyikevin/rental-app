
from app.extensions import db
from app.models.base import TimestampMixin


class Tenant(TimestampMixin, db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(
        db.String(80),
        nullable=False
    )

    last_name = db.Column(
        db.String(80),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )

    email = db.Column(db.String(120))

    identification_number = db.Column(
        db.String(80),
        unique=True
    )

    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(30))

    notes = db.Column(db.Text)

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    lease_memberships = db.relationship(
        "LeaseTenant",
        back_populates="tenant"
    )

    payments = db.relationship(
        "Payment",
        back_populates="tenant"
    )

    def __repr__(self):
        return f"<Tenant {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
