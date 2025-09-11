# ADA Portal (Django + MSSQL + Microsoft SSO)

## Quickstart
1. Install system deps (Windows): ODBC Driver 18 for SQL Server.
2. Create venv and install packages:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure `.env` from `.env.sample` (DB + Azure).
4. Initialize DB:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Run on port **3000**:
   ```bash
   python manage.py runserver 0.0.0.0:3000
   ```

### Windows Integrated Auth (IIS) Option
Use `django-windowsauth` behind IIS with Windows Authentication enabled (disable Anonymous). Update `AUTHENTICATION_BACKENDS` and add WindowsAuth middleware.

### UI
- Search by **ADA Rider Name** or **ADA Rider ID**
- ADA Rider Info with **Save / Cancel / Inactive / Notes**
- **ADA Ticket Purchases**
- **Finance Transmittal Report**
