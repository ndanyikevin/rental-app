
from app.extensions import db

from app.models.base import TimestampMixin


class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    description = db.Column(db.String(255))

    permissions = db.Column(
        db.JSON,
        nullable=False,
        default=dict
    )

    users = db.relationship(
        "User",
        back_populates="role"
    )

    def __repr__(self):
        return f"<Role {self.name}>"
