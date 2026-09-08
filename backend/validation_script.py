import os
from flask import Flask
from app import create_app
from models import db, Patient, Invoice, InvoiceItem, MedicineMaster, MedicineBatch, MedicinePurchase, MedicineIssue, LabTest, LabOrder, LabOrderItem
import uuid

app = create_app()
client = app.test_client()

print('--- Starting Validation ---')

# Helper to print route info
def test_route(method, url, data=None, follow_redirects=False):
    if method == 'GET':
        resp = client.get(url, follow_redirects=follow_redirects)
    else:
        resp = client.post(url, data=data, follow_redirects=follow_redirects)
    print(f'GET {url} => {resp.status_code}')
    # Print first 100 chars of response data as template evidence
    snippet = resp.data.decode('utf-8')[:200].replace('\n', ' ')
    print(f'  Template snippet: {snippet[:100]}...')
    return resp

# Ensure sample patient exists
with app.app_context():
    patient = Patient.query.first()
    if not patient:
        print('No patient found!')
    else:
        print(f'Patient ID: {patient.id}')

# Billing: create invoice
invoice_data = {
    'patient_id': str(patient.id),
    'appointment_id': '',
    'opd_visit_id': '',
    'item_name': ['Consultation'],
    'item_type': ['consultation'],
    'quantity': ['1'],
    'unit_price': ['500'],
    'discount': '0'
}
resp = test_route('POST', '/billing/invoice/create', data=invoice_data, follow_redirects=True)
# Get created invoice id
with app.app_context():
    invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    inv_id = invoice.id if invoice else None
    print(f'Created Invoice ID: {inv_id}')

# Test Billing routes
test_route('GET', '/billing/')
if inv_id:
    test_route('GET', f'/billing/invoice/{inv_id}')
    test_route('GET', f'/billing/invoice/{inv_id}/print')
    test_route('POST', f'/billing/invoice/{inv_id}/pay')

# Pharmacy: add medicine
med_data = {
    'medicine_name': f'TestMed_{uuid.uuid4().hex[:6]}',
    'category': 'Antibiotic',
    'dosage_form': 'Tablet',
    'manufacturer': 'TestCo',
    'min_stock': '5',
    'unit': 'Box'
}
test_route('POST', '/pharmacy/medicine/create', data=med_data, follow_redirects=True)
# Get medicine id
with app.app_context():
    med = MedicineMaster.query.order_by(MedicineMaster.id.desc()).first()
    med_id = med.id if med else None
    print(f'Medicine ID: {med_id}')

# Pharmacy purchase
purchase_data = {
    'supplier_id': '1',
    'medicine_id': str(med_id),
    'quantity': '10',
    'rate': '20',
    'expiry_date': '2025-12-31'
}
# Note: the form expects list fields; use same name with multiple values
purchase_data_multi = {
    'supplier_id': '1',
    'medicine_id': [str(med_id)],
    'quantity': ['10'],
    'rate': ['20'],
    'expiry_date': ['2025-12-31']
}
test_route('POST', '/pharmacy/purchase/create', data=purchase_data_multi, follow_redirects=True)

# Pharmacy issue
issue_data = {
    'patient_id': str(patient.id),
    'batch_id': ['1'],  # assume first batch
    'quantity': ['2']
}
test_route('POST', '/pharmacy/issue/create', data=issue_data, follow_redirects=True)

# Pharmacy dashboard
test_route('GET', '/pharmacy/')

# Laboratory: create lab test
lab_test_data = {
    'test_name': 'TestX',
    'category': 'Pathology',
    'rate': '150',
    'normal_range': '',
    'unit': ''
}
test_route('POST', '/laboratory/tests/add', data=lab_test_data, follow_redirects=True)
with app.app_context():
    lab_test = LabTest.query.filter_by(test_name='TestX').first()
    lab_test_id = lab_test.id if lab_test else None
    print(f'LabTest ID: {lab_test_id}')

# Lab order creation
order_data = {
    'patient_id': str(patient.id),
    'doctor_id': '',
    'order_date': '',
    'test_id[]': [str(lab_test_id)]
}
test_route('POST', '/laboratory/orders/new', data=order_data, follow_redirects=True)
with app.app_context():
    lab_order = LabOrder.query.order_by(LabOrder.id.desc()).first()
    order_id = lab_order.id if lab_order else None
    print(f'LabOrder ID: {order_id}')

# Lab result entry
if order_id:
    result_data = {
        'item_id[]': [str(lab_order.items[0].id)],
        'result_value[]': ['Normal'],
        'notes[]': ['All good']
    }
    test_route('POST', f'/laboratory/orders/enter-results/{order_id}', data=result_data, follow_redirects=True)
    test_route('GET', f'/laboratory/orders/report/{order_id}')

# Lab dashboard
test_route('GET', '/laboratory/')

# Analytics dashboard
test_route('GET', '/financial-analytics/')

print('--- Validation Completed ---')
