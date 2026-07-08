# AI-Powered Business Analytics Dashboard

An advanced, premium-designed operations and analytics dashboard featuring real-time data visualization, a machine learning forecasting engine, an interactive database-aware AI Chatbot, and a complete CRUD management suite.

---

## 🚀 Key Features

*   **Premium Glassmorphic Dark UI**: A sleek, high-tech interface styled with a custom dark theme, vibrant gradients, subtle micro-animations, and fully responsive layouts.
*   **Dynamic Data Visualizations**: Real-time sales trends, product margins, and payment method statistics powered by **Chart.js**.
*   **Database-Aware AI Assistant**: An interactive chat window that queries live SQL tables directly to answer natural language questions (e.g., "What is our total revenue?"), falling back seamlessly when no external API keys are configured.
*   **ML Revenue Forecasting**: Integrated linear regression models to predict next-month metrics on demand.
*   **Unified Data Manager (CRUD)**: Create, read, update, and delete entries for Sales, Products, Customers, Employees, and Payments with automatic layout resets and selection lookups.
*   **Demo Authentication**: Quick-login support with pre-filled test credentials for seamless evaluations.

---

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, JWT Auth, Uvicorn.
*   **Frontend**: Vanilla HTML5, Vanilla CSS3 (Glassmorphism, custom layout grids), JavaScript (ES6 Fetch API, LocalStorage).
*   **Machine Learning & Analytics**: Pandas, NumPy, Scikit-Learn, Joblib.
*   **Database**: SQLite.

---

## 📂 Project Structure

```
├── backend/
│   ├── models.py          # SQLAlchemy Database Models
│   ├── schemas.py         # Pydantic Schemas for Validation
│   ├── crud.py            # Database CRUD Operations
│   ├── main.py            # FastAPI Entry Point & CORS Setup
│   ├── config.py          # Environment configurations
│   ├── database.py        # SQLite Engine & Session Configuration
│   ├── services/
│   │   ├── ai_service.py  # AI Query Fallback Service
│   │   └── ...            # Analytics & Prediction Services
│   └── routers/           # Endpoint Route Controllers
├── database/
│   └── business.db        # SQLite Database File
├── frontend/
│   ├── css/
│   │   └── style.css      # Premium Glassmorphic Stylesheet
│   ├── js/
│   │   ├── api.js         # API request utilities
│   │   └── dashboard.js   # Dashboard UI Controller
│   ├── login.html         # Portal Authentication
│   └── dashboard.html     # Analytics Portal Workspace
└── requirements.txt       # Python dependencies list
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Princy-Sanjeevidoss/AI-Business-Analytics-Dashboard.git
cd AI-Business-Analytics-Dashboard
```

### 2. Configure Environment Variables
Create a `.env` file in the root folder or copy the template:
```bash
cp .env.example .env
```

### 3. Backend Setup
Create a virtual environment and install dependencies:
```bash
# Create environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Run the backend server:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```
*The API server will run at `http://127.0.0.1:8002`.*

### 4. Frontend Launch
You don't need a build system for the frontend. Simply open the login page directly in any modern browser:
*   Double click `frontend/login.html` or open it via file browser.

---

## 🔑 Demo Credentials

Click the **Demo Admin** button on the login screen to autofill, or input:
*   **Username**: `admin`
*   **Password**: `admin123`
