
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin


class Expense(TimestampMixin, db.Model):
    __tablename__ = "expenses"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_expense_amount_positive"
        ),
    )

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

    recorded_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    category = db.Column(
        db.String(80),
        nullable=False
    )

    description = db.Column(db.Text)

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    expense_date = db.Column(
        db.Date,
        nullable=False
    )

    payment_method = db.Column(db.String(30))
    reference_number = db.Column(db.String(100))

    status = db.Column(
        db.String(20),
        nullable=False,
        default="posted"
    )

    property = db.relationship(
        "Property",
        back_populates="expenses"
    )

    unit = db.relationship("Unit")

    recorded_by = db.relationship(
        "User",
        back_populates="expenses"
    )

    def __repr__(self):
        return f"<Expense {self.category}: {self.amount}>"
