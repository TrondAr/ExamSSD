from flask import Blueprint, render_template, request, redirect, url_for
from database import create_user, get_user_by_email
from validators import validate_email, validate_password_strength
from security import hash_password
from utils.decorators import requires_role

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@requires_role('admin')
def dashboard():
    return render_template('dashboard_admin.html')

@admin_bp.route('/create_practitioner', methods=['GET', 'POST'])
@requires_role('admin')
def create_practitioner():    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            return render_template('practitioner.html', error='Email and password required')
        
        ok, msg = validate_email(email)
        if not ok:
            return render_template('practitioner.html', error=msg)
        
        ok, msg = validate_password_strength(password)
        if not ok:
            return render_template('practitioner.html', error=msg)
        
        if get_user_by_email(email):
            return render_template('practitioner.html', error='User already exists')

        hashed = hash_password(password)
        create_user(email, hashed, role='practitioner')
        return redirect(url_for('admin.create_practitioner', created='1'))
    
    created = request.args.get('created')
    return render_template('practitioner.html', created=created)
