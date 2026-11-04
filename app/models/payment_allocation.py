
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin


class PaymentAllocation(TimestampMixin, db.Model):
    __tablename__ = "payment_allocations"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_allocation_amount_positive"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    rent_charge_id = db.Column(
        db.Integer,
        db.ForeignKey("rent_charges.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    payment = db.relationship(
        "Payment",
        back_populates="allocations"
    )

    rent_charge = db.relationship(
        "RentCharge",
        back_populates="allocations"
    )

    def __repr__(self):
        return f"<PaymentAllocation {self.amount}>"
