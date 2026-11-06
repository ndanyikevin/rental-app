
from flask_login import UserMixin

from app.extensions import db, bcrypt
from app.models.base import TimestampMixin


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # Increment to invalidate previously issued login sessions.
    session_version = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    last_login_at = db.Column(db.DateTime(timezone=True))

    role = db.relationship(
        "Role",
        back_populates="users"
    )

    payments = db.relationship(
        "Payment",
        back_populates="recorded_by",
        foreign_keys="Payment.recorded_by_user_id"
    )

    expenses = db.relationship(
        "Expense",
        back_populates="recorded_by"
    )

    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user"
    )

    reported_maintenance = db.relationship(
        "Maintenance",
        back_populates="reported_by",
        foreign_keys="Maintenance.reported_by_user_id"
    )

    assigned_maintenance = db.relationship(
        "Maintenance",
        back_populates="assigned_to",
        foreign_keys="Maintenance.assigned_to_user_id"
    )

    def get_id(self):
        return f"{self.id}:{self.session_version}"

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.username}>"
