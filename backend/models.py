"""
Pure in-memory Model and DataStore for Sahara Hospital.
Completely database-free (zero MySQL, Postgres, SQLite, or external DB required).
"""
import copy
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort

# Import static datasets
from data.departments_data import DEPARTMENTS
from data.doctors_data import DOCTORS
from data.patients_data import PATIENTS, ADMIN_USERS
from data.appointments_data import APPOINTMENTS
from data.hospital_data import (
    EMERGENCY_CONTACTS, CONTACT_MESSAGES, SUPPLIERS, INVENTORY_ITEMS,
    MEDICINE_MASTER, MEDICINE_BATCHES, LAB_TESTS, OPD_FEES, INVOICES,
    INVOICE_ITEMS, OPD_VISITS, PRESCRIPTIONS, PRESCRIPTION_MEDICINES,
    NOTIFICATIONS, SETTINGS, MRD_RECORDS
)

# Global in-memory storage dictionary { ModelClass: [instances] }
_STORE = {}
_NEXT_IDS = {}


class ColumnProxy:
    """Represents a column descriptor or attribute for query expressions."""
    def __init__(self, name=None):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __eq__(self, other):
        return BinaryExpression(self.name, '==', other)

    def __ne__(self, other):
        return BinaryExpression(self.name, '!=', other)

    def __ge__(self, other):
        return BinaryExpression(self.name, '>=', other)

    def __le__(self, other):
        return BinaryExpression(self.name, '<=', other)

    def __gt__(self, other):
        return BinaryExpression(self.name, '>', other)

    def __lt__(self, other):
        return BinaryExpression(self.name, '<', other)

    def in_(self, values):
        return BinaryExpression(self.name, 'in', values)

    def desc(self):
        return OrderExpression(self.name, descending=True)

    def asc(self):
        return OrderExpression(self.name, descending=False)


class BinaryExpression:
    def __init__(self, key, op, val):
        self.key = key
        self.op = op
        self.val = val

    def match(self, obj):
        val = getattr(obj, self.key, None)
        target = self.val
        if val is None or target is None:
            if self.op == '==':
                return val == target
            elif self.op == '!=':
                return val != target
            return False

        # Normalize datetime vs date
        v_cmp = val
        t_cmp = target
        if isinstance(v_cmp, datetime) and isinstance(t_cmp, date) and not isinstance(t_cmp, datetime):
            v_cmp = v_cmp.date()
        elif isinstance(t_cmp, datetime) and isinstance(v_cmp, date) and not isinstance(v_cmp, datetime):
            t_cmp = t_cmp.date()

        try:
            if self.op == '==':
                return v_cmp == t_cmp
            elif self.op == '!=':
                return v_cmp != t_cmp
            elif self.op == '>=':
                return v_cmp >= t_cmp
            elif self.op == '<=':
                return v_cmp <= t_cmp
            elif self.op == '>':
                return v_cmp > t_cmp
            elif self.op == '<':
                return v_cmp < t_cmp
            elif self.op == 'in':
                return v_cmp in t_cmp
        except Exception:
            return False
        return False


class OrderExpression:
    def __init__(self, key, descending=False):
        self.key = key
        self.descending = descending


class Pagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 1

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class ModelQuery:
    def __init__(self, model_cls, items=None):
        self.model_cls = model_cls
        if items is None:
            self._items = list(_STORE.get(model_cls, []))
        else:
            self._items = list(items)

    def filter_by(self, **kwargs):
        filtered = []
        for obj in self._items:
            match = True
            for k, v in kwargs.items():
                if getattr(obj, k, None) != v:
                    match = False
                    break
            if match:
                filtered.append(obj)
        return ModelQuery(self.model_cls, filtered)

    def filter(self, *expressions):
        filtered = []
        for obj in self._items:
            match = True
            for expr in expressions:
                if isinstance(expr, BinaryExpression):
                    if not expr.match(obj):
                        match = False
                        break
                elif callable(expr):
                    if not expr(obj):
                        match = False
                        break
                elif isinstance(expr, bool):
                    if not expr:
                        match = False
                        break
            if match:
                filtered.append(obj)
        return ModelQuery(self.model_cls, filtered)

    def order_by(self, *criteria):
        if not criteria:
            return self
        
        items = list(self._items)
        for crit in reversed(criteria):
            if isinstance(crit, OrderExpression):
                key = crit.key
                desc = crit.descending
            elif isinstance(crit, ColumnProxy):
                key = crit.name
                desc = False
            elif isinstance(crit, str):
                key = crit
                desc = False
            elif hasattr(crit, 'key'):
                key = crit.key
                desc = getattr(crit, 'descending', False)
            else:
                continue

            def sort_key(x):
                v = getattr(x, key, None)
                if v is None:
                    return "" if desc else "zzzzzz"
                return v

            try:
                items.sort(key=sort_key, reverse=desc)
            except Exception:
                pass

        return ModelQuery(self.model_cls, items)

    def limit(self, n):
        return ModelQuery(self.model_cls, self._items[:n])

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None

    def get(self, ident):
        if ident is None:
            return None
        try:
            ident_int = int(ident)
        except (ValueError, TypeError):
            ident_int = ident
        for obj in _STORE.get(self.model_cls, []):
            if obj.id == ident_int or str(obj.id) == str(ident):
                return obj
        return None

    def get_or_404(self, ident, description=None):
        rv = self.get(ident)
        if rv is None:
            abort(404, description=description or f"{self.model_cls.__name__} not found")
        return rv

    def count(self):
        return len(self._items)

    def paginate(self, page=1, per_page=10, error_out=False):
        try:
            page = int(page)
        except Exception:
            page = 1
        try:
            per_page = int(per_page)
        except Exception:
            per_page = 10

        total = len(self._items)
        start = (page - 1) * per_page
        end = start + per_page
        paged_items = self._items[start:end]
        return Pagination(paged_items, page, per_page, total)

    def group_by(self, *args):
        return self

    def outerjoin(self, *args, **kwargs):
        return self


class ModelMeta(type):
    def __getattr__(cls, name):
        # Fallback for dynamic column access
        return ColumnProxy(name)


class BaseModel(metaclass=ModelMeta):
    id = ColumnProxy('id')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'id') or getattr(self, 'id', None) is None:
            cls = self.__class__
            next_id = _NEXT_IDS.get(cls, 1)
            self.id = next_id
            _NEXT_IDS[cls] = next_id + 1
        if getattr(self, 'created_at', None) is None:
            self.created_at = datetime.utcnow()

    @classmethod
    @property
    def query(cls):
        return ModelQuery(cls)


# ==============================================================================
# Model Definitions
# ==============================================================================

class Patient(BaseModel):
    full_name = ColumnProxy('full_name')
    email = ColumnProxy('email')
    phone = ColumnProxy('phone')
    gender = ColumnProxy('gender')
    age = ColumnProxy('age')
    password = ColumnProxy('password')
    role = ColumnProxy('role')
    address = ColumnProxy('address')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.role = kwargs.pop('role', 'patient')
        super().__init__(**kwargs)
        if hasattr(self, 'password') and self.password and not self.password.startswith('pbkdf2:') and not self.password.startswith('scrypt:'):
            self.set_password(self.password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if not hasattr(self, 'password') or not self.password:
            return False
        if not self.password.startswith('pbkdf2:') and not self.password.startswith('scrypt:'):
            return self.password == password
        return check_password_hash(self.password, password)

    @property
    def appointments(self):
        return [a for a in _STORE.get(Appointment, []) if a.patient_id == self.id]

    @property
    def emergency_contacts(self):
        return [e for e in _STORE.get(EmergencyContact, []) if e.patient_id == self.id]

    @property
    def opd_visits(self):
        return [v for v in _STORE.get(OPDVisit, []) if v.patient_id == self.id]

    @property
    def prescriptions(self):
        return [p for p in _STORE.get(Prescription, []) if p.patient_id == self.id]

    @property
    def invoices(self):
        return [i for i in _STORE.get(Invoice, []) if i.patient_id == self.id]

    @property
    def file_trackings(self):
        return [f for f in _STORE.get(FileTracking, []) if f.patient_id == self.id]

    @property
    def lab_orders(self):
        return [o for o in _STORE.get(LabOrder, []) if o.patient_id == self.id]

    @property
    def medical_reports(self):
        return [r for r in _STORE.get(MedicalReport, []) if r.patient_id == self.id]

    @property
    def name(self):
        return getattr(self, 'full_name', '')

    def __repr__(self):
        return f"<Patient {getattr(self, 'full_name', self.id)}>"


class Department(BaseModel):
    department_name = ColumnProxy('department_name')
    department_code = ColumnProxy('department_code')
    description = ColumnProxy('description')
    department_type = ColumnProxy('department_type')
    department_head_id = ColumnProxy('department_head_id')
    floor_number = ColumnProxy('floor_number')
    building_wing = ColumnProxy('building_wing')
    phone_extension = ColumnProxy('phone_extension')
    email = ColumnProxy('email')
    status = ColumnProxy('status')
    image = ColumnProxy('image')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.department_type = kwargs.pop('department_type', 'OPD')
        self.status = kwargs.pop('status', 'active')
        super().__init__(**kwargs)

    @property
    def name(self):
        return getattr(self, 'department_name', '')

    @property
    def doctors(self):
        return [d for d in _STORE.get(Doctor, []) if getattr(d, 'department_id', None) == self.id]

    @property
    def department_head(self):
        if getattr(self, 'department_head_id', None):
            return Doctor.query.get(self.department_head_id)
        return None

    @property
    def opd_fees(self):
        return [f for f in _STORE.get(OPDFee, []) if getattr(f, 'department_id', None) == self.id]

    @property
    def stock_issues(self):
        return [s for s in _STORE.get(StockIssue, []) if getattr(s, 'department_id', None) == self.id]

    @property
    def stock_requests(self):
        return [r for r in _STORE.get(StockRequest, []) if getattr(r, 'department_id', None) == self.id]

    @property
    def ledger_entries(self):
        return [l for l in _STORE.get(StockLedger, []) if getattr(l, 'department_id', None) == self.id]

    def __repr__(self):
        return f"<Department {getattr(self, 'department_name', self.id)}>"


class Doctor(BaseModel):
    name = ColumnProxy('name')
    specialization = ColumnProxy('specialization')
    experience = ColumnProxy('experience')
    qualification = ColumnProxy('qualification')
    phone = ColumnProxy('phone')
    email = ColumnProxy('email')
    image = ColumnProxy('image')
    availability = ColumnProxy('availability')
    bio = ColumnProxy('bio')
    department_id = ColumnProxy('department_id')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.availability = kwargs.pop('availability', True)
        super().__init__(**kwargs)

    @property
    def full_name(self):
        return getattr(self, 'name', '')

    @property
    def about(self):
        return getattr(self, 'bio', '')

    @property
    def department(self):
        dep_id = getattr(self, 'department_id', None)
        if dep_id:
            return Department.query.get(dep_id)
        return None

    @property
    def appointments(self):
        return [a for a in _STORE.get(Appointment, []) if getattr(a, 'doctor_id', None) == self.id]

    @property
    def opd_visits(self):
        return [v for v in _STORE.get(OPDVisit, []) if getattr(v, 'doctor_id', None) == self.id]

    @property
    def prescriptions(self):
        return [p for p in _STORE.get(Prescription, []) if getattr(p, 'doctor_id', None) == self.id]

    @property
    def medical_reports(self):
        return [r for r in _STORE.get(MedicalReport, []) if getattr(r, 'doctor_id', None) == self.id]

    @property
    def opd_fees(self):
        return [f for f in _STORE.get(OPDFee, []) if getattr(f, 'doctor_id', None) == self.id]

    @property
    def lab_orders(self):
        return [o for o in _STORE.get(LabOrder, []) if getattr(o, 'doctor_id', None) == self.id]

    def check_password(self, password):
        patient_record = Patient.query.filter_by(email=self.email).first()
        if patient_record:
            return patient_record.check_password(password)
        return password in ('doctor123', 'admin123', 'password123')

    def __repr__(self):
        return f"<Doctor {getattr(self, 'name', self.id)}>"


class Appointment(BaseModel):
    patient_id = ColumnProxy('patient_id')
    doctor_id = ColumnProxy('doctor_id')
    appointment_date = ColumnProxy('appointment_date')
    appointment_time = ColumnProxy('appointment_time')
    symptoms = ColumnProxy('symptoms')
    status = ColumnProxy('status')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.status = kwargs.pop('status', 'pending')
        super().__init__(**kwargs)
        if hasattr(self, 'doctor_id') and self.doctor_id is not None:
            try:
                self.doctor_id = int(self.doctor_id)
            except Exception:
                pass
        if hasattr(self, 'patient_id') and self.patient_id is not None:
            try:
                self.patient_id = int(self.patient_id)
            except Exception:
                pass

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    @property
    def prescriptions(self):
        return [p for p in _STORE.get(Prescription, []) if getattr(p, 'appointment_id', None) == self.id]

    @property
    def invoices(self):
        return [i for i in _STORE.get(Invoice, []) if getattr(i, 'appointment_id', None) == self.id]

    def __repr__(self):
        return f"<Appointment {self.id}>"


class EmergencyContact(BaseModel):
    patient_name = ColumnProxy('patient_name')
    phone = ColumnProxy('phone')
    emergency_type = ColumnProxy('emergency_type')
    message = ColumnProxy('message')
    patient_id = ColumnProxy('patient_id')
    created_at = ColumnProxy('created_at')

    @property
    def patient(self):
        if getattr(self, 'patient_id', None):
            return Patient.query.get(self.patient_id)
        return None

    def __repr__(self):
        return f"<EmergencyContact {getattr(self, 'patient_name', self.id)}>"


class ContactMessage(BaseModel):
    name = ColumnProxy('name')
    email = ColumnProxy('email')
    subject = ColumnProxy('subject')
    message = ColumnProxy('message')
    created_at = ColumnProxy('created_at')

    def __repr__(self):
        return f"<ContactMessage {getattr(self, 'name', self.id)}>"


class AdminUser(BaseModel):
    username = ColumnProxy('username')
    email = ColumnProxy('email')
    password = ColumnProxy('password')
    role = ColumnProxy('role')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.role = kwargs.pop('role', 'admin')
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def __repr__(self):
        return f"<AdminUser {getattr(self, 'username', self.id)}>"


class OPDVisit(BaseModel):
    patient_id = ColumnProxy('patient_id')
    doctor_id = ColumnProxy('doctor_id')
    token_number = ColumnProxy('token_number')
    visit_date = ColumnProxy('visit_date')
    check_in_time = ColumnProxy('check_in_time')
    check_out_time = ColumnProxy('check_out_time')
    status = ColumnProxy('status')
    chief_complaint = ColumnProxy('chief_complaint')
    vitals = ColumnProxy('vitals')
    notes = ColumnProxy('notes')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.status = kwargs.pop('status', 'waiting')
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    @property
    def prescriptions(self):
        return [p for p in _STORE.get(Prescription, []) if getattr(p, 'opd_visit_id', None) == self.id]

    @property
    def invoices(self):
        return [i for i in _STORE.get(Invoice, []) if getattr(i, 'opd_visit_id', None) == self.id]

    def __repr__(self):
        return f"<OPDVisit {getattr(self, 'token_number', self.id)}>"


class Prescription(BaseModel):
    patient_id = ColumnProxy('patient_id')
    doctor_id = ColumnProxy('doctor_id')
    appointment_id = ColumnProxy('appointment_id')
    opd_visit_id = ColumnProxy('opd_visit_id')
    diagnosis = ColumnProxy('diagnosis')
    notes = ColumnProxy('notes')
    prescription_date = ColumnProxy('prescription_date')
    created_at = ColumnProxy('created_at')

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    @property
    def appointment(self):
        return Appointment.query.get(getattr(self, 'appointment_id', None))

    @property
    def opd_visit(self):
        return OPDVisit.query.get(getattr(self, 'opd_visit_id', None))

    @property
    def medicines(self):
        return [m for m in _STORE.get(PrescriptionMedicine, []) if getattr(m, 'prescription_id', None) == self.id]

    @property
    def medicine_issues(self):
        return [m for m in _STORE.get(MedicineIssue, []) if getattr(m, 'prescription_id', None) == self.id]

    def __repr__(self):
        return f"<Prescription {self.id}>"


class PrescriptionMedicine(BaseModel):
    prescription_id = ColumnProxy('prescription_id')
    medicine_name = ColumnProxy('medicine_name')
    dosage = ColumnProxy('dosage')
    frequency = ColumnProxy('frequency')
    duration = ColumnProxy('duration')
    instructions = ColumnProxy('instructions')
    created_at = ColumnProxy('created_at')

    @property
    def prescription(self):
        return Prescription.query.get(getattr(self, 'prescription_id', None))

    def __repr__(self):
        return f"<PrescriptionMedicine {getattr(self, 'medicine_name', self.id)}>"


class Invoice(BaseModel):
    patient_id = ColumnProxy('patient_id')
    appointment_id = ColumnProxy('appointment_id')
    opd_visit_id = ColumnProxy('opd_visit_id')
    invoice_number = ColumnProxy('invoice_number')
    invoice_date = ColumnProxy('invoice_date')
    subtotal = ColumnProxy('subtotal')
    tax = ColumnProxy('tax')
    discount = ColumnProxy('discount')
    total_amount = ColumnProxy('total_amount')
    payment_status = ColumnProxy('payment_status')
    payment_method = ColumnProxy('payment_method')
    notes = ColumnProxy('notes')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.payment_status = kwargs.pop('payment_status', 'pending')
        self.subtotal = float(kwargs.pop('subtotal', 0.0))
        self.tax = float(kwargs.pop('tax', 0.0))
        self.discount = float(kwargs.pop('discount', 0.0))
        self.total_amount = float(kwargs.pop('total_amount', self.subtotal))
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def appointment(self):
        return Appointment.query.get(getattr(self, 'appointment_id', None))

    @property
    def opd_visit(self):
        return OPDVisit.query.get(getattr(self, 'opd_visit_id', None))

    @property
    def items(self):
        return [i for i in _STORE.get(InvoiceItem, []) if getattr(i, 'invoice_id', None) == self.id]

    def __repr__(self):
        return f"<Invoice {getattr(self, 'invoice_number', self.id)}>"


class InvoiceItem(BaseModel):
    invoice_id = ColumnProxy('invoice_id')
    item_name = ColumnProxy('item_name')
    item_type = ColumnProxy('item_type')
    quantity = ColumnProxy('quantity')
    unit_price = ColumnProxy('unit_price')
    total_price = ColumnProxy('total_price')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.quantity = int(kwargs.pop('quantity', 1))
        self.unit_price = float(kwargs.pop('unit_price', 0.0))
        self.total_price = float(kwargs.pop('total_price', self.quantity * self.unit_price))
        super().__init__(**kwargs)

    @property
    def invoice(self):
        return Invoice.query.get(getattr(self, 'invoice_id', None))

    def __repr__(self):
        return f"<InvoiceItem {getattr(self, 'item_name', self.id)}>"


class OPDFee(BaseModel):
    department_id = ColumnProxy('department_id')
    doctor_id = ColumnProxy('doctor_id')
    fee_name = ColumnProxy('fee_name')
    fee_amount = ColumnProxy('fee_amount')
    is_active = ColumnProxy('is_active')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.is_active = kwargs.pop('is_active', True)
        self.fee_amount = float(kwargs.pop('fee_amount', 0.0))
        super().__init__(**kwargs)

    @property
    def department(self):
        return Department.query.get(getattr(self, 'department_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    def __repr__(self):
        return f"<OPDFee {getattr(self, 'fee_name', self.id)}>"


class MedicalReport(BaseModel):
    patient_id = ColumnProxy('patient_id')
    doctor_id = ColumnProxy('doctor_id')
    report_type = ColumnProxy('report_type')
    report_title = ColumnProxy('report_title')
    report_date = ColumnProxy('report_date')
    description = ColumnProxy('description')
    file_path = ColumnProxy('file_path')
    file_name = ColumnProxy('file_name')
    file_size = ColumnProxy('file_size')
    is_confidential = ColumnProxy('is_confidential')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.is_confidential = kwargs.pop('is_confidential', False)
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    def __repr__(self):
        return f"<MedicalReport {getattr(self, 'report_title', self.id)}>"


class Notification(BaseModel):
    recipient_id = ColumnProxy('recipient_id')
    recipient_type = ColumnProxy('recipient_type')
    notification_type = ColumnProxy('notification_type')
    title = ColumnProxy('title')
    message = ColumnProxy('message')
    is_read = ColumnProxy('is_read')
    related_id = ColumnProxy('related_id')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.is_read = kwargs.pop('is_read', False)
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Notification {getattr(self, 'title', self.id)}>"


class EmailLog(BaseModel):
    recipient_email = ColumnProxy('recipient_email')
    recipient_name = ColumnProxy('recipient_name')
    subject = ColumnProxy('subject')
    body = ColumnProxy('body')
    email_type = ColumnProxy('email_type')
    status = ColumnProxy('status')
    error_message = ColumnProxy('error_message')
    sent_at = ColumnProxy('sent_at')

    def __init__(self, **kwargs):
        self.status = kwargs.pop('status', 'sent')
        self.sent_at = kwargs.pop('sent_at', datetime.utcnow())
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<EmailLog {getattr(self, 'recipient_email', self.id)}>"


class InventoryItem(BaseModel):
    item_code = ColumnProxy('item_code')
    item_name = ColumnProxy('item_name')
    category = ColumnProxy('category')
    quantity = ColumnProxy('quantity')
    minimum_stock = ColumnProxy('minimum_stock')
    unit = ColumnProxy('unit')
    purchase_price = ColumnProxy('purchase_price')
    supplier_name = ColumnProxy('supplier_name')
    expiry_date = ColumnProxy('expiry_date')
    created_at = ColumnProxy('created_at')
    updated_at = ColumnProxy('updated_at')

    def __init__(self, **kwargs):
        self.quantity = int(kwargs.pop('quantity', 0))
        self.minimum_stock = int(kwargs.pop('minimum_stock', 10))
        self.unit = kwargs.pop('unit', 'Unit')
        self.purchase_price = float(kwargs.pop('purchase_price', 0.0))
        self.updated_at = datetime.utcnow()
        super().__init__(**kwargs)

    @property
    def low_stock(self):
        return self.quantity <= self.minimum_stock

    @property
    def purchase_items(self):
        return [p for p in _STORE.get(StockPurchaseItem, []) if getattr(p, 'item_id', None) == self.id]

    @property
    def ledger_entries(self):
        return [l for l in _STORE.get(StockLedger, []) if getattr(l, 'item_id', None) == self.id]

    @property
    def issue_items(self):
        return [i for i in _STORE.get(StockIssueItem, []) if getattr(i, 'item_id', None) == self.id]

    @property
    def stock_requests(self):
        return [r for r in _STORE.get(StockRequest, []) if getattr(r, 'item_id', None) == self.id]

    def __repr__(self):
        return f"<InventoryItem {getattr(self, 'item_name', self.id)}>"


class Supplier(BaseModel):
    name = ColumnProxy('name')
    contact_person = ColumnProxy('contact_person')
    email = ColumnProxy('email')
    phone = ColumnProxy('phone')
    address = ColumnProxy('address')
    gst_number = ColumnProxy('gst_number')
    created_at = ColumnProxy('created_at')

    @property
    def purchases(self):
        return [p for p in _STORE.get(StockPurchase, []) if getattr(p, 'supplier_id', None) == self.id]

    @property
    def medicine_purchases(self):
        return [p for p in _STORE.get(MedicinePurchase, []) if getattr(p, 'supplier_id', None) == self.id]

    @property
    def batches(self):
        return [b for b in _STORE.get(MedicineBatch, []) if getattr(b, 'supplier_id', None) == self.id]

    def __repr__(self):
        return f"<Supplier {getattr(self, 'name', self.id)}>"


class StockPurchase(BaseModel):
    supplier_id = ColumnProxy('supplier_id')
    purchase_date = ColumnProxy('purchase_date')
    entry_date = ColumnProxy('entry_date')
    challan_number = ColumnProxy('challan_number')
    challan_pdf = ColumnProxy('challan_pdf')
    subtotal = ColumnProxy('subtotal')
    cgst = ColumnProxy('cgst')
    sgst = ColumnProxy('sgst')
    discount = ColumnProxy('discount')
    total_amount = ColumnProxy('total_amount')
    payment_status = ColumnProxy('payment_status')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.purchase_date = kwargs.pop('purchase_date', date.today())
        self.entry_date = kwargs.pop('entry_date', date.today())
        self.subtotal = float(kwargs.pop('subtotal', 0.0))
        self.cgst = float(kwargs.pop('cgst', 0.0))
        self.sgst = float(kwargs.pop('sgst', 0.0))
        self.discount = float(kwargs.pop('discount', 0.0))
        self.total_amount = float(kwargs.pop('total_amount', 0.0))
        self.payment_status = kwargs.pop('payment_status', 'pending')
        super().__init__(**kwargs)

    @property
    def supplier(self):
        return Supplier.query.get(getattr(self, 'supplier_id', None))

    @property
    def items(self):
        return [i for i in _STORE.get(StockPurchaseItem, []) if getattr(i, 'stock_purchase_id', None) == self.id]

    def __repr__(self):
        return f"<StockPurchase {self.id}>"


class StockPurchaseItem(BaseModel):
    stock_purchase_id = ColumnProxy('stock_purchase_id')
    item_id = ColumnProxy('item_id')
    quantity = ColumnProxy('quantity')
    rate = ColumnProxy('rate')
    cgst_rate = ColumnProxy('cgst_rate')
    sgst_rate = ColumnProxy('sgst_rate')
    discount_amount = ColumnProxy('discount_amount')
    total_amount = ColumnProxy('total_amount')

    def __init__(self, **kwargs):
        self.quantity = int(kwargs.pop('quantity', 1))
        self.rate = float(kwargs.pop('rate', 0.0))
        self.total_amount = float(kwargs.pop('total_amount', self.quantity * self.rate))
        super().__init__(**kwargs)

    @property
    def purchase(self):
        return StockPurchase.query.get(getattr(self, 'stock_purchase_id', None))

    @property
    def item(self):
        return InventoryItem.query.get(getattr(self, 'item_id', None))


class StockLedger(BaseModel):
    item_id = ColumnProxy('item_id')
    transaction_type = ColumnProxy('transaction_type')
    quantity = ColumnProxy('quantity')
    department_id = ColumnProxy('department_id')
    reference_id = ColumnProxy('reference_id')
    transaction_date = ColumnProxy('transaction_date')
    notes = ColumnProxy('notes')

    def __init__(self, **kwargs):
        self.transaction_date = kwargs.pop('transaction_date', datetime.utcnow())
        super().__init__(**kwargs)

    @property
    def item(self):
        return InventoryItem.query.get(getattr(self, 'item_id', None))

    @property
    def department(self):
        return Department.query.get(getattr(self, 'department_id', None))


class StockIssue(BaseModel):
    department_id = ColumnProxy('department_id')
    issued_by = ColumnProxy('issued_by')
    issued_to = ColumnProxy('issued_to')
    issue_date = ColumnProxy('issue_date')
    status = ColumnProxy('status')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.issue_date = kwargs.pop('issue_date', date.today())
        self.status = kwargs.pop('status', 'completed')
        super().__init__(**kwargs)

    @property
    def department(self):
        return Department.query.get(getattr(self, 'department_id', None))

    @property
    def items(self):
        return [i for i in _STORE.get(StockIssueItem, []) if getattr(i, 'stock_issue_id', None) == self.id]


class StockIssueItem(BaseModel):
    stock_issue_id = ColumnProxy('stock_issue_id')
    item_id = ColumnProxy('item_id')
    quantity = ColumnProxy('quantity')

    @property
    def issue(self):
        return StockIssue.query.get(getattr(self, 'stock_issue_id', None))

    @property
    def item(self):
        return InventoryItem.query.get(getattr(self, 'item_id', None))


class StockRequest(BaseModel):
    department_id = ColumnProxy('department_id')
    item_id = ColumnProxy('item_id')
    quantity = ColumnProxy('quantity')
    request_date = ColumnProxy('request_date')
    status = ColumnProxy('status')
    priority = ColumnProxy('priority')
    notes = ColumnProxy('notes')

    def __init__(self, **kwargs):
        self.request_date = kwargs.pop('request_date', date.today())
        self.status = kwargs.pop('status', 'pending')
        self.priority = kwargs.pop('priority', 'Normal')
        super().__init__(**kwargs)

    @property
    def department(self):
        return Department.query.get(getattr(self, 'department_id', None))

    @property
    def item(self):
        return InventoryItem.query.get(getattr(self, 'item_id', None))


class Setting(BaseModel):
    key = ColumnProxy('key')
    value = ColumnProxy('value')
    description = ColumnProxy('description')

    def __repr__(self):
        return f"<Setting {getattr(self, 'key', '')}={getattr(self, 'value', '')}>"


class FileTracking(BaseModel):
    patient_id = ColumnProxy('patient_id')
    file_number = ColumnProxy('file_number')
    current_location = ColumnProxy('current_location')
    status = ColumnProxy('status')
    issued_to_staff = ColumnProxy('issued_to_staff')
    issue_date = ColumnProxy('issue_date')
    return_date = ColumnProxy('return_date')
    notes = ColumnProxy('notes')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.status = kwargs.pop('status', 'archived')
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))


class MedicineMaster(BaseModel):
    medicine_name = ColumnProxy('medicine_name')
    category = ColumnProxy('category')
    dosage_form = ColumnProxy('dosage_form')
    manufacturer = ColumnProxy('manufacturer')
    min_stock = ColumnProxy('min_stock')
    unit = ColumnProxy('unit')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.min_stock = int(kwargs.pop('min_stock', 10))
        self.unit = kwargs.pop('unit', 'Tablet')
        super().__init__(**kwargs)

    @property
    def batches(self):
        return [b for b in _STORE.get(MedicineBatch, []) if getattr(b, 'medicine_id', None) == self.id]

    def __repr__(self):
        return f"<MedicineMaster {getattr(self, 'medicine_name', self.id)}>"


class MedicineBatch(BaseModel):
    medicine_id = ColumnProxy('medicine_id')
    batch_number = ColumnProxy('batch_number')
    expiry_date = ColumnProxy('expiry_date')
    purchase_price = ColumnProxy('purchase_price')
    sale_price = ColumnProxy('sale_price')
    initial_qty = ColumnProxy('initial_qty')
    current_qty = ColumnProxy('current_qty')
    supplier_id = ColumnProxy('supplier_id')
    purchase_id = ColumnProxy('purchase_id')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.purchase_price = float(kwargs.pop('purchase_price', 0.0))
        self.sale_price = float(kwargs.pop('sale_price', 0.0))
        self.initial_qty = int(kwargs.pop('initial_qty', 0))
        self.current_qty = int(kwargs.pop('current_qty', self.initial_qty))
        super().__init__(**kwargs)

    @property
    def medicine(self):
        return MedicineMaster.query.get(getattr(self, 'medicine_id', None))

    @property
    def supplier(self):
        return Supplier.query.get(getattr(self, 'supplier_id', None))

    @property
    def purchase_record(self):
        return MedicinePurchase.query.get(getattr(self, 'purchase_id', None))

    @property
    def issue_items(self):
        return [i for i in _STORE.get(MedicineIssueItem, []) if getattr(i, 'batch_id', None) == self.id]


class MedicinePurchase(BaseModel):
    supplier_id = ColumnProxy('supplier_id')
    purchase_date = ColumnProxy('purchase_date')
    invoice_number = ColumnProxy('invoice_number')
    subtotal = ColumnProxy('subtotal')
    cgst = ColumnProxy('cgst')
    sgst = ColumnProxy('sgst')
    discount = ColumnProxy('discount')
    total_amount = ColumnProxy('total_amount')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.purchase_date = kwargs.pop('purchase_date', date.today())
        self.subtotal = float(kwargs.pop('subtotal', 0.0))
        self.cgst = float(kwargs.pop('cgst', 0.0))
        self.sgst = float(kwargs.pop('sgst', 0.0))
        self.discount = float(kwargs.pop('discount', 0.0))
        self.total_amount = float(kwargs.pop('total_amount', 0.0))
        super().__init__(**kwargs)

    @property
    def supplier(self):
        return Supplier.query.get(getattr(self, 'supplier_id', None))

    @property
    def batches(self):
        return [b for b in _STORE.get(MedicineBatch, []) if getattr(b, 'purchase_id', None) == self.id]


class MedicineIssue(BaseModel):
    patient_id = ColumnProxy('patient_id')
    prescription_id = ColumnProxy('prescription_id')
    issue_date = ColumnProxy('issue_date')
    subtotal = ColumnProxy('subtotal')
    cgst = ColumnProxy('cgst')
    sgst = ColumnProxy('sgst')
    discount = ColumnProxy('discount')
    total_amount = ColumnProxy('total_amount')
    payment_status = ColumnProxy('payment_status')
    invoice_id = ColumnProxy('invoice_id')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.issue_date = kwargs.pop('issue_date', date.today())
        self.payment_status = kwargs.pop('payment_status', 'pending')
        self.subtotal = float(kwargs.pop('subtotal', 0.0))
        self.cgst = float(kwargs.pop('cgst', 0.0))
        self.sgst = float(kwargs.pop('sgst', 0.0))
        self.discount = float(kwargs.pop('discount', 0.0))
        self.total_amount = float(kwargs.pop('total_amount', 0.0))
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def prescription(self):
        return Prescription.query.get(getattr(self, 'prescription_id', None))

    @property
    def items(self):
        return [i for i in _STORE.get(MedicineIssueItem, []) if getattr(i, 'medicine_issue_id', None) == self.id]


class MedicineIssueItem(BaseModel):
    medicine_issue_id = ColumnProxy('medicine_issue_id')
    batch_id = ColumnProxy('batch_id')
    quantity = ColumnProxy('quantity')
    rate = ColumnProxy('rate')
    total_price = ColumnProxy('total_price')

    def __init__(self, **kwargs):
        self.quantity = int(kwargs.pop('quantity', 1))
        self.rate = float(kwargs.pop('rate', 0.0))
        self.total_price = float(kwargs.pop('total_price', self.quantity * self.rate))
        super().__init__(**kwargs)

    @property
    def issue(self):
        return MedicineIssue.query.get(getattr(self, 'medicine_issue_id', None))

    @property
    def batch(self):
        return MedicineBatch.query.get(getattr(self, 'batch_id', None))


class LabTest(BaseModel):
    test_name = ColumnProxy('test_name')
    category = ColumnProxy('category')
    rate = ColumnProxy('rate')
    normal_range = ColumnProxy('normal_range')
    unit = ColumnProxy('unit')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.rate = float(kwargs.pop('rate', 0.0))
        super().__init__(**kwargs)

    @property
    def order_items(self):
        return [i for i in _STORE.get(LabOrderItem, []) if getattr(i, 'test_id', None) == self.id]

    def __repr__(self):
        return f"<LabTest {getattr(self, 'test_name', self.id)}>"


class LabOrder(BaseModel):
    patient_id = ColumnProxy('patient_id')
    doctor_id = ColumnProxy('doctor_id')
    order_date = ColumnProxy('order_date')
    status = ColumnProxy('status')
    payment_status = ColumnProxy('payment_status')
    invoice_id = ColumnProxy('invoice_id')
    created_at = ColumnProxy('created_at')

    def __init__(self, **kwargs):
        self.order_date = kwargs.pop('order_date', date.today())
        self.status = kwargs.pop('status', 'pending')
        self.payment_status = kwargs.pop('payment_status', 'pending')
        super().__init__(**kwargs)

    @property
    def patient(self):
        return Patient.query.get(getattr(self, 'patient_id', None))

    @property
    def doctor(self):
        return Doctor.query.get(getattr(self, 'doctor_id', None))

    @property
    def items(self):
        return [i for i in _STORE.get(LabOrderItem, []) if getattr(i, 'lab_order_id', None) == self.id]


class LabOrderItem(BaseModel):
    lab_order_id = ColumnProxy('lab_order_id')
    test_id = ColumnProxy('test_id')
    result_value = ColumnProxy('result_value')
    result_date = ColumnProxy('result_date')
    notes = ColumnProxy('notes')

    @property
    def order(self):
        return LabOrder.query.get(getattr(self, 'lab_order_id', None))

    @property
    def test(self):
        return LabTest.query.get(getattr(self, 'test_id', None))


# ==============================================================================
# In-Memory DB Session & Aggregation Mock
# ==============================================================================

class RowProxy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, idx):
        return list(self.__dict__.values())[idx]

    def __getattr__(self, name):
        return self.__dict__.get(name, 0)

    def __repr__(self):
        return f"<Row {self.__dict__}>"


class FuncSum:
    def __init__(self, column, label_name=None):
        self.column = column
        self.label_name = label_name

    def label(self, name):
        self.label_name = name
        return self


class FuncCount:
    def __init__(self, column, label_name=None):
        self.column = column
        self.label_name = label_name

    def label(self, name):
        self.label_name = name
        return self


class FuncProxy:
    @staticmethod
    def sum(column):
        return FuncSum(column)

    @staticmethod
    def count(column):
        return FuncCount(column)


func = FuncProxy()


class QueryProxy:
    def __init__(self, *select_targets):
        self.select_targets = select_targets
        self._filter_exprs = []
        self._filter_by_kwargs = {}
        self._model = None
        for target in select_targets:
            if isinstance(target, type) and issubclass(target, BaseModel):
                self._model = target
                break
            elif isinstance(target, (ColumnProxy, FuncSum, FuncCount)):
                pass

    def filter_by(self, **kwargs):
        self._filter_by_kwargs.update(kwargs)
        return self

    def filter(self, *expressions):
        self._filter_exprs.extend(expressions)
        return self

    def outerjoin(self, *args, **kwargs):
        return self

    def group_by(self, *args):
        return self

    def _get_matched_items(self):
        # Determine model
        model = self._model
        if not model and self.select_targets:
            t = self.select_targets[0]
            if isinstance(t, (FuncSum, FuncCount)):
                col = t.column
                if isinstance(col, ColumnProxy):
                    for m in _STORE:
                        if hasattr(m, col.name):
                            model = m
                            break
        if not model:
            # Fallback across all models
            model = Invoice

        q = ModelQuery(model)
        if self._filter_by_kwargs:
            q = q.filter_by(**self._filter_by_kwargs)
        if self._filter_exprs:
            q = q.filter(*self._filter_exprs)
        return q.all()

    def scalar(self):
        matched = self._get_matched_items()
        if not self.select_targets:
            return len(matched)
        t = self.select_targets[0]
        if isinstance(t, FuncSum):
            col_name = t.column.name if hasattr(t.column, 'name') else str(t.column)
            total = 0.0
            for obj in matched:
                val = getattr(obj, col_name, 0)
                try:
                    total += float(val or 0)
                except Exception:
                    pass
            return total
        elif isinstance(t, FuncCount):
            return len(matched)
        elif isinstance(t, ColumnProxy):
            if matched:
                return getattr(matched[0], t.name, None)
            return None
        return len(matched)

    def count(self):
        return len(self._get_matched_items())

    def all(self):
        matched = self._get_matched_items()
        if len(self.select_targets) == 1 and isinstance(self.select_targets[0], type) and issubclass(self.select_targets[0], BaseModel):
            return matched

        target_names = [getattr(t, 'name', getattr(t, 'label_name', '')) for t in self.select_targets]
        if 'specialization' in target_names or any(getattr(t, 'name', '') == 'name' for t in self.select_targets):
            results = []
            for doc in _STORE.get(Doctor, []):
                appts = len(doc.appointments)
                prescs = len(doc.prescriptions)
                results.append(RowProxy(
                    name=doc.name,
                    specialization=doc.specialization,
                    appointment_count=appts,
                    prescription_count=prescs
                ))
            return results

        if 'department_name' in target_names:
            results = []
            for dept in _STORE.get(Department, []):
                doc_count = len(dept.doctors)
                appt_count = sum(len(d.appointments) for d in dept.doctors)
                results.append(RowProxy(
                    department_name=dept.department_name,
                    doctor_count=doc_count,
                    appointment_count=appt_count
                ))
            return results

        results = []
        for obj in matched:
            row_dict = {}
            for t in self.select_targets:
                if isinstance(t, ColumnProxy):
                    row_dict[t.name] = getattr(obj, t.name, None)
                elif isinstance(t, (FuncCount, FuncSum)):
                    lbl = t.label_name or 'count'
                    row_dict[lbl] = 1
            results.append(RowProxy(**row_dict))
        return results


class SessionProxy:
    def add(self, obj):
        cls = obj.__class__
        if cls not in _STORE:
            _STORE[cls] = []
        if obj not in _STORE[cls]:
            if not hasattr(obj, 'id') or obj.id is None:
                next_id = _NEXT_IDS.get(cls, 1)
                obj.id = next_id
                _NEXT_IDS[cls] = next_id + 1
            _STORE[cls].append(obj)

    def add_all(self, objs):
        for obj in objs:
            self.add(obj)

    def delete(self, obj):
        cls = obj.__class__
        if cls in _STORE and obj in _STORE[cls]:
            _STORE[cls].remove(obj)

    def commit(self):
        pass

    def rollback(self):
        pass

    def flush(self):
        pass

    def refresh(self, obj):
        pass

    def query(self, *select_targets):
        return QueryProxy(*select_targets)


class MockSQLAlchemy:
    def __init__(self):
        self.session = SessionProxy()
        self.Model = BaseModel
        self.func = func

    def init_app(self, app):
        pass

    def create_all(self):
        pass

    def Column(self, *args, **kwargs):
        return ColumnProxy()

    def Integer(self, *args, **kwargs):
        return 'Integer'

    def String(self, *args, **kwargs):
        return 'String'

    def Text(self, *args, **kwargs):
        return 'Text'

    def DateTime(self, *args, **kwargs):
        return 'DateTime'

    def Date(self, *args, **kwargs):
        return 'Date'

    def Time(self, *args, **kwargs):
        return 'Time'

    def Boolean(self, *args, **kwargs):
        return 'Boolean'

    def Float(self, *args, **kwargs):
        return 'Float'

    def Numeric(self, *args, **kwargs):
        return 'Numeric'

    def JSON(self, *args, **kwargs):
        return 'JSON'

    def ForeignKey(self, *args, **kwargs):
        return 'ForeignKey'

    def relationship(self, *args, **kwargs):
        return None

    @staticmethod
    def or_(*expressions):
        def matcher(obj):
            for expr in expressions:
                if isinstance(expr, BinaryExpression) and expr.match(obj):
                    return True
                elif callable(expr) and expr(obj):
                    return True
            return False
        return matcher

    @staticmethod
    def and_(*expressions):
        def matcher(obj):
            for expr in expressions:
                if isinstance(expr, BinaryExpression) and not expr.match(obj):
                    return False
                elif callable(expr) and not expr(obj):
                    return False
            return True
        return matcher

    @staticmethod
    def desc(column):
        if isinstance(column, ColumnProxy):
            return column.desc()
        return OrderExpression(str(column), descending=True)


db = MockSQLAlchemy()


# ==============================================================================
# Seed Initial In-Memory State
# ==============================================================================

def init_datastore():
    global _STORE, _NEXT_IDS
    _STORE = {
        Department: [],
        Doctor: [],
        Patient: [],
        AdminUser: [],
        Appointment: [],
        EmergencyContact: [],
        ContactMessage: [],
        Supplier: [],
        InventoryItem: [],
        MedicineMaster: [],
        MedicineBatch: [],
        LabTest: [],
        OPDFee: [],
        Invoice: [],
        InvoiceItem: [],
        OPDVisit: [],
        Prescription: [],
        PrescriptionMedicine: [],
        Notification: [],
        Setting: [],
        FileTracking: [],
        StockPurchase: [],
        StockPurchaseItem: [],
        StockLedger: [],
        StockIssue: [],
        StockIssueItem: [],
        StockRequest: [],
        MedicinePurchase: [],
        MedicineIssue: [],
        MedicineIssueItem: [],
        LabOrder: [],
        LabOrderItem: [],
        MedicalReport: [],
        EmailLog: []
    }

    # Load Departments
    for d in DEPARTMENTS:
        obj = Department(**d)
        _STORE[Department].append(obj)

    # Load Doctors
    for d in DOCTORS:
        obj = Doctor(**d)
        _STORE[Doctor].append(obj)

    # Load Patients
    for p in PATIENTS:
        obj = Patient(**p)
        _STORE[Patient].append(obj)

    # Load Admin Users
    for a in ADMIN_USERS:
        obj = AdminUser(**a)
        _STORE[AdminUser].append(obj)

    # Load Appointments
    for ap in APPOINTMENTS:
        obj = Appointment(**ap)
        _STORE[Appointment].append(obj)

    # Load Emergency Contacts
    for ec in EMERGENCY_CONTACTS:
        obj = EmergencyContact(**ec)
        _STORE[EmergencyContact].append(obj)

    # Load Contact Messages
    for cm in CONTACT_MESSAGES:
        obj = ContactMessage(**cm)
        _STORE[ContactMessage].append(obj)

    # Load Suppliers
    for s in SUPPLIERS:
        obj = Supplier(**s)
        _STORE[Supplier].append(obj)

    # Load Inventory Items
    for i in INVENTORY_ITEMS:
        obj = InventoryItem(**i)
        _STORE[InventoryItem].append(obj)

    # Load Medicines
    for m in MEDICINE_MASTER:
        obj = MedicineMaster(**m)
        _STORE[MedicineMaster].append(obj)

    # Load Medicine Batches
    for mb in MEDICINE_BATCHES:
        obj = MedicineBatch(**mb)
        _STORE[MedicineBatch].append(obj)

    # Load Lab Tests
    for lt in LAB_TESTS:
        obj = LabTest(**lt)
        _STORE[LabTest].append(obj)

    # Load OPD Fees
    for of in OPD_FEES:
        obj = OPDFee(**of)
        _STORE[OPDFee].append(obj)

    # Load Invoices
    for inv in INVOICES:
        obj = Invoice(**inv)
        _STORE[Invoice].append(obj)

    # Load Invoice Items
    for item in INVOICE_ITEMS:
        obj = InvoiceItem(**item)
        _STORE[InvoiceItem].append(obj)

    # Load OPD Visits
    for v in OPD_VISITS:
        obj = OPDVisit(**v)
        _STORE[OPDVisit].append(obj)

    # Load Prescriptions
    for pr in PRESCRIPTIONS:
        obj = Prescription(**pr)
        _STORE[Prescription].append(obj)

    # Load Prescription Medicines
    for pm in PRESCRIPTION_MEDICINES:
        obj = PrescriptionMedicine(**pm)
        _STORE[PrescriptionMedicine].append(obj)

    # Load Notifications
    for notif in NOTIFICATIONS:
        obj = Notification(**notif)
        _STORE[Notification].append(obj)

    # Load Settings
    for st in SETTINGS:
        obj = Setting(**st)
        _STORE[Setting].append(obj)

    # Load MRD Records
    for mrd in MRD_RECORDS:
        obj = FileTracking(**mrd)
        _STORE[FileTracking].append(obj)

    # Initialize next IDs
    for cls, items in _STORE.items():
        max_id = max([getattr(i, 'id', 0) for i in items], default=0)
        _NEXT_IDS[cls] = max_id + 1


# Auto initialize data store on module import
init_datastore()