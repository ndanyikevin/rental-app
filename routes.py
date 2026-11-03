from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Property, Unit, Tenant, Payment
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    total_props = Property.query.count()
    total_units = Unit.query.count()
    occupied = Unit.query.filter_by(status='Occupied').count()
    vacant = Unit.query.filter_by(status='Vacant').count()
    expected = db.session.query(db.func.sum(Unit.monthly_rent)).filter_by(status='Occupied').scalar() or 0

    # this month collection
    this_month = datetime.now().strftime('%Y-%m')
    collected = db.session.query(db.func.sum(Payment.amount_paid)).filter_by(month=this_month).scalar() or 0
    outstanding = db.session.query(
        db.func.sum(Payment.amount_due - Payment.amount_paid)
    ).scalar() or 0

    occupancy = round((occupied / total_units * 100), 1) if total_units else 0

    return render_template('dashboard.html',
        total_props=total_props, total_units=total_units,
        occupied=occupied, vacant=vacant, occupancy=occupancy,
        expected=expected, collected=collected, outstanding=outstanding)

# ---------- PROPERTIES ----------
@main_bp.route('/properties', methods=['GET', 'POST'])
@login_required
def properties():
    if request.method == 'POST':
        p = Property(
            name=request.form['name'], # type: ignore
            location=request.form.get('location', '')
        )
        db.session.add(p)
        db.session.commit()
        flash('Property added.', 'success')
        return redirect(url_for('main.properties'))
    props = Property.query.order_by(Property.name).all()
    return render_template('properties.html', properties=props)

@main_bp.route('/properties/<int:pid>/delete', methods=['POST'])
@login_required
def delete_property(pid):
    p = Property.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('Property deleted.', 'success')
    return redirect(url_for('main.properties'))

# ---------- UNITS ----------
@main_bp.route('/units', methods=['GET', 'POST'])
@login_required
def units():
    if request.method == 'POST':
        u = Unit(
            property_id=int(request.form['property_id']),
            unit_number=request.form['unit_number'],
            unit_type=request.form.get('unit_type', ''),
            bedrooms=int(request.form.get('bedrooms') or 0),
            monthly_rent=float(request.form['monthly_rent']),
            status=request.form.get('status', 'Vacant')
        ) # type: ignore
        db.session.add(u)
        db.session.commit()
        flash('Unit added.', 'success')
        return redirect(url_for('main.units'))
    all_units = Unit.query.all()
    props = Property.query.order_by(Property.name).all()
    return render_template('units.html', units=all_units, properties=props)

@main_bp.route('/units/<int:uid>/delete', methods=['POST'])
@login_required
def delete_unit(uid):
    u = Unit.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    flash('Unit deleted.', 'success')
    return redirect(url_for('main.units'))

# ---------- TENANTS ----------
@main_bp.route('/tenants', methods=['GET', 'POST'])
@login_required
def tenants():
    if request.method == 'POST':
        unit_id = int(request.form['unit_id'])
        # mark unit as occupied
        unit = Unit.query.get_or_404(unit_id)
        unit.status = 'Occupied'
        t = Tenant(
            name=request.form['name'],
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            unit_id=unit_id,
            deposit_paid=float(request.form.get('deposit_paid') or 0),
            lease_end=datetime.strptime(request.form['lease_end'], '%Y-%m-%d').date()
                     if request.form.get('lease_end') else None,
        ) # type: ignore
        db.session.add(t)
        db.session.commit()
        flash('Tenant added.', 'success')
        return redirect(url_for('main.tenants'))
    all_tenants = Tenant.query.all()
    vacant_units = Unit.query.filter_by(status='Vacant').all()
    return render_template('tenants.html', tenants=all_tenants, vacant_units=vacant_units)

@main_bp.route('/tenants/<int:tid>/delete', methods=['POST'])
@login_required
def delete_tenant(tid):
    t = Tenant.query.get_or_404(tid)
    t.unit.status = 'Vacant'
    db.session.delete(t)
    db.session.commit()
    flash('Tenant removed.', 'success')
    return redirect(url_for('main.tenants'))

# ---------- PAYMENTS ----------
@main_bp.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    if request.method == 'POST':
        unit_id = int(request.form['unit_id'])
        unit = Unit.query.get_or_404(unit_id)
        p = Payment(
            unit_id=unit_id,
            month=request.form['month'],                 # e.g. 2025-11
            amount_due=float(request.form.get('amount_due') or unit.monthly_rent),
            amount_paid=float(request.form.get('amount_paid') or 0),
            payment_date=datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
                         if request.form.get('payment_date') else None,
            notes=request.form.get('notes', '')
        ) # type: ignore
        db.session.add(p)
        db.session.commit()
        flash('Payment recorded.', 'success')
        return redirect(url_for('main.payments'))

    all_payments = Payment.query.order_by(Payment.id.desc()).all()
    occupied_units = Unit.query.filter(Unit.status == 'Occupied').all() # type: ignore
    return render_template('payments.html', payments=all_payments, units=occupied_units)