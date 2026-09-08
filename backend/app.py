import os
from flask import Flask, render_template, session
from config import Config
from models import db

# Import route blueprints
from routes.home import home_bp
from routes.doctors import doctors_bp
from routes.departments import departments_bp
from routes.appointments import appointments_bp
from routes.contact import contact_bp
from routes.emergency import emergency_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.opd import opd_bp
from routes.prescriptions import prescriptions_bp
from routes.billing import billing_bp
from routes.reports import reports_bp
from routes.analytics import analytics_bp
from routes.notifications import notifications_bp
from routes.staff import staff_bp
from routes.inventory import inventory_bp
from routes.mrd import mrd_bp
from routes.pharmacy import pharmacy_bp
from routes.laboratory import laboratory_bp
from routes.financial_analytics import financial_analytics_bp
from routes.superadmin import superadmin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']

    # Initialize in-memory datastore interface
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(contact_bp, url_prefix='/contact')
    app.register_blueprint(emergency_bp, url_prefix='/emergency')
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(opd_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(mrd_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(laboratory_bp)
    app.register_blueprint(financial_analytics_bp)

    return app


# Create the Flask application for Gunicorn / production
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)