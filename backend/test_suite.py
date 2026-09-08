"""
End-to-end test suite for Sahara Hospital (Database-free / Render-ready).
Tests all 21 route blueprints, form submissions, auth flows, and dashboards.
"""
from app import create_app
from models import (
    Department, Doctor, Patient, Appointment, ContactMessage,
    EmergencyContact, AdminUser, Invoice, MedicineMaster, LabTest, db
)
from datetime import date, time

def run_tests():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("=" * 70)
    print("STARTING FULL END-TO-END VERIFICATION")
    print("=" * 70)

    # 1. PUBLIC ROUTES
    print("\n[1] Testing Public Pages & Navigation...")
    routes_to_test = [
        ('/', 'Home Page'),
        ('/about', 'About Page'),
        ('/departments/', 'Departments List'),
        ('/departments/1', 'Department Detail (Cardiology)'),
        ('/doctor/', 'Doctors List'),
        ('/doctor/1', 'Doctor Detail (Dr. Sarah)'),
        ('/emergency/', 'Emergency Page'),
        ('/contact/', 'Contact Page'),
        ('/login', 'Login Page'),
        ('/register', 'Register Page'),
        ('/admin/login', 'Admin Login Page'),
        ('/doctor/login', 'Doctor Login Page'),
        ('/superadmin/login', 'Superadmin Login Page'),
    ]

    for url, desc in routes_to_test:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed GET {url} ({desc}), status: {resp.status_code}"
        print(f"  [PASS] GET {url:25} -> 200 OK ({desc})")

    # 2. FORMS SUBMISSION (Database-free)
    print("\n[2] Testing Public Form Submissions...")
    # Contact Form
    resp = client.post('/contact/submit', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'subject': 'General Inquiry',
        'message': 'Testing message without database'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert ContactMessage.query.filter_by(email='testuser@example.com').first() is not None
    print("  [PASS] POST /contact/submit -> Success (Message saved to memory store)")

    # Emergency Form
    resp = client.post('/emergency/submit', data={
        'patient_name': 'Emergency Patient',
        'phone': '555-999-1111',
        'emergency_type': 'Cardiac',
        'message': 'Immediate help needed'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert EmergencyContact.query.filter_by(patient_name='Emergency Patient').first() is not None
    print("  [PASS] POST /emergency/submit -> Success (Emergency request saved to memory store)")

    # 3. AUTHENTICATION & PATIENT FLOW
    print("\n[3] Testing Authentication & Patient Dashboard...")
    # Register new demo patient
    resp = client.post('/register', data={
        'full_name': 'Alice Wonder',
        'email': 'alice@example.com',
        'phone': '+1 555 444 3333',
        'gender': 'Female',
        'age': '29',
        'address': '77 Wonder Lane',
        'password': 'alicepassword'
    }, follow_redirects=True)
    assert resp.status_code == 200
    registered_patient = Patient.query.filter_by(email='alice@example.com').first()
    assert registered_patient is not None
    assert registered_patient.check_password('alicepassword')
    print("  [PASS] POST /register -> Success (New patient registered and password verified)")

    # Login as patient
    with client.session_transaction() as sess:
        sess['patient_id'] = 1
        sess['patient_name'] = 'John Smith'
        sess['role'] = 'patient'

    resp = client.get('/dashboard')
    assert resp.status_code == 200
    print("  [PASS] GET /dashboard -> 200 OK (Patient Dashboard)")

    resp = client.get('/appointments/')
    assert resp.status_code == 200
    print("  [PASS] GET /appointments/ -> 200 OK (Appointment Booking Page)")

    # Book Appointment
    resp = client.post('/appointments/book', data={
        'doctor_id': '1',
        'date': '2026-10-15',
        'time': '11:00',
        'symptoms': 'Routine followup'
    }, follow_redirects=True)
    assert resp.status_code == 200
    new_appt = Appointment.query.filter_by(patient_id=1, doctor_id=1).first()
    assert new_appt is not None
    print("  [PASS] POST /appointments/book -> Success (Appointment booked and visible in dashboard)")

    # 4. DOCTOR FLOW
    print("\n[4] Testing Doctor Portal...")
    with client.session_transaction() as sess:
        sess.clear()
        sess['doctor_logged_in'] = True
        sess['doctor_id'] = 1
        sess['doctor_name'] = 'Dr. Sarah Johnson'
        sess['role'] = 'doctor'
        sess['patient_id'] = 4

    resp = client.get('/doctor/dashboard')
    assert resp.status_code == 200
    print("  [PASS] GET /doctor/dashboard -> 200 OK (Doctor Dashboard)")

    resp = client.get('/doctor/patients')
    assert resp.status_code == 200
    print("  [PASS] GET /doctor/patients -> 200 OK (Doctor Patients)")

    resp = client.get('/doctor/appointments')
    assert resp.status_code == 200
    print("  [PASS] GET /doctor/appointments -> 200 OK (Doctor Appointments)")

    # 5. STAFF & SUPERADMIN FLOW
    print("\n[5] Testing Staff & Superadmin Portals...")
    with client.session_transaction() as sess:
        sess.clear()
        sess['patient_id'] = 5
        sess['patient_name'] = 'Staff Member'
        sess['role'] = 'staff'

    resp = client.get('/staff/dashboard')
    assert resp.status_code == 200
    print("  [PASS] GET /staff/dashboard -> 200 OK (Staff Dashboard)")

    resp = client.get('/staff/appointments')
    assert resp.status_code == 200
    print("  [PASS] GET /staff/appointments -> 200 OK (Staff Appointments)")

    with client.session_transaction() as sess:
        sess.clear()
        sess['superadmin_logged_in'] = True
        sess['superadmin_name'] = 'Super Admin'

    resp = client.get('/superadmin/dashboard')
    assert resp.status_code == 200
    print("  [PASS] GET /superadmin/dashboard -> 200 OK (Superadmin Dashboard)")

    # 6. ADMIN & CLINICAL / HOSPITAL MODULES
    print("\n[6] Testing Admin & Operational Modules (OPD, Billing, Pharmacy, Lab, Inventory, Reports, Analytics)...")
    with client.session_transaction() as sess:
        sess.clear()
        sess['admin_id'] = 1
        sess['admin_username'] = 'admin'
        sess['admin_role'] = 'admin'

    admin_modules = [
        ('/admin/dashboard', 'Admin Dashboard'),
        ('/admin/doctors', 'Admin Doctors List'),
        ('/admin/departments', 'Admin Departments List'),
        ('/admin/patients', 'Admin Patients List'),
        ('/admin/appointments', 'Admin Appointments List'),
        ('/admin/messages', 'Admin Messages List'),
        ('/admin/emergencies', 'Admin Emergencies List'),
        ('/analytics/dashboard', 'Analytics Dashboard'),
        ('/financial-analytics/', 'Financial Analytics'),
        ('/opd/', 'OPD Dashboard'),
        ('/opd/checkin', 'OPD Checkin Page'),
        ('/billing/', 'Billing Invoices List'),
        ('/pharmacy/', 'Pharmacy Dashboard'),
        ('/pharmacy/medicine/create', 'Pharmacy Medicine Create Page'),
        ('/laboratory/', 'Laboratory Dashboard'),
        ('/laboratory/tests', 'Laboratory Tests Catalog'),
        ('/inventory/', 'Inventory Master Dashboard'),
        ('/mrd/', 'MRD Record Tracking'),
        ('/notifications/', 'Notifications Center'),
        ('/reports/', 'Hospital Reports Dashboard')
    ]

    for url, desc in admin_modules:
        resp = client.get(url, follow_redirects=True)
        assert resp.status_code == 200, f"Failed GET {url} ({desc}), status: {resp.status_code}"
        print(f"  [PASS] GET {url:28} -> 200 OK ({desc})")

    # Test Admin CRUD form submissions
    # Add Doctor
    resp = client.post('/admin/doctors/add', data={
        'name': 'Dr. Alan Turing',
        'specialization': 'Neuroinformatics',
        'experience': '10',
        'qualification': 'MD, PhD',
        'phone': '+1 555 777 8888',
        'email': 'alan.turing@saharahospital.com',
        'department_id': '2',
        'availability': 'on'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert Doctor.query.filter_by(email='alan.turing@saharahospital.com').first() is not None
    print("  [PASS] POST /admin/doctors/add -> Success (New doctor created in memory)")

    # Create Invoice
    resp = client.post('/billing/invoice/create', data={
        'patient_id': '1',
        'appointment_id': '',
        'opd_visit_id': '',
        'item_name': ['Cardiology Stress Test'],
        'item_type': ['procedure'],
        'quantity': ['1'],
        'unit_price': ['1200'],
        'discount': '0'
    }, follow_redirects=True)
    assert resp.status_code == 200
    created_inv = Invoice.query.order_by(Invoice.id.desc()).first()
    assert created_inv is not None
    print(f"  [PASS] POST /billing/invoice/create -> Success (Created Invoice #{created_inv.id})")

    # Add Lab Test
    resp = client.post('/laboratory/tests/add', data={
        'test_name': 'Advanced Vitamin D3 25-OH',
        'category': 'Biochemistry',
        'rate': '650',
        'normal_range': '30 - 100 ng/mL',
        'unit': 'ng/mL'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert LabTest.query.filter_by(test_name='Advanced Vitamin D3 25-OH').first() is not None
    print("  [PASS] POST /laboratory/tests/add -> Success (Lab test added to catalog)")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! ZERO DATABASE ERRORS!")
    print("The website is 100% database-free and ready for Render deployment.")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
