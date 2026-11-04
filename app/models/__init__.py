# Import model classes here as they are implemented.
# This ensures SQLAlchemy and Flask-Migrate can discover them.

from app.models.role import Role
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.lease import Lease
from app.models.lease_tenant import LeaseTenant
from app.models.rent_charge import RentCharge
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
from app.models.expense import Expense
from app.models.maintenance import Maintenance
from app.models.audit_log import AuditLog

__all__ = [
    "Role",
    "User",
    "Property",
    "Unit",
    "Tenant",
    "Lease",
    "LeaseTenant",
    "RentCharge",
    "Payment",
    "PaymentAllocation",
    "Expense",
    "Maintenance",
    "AuditLog",
]
