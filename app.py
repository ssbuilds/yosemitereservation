import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import schedule
import time
import threading
from utils import send_notification_email, mask_email
from email.mime.text import MIMEText
from datetime import datetime
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO if not os.environ.get('FLASK_DEBUG') else logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Ensure we have a strong session secret
if not os.environ.get("SESSION_SECRET"):
    logger.error("SESSION_SECRET not set! Please configure this environment variable.")
    raise ValueError("SESSION_SECRET must be set")

app.secret_key = os.environ.get("SESSION_SECRET")

# Configure PostgreSQL database with secure timeout and pooling settings
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

db.init_app(app)

def init_db():
    """Initialize the database and create tables"""
    try:
        with app.app_context():
            # Import models here to ensure they're registered with SQLAlchemy
            from models import MonitoringRequest
            db.create_all()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def send_notification(email, month, available_dates=None):
    """
    Send a notification to the user about campsite availability
    """
    try:
        if send_notification_email(email, month, available_dates):
            logger.info(f"Successfully sent notification to {email} for {month}")
            return True
        else:
            logger.error(f"Failed to send notification to {email} for {month}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def check_reservations():
    from scraper import check_yosemite_availability
    from models import MonitoringRequest

    try:
        with app.app_context():
            active_requests = MonitoringRequest.query.filter_by(active=True).all()
            for request in active_requests:
                available, dates = check_yosemite_availability(request.month)
                if available:
                    if send_notification(request.email, request.month, dates):
                        request.active = False
                        db.session.commit()
    except Exception as e:
        logger.error(f"Error checking reservations: {str(e)}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Initialize database
init_db()

# Initialize scheduler
scheduler_thread = None

@app.before_request
def ensure_scheduler():
    global scheduler_thread
    if scheduler_thread is None:
        schedule.every(30).minutes.do(check_reservations)
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info("Initialized scheduler thread")

@app.route('/')
def index():
    return render_template('index.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_auth' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_password = os.environ.get("ADMIN_PASSWORD")
        if not admin_password:
            flash('Admin password not configured', 'error')
            return redirect(url_for('index'))

        if request.form.get('password') == admin_password:
            session['admin_auth'] = True
            flash('Successfully logged in', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid password', 'error')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_auth', None)
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@admin_required
def dashboard():
    from models import MonitoringRequest
    requests = MonitoringRequest.query.all()
    # Mask emails before sending to template
    for request in requests:
        request.masked_email = mask_email(request.email)
    return render_template('dashboard.html', requests=requests)

@app.route('/monitor', methods=['POST'])
def monitor():
    from models import MonitoringRequest
    from scraper import check_yosemite_availability

    email = request.form.get('email')
    month = request.form.get('month')

    if not email or not month:
        flash('Please provide both email and month', 'error')
        return redirect(url_for('index'))

    try:
        new_request = MonitoringRequest(email=email, month=month)
        db.session.add(new_request)
        db.session.commit()

        # Check availability immediately
        logger.info(f"Checking immediate availability for {email} - {month}")
        available, dates = check_yosemite_availability(month)
        if available:
            if send_notification(email, month, dates):
                new_request.active = False
                db.session.commit()
                flash('Availability found! Check your email for details.', 'success')
            else:
                flash('Availability found but failed to send email notification.', 'error')
        else:
            flash('Monitoring request has been set up! You will be notified when availability is detected.', 'success')
    except Exception as e:
        logger.error(f"Error creating monitoring request: {str(e)}")
        db.session.rollback()
        flash('An error occurred while setting up the monitoring request', 'error')

    return redirect(url_for('dashboard'))

# Add security headers to Flask app
@app.after_request
def add_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable HSTS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    # Set debug mode based on environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)