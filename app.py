import os
from flask import Flask
from flask_session import Session
from extensions import csrf, limiter
from database import init_db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.practitioner import practitioner_bp
from routes.patient import patient_bp
from routes.reset import reset_bp
from routes.files import files_bp
from routes.api import api_bp
from routes.xss_demo import xss_bp
from flask_mail import Mail
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'private_uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config["WTF_CSRF_TIME_LIMIT"] = 60*60 
app.config["MAIL_SUPPRESS_SEND"] = True
app.config["UPLOAD_DIR"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16 MB limit
csrf.init_app(app)
limiter.init_app(app)

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(practitioner_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(files_bp)
app.register_blueprint(api_bp)
app.register_blueprint(xss_bp)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False # set to true in production with https

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)
mail = Mail(app)

Session(app)

@app.route('/')
def home():
    return 'Welcome to the Home Page! <a href="/login">Login</a>'

if __name__ == '__main__':
    app.run(debug=True)