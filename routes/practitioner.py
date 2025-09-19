from flask import Blueprint, render_template
from utils.decorators import requires_role

practitioner_bp = Blueprint('practitioner', __name__, url_prefix='/practitioner')

@practitioner_bp.route('/dashboard')
@requires_role('practitioner')
def dashboard():
    return render_template('dashboard_practitioner.html')