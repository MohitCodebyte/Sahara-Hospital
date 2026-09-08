"""
Static demo data for hospital operational modules:
Inventory, Pharmacy, Laboratory, Billing, OPD, Emergency, Contact, Notifications.
"""
from datetime import date, time, datetime

EMERGENCY_CONTACTS = [
    {
        "id": 1,
        "patient_name": "Sahara Hospital 24/7 Emergency Center",
        "phone": "+1 (800) 555-9111",
        "emergency_type": "24/7 Trauma & Critical Care",
        "message": "Immediate 24/7 Emergency response, cardiac ambulance with mobile ICU support ready.",
        "patient_id": 1
    }
]

CONTACT_MESSAGES = [
    {
        "id": 1,
        "name": "Sarah Miller",
        "email": "sarah.m@example.com",
        "subject": "Inquiry regarding Cardiology outpatient consultation",
        "message": "Hello, I would like to know the consultation hours for Dr. Sarah Johnson next Tuesday."
    },
    {
        "id": 2,
        "name": "David Clark",
        "email": "david.c@example.com",
        "subject": "Health insurance coverage verification",
        "message": "Do you accept Blue Cross Blue Shield for standard diagnostic scans?"
    }
]

SUPPLIERS = [
    {
        "id": 1,
        "name": "Apex Medical Supplies",
        "contact_person": "Rohan Gupta",
        "email": "rohan@apexmed.com",
        "phone": "+91 9876543210",
        "address": "G-12 Industrial Area, Sector 5, Medical City",
        "gst_number": "07AAAAA1111A1Z0"
    },
    {
        "id": 2,
        "name": "BioPharma Distributors",
        "contact_person": "Anjali Sharma",
        "email": "sales@biopharma.com",
        "phone": "+91 8765432109",
        "address": "45 Pharmaceutical Complex, Phase II",
        "gst_number": "08BBBBB2222B2Z1"
    }
]

INVENTORY_ITEMS = [
    {
        "id": 1,
        "item_code": "INV-SUR-001",
        "item_name": "Sterile Surgical Gloves (Medium)",
        "category": "Surgical Supplies",
        "quantity": 250,
        "minimum_stock": 50,
        "unit": "Pairs",
        "purchase_price": 15.0,
        "supplier_name": "Apex Medical Supplies",
        "expiry_date": date(2027, 12, 31)
    },
    {
        "id": 2,
        "item_code": "INV-PPE-002",
        "item_name": "N95 Protective Medical Masks",
        "category": "PPE",
        "quantity": 500,
        "minimum_stock": 100,
        "unit": "Box (50)",
        "purchase_price": 25.0,
        "supplier_name": "Apex Medical Supplies",
        "expiry_date": date(2028, 6, 30)
    },
    {
        "id": 3,
        "item_code": "INV-IV-003",
        "item_name": "Normal Saline IV Infusion 500ml",
        "category": "Fluids & Infusions",
        "quantity": 180,
        "minimum_stock": 40,
        "unit": "Bottles",
        "purchase_price": 45.0,
        "supplier_name": "BioPharma Distributors",
        "expiry_date": date(2026, 11, 15)
    },
    {
        "id": 4,
        "item_code": "INV-CAN-004",
        "item_name": "IV Cannula 20G (Pink)",
        "category": "Disposables",
        "quantity": 300,
        "minimum_stock": 50,
        "unit": "Pieces",
        "purchase_price": 18.0,
        "supplier_name": "Apex Medical Supplies",
        "expiry_date": date(2027, 8, 20)
    }
]

MEDICINE_MASTER = [
    {
        "id": 1,
        "medicine_name": "Amoxicillin 500mg",
        "category": "Antibiotic",
        "dosage_form": "Capsule",
        "manufacturer": "Cipla Healthcare",
        "min_stock": 50,
        "unit": "Strip (10 Caps)"
    },
    {
        "id": 2,
        "medicine_name": "Paracetamol 650mg",
        "category": "Analgesics & Antipyretic",
        "dosage_form": "Tablet",
        "manufacturer": "Crocin Laboratories",
        "min_stock": 100,
        "unit": "Strip (15 Tabs)"
    },
    {
        "id": 3,
        "medicine_name": "Cough Syrup 100ml",
        "category": "Antitussives",
        "dosage_form": "Syrup",
        "manufacturer": "Benadryl Global",
        "min_stock": 25,
        "unit": "Bottle"
    },
    {
        "id": 4,
        "medicine_name": "Atorvastatin 20mg",
        "category": "Cardiovascular",
        "dosage_form": "Tablet",
        "manufacturer": "Sun Pharma",
        "min_stock": 30,
        "unit": "Strip (10 Tabs)"
    },
    {
        "id": 5,
        "medicine_name": "Metformin 500mg",
        "category": "Antidiabetic",
        "dosage_form": "Tablet",
        "manufacturer": "Abbott Healthcare",
        "min_stock": 60,
        "unit": "Strip (15 Tabs)"
    }
]

MEDICINE_BATCHES = [
    {
        "id": 1,
        "medicine_id": 1,
        "batch_number": "AMX-2024-B1",
        "expiry_date": date(2026, 12, 31),
        "purchase_price": 45.0,
        "sale_price": 65.0,
        "initial_qty": 200,
        "current_qty": 180,
        "supplier_id": 1,
        "purchase_id": 1
    },
    {
        "id": 2,
        "medicine_id": 2,
        "batch_number": "PCM-2024-C2",
        "expiry_date": date(2027, 6, 30),
        "purchase_price": 20.0,
        "sale_price": 32.0,
        "initial_qty": 500,
        "current_qty": 420,
        "supplier_id": 1,
        "purchase_id": 1
    }
]

LAB_TESTS = [
    {
        "id": 1,
        "test_name": "Complete Blood Count (CBC)",
        "category": "Pathology",
        "rate": 350.0,
        "normal_range": "4.0 - 11.0",
        "unit": "10^3/uL"
    },
    {
        "id": 2,
        "test_name": "Lipid Profile Panel",
        "category": "Biochemistry",
        "rate": 750.0,
        "normal_range": "Desirable < 200",
        "unit": "mg/dL"
    },
    {
        "id": 3,
        "test_name": "Digital Chest X-Ray (PA View)",
        "category": "Radiology",
        "rate": 450.0,
        "normal_range": "Normal lung fields & cardiac size",
        "unit": "PA Scan"
    },
    {
        "id": 4,
        "test_name": "HbA1c Glycated Hemoglobin",
        "category": "Biochemistry",
        "rate": 500.0,
        "normal_range": "< 5.7 (Normal)",
        "unit": "%"
    },
    {
        "id": 5,
        "test_name": "Thyroid Stimulating Hormone (TSH)",
        "category": "Endocrinology",
        "rate": 400.0,
        "normal_range": "0.4 - 4.0",
        "unit": "uIU/mL"
    }
]

OPD_FEES = [
    {
        "id": 1,
        "department_id": 1,
        "doctor_id": 1,
        "fee_name": "Cardiology Specialist Consultation",
        "fee_amount": 800.0,
        "is_active": True
    },
    {
        "id": 2,
        "department_id": 2,
        "doctor_id": 2,
        "fee_name": "Neurology Initial Consultation",
        "fee_amount": 850.0,
        "is_active": True
    },
    {
        "id": 3,
        "department_id": 3,
        "doctor_id": 3,
        "fee_name": "Orthopedics Evaluation Fee",
        "fee_amount": 700.0,
        "is_active": True
    }
]

INVOICES = [
    {
        "id": 1,
        "patient_id": 1,
        "appointment_id": 1,
        "opd_visit_id": None,
        "invoice_number": "INV-2024-00101",
        "invoice_date": date.today(),
        "subtotal": 800.0,
        "tax": 0.0,
        "discount": 0.0,
        "total_amount": 800.0,
        "payment_status": "paid",
        "payment_method": "Credit Card",
        "notes": "Cardiology Consultation Paid"
    },
    {
        "id": 2,
        "patient_id": 2,
        "appointment_id": 2,
        "opd_visit_id": None,
        "invoice_number": "INV-2024-00102",
        "invoice_date": date.today(),
        "subtotal": 1200.0,
        "tax": 0.0,
        "discount": 0.0,
        "total_amount": 1200.0,
        "payment_status": "pending",
        "payment_method": "Cash",
        "notes": "Neurology OPD and Lab Work"
    }
]

INVOICE_ITEMS = [
    {
        "id": 1,
        "invoice_id": 1,
        "item_name": "Cardiology Specialist Consultation",
        "item_type": "consultation",
        "quantity": 1,
        "unit_price": 800.0,
        "total_price": 800.0
    },
    {
        "id": 2,
        "invoice_id": 2,
        "item_name": "Neurology Initial Consultation",
        "item_type": "consultation",
        "quantity": 1,
        "unit_price": 850.0,
        "total_price": 850.0
    },
    {
        "id": 3,
        "invoice_id": 2,
        "item_name": "Complete Blood Count (CBC)",
        "item_type": "lab_test",
        "quantity": 1,
        "unit_price": 350.0,
        "total_price": 350.0
    }
]

OPD_VISITS = [
    {
        "id": 1,
        "patient_id": 1,
        "doctor_id": 1,
        "token_number": "CARD-T01",
        "visit_date": date.today(),
        "check_in_time": time(9, 30),
        "check_out_time": time(10, 15),
        "status": "completed",
        "chief_complaint": "Follow-up for mild hypertension management.",
        "vitals": {"bp": "120/80", "pulse": "72", "temp": "98.4", "weight": "70kg", "height": "175cm"},
        "notes": "Blood pressure well controlled. Continue regular aerobic exercise."
    },
    {
        "id": 2,
        "patient_id": 2,
        "doctor_id": 2,
        "token_number": "NEUR-T02",
        "visit_date": date.today(),
        "check_in_time": time(10, 45),
        "check_out_time": None,
        "status": "waiting",
        "chief_complaint": "Tension headaches during screen work.",
        "vitals": {"bp": "122/82", "pulse": "78", "temp": "98.6", "weight": "62kg", "height": "165cm"},
        "notes": "Awaiting initial assessment."
    }
]

PRESCRIPTIONS = [
    {
        "id": 1,
        "patient_id": 1,
        "doctor_id": 1,
        "appointment_id": 1,
        "opd_visit_id": 1,
        "diagnosis": "Essential Mild Hypertension",
        "notes": "Low sodium diet, daily 30 min morning walk.",
        "prescription_date": date.today()
    }
]

PRESCRIPTION_MEDICINES = [
    {
        "id": 1,
        "prescription_id": 1,
        "medicine_name": "Atorvastatin 20mg",
        "dosage": "1 Tab",
        "frequency": "Once daily at bedtime",
        "duration": "30 Days",
        "instructions": "Take after dinner with water."
    }
]

NOTIFICATIONS = [
    {
        "id": 1,
        "recipient_id": 1,
        "recipient_type": "patient",
        "notification_type": "appointment",
        "title": "Appointment Confirmed",
        "message": "Your appointment with Dr. Sarah Johnson has been confirmed for today at 10:00 AM.",
        "is_read": False,
        "related_id": 1
    },
    {
        "id": 2,
        "recipient_id": 1,
        "recipient_type": "admin",
        "notification_type": "inventory",
        "title": "Inventory Stock Status Normal",
        "message": "All essential emergency medical supplies are above minimum stock thresholds.",
        "is_read": True,
        "related_id": 1
    }
]

SETTINGS = [
    {
        "id": 1,
        "key": "hospital_name",
        "value": "Sahara Multi-Speciality Hospital",
        "description": "Hospital display name"
    },
    {
        "id": 2,
        "key": "emergency_phone",
        "value": "+1 (800) 555-9111",
        "description": "Emergency hotline number"
    },
    {
        "id": 3,
        "key": "currency_symbol",
        "value": "$",
        "description": "Currency symbol for billing"
    }
]

MRD_RECORDS = [
    {
        "id": 1,
        "patient_id": 1,
        "file_number": "MRD-2024-001",
        "current_location": "Central Archives - Shelf A3",
        "status": "archived",
        "issued_to_staff": None,
        "issue_date": None,
        "return_date": None,
        "notes": "Complete medical history digitized."
    }
]
