
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin

from decimal import Decimal


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_payment_amount_positive"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    receipt_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    lease_id = db.Column(
        db.Integer,
        db.ForeignKey("leases.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    payment_date = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=False
    )

    reference_number = db.Column(
        db.String(100),
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="posted"
    )

    notes = db.Column(db.Text)

    recorded_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="payments"
    )

    lease = db.relationship(
        "Lease",
        back_populates="payments"
    )

    recorded_by = db.relationship(
        "User",
        back_populates="payments",
        foreign_keys=[recorded_by_user_id]
    )

    allocations = db.relationship(
        "PaymentAllocation",
        back_populates="payment"
    )

    @property
    def allocated_amount(self):
        return sum(
            (allocation.amount for allocation in self.allocations), # pyright: ignore[reportGeneralTypeIssues]
            start=Decimal("0.00")
        )

    @property
    def unallocated_amount(self):
        return self.amount - self.allocated_amount

    def __repr__(self):
        return f"<Payment {self.receipt_number}>"
