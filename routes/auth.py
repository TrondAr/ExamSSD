from  flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import limiter
from database import get_user_by_email, create_user
from security import hash_password
from validators import validate_email, validate_password_strength
from services.auth_service import verify_password

auth_bp = Blueprint('auth', __name__)

ROLE_REDIRECTS = {
    'admin': 'admin.dashboard',
    'practitioner': 'practitioner.dashboard',
    'patient': 'patient.dashboard'
}

@limiter.limit("5 per minute")
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not verify_password(email, password):
            return render_template('login.html', error='Invalid email or password')

        user = get_user_by_email(email)
        if not user['is_active']:
            return render_template('login.html', error='Account inactive')

        session.clear()
        session['user_id'] = user['id']
        session['role'] = user['role']

        dest = ROLE_REDIRECTS.get(user['role'])
        if dest:
            return redirect(url_for(dest))
        return redirect(url_for('auth.profile'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from database import get_practitioners, add_gp_link, get_user_by_email

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        chosen_gp = request.form.get('practitioner_id')

        ok, msg = validate_email(email)
        if not ok:
            return render_template('register.html', error=msg, practitioners=get_practitioners())

        ok, msg = validate_password_strength(password)
        if not ok:
            return render_template('register.html', error=msg, practitioners=get_practitioners())

        if get_user_by_email(email):
            return render_template('register.html', error='User already exists', practitioners=get_practitioners())

        hashed = hash_password(password)
        create_user(email, hashed, role='patient')
        
        patient = get_user_by_email(email)
        if chosen_gp:
            try:
                gp_id = int(chosen_gp)
                add_gp_link(gp_id, patient['id'])
            except Exception:                
                pass
        return redirect(url_for('auth.login'))
    
    practitioners = get_practitioners()
    return render_template('register.html', practitioners=practitioners)

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return f"Logged in as {session.get('role')} (user_id={session.get('user_id')})"

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))