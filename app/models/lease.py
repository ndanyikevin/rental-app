
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin


class Lease(TimestampMixin, db.Model):
    __tablename__ = "leases"

    __table_args__ = (
        CheckConstraint(
            "monthly_rent IS NULL OR monthly_rent >= 0",
            name="ck_lease_rent_nonnegative"
        ),
        CheckConstraint(
            "deposit_amount >= 0",
            name="ck_lease_deposit_nonnegative"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    lease_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    unit_id = db.Column(
        db.Integer,
        db.ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    # UNIT: One rent charge for the entire unit.
    # INDIVIDUAL: Each tenant has an agreed rent amount.
    billing_mode = db.Column(
        db.String(20),
        nullable=False,
        default="UNIT"
    )

    monthly_rent = db.Column(
        db.Numeric(12, 2)
    )

    deposit_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="draft"
    )

    terms = db.Column(db.Text)

    unit = db.relationship(
        "Unit",
        back_populates="leases"
    )

    tenant_memberships = db.relationship(
        "LeaseTenant",
        back_populates="lease"
    )

    rent_charges = db.relationship(
        "RentCharge",
        back_populates="lease"
    )

    payments = db.relationship(
        "Payment",
        back_populates="lease"
    )

    def __repr__(self):
        return f"<Lease {self.lease_number}>"
