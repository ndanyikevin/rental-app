from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    units = db.relationship('Unit', backref='property', cascade='all, delete-orphan')

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    unit_number = db.Column(db.String(50), nullable=False)
    unit_type = db.Column(db.String(50))          # e.g. 1BR, 2BR, Studio
    bedrooms = db.Column(db.Integer, default=0)
    monthly_rent = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(30), default='Vacant')  # Vacant / Occupied / Maintenance
    tenant = db.relationship('Tenant', backref='unit', uselist=False, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='unit', cascade='all, delete-orphan')

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), unique=True, nullable=False)
    move_in_date = db.Column(db.Date, default=datetime.utcnow)
    lease_end = db.Column(db.Date)
    deposit_paid = db.Column(db.Float, default=0)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)    # e.g. "2025-11"
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0)
    payment_date = db.Column(db.Date)
    notes = db.Column(db.String(255))

    @property
    def balance(self):
        return (self.amount_due or 0) - (self.amount_paid or 0)

    @property
    def status(self):
        if self.balance <= 0:
            return "Paid"
        if self.amount_paid and self.amount_paid > 0:
            return "Partial"
        return "Unpaid"