# ArteryVision — Coronary Imaging Workspace

ArteryVision is a full-stack web application for organizing coronary imaging cases and supporting artery-segmentation and stenosis-detection research workflows. It combines a React + Vite interface with a FastAPI backend and PostgreSQL database.

## GitHub Repository

- **Repository:** [Team_3_Segmentation_Artery_DL](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL)
- **My working branch:** [Himanshu](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL/tree/Himanshu)

To clone the project directly from the `Himanshu` branch, run:

```bash
git clone --branch Himanshu https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL.git
cd Team_3_Segmentation_Artery_DL
```

> **Scope notice:** This project currently provides workspace, authentication, case/patient management, secure image storage, metadata, reporting, and model-registry functionality. AI/deep-learning inference for artery segmentation and stenosis detection is **not implemented** in this version. The application is for development and research support, not for standalone clinical diagnosis.

## Features

- **Authentication:** User registration and login using password hashing and JWT-based sessions.
- **Role-based access control (RBAC):** Backend authorization for protected operations.
- **Case management:** Create, view, update, and manage imaging cases.
- **Patient records:** Store patient identifiers and associated case metadata.
- **Medical image workflow:** Upload and retrieve supported image files with file-size and extension checks.
- **Results and reports:** Store/retrieve analysis-result records and generate report outputs where supported.
- **Model Registry:** Manage model metadata through the application’s registry workflow.
- **Dashboard and notifications:** Workspace summaries and notification endpoints.
- **Activity/audit logs:** Record relevant actions, including administrator role changes.
- **Settings:** Profile, password, backend connection, security information, and administrator-only Role Management.
- **Local development:** Run the React frontend and FastAPI backend locally with PostgreSQL.

## Role Management

The supported roles are:

| Role | Purpose |
|---|---|
| `clinician` | Clinical workflow access permitted by backend policies |
| `researcher` | Default role for new registrations and research workflow access |
| `ml_engineer` | Model-registry and ML-related access permitted by backend policies |
| `administrator` | User and role administration, plus other explicitly authorized operations |

Role-management behavior:

- Public registration assigns `researcher`; clients cannot choose an elevated role in the registration request.
- Administrators can open **Settings → Role Management** to view registered users and update another user’s role.
- The backend checks administrator permissions for both listing users and updating roles. Hiding the UI alone is not treated as authorization.
- An administrator cannot change their own role through the role-management endpoint.
- Role changes revoke the target user’s active sessions so that the user must sign in again.
- Role changes are recorded in the audit log.

For a fresh local database, register a trusted account first. Then, using pgAdmin’s Query Tool or another secure database administrator session, promote that account to the first administrator:

```sql
UPDATE users
SET role = 'administrator'
WHERE email = 'your-registered-email@example.com';
```

Replace the email with your own registered account’s email. Run this only against your own development database and only for a trusted account. Do not expose a public endpoint that lets users bootstrap themselves as administrators.

## Technology Stack

**Frontend**
- React
- Vite
- `lucide-react` icons
- JavaScript and CSS

**Backend**
- Python
- FastAPI and Uvicorn
- SQLAlchemy
- Pydantic Settings
- PostgreSQL with Psycopg
- JWT authentication and password hashing
- Pytest and HTTPX for tests

## Project Structure

```text
Artery-Vision/
├── src/
│   ├── App.jsx
│   ├── api.js
│   ├── main.jsx
│   ├── styles.css
│   └── styles_addon.css
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── admin_users.py
│   │   │   ├── cases.py
│   │   │   ├── patients.py
│   │   │   ├── images.py
│   │   │   ├── results.py
│   │   │   ├── reports.py
│   │   │   ├── models.py
│   │   │   └── audit_logs.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── .env.example
├── package.json
├── vite.config.js
└── README.md
```

## Prerequisites

Install the following before running the app:

- Node.js (20 or newer recommended)
- Python 3.11 or 3.12 recommended
- PostgreSQL
- Git (for version control)

## Setup and Run Locally

### 1. Clone the repository

If you have not cloned the project yet, use the branch-specific command above or run:

```bash
git clone --branch Himanshu https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL.git
cd Team_3_Segmentation_Artery_DL
```

If you are already working in the cloned repository, skip the clone step and switch to your branch with `git switch Himanshu`.

### 2. Configure PostgreSQL

Create a PostgreSQL database named `arterysegmentation_db`, or choose another database name and update `DATABASE_URL` below accordingly.

### 3. Configure the backend

Open a terminal in the project root and run the following commands in PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your own PostgreSQL password and secret key:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/arterysegmentation_db
SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
REPORT_DIR=reports
MAX_UPLOAD_SIZE_MB=100
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Generate a secret key with Python:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated value after `SECRET_KEY=`. Keep `.env` private and never commit it to GitHub. If your PostgreSQL password contains URL-special characters (such as `@`, `:`, `/`, or `#`), URL-encode them in `DATABASE_URL`.

Start the backend **from the `backend` directory**:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful URLs:

- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 4. Configure and run the frontend

Open a **second terminal** at the project root (the directory containing `package.json`):

```powershell
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Ensure the root `.env.local` contains the backend base URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Open the URL printed by Vite, usually `http://localhost:5173`. Restart Vite after changing a `VITE_` environment variable.

## Application Links (Local Development)

Use these original local URLs while the services are running on your computer:

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API base URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Backend health check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive backend API documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

These are local development URLs. They are accessible from your computer while the frontend and backend are running; they are not public deployment links.

## API Endpoints

The backend exposes these main endpoints (see `/docs` for request and response schemas):

| Area | Endpoints |
|---|---|
| Health | `GET /health` |
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Administrator user management | `GET /admin/users`, `PATCH /admin/users/{user_id}/role` |
| Cases | `POST /cases`, `GET /cases`, `GET /cases/{case_id}`, `PATCH /cases/{case_id}`, `DELETE /cases/{case_id}` |
| Case history | `GET /cases/{case_id}/history` |
| Images | `POST /cases/{case_id}/upload`, `GET /cases/{case_id}/images`, `GET /cases/{case_id}/images/{image_id}/file` |
| Results | `GET /cases/{case_id}/results` |

Additional routers support patients, dashboard data, notifications, preprocessing, model registry metadata, audit logs, and reports. Their exact routes and schemas are available in FastAPI’s interactive documentation.

Supported upload extensions are `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.dcm`, `.nii`, and `.nii.gz`. Extension and size checks do not replace full medical-file validation.

## Run Tests and Build

Backend tests (from the `backend` directory, with the virtual environment activated):

```powershell
pytest -q
```

Frontend production build (from the project root):

```powershell
npm run build
```

## Security and Limitations

- Never commit `.env`, `.env.local`, database passwords, secret keys, access tokens, or real patient information.
- Use synthetic or de-identified data for demonstrations. Do not expose real patient scans or identifying health information to unauthorized users.
- Do not expose the PostgreSQL port to the public internet.
- Backend authorization must remain the source of truth for role and case access.
- This version does not include AI/deep-learning inference for segmentation or stenosis detection. The backend health response reports `ai_inference: not_implemented`; model outputs must not be represented as generated by this application.
- For production deployments, configure HTTPS, secret management, logging, backups, database migrations, and a hardened deployment server. The development `--reload` server is not intended for production.

## Current Contribution

This branch documents and includes the administrator Role Management work: the Settings UI for administrators, supported role choices, backend-protected user-list and role-update endpoints, default researcher assignment during registration, audit logging, session revocation on role changes, and tests covering the role-management flow.
