from flask import Blueprint, render_template, request, redirect, url_for, current_app
from services.reset_service import create_reset_for_email, lookup_valid_token, consume_token, set_new_password
from validators import validate_password_strength, validate_email

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        ok, msg = validate_email(email)
        if not ok:
            return render_template('forgot_password.html', error=msg)

        raw = create_reset_for_email(email)
        if raw:            
            reset_link = url_for('reset.reset_password', token=raw, _external=True)
            if current_app.config.get("MAIL_SUPPRESS_SEND", False):
                print(f"[DEMO] Password reset link for {email}: {reset_link}")      
        return render_template('forgot_password_done.html', reset_link=None)
    return render_template('forgot_password.html')

@reset_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token') if request.method == 'GET' else request.form.get('token')
    if not token:        
        return redirect(url_for('reset.forgot_password'))

    row = lookup_valid_token(token)
    if not row:
        return render_template('reset_password_invalid.html'), 400

    if request.method == 'POST':
        new_password = request.form.get('password', '')
        ok, msg = validate_password_strength(new_password)
        if not ok:
            return render_template('reset_password.html', token=token, error=msg)
        
        set_new_password(row['user_id'], new_password)
        consume_token(row['id'])
        
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)
