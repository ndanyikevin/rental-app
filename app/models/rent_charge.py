
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin

from decimal import Decimal


class RentCharge(TimestampMixin, db.Model):
    __tablename__ = "rent_charges"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_rent_charge_amount_positive"
        ),
        db.UniqueConstraint(
            "lease_id",
            "tenant_id",
            "period_start",
            name="uq_lease_tenant_rent_period"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    lease_id = db.Column(
        db.Integer,
        db.ForeignKey("leases.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    description = db.Column(
        db.String(255),
        nullable=False,
        default="Monthly rent"
    )

    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)

    due_date = db.Column(db.Date, nullable=False)

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="posted"
    )

    lease = db.relationship(
        "Lease",
        back_populates="rent_charges"
    )

    tenant = db.relationship("Tenant")

    allocations = db.relationship(
        "PaymentAllocation",
        back_populates="rent_charge"
    )

    @property
    def amount_paid(self):
        return sum(
            (allocation.amount for allocation in self.allocations), # type: ignore
            start=Decimal("0.00")
        )

    @property
    def balance(self):
        return self.amount - self.amount_paid

    @property
    def is_paid(self):
        return self.balance <= 0

    def __repr__(self):
        return f"<RentCharge {self.id}: {self.amount}>"
