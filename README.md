# ArteryVision — Coronary Imaging Workspace

ArteryVision is a full-stack web application developed for organizing coronary imaging cases and supporting artery segmentation and stenosis detection research workflows.

The system combines a **React + Vite frontend**, **FastAPI backend**, **PostgreSQL database**, and **deep-learning inference pipeline** for research-oriented medical image analysis. It provides case and patient management, medical image upload, AI-based stenosis inference, result visualization, reporting, model evaluation, explainable AI (XAI), model registry, activity logging, and role-based access control.

> **Research and educational use only:** ArteryVision is a research-support application and is not intended to provide standalone clinical diagnosis or replace professional medical interpretation.

---

## GitHub Repository

- **Repository:** [Team_3_Segmentation_Artery_DL](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL)
- **Working Branch:** [Manideepa](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL/tree/Manideepa)

## Project Website

**Live Application:** [https://arteryvision.vercel.app/](https://arteryvision.vercel.app/)

---

## Project Overview

ArteryVision provides an integrated workspace for coronary imaging research workflows.

The application supports the complete workflow from case creation and image upload to AI inference, result visualization, evaluation, reporting, and research-oriented interpretation.

### Main Workflow

1. User authentication
2. Case and patient creation
3. Coronary image upload
4. Image validation and preprocessing
5. AI-based stenosis inference
6. Stenosis localization and visualization
7. Analysis result generation
8. Explainable AI visualization
9. Model evaluation
10. Report generation and export
11. Activity and audit logging
12. Model registry and research management

---

# Features

## 1. Authentication

- User registration and login
- Password hashing
- JWT-based authentication
- Authenticated application sessions
- Protected backend endpoints
- Session handling and revocation

## 2. Role-Based Access Control

The application supports role-based access control for protected operations.

Supported roles include:

| Role | Purpose |
|---|---|
| `clinician` | Clinical-workflow-oriented access according to backend policies |
| `researcher` | Default research workflow access |
| `ml_engineer` | Model and machine-learning related access |
| `administrator` | User, role, audit, and administrative operations |

Administrative role management is protected at the backend level rather than relying only on frontend visibility.

Role changes can revoke active sessions and are recorded through the activity/audit workflow.

---

## 3. Dashboard

The dashboard provides an overview of the research workspace, including:

- Total cases
- Uploaded image records
- Stored analysis results
- Case status information
- Workspace notifications
- Quick access to important application functions

---

## 4. Case Management

Users can:

- Create imaging cases
- View existing cases
- Update case information
- Track case status
- View case history
- Upload associated medical images
- Access analysis results
- Generate reports and exports

---

## 5. Patient Management

The application provides patient-related case metadata management for the research workflow.

Patient information is associated with cases and protected through the application's authentication and authorization mechanisms.

For demonstrations and testing, synthetic or de-identified data should be used.

---

## 6. Medical Image Workflow

The application supports medical image upload and retrieval with validation controls.

Supported image extensions include:

- `.png`
- `.jpg`
- `.jpeg`
- `.tif`
- `.tiff`
- `.dcm`
- `.nii`
- `.nii.gz`

The upload workflow includes file extension and file-size checks.

> File extension and size validation do not replace complete clinical or medical-file validation.

---

# AI and Deep Learning

## 7. Artery Segmentation

The project uses deep-learning-based artery segmentation research workflows based on the **ARCADE dataset**.

The segmentation experiments include U-Net-based approaches and model evaluation using standard segmentation metrics.

### Syntax Segmentation Evaluation

Final syntax segmentation evaluation results include:

| Metric | Result |
|---|---:|
| Dice Score | 0.7132 |
| IoU | 0.5689 |
| Sensitivity | 0.7448 |
| Specificity | 0.9882 |
| Hausdorff Distance | 57.3 px |

An Attention U-Net comparison achieved:

| Metric | Result |
|---|---:|
| Dice Score | 0.7094 |
| IoU | 0.5630 |

The baseline U-Net comparison achieved:

| Metric | Result |
|---|---:|
| Dice Score | 0.7011 |
| IoU | 0.5530 |

These values represent research evaluation results and should not be interpreted as clinical performance.

---

# Stenosis Detection

## 8. Stenosis Inference

The project integrates a trained **U-Net-based stenosis model** into the backend inference pipeline.

The backend performs research-oriented stenosis inference and provides analysis outputs to the frontend.

The inference workflow includes:

1. Image input
2. Image preprocessing
3. Model inference
4. Stenosis mask generation
5. Stenosis localization visualization
6. Coverage-based estimation
7. Confidence/result generation
8. Severity classification
9. Storage and display of analysis results

The trained model is integrated through the backend inference module:

```text
backend/app/stenosis_inference.py
```

The trained model is stored under:

```text
backend/models/stenosis_unet_best.pth
```

---

## 9. Stenosis Evaluation

Research evaluation of the stenosis model produced the following results:

| Metric | Result |
|---|---:|
| Dice Score | 0.3895 |
| IoU | 0.2626 |
| Sensitivity | 0.5617 |
| Specificity | 0.9889 |
| Hausdorff Distance | 76.2 px |

An earlier Attention-based stenosis experiment achieved a Dice score of approximately **0.3368**.

These results are experimental model-evaluation metrics and should not be interpreted as clinically validated stenosis measurements.

---

# Severity Analysis

## 10. Severity Distribution

The research evaluation includes a severity distribution based on the project's implemented heuristic classification.

| Severity | Number of Samples |
|---|---:|
| Mild | 38 |
| Moderate | 203 |
| Severe | 59 |

Total evaluated samples:

**300**

The application uses the following research heuristic for estimated narrowing coverage:

- **Mild:** coverage below 1%
- **Moderate:** coverage from 1% to 3%
- **Severe:** coverage above 3%

> These thresholds are research heuristics based on segmentation coverage and are **not clinical stenosis grading criteria**.

---

# Explainable AI

## 11. Explainable AI (XAI)

ArteryVision includes an Explainable AI research visualization component.

XAI visualizations are generated from the stenosis research evaluation and are used to provide visual interpretation of model outputs.

The project contains XAI visualization outputs corresponding to the evaluated samples.

The XAI interface allows users to inspect research-oriented visual explanations alongside model predictions.

> XAI visualizations are intended to support model interpretation and research analysis. They do not constitute clinical explanations or diagnostic evidence.

---

# Results and Reports

## 12. Analysis Results

The Results & Reports section provides access to stored analysis outputs associated with imaging cases.

Results may include:

- Model version
- Stenosis visualization
- Estimated narrowing
- Confidence score
- Severity category
- Research notes
- Case information
- Analysis metadata

The application also provides result comparison and visualization functionality.

---

## 13. Reports and Export

Research outputs can be exported through supported formats.

The reporting workflow supports:

- PDF reports
- JSON data
- CSV data
- Analysis result records
- Case-related research outputs

Generated reports are intended for research documentation and evaluation.

---

# Model Management

## 14. Model Registry

The Model Registry provides a structured area for managing model metadata within the research application.

Model-related information can include:

- Model name
- Model version
- Model type
- Dataset information
- Evaluation information
- Research metadata
- Model status

The registry is intended to support organized tracking of machine-learning models used within the project.

---

# Model Evaluation

## 15. Evaluation Dashboard

The Model Evaluation section provides research metrics for evaluating the segmentation and stenosis models.

The evaluation workflow includes:

- Dice Score
- IoU
- Sensitivity
- Specificity
- Hausdorff Distance
- Model comparison
- Stenosis evaluation
- Severity distribution

The evaluation results are displayed within the application to support research analysis and comparison.

---

# Security

## 16. Security and Access Control

Security was considered throughout the application development process.

Implemented security-related controls include:

- Password hashing
- JWT-based authentication
- Protected API endpoints
- Backend authorization
- Role-based access control
- Administrator-only role management
- Session revocation following role changes
- Audit/activity logging
- File extension validation
- File-size validation
- Environment-variable based secret configuration
- CORS configuration
- Protection of sensitive configuration files through `.gitignore`

### Security Practices

The following information must never be committed to the repository:

```text
.env
.env.local
database passwords
secret keys
access tokens
real patient information
```

For demonstrations and testing, synthetic or de-identified medical data should be used.

The PostgreSQL database should not be exposed directly to the public internet.

---

# Testing

## 17. Backend Testing

Backend functionality was tested using the project's automated test suite.

The test suite covers areas including:

- Report generation
- Report builder behavior
- Formula/input sanitization
- Administrative role management
- Session revocation
- Backend workflow behavior

The backend test command is:

```bash
pytest -q
```

The project testing workflow successfully passed the implemented automated tests during development.

---

## 18. Frontend Testing and Build Verification

The frontend production build was verified using:

```bash
npm run build
```

The Vite production build completed successfully.

The application was also tested through the integrated frontend-backend workflow.

---

## 19. API Testing

The FastAPI backend provides interactive API documentation through:

```text
/docs
```

Important API areas include:

- Authentication
- User management
- Cases
- Patients
- Images
- Results
- Reports
- Model registry
- Audit logs
- Dashboard data

The API was tested as part of the application integration workflow.

---

# API Endpoints

## 20. Main API Areas

| Area | Example Endpoints |
|---|---|
| Health | `GET /health` |
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Users | `GET /admin/users`, `PATCH /admin/users/{user_id}/role` |
| Cases | `POST /cases`, `GET /cases`, `GET /cases/{case_id}` |
| Case History | `GET /cases/{case_id}/history` |
| Images | `POST /cases/{case_id}/upload` |
| Results | `GET /cases/{case_id}/results` |
| Reports | Report-generation endpoints |
| Model Registry | Model metadata endpoints |
| Audit Logs | Activity/audit endpoints |

The complete API schema can be accessed through FastAPI's interactive documentation.

---

# Technology Stack

## 21. Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React icons

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- PostgreSQL
- Psycopg
- JWT authentication
- Password hashing
- Pytest
- HTTPX

## AI / Machine Learning

- Python
- PyTorch
- U-Net
- Attention-based segmentation experiments
- ARCADE dataset
- Image preprocessing
- Segmentation evaluation
- Stenosis inference
- Explainable AI visualization

## Deployment / Infrastructure

- Vercel
- Docker configuration
- Docker Compose
- Nginx configuration
- PostgreSQL
- Environment-based configuration

---

# Project Structure

The main project structure is organized as follows:

```text
Team_3_Segmentation_Artery_DL/
│
├── src/
│   ├── App.jsx
│   ├── api.js
│   ├── main.jsx
│   ├── styles.css
│   └── styles_addon.css
│
├── public/
│   └── xai/
│       ├── 1_xai.png
│       ├── 2_xai.png
│       ├── ...
│       └── 300_xai.png
│
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
│   │   │
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── images.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── stenosis_inference.py
│   │   └── main.py
│   │
│   ├── models/
│   │   └── stenosis_unet_best.pth
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .dockerignore
├── .gitignore
├── package.json
├── vite.config.js
└── README.md
```

---

# Prerequisites

## 22. Required Software

For local development, install:

- Node.js 20 or newer
- Python 3.11 or newer
- PostgreSQL
- Git

---

# Local Setup

## 23. Clone the Repository

To clone the Manideepa branch:

```bash
git clone --branch Manideepa https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL.git
cd Team_3_Segmentation_Artery_DL
```

If the repository is already cloned:

```bash
git switch Manideepa
```

---

## 24. Configure PostgreSQL

Create a PostgreSQL database named:

```text
arterysegmentation_db
```

The database connection should be configured through the backend environment file.

---

## 25. Configure the Backend

Open PowerShell in the project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create the backend environment file:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables in:

```text
backend/.env
```

Example:

```text
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/arterysegmentation_db
SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
REPORT_DIR=reports
MAX_UPLOAD_SIZE_MB=100
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Generate a secure secret key using:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not commit the `.env` file.

---

## 26. Start the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend health endpoint:

```text
http://127.0.0.1:8000/health
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 27. Configure the Frontend

Open a second terminal in the project root.

Install dependencies:

```powershell
npm ci
```

Create the frontend environment file:

```powershell
Copy-Item .env.example .env.local
```

Set:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

The application will normally be available at:

```text
http://localhost:5173
```

---

# Docker

## 28. Docker Configuration

The project contains Docker-related configuration for containerized deployment and development.

Important files include:

```text
Dockerfile
backend/Dockerfile
docker-compose.yml
nginx.conf
.dockerignore
```

Docker configuration allows the frontend/backend application components to be packaged and deployed using container-based workflows.

---

# Deployment

## 29. Live Application

The deployed ArteryVision frontend is available at:

**https://arteryvision.vercel.app/**

The deployed interface provides access to the research workspace and its implemented frontend functionality.

Production deployments should use secure environment variables and should not expose development secrets or real patient information.

---

# Research Dataset

## 30. ARCADE Dataset

The machine-learning experiments use the **ARCADE dataset** for coronary artery segmentation and stenosis-related research evaluation.

The dataset workflow includes:

- Training data
- Validation data
- Test data
- Artery syntax categories
- Stenosis annotations
- Segmentation masks
- Model evaluation

The dataset is used for research and model development purposes.

---

# Model Evaluation Summary

## 31. Segmentation Results

### Syntax Segmentation

| Model / Configuration | Dice | IoU |
|---|---:|---:|
| Baseline U-Net | 0.7011 | 0.5530 |
| Attention U-Net | 0.7094 | 0.5630 |
| Final Syntax Configuration | **0.7132** | **0.5689** |

Additional final syntax metrics:

| Metric | Value |
|---|---:|
| Sensitivity | 0.7448 |
| Specificity | 0.9882 |
| Hausdorff Distance | 57.3 px |

### Stenosis Evaluation

| Metric | Value |
|---|---:|
| Dice | 0.3895 |
| IoU | 0.2626 |
| Sensitivity | 0.5617 |
| Specificity | 0.9889 |
| Hausdorff Distance | 76.2 px |

These values are experimental research metrics and are not clinical validation results.

---

# Limitations

## 32. Research Limitations

The following limitations apply:

- Model performance is based on research datasets and experimental evaluation.
- Stenosis severity estimation uses a project-specific heuristic.
- The system has not been clinically validated.
- Results should not be interpreted as medical diagnosis.
- Dataset characteristics may affect model generalization.
- Medical image file validation does not replace complete clinical data validation.
- XAI visualizations provide research-oriented model interpretation rather than clinical explanations.
- Production deployment requires additional hardening, monitoring, backups, migration management, and security controls.

---

# Security and Privacy Notice

## 33. Data Protection

This project should be demonstrated using synthetic or de-identified medical data.

Do not upload or commit:

```text
Real patient scans
Patient identifiers
Personal health information
Passwords
Database credentials
JWT secrets
Environment files
Access tokens
```

Environment files should remain local and should be excluded from Git version control.

---

# Team Development

## 34. Branch-Based Development

The project uses Git branches for collaborative development.

The current working branch documented in this README is:

```text
Manideepa
```

Branch-specific development allows individual contributions to be developed and tested before integration with the main project branch.

Repository:

```text
Team_3_Segmentation_Artery_DL
```

---

# Current Contribution

## 35. Development Contribution

The project includes contributions across:

- AI pipeline and integration
- ARCADE dataset preparation and evaluation
- U-Net-based stenosis segmentation
- Backend inference integration
- FastAPI API integration
- React frontend integration
- Prediction visualization
- Explainable AI visualization
- Model evaluation
- Results and reporting workflow
- Testing and debugging
- Security and role-based access control
- Deployment preparation

The `Manideepa` branch contains the corresponding development work and integration changes associated with the project workflow.

---

# Testing and Verification Summary

## 36. Verification Status

The project was verified through multiple development and testing activities.

### Backend

- Automated backend tests executed successfully.
- Authentication and protected API workflows tested.
- Role-based authorization tested.
- Session revocation behavior tested.
- Report-generation functionality tested.

### Frontend

- React application build verified.
- Vite production build completed successfully.
- Application pages and navigation tested.

### AI Pipeline

- Stenosis inference integrated into the backend.
- Model output visualizations verified.
- Stenosis localization tested.
- Research result records verified.

### Integration

- Frontend and backend communication tested.
- Image upload workflow tested.
- Case creation and result workflow tested.
- Analysis result visualization tested.
- Report and export functionality tested.

### Security

- Environment files excluded from version control.
- Backend authorization tested.
- Role-management restrictions tested.
- Session revocation tested.
- File upload validation implemented.

---

# Important Notice

ArteryVision is a **research and educational software project**.

The model outputs, estimated narrowing values, severity categories, segmentation masks, XAI visualizations, and other generated results are intended for research evaluation and demonstration only.

They must **not** be used as a substitute for professional medical diagnosis, clinical decision-making, or interpretation by qualified healthcare professionals.

---

# License

This repository is maintained as part of the project development and research workflow.

Refer to the repository license information for applicable usage and distribution terms.

---

# Project Links

- **Live Application:** https://arteryvision.vercel.app/
- **GitHub Repository:** https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL
- **Working Branch:** https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL/tree/Manideepa

---

# ArteryVision

**Coronary Imaging Workspace for Artery Segmentation and Stenosis Detection Research**
