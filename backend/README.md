# ArteryVision Backend (FastAPI)

Backend-only starter for the Artery Segmentation and Stenosis Detection project. It implements user registration/login, JWT-protected routes, case CRUD, image uploads/downloads, case history, and result retrieval. It does **not** implement AI or deep-learning inference.

## 1. Prerequisites
- Python 3.11 or 3.12 recommended
- PostgreSQL installed and running
- A PostgreSQL database named `arterysegmentation_db` (or update `DATABASE_URL` to match your existing database)

Create the database using pgAdmin or psql before starting the backend.

## 2. Setup on Windows (PowerShell)
Run these commands in this `backend` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace `YOUR_POSTGRES_PASSWORD` with your local PostgreSQL password. Replace `SECRET_KEY` with a long random string. If your database username differs from `postgres`, update the URL too. If the password contains characters such as `@`, `:`, `/`, or `#`, URL-encode them in the connection URL.

## 3. Run

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. The server creates the proposed tables on startup for local development.

## 4. Suggested test order
1. `POST /auth/register` with `full_name`, `email`, and `password` (minimum 8 characters).
2. `POST /auth/login` with `email` and `password`; copy `access_token` from the response.
3. In Swagger, click **Authorize** and enter the token (usually just the token text; the UI adds Bearer).
4. `POST /cases` with JSON such as:
   ```json
   {
     "case_name": "CCTA demo case 001",
     "imaging_modality": "CCTA",
     "anatomical_region": "Coronary arteries",
     "scan_date": null
   }
   ```
5. Use the returned `case_id` with `POST /cases/{case_id}/upload` and choose a supported file.
6. Use `GET /cases`, `GET /cases/{case_id}/images`, `GET /cases/{case_id}/history`, and `GET /cases/{case_id}/results` to check saved data.

## Supported upload filename extensions
`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.dcm`, `.nii`, `.nii.gz`. Extension and size validation are implemented; full medical-file parsing/validation is not. The maximum upload size is controlled by `MAX_UPLOAD_SIZE_MB` in `.env`.

## API endpoints
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /admin/users` (administrator only)
- `PATCH /admin/users/{user_id}/role` (administrator only)
- `POST /cases`
- `GET /cases`
- `GET /cases/{case_id}`
- `PATCH /cases/{case_id}`
- `DELETE /cases/{case_id}`
- `GET /cases/{case_id}/history`
- `POST /cases/{case_id}/upload`
- `GET /cases/{case_id}/images`
- `GET /cases/{case_id}/images/{image_id}/file`
- `GET /cases/{case_id}/results`
- `GET /health`

Public registration assigns the `researcher` role and does not accept a role from the request. The administrator-only Role Management panel is located in Settings. It lists registered accounts and can assign `clinician`, `researcher`, `ml_engineer`, or `administrator`. Backend authorization is enforced on both management endpoints; the signed-in administrator cannot change their own role, and role changes revoke the target user's sessions. For the first administrator in a fresh local database, use a controlled database operation to set one trusted account's `role` to `administrator`; never make a public bootstrap endpoint for this.

## Important notes
- Uploaded images and results may contain sensitive medical information. Use public/de-identified data for student development and protect stored files.
- The `Analysis Results` table and result-retrieval API are included, but no AI-analysis endpoint or model inference is implemented here.
- `create_all()` is for local development. For ongoing schema changes or production, use database migrations (e.g. Alembic).
- Change the development secret key before sharing or deploying.
