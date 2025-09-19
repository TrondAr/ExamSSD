from flask import Blueprint, render_template
from utils.decorators import requires_role
from database import get_user_by_id
from flask import session, redirect, url_for

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@requires_role('patient')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = get_user_by_id(user_id)
    return render_template('dashboard_patient.html', user=user)