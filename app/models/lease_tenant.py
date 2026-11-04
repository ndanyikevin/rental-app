
from sqlalchemy import CheckConstraint

from app.extensions import db
from app.models.base import TimestampMixin


class LeaseTenant(TimestampMixin, db.Model):
    __tablename__ = "lease_tenants"

    __table_args__ = (
        db.UniqueConstraint(
            "lease_id",
            "tenant_id",
            name="uq_lease_tenant"
        ),
        CheckConstraint(
            "monthly_rent_amount IS NULL OR monthly_rent_amount >= 0",
            name="ck_membership_rent_nonnegative"
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
        nullable=False,
        index=True
    )

    monthly_rent_amount = db.Column(
        db.Numeric(12, 2)
    )

    is_primary = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    joined_on = db.Column(db.Date, nullable=False)

    left_on = db.Column(db.Date)

    lease = db.relationship(
        "Lease",
        back_populates="tenant_memberships"
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="lease_memberships"
    )

    def __repr__(self):
        return f"<LeaseTenant lease={self.lease_id} tenant={self.tenant_id}>"
