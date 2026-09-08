"""
Static demo data for Appointments.
"""
from datetime import date, time

APPOINTMENTS = [
    {
        "id": 1,
        "patient_id": 1,
        "doctor_id": 1,
        "appointment_date": date.today(),
        "appointment_time": time(10, 0),
        "symptoms": "Routine annual cardiac evaluation and blood pressure checkup.",
        "status": "confirmed"
    },
    {
        "id": 2,
        "patient_id": 2,
        "doctor_id": 2,
        "appointment_date": date.today(),
        "appointment_time": time(11, 30),
        "symptoms": "Persistent tension headaches and occasional dizziness.",
        "status": "pending"
    },
    {
        "id": 3,
        "patient_id": 3,
        "doctor_id": 3,
        "appointment_date": date.today(),
        "appointment_time": time(14, 0),
        "symptoms": "Right knee pain following marathon training.",
        "status": "pending"
    },
    {
        "id": 4,
        "patient_id": 1,
        "doctor_id": 4,
        "appointment_date": date.today(),
        "appointment_time": time(15, 30),
        "symptoms": "General wellness consultation for family member.",
        "status": "completed"
    }
]
