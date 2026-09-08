# Sahara Hospital - Database-Free Healthcare Web Application

A fully animated modern hospital website and management system built with Python Flask, HTML5, Vanilla CSS, and Bootstrap 5. **Completely database-free (zero external database setup required)** and ready for instant deployment on **Render**.

---

## 🌟 Key Features

- **Database-Free Architecture**: No MySQL, PostgreSQL, SQLite, or MongoDB required. Operates using high-speed in-memory data structures pre-populated with realistic healthcare demo datasets.
- **Render-Ready**: Includes `render.yaml`, `Procfile`, and dynamic `PORT` binding for instant 1-click cloud deployment.
- **Realistic Static Demo Data**: Pre-seeded with authentic medical departments, doctor profiles with high-resolution Unsplash portraits, patient records, invoices, pharmacy medicines, lab tests, inventory, and OPD queues.
- **Interactive Forms**: Appointment booking, emergency hotlines, and contact messages submit smoothly without errors.
- **Multi-Role Authentication**: Dedicated portals for Patients, Doctors, Hospital Staff, Admin, and Superadmin with pre-configured demo logins.
- **Hospital Management Modules**:
  - **OPD Queue & Token System**: Patient check-in and queue management.
  - **Pharmacy Module**: Medicine catalog, batch management, and dispensing.
  - **Laboratory System**: Diagnostic test master and lab order tracking.
  - **Billing & Invoices**: Itemized invoice creation and receipt printing.
  - **Inventory & Supply Chain**: Supplier directory, purchase orders, and stock ledgers.
  - **Medical Records (MRD)**: File tracking and digital archive registry.
  - **Analytics & Reports**: Visual statistics for patient volume, revenue, and doctor performance.

---

## 🔑 Demo Login Credentials

| Role | Username / Email | Password | Dashboard URL |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | `/admin/dashboard` |
| **Doctor** | `sarah.johnson@saharahospital.com` | `doctor123` | `/doctor/dashboard` |
| **Patient** | `john.smith@email.com` | `password123` | `/dashboard` |
| **Staff** | `staff@saharahospital.com` | `staff123` | `/staff/dashboard` |
| **Superadmin** | `superadmin@sahara.com` | `super123` | `/superadmin/dashboard` |

---

## 🚀 Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
cd backend
python app.py
```
Or with Gunicorn:
```bash
gunicorn "app:create_app()"
```

Open your browser at `http://127.0.0.1:5000`

---

## ☁️ Deploying on Render

### Option A: Web Service via Git Repository (Recommended)
1. In the Render Dashboard, click **New +** -> **Web Service**.
2. Connect your Git repository.
3. Configure the following settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir backend "app:create_app()"`
   - **Branch**: `main` (or your default branch)
4. Click **Create Web Service**.

### Option B: Deploy via Blueprint (`render.yaml`)
Render will automatically detect `render.yaml` and configure the Web Service with zero manual input required!

---

## 📂 Project Architecture

```
Sahara Hospital/
├── backend/
│   ├── app.py                     # Flask application factory and blueprint registration
│   ├── config.py                  # Environment and secret configuration
│   ├── models.py                  # Pure in-memory model & query engine (DB-free)
│   ├── requirements.txt           # Python dependencies
│   ├── Procfile                   # Backend-specific Procfile
│   ├── data/                      # Static demo data store
│   │   ├── departments_data.py    # Department listings & Unsplash photos
│   │   ├── doctors_data.py        # Doctor credentials, bios & portraits
│   │   ├── patients_data.py       # Safe demo patients & admin accounts
│   │   ├── appointments_data.py   # Scheduled appointments
│   │   └── hospital_data.py       # Inventory, Pharmacy, Lab, Invoices, OPD data
│   ├── routes/                    # 21 modular Flask Blueprints
│   ├── templates/                 # Jinja2 HTML views
│   ├── static/                    # CSS, JS, and image assets
│   ├── validation_script.py       # Verification script
│   └── test_suite.py              # Full end-to-end automated test suite
├── render.yaml                    # Render Blueprint configuration
├── Procfile                       # Root deployment Procfile
├── requirements.txt               # Root dependencies
└── README.md                      # Documentation
```
