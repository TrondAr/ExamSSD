# ExamSSD Flask App

A Flask-based demo app with user auth, admin/practitioner/patient roles, secure file upload, and password reset.

## Features
- User registration/login with bcrypt
- Role-based blueprints (admin, practitioner, patient)
- CSRF protection and rate limiting
- Secure file uploads (private storage) with access control
- Password reset tokens with expiry and single-use
- Basic XSS/SQLi demo tests

## Requirements
- Python 3.10+

## Setup
```powershell
# Clone
git clone <your_repo_url>
cd ExamSSD

# Create & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run
python app.py
```

Set environment variables:
- `SECRET_KEY` (required)
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` (optional for email; app defaults to suppressed send)

## Testing
```powershell
python -m pytest -q
```

## Notes
- For production, configure Flask-Limiter storage (Redis) and HTTPS cookies.
- Do not commit `.env`, `user_database.db`, or `private_uploads/`.
