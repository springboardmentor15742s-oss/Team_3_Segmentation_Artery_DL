
# ArteryVision – AI-Powered Coronary Artery Segmentation and Stenosis Analysis

<p align="center">
  <img src="https://img.shields.io/badge/Project-ArteryVision-0284C7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Deep%20Learning-PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
</p>

<p align="center">
  <b>A Full-Stack Medical Imaging Workspace for Coronary Artery Segmentation, Stenosis Analysis, and Research-Based Visualization.</b>
</p>

---

## 1. Project Overview

**ArteryVision** is a full-stack AI-assisted coronary imaging workspace developed to support the organization, visualization, and research-based analysis of coronary artery medical images.

The platform integrates a web-based interface, backend APIs, database management, image preprocessing, and deep learning-based segmentation workflows into a centralized application.

It is designed to help researchers and authorized users manage coronary imaging cases, upload medical images, perform image preprocessing, generate stenosis-region segmentation masks using deep learning models, and review stored analysis results.

The system combines traditional image-processing techniques with a U-Net-based deep learning architecture to support automated image analysis workflows.

### Project Repository

- **Repository:** [Team_3_Segmentation_Artery_DL](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL)
- **Working Branch:** [review]
- **Application:** ArteryVision
- **Domain:** Medical Image Processing and Deep Learning
## Live Application

**ArteryVision:** https://arteryvision.vercel.app/

---

## 2. Project Objectives

The main objectives of ArteryVision are:

1. To develop a centralized platform for managing coronary artery imaging cases.
2. To implement secure user authentication and role-based access control.
3. To provide functionality for uploading, storing, and retrieving medical images.
4. To perform image preprocessing and normalization before analysis.
5. To integrate deep learning-based U-Net models for coronary artery segmentation and stenosis-region identification.
6. To generate and visualize segmentation masks.
7. To calculate research-oriented segmentation and mask-coverage metrics.
8. To maintain patient metadata and imaging case records.
9. To provide a dedicated results and reports section.
10. To evaluate model performance using established segmentation metrics.
11. To maintain model metadata and analysis history.
12. To provide a responsive and user-friendly research workspace.

---

## 3. Key Features

### 3.1 User Authentication and Authorization

- User registration and login.
- Secure password hashing.
- JWT-based authentication.
- Protected API endpoints.
- Role-based access control.
- User profile management.
- Administrator-controlled role management.

### 3.2 Dashboard

The dashboard provides a centralized overview of the application.

It includes:
- Total imaging cases.
- Completed cases.
- Processing cases.
- Cases requiring attention.
- Workspace summaries.
- Quick navigation to major application modules.

### 3.3 Case Management

Users can create and manage coronary imaging cases.

Features include:
- Create new imaging cases.
- Provide case names and imaging modalities.
- Select anatomical regions.
- Link de-identified patient records.
- Add research-related notes.
- View and update case information.
- Search and filter cases.
- Track case status.
- Delete cases when authorized.

### 3.4 Patient Management

The patient module maintains minimal, de-identified patient metadata.

Available information includes:
- De-identified patient code.
- Age.
- Sex.
- Medical history.
- Risk factors.
- Clinical notes.

Patient records can be searched and linked to imaging cases.

**Privacy Note:** Only public, synthetic, or properly de-identified data should be used. Direct patient identifiers must not be entered into the demonstration system.

### 3.5 Medical Image Upload

The application supports uploading medical images and associating them with specific imaging cases.

Supported upload extensions include:

- PNG
- JPG
- JPEG
- TIFF
- TIF
- DICOM
- NIfTI

The backend validates uploaded files and manages their storage and retrieval.

### 3.6 Image Preprocessing

The preprocessing module prepares images for further inspection and analysis.

Available preprocessing operations include:

- Grayscale conversion.
- Intensity normalization.
- Median filtering.
- Noise reduction.
- Contrast enhancement.
- Image resizing.
- Normalized image preview generation.

Preprocessing helps maintain a consistent image representation before the deep learning inference workflow.

### 3.7 AI-Based Coronary Artery Segmentation

The platform includes deep learning-based segmentation workflows using U-Net architectures.

The project incorporates model checkpoints for different segmentation experiments, including:

- U-Net.
- Attention U-Net.
- Multiclass U-Net.
- Multiclass U-Net V2.
- Stenosis U-Net.

The models are intended for research-oriented segmentation and analysis of coronary artery images.

The available stenosis inference implementation uses a trained U-Net checkpoint to generate a binary stenosis-region prediction mask for supported raster images.

### 3.8 Stenosis Analysis

The stenosis analysis workflow performs:

1. Image retrieval from the selected case.
2. Grayscale conversion.
3. Image resizing.
4. Pixel normalization.
5. Deep learning inference.
6. Sigmoid activation.
7. Probability thresholding.
8. Binary mask generation.
9. Prediction image storage.
10. Result record creation.

The current stenosis inference implementation uses:
- Input size: 256 × 256.
- Input channels: 1.
- Output channels: 1.
- Activation: Sigmoid.
- Mask threshold: 0.40.
- Execution device: CPU.

The generated mask can be reviewed through the results interface.

### 3.9 Results and Reports

The Results & Reports section provides access to saved analysis records.

Features include:
- View saved predictions.
- Review model versions.
- View estimated mask coverage.
- Review research severity labels.
- Compare saved analysis results.
- Access prediction images.
- Export available reports in PDF, JSON, and CSV formats.

### 3.10 Model Evaluation

The Model Evaluation module presents recorded segmentation evaluation metrics.

The metrics include:

- Dice Coefficient.
- Intersection over Union (IoU).
- Sensitivity.
- Specificity.
- Hausdorff Distance.

Recorded ARCADE test-set metrics displayed in the application:

| Metric | Syntax Segmentation | Stenosis Segmentation |
|---|---:|---:|
| Dice | 0.7132 | 0.3895 |
| IoU | 0.5689 | 0.2626 |
| Sensitivity | 0.7448 | 0.5617 |
| Specificity | 0.9882 | 0.9889 |
| Hausdorff Distance | 57.3 px | 76.2 px |

These are research/test-set evaluation values, not clinical performance guarantees.

### 3.11 Explainable AI (XAI)

The platform includes reference-based Explainable AI visualizations.

These visualizations demonstrate how image regions can be highlighted to provide insight into model attention and prediction behavior.

The available XAI reference images are intended for research demonstration and are not automatically generated explanations for every uploaded case.

### 3.12 Model Registry

The Model Registry provides a centralized location for model metadata.

It supports:
- Model names.
- Model versions.
- Intended tasks.
- Model status.
- Reported evaluation metrics.

Authorized administrators and ML engineers can manage model metadata.

### 3.13 Notifications and Audit Logs

The application includes:
- Workspace notifications.
- Case activity history.
- Audit logging.
- User activity tracking.
- Administrative action records.

### 3.14 Settings and User Management

The Settings module provides account and administrative functionality.

Supported roles include:
- Researcher.
- Clinician.
- ML Engineer.
- Administrator.

Permissions are enforced by the backend.

---

## 4. Application Workflow

The general workflow of ArteryVision is:

```text
User Registration / Login
          |
          v
       Dashboard
          |
          v
     Create New Case
          |
          v
  Link Patient Metadata
          |
          v
     Upload Medical Image
          |
          v
    Image Validation
          |
          v
   Image Preprocessing
          |
          v
    Deep Learning Model
          |
          v
   Coronary Segmentation
          |
          v
    Stenosis Mask Generation
          |
          v
   Save Analysis Results
          |
          v
   Results & Visualization
          |
          v
    Model Evaluation
```

---

## 5. System Architecture

ArteryVision follows a full-stack client-server architecture.

### Frontend Layer
The frontend provides the user interface and handles:
- Authentication.
- Dashboard navigation.
- Case management.
- Patient management.
- Image upload.
- Image visualization.
- Result presentation.
- Model evaluation.

### Backend Layer
The backend handles:
- REST API requests.
- Authentication and authorization.
- Database operations.
- Image validation and storage.
- Image preprocessing.
- Deep learning inference.
- Prediction storage.
- Report generation.
- Notifications and audit logging.

### Deep Learning Layer
The AI layer consists of:
- PyTorch-based model implementations.
- U-Net-based segmentation architectures.
- Trained model checkpoints.
- Image preprocessing.
- Model inference.
- Segmentation mask generation.
- Evaluation metrics.

### Database Layer
PostgreSQL maintains structured application data, including:
- User records.
- Patient metadata.
- Imaging cases.
- Image references.
- Analysis results.
- Model metadata.
- Notifications.
- Audit records.

### Architecture Diagram

```text
              USER
                |
                v
       REACT FRONTEND
                |
                v
         FASTAPI BACKEND
                |
       +--------+---------+
       |        |         |
       v        v         v
  AUTHENTICATION CASES  IMAGE APIs
       |        |         |
       +--------+---------+
                |
                v
       IMAGE PREPROCESSING
                |
                v
        PYTORCH MODELS
                |
                v
       SEGMENTATION MASK
                |
                v
        RESULTS STORAGE
                |
          +-----+------+
          |            |
          v            v
      POSTGRESQL    FILE STORAGE
          |            |
          +-----+------+
                |
                v
        RESULTS & REPORTS
```

---

## 6. Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| React | Frontend development |
| Vite | Development and build tooling |
| JavaScript | Application logic |
| CSS | Styling and responsive design |
| Lucide React | Icons |

### Backend

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| SQLAlchemy | Database ORM |
| Pydantic | Data validation and configuration |
| PostgreSQL | Database |
| Psycopg | PostgreSQL connectivity |
| PyJWT | Authentication |
| Pillow | Image processing |
| NumPy | Numerical operations |
| PyTorch | Deep learning |
| pydicom | DICOM handling |
| nibabel | NIfTI handling |
| ReportLab | PDF generation |

### Machine Learning

| Technology | Purpose |
|---|---|
| PyTorch | Deep learning framework |
| U-Net | Image segmentation architecture |
| Attention U-Net | Attention-based segmentation experiments |
| Multiclass U-Net | Multiclass segmentation experiments |
| NumPy | Image and mask calculations |

---

## 7. Project Directory Structure

The main project organization is:

```text
Team_3_Segmentation_Artery_DL/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── admin_users.py
│   │   │   ├── audit_logs.py
│   │   │   ├── cases.py
│   │   │   ├── dashboard.py
│   │   │   ├── images.py
│   │   │   ├── models.py
│   │   │   ├── notifications.py
│   │   │   ├── patients.py
│   │   │   ├── preprocessing.py
│   │   │   ├── reports.py
│   │   │   └── results.py
│   │   │
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── audit.py
│   │   └── stenosis_inference.py
│   │
│   ├── models/
│   │   └── stenosis_unet_best.pth
│   │
│   ├── tests/
│   └── requirements.txt
│
├── public/
│   └── xai/
│
├── src/
│   ├── App.jsx
│   ├── api.js
│   ├── main.jsx
│   ├── styles.css
│   └── styles_addon.css
│
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
├── vercel.json
├── .gitignore
└── README.md
```

---

## 8. Installation and Setup

### Prerequisites

Install the following:

- Python 3.11 or 3.12 (recommended).
- Node.js 20 or newer.
- npm.
- PostgreSQL.
- Git.
- Visual Studio Code.

### Step 1: Clone the Repository

```bash
git clone --branch review https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL.git

cd Team_3_Segmentation_Artery_DL
```

### Step 2: Create the Database

Create a PostgreSQL database:

```sql
CREATE DATABASE arterysegmentation_db;
```

### Step 3: Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file inside the backend directory:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/arterysegmentation_db

SECRET_KEY=YOUR_SECURE_SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES=60

UPLOAD_DIR=uploads

REPORT_DIR=reports

MAX_UPLOAD_SIZE_MB=100

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Replace the database credentials and secret key with your own values.

### Step 5: Start the Backend

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

### Step 6: Frontend Setup

Open another terminal in the project root.

Create `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Install dependencies:

```bash
npm ci
```

### Step 7: Start the Frontend

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

The application is now available locally, provided that the backend, database, and required model files are configured correctly.

---

## 9. API Documentation

ArteryVision uses FastAPI to expose REST API endpoints.

After starting the backend, access the interactive documentation:

**Swagger UI**

```text
http://127.0.0.1:8000/docs
```

**ReDoc**

```text
http://127.0.0.1:8000/redoc
```

Main API modules include:

| Module | Functionality |
|---|---|
| Authentication | Registration and login |
| Dashboard | Workspace summaries |
| Cases | Case creation and management |
| Patients | Patient metadata |
| Images | Upload and retrieval |
| Preprocessing | Image preprocessing |
| Analysis | Stenosis inference |
| Results | Saved analysis results |
| Reports | Report generation |
| Model Registry | Model metadata |
| Notifications | User notifications |
| Audit Logs | Activity tracking |

Refer to Swagger UI for the exact endpoint paths and request schemas.

---

## 10. Testing

### Backend Testing

Run the backend test suite:

```bash
cd backend
pytest -q
```

### Frontend Build Testing

From the project root:

```bash
npm run build
```

### Manual Application Testing

1. Register a user account.
2. Log in to the application.
3. Create an imaging case.
4. Add de-identified patient metadata.
5. Link the patient to the case.
6. Upload a supported medical image.
7. Inspect the original image.
8. Run preprocessing.
9. Request stenosis analysis on a supported raster image.
10. Review the generated prediction.
11. Open Results & Reports.
12. Compare stored result records.
13. Review model-evaluation metrics.
14. Test the application settings and role permissions.

---

## 11. Deployment

The frontend is configured for deployment using Vercel.

### Frontend Deployment

1. Connect the GitHub repository to Vercel.
2. Select the `review` branch when deploying that branch.
3. Configure the frontend build command:

```bash
npm run build
```

4. Set the output directory:

```text
dist
```

5. Configure the environment variable:

```env
VITE_API_BASE_URL= https://arteryvision-backend.onrender.com/
```

6. Deploy the application.

### Backend Deployment

The FastAPI backend must be deployed separately.

The backend hosting environment requires:
- Python dependencies.
- PostgreSQL connection.
- Environment variables.
- Model checkpoint.
- Image and report storage.
- Appropriate CORS configuration.

A typical production start command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Note:** A frontend deployment alone does not deploy the FastAPI backend or database. Both services must be configured and connected.

---

## 12. Security and Privacy

Security is an important consideration because the application deals with medical imaging workflows.

The project incorporates:

- Password hashing.
- JWT authentication.
- Protected API endpoints.
- Role-based authorization.
- Backend-side request validation.
- Controlled image upload and retrieval.
- Database-backed user and case management.
- Audit logging.

Only public, synthetic, or properly de-identified datasets should be used for demonstrations and testing.

Do not upload identifiable patient information or commit confidential credentials to GitHub.

---

## 13. Current Scope and Limitations

- The application provides a research-oriented coronary imaging workflow.
- The stenosis U-Net inference implementation currently supports PNG, JPG/JPEG, and TIFF raster images.
- DICOM and NIfTI upload and preprocessing support does not automatically imply direct support in the current stenosis inference endpoint.
- Model evaluation metrics represent recorded research/test-set results.
- XAI reference visualizations are not necessarily generated for the currently uploaded image.
- The model registry stores metadata and does not itself train or execute models.
- The current inference implementation uses CPU execution.
- Mask coverage and severity labels are research-oriented outputs, not clinically validated stenosis measurements.

**ArteryVision is not a standalone diagnostic system and must not be used as a substitute for professional medical interpretation.**

---

## 14. Future Enhancements

Potential future improvements include:

1. Integration of additional validated segmentation architectures.
2. Improved coronary artery segmentation and stenosis localization.
3. Direct DICOM and NIfTI inference support.
4. Case-specific Explainable AI visualizations.
5. More comprehensive image-overlay functionality.
6. Additional model-evaluation metrics.
7. Model version tracking and comparison.
8. Improved image visualization tools.
9. Persistent cloud-based image storage.
10. Expanded automated testing and monitoring.
11. Further optimization of inference performance.

---

## 15. Team and Contribution

**Project:** ArteryVision – Coronary Imaging Workspace

**Repository:** Team_3_Segmentation_Artery_DL

**Branch:** `review`

This project is developed as part of a collaborative team-based software and deep learning project.

The development combines frontend engineering, backend API development, database management, image preprocessing, deep learning model integration, and application testing.

---

## 16. License

Refer to the repository's `LICENSE` file for licensing and distribution information.

---

## Conclusion

ArteryVision provides an integrated research-oriented platform for coronary artery imaging workflows. By combining full-stack web technologies, medical image processing, deep learning-based segmentation, and structured result management, the platform establishes a foundation for experimentation and research in automated coronary image analysis.

The application brings image upload, case management, preprocessing, model inference, segmentation visualization, evaluation, and reporting together in one workspace.

**ArteryVision – Bringing AI-Assisted Coronary Imaging and Research Together.**
