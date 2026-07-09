# AI-Powered Business Analytics Dashboard

A complete business analytics platform combining an interactive FastAPI backend, a polished glassmorphic frontend, machine learning forecasting, database-driven AI insights, and full CRUD management for customers, products, sales, employees, and payments.

---

## 🚀 What this project delivers

*   **Analytics dashboard** with sales trends, profit margins, payment breakdowns, and KPI summaries.
*   **AI assistant** that can answer natural language questions using live SQL-backed data.
*   **ML forecasting** using saved regression models for revenue and sales predictions.
*   **CRUD management** for Customers, Products, Sales, Employees, and Payments.
*   **Responsive modern UI** with dark glassmorphic styling and client-side dashboard controls.
*   **Convenient startup scripts** for Windows PowerShell and batch execution.

---

## 🧰 Technology Stack

*   **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn
*   **Frontend**: HTML, CSS, JavaScript
*   **Machine learning**: scikit-learn, pandas, numpy, joblib
*   **Database**: SQLite

---

## 📁 Repository Structure

```
├── backend/
│   ├── models.py           # Database models
│   ├── schemas.py          # Request/response schemas
│   ├── crud.py             # CRUD helper functions
│   ├── main.py             # FastAPI app entrypoint
│   ├── database.py         # SQLite engine and session setup
│   ├── dependencies.py     # API dependency helpers
│   ├── config.py           # app configuration
│   ├── routes.py           # root routes and router imports
│   ├── security.py         # auth utilities and password hashing
│   ├── seed.py             # database seeding logic
│   ├── visualization.py    # chart / analytics helpers
│   ├── data_analysis.py    # analysis helper functions
│   ├── ml/                 # prediction and analytics routers
│   │   ├── routers/
│   │   └── services/
├── frontend/
│   ├── css/
│   │   └── style.css       # application styling
│   ├── js/
│   │   ├── api.js          # client API utilities
│   │   └── dashboard.js    # dashboard UI logic
│   ├── login.html          # login portal
│   ├── dashboard.html      # analytics and management interface
│   └── analytics.html      # analytics-specific page
├── database/
│   └── schema.sql          # database schema definition
├── data/                   # sample CSV datasets
├── ml/                     # modeling notebooks and scripts
│   ├── customer_segmentation.py
│   ├── sales_prediction.py
│   └── models/
├── sample_uploads/         # sample upload templates
├── requirements.txt        # Python dependencies
├── start_dashboard.ps1     # PowerShell launcher
├── start_dashboard.bat     # Windows batch launcher
└── start_public_link.ps1   # start server and expose public URL
```

---

## ⚙️ Setup & Run

### Prerequisites

*   Python 3.11+ (or compatible 3.x install)
*   Git
*   `pip` available in the environment

### 1. Clone the repo

```bash
git clone https://github.com/Princy-Sanjeevidoss/AI-Business-Analytics-Dashboard.git
cd AI-Business-Analytics-Dashboard
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

Use the provided PowerShell script:

```powershell
.
"start_dashboard.ps1"
```

Or run Uvicorn directly:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```

### 5. Open the app

Visit:

```text
http://127.0.0.1:8002/app/login.html
```

Or use the backend redirect route:

```text
http://127.0.0.1:8002/login
```

---

## 🔧 Notes

*   The backend mounts the `frontend/` folder at `/app` and serves HTML/CSS/JS statically.
*   On startup, the app creates database tables and seeds initial data via `backend.seed.seed_data()`.
*   `sample_uploads/` includes CSV templates for customers, employees, payments, products, and sales.
*   `backend/routers/` exposes routes for auth, AI, analytics, import, prediction, and CRUD operations.

---

## 🔑 Demo Credentials

Use the demo login button on the frontend or enter:

*   **Username**: `admin`
*   **Password**: `admin123`

---

## 📌 Helpful Commands

```bash
# Run backend server manually
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
.venv\Scripts\activate
```

---

## 💡 Helpful Tips

*   If the browser does not load the page, verify the backend is running and that port `8002` is available.
*   Use the `start_public_link.ps1` script to expose the app publicly when needed.
