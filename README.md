# ArteryVision AI

## Artery Segmentation and Stenosis Detection Using Advanced Deep Learning Techniques

ArteryVision AI is an AI-powered medical image analysis project designed to assist in **artery segmentation and stenosis detection** from CTA (Computed Tomography Angiography) images.

The system uses deep learning techniques to identify artery regions from medical images and supports visualization and analysis of possible stenosis (narrowing) regions.

## 🎯 Project Objectives

- Segment arteries from CTA medical images.
- Detect and localize possible stenosis regions.
- Analyze the degree of artery narrowing.
- Generate visual outputs for easier interpretation.
- Evaluate deep learning segmentation models.
- Integrate the AI/ML module with the application.

## 🧠 AI/ML Module

The project uses deep learning-based image segmentation techniques.

### Models

- U-Net
- Attention U-Net

The models are trained and evaluated using the **ImageCAS dataset** for coronary artery segmentation.

### Evaluation Metrics

- Dice Score
- Intersection over Union (IoU)
- Precision
- Recall

### AI Workflow

```text
CTA Image
    ↓
Image Preprocessing
    ↓
Deep Learning Model
    ↓
Artery Segmentation
    ↓
Thresholding / Post-processing
    ↓
Stenosis Analysis
    ↓
Visualization of Results
```

## 📊 Model Results

### U-Net

- Best Validation Dice: 0.7498
- Test Dice: 0.7109
- IoU: 0.5515
- Precision: 0.7117
- Recall: 0.7101

### Attention U-Net

- Best Validation Dice: 0.7630
- Test Dice: 0.7193
- IoU: 0.5617
- Precision: 0.7350
- Recall: 0.7043

These results are based on the current experimental training setup and may be further improved during project finalization.

## 🖥️ Application Architecture

### Frontend

- React
- JavaScript / TypeScript
- Tailwind CSS

The frontend provides the user interface for uploading and viewing medical images and AI-generated results.

### Backend

- FastAPI
- Python
- Pydantic
- SQLAlchemy

The backend handles API requests and communication between the frontend, database and AI/ML module.

### Database

- PostgreSQL

The database is used for storing application-related information.

### AI/ML

- PyTorch
- NumPy
- OpenCV
- Medical image processing tools

The AI module performs artery segmentation and supports stenosis analysis and visualization.

## 🔬 Project Workflow

```text
User
 ↓
Upload CTA Image
 ↓
Frontend
 ↓
Backend API
 ↓
AI/ML Model
 ↓
Artery Segmentation
 ↓
Stenosis Analysis
 ↓
Visualization
 ↓
Results Display
```

## 🗂️ Dataset

The project uses the **ImageCAS dataset**, which provides coronary artery CTA images and corresponding annotations for artery segmentation research.

The dataset is used for training and evaluating the deep learning segmentation models.

Due to dataset size and storage requirements, the complete dataset is not included in the GitHub repository.

## 📈 Current Project Status

- [x] Initial project planning
- [x] Dataset exploration and preparation
- [x] U-Net model implementation
- [x] Attention U-Net implementation
- [x] Model training and evaluation
- [x] Segmentation performance evaluation
- [x] Thresholded segmentation output generation
- [ ] Stenosis analysis finalization
- [ ] AI/ML and application integration
- [ ] Complete system testing
- [ ] Final documentation
- [ ] Deployment

## 🚀 Future Improvements

- Improve segmentation accuracy.
- Enhance stenosis detection and localization.
- Add artery centerline extraction.
- Estimate vessel diameter and percentage narrowing.
- Improve visualization of stenotic regions.
- Integrate explainable AI techniques.
- Improve inference speed.
- Complete end-to-end application integration and deployment.

## 👥 Project Information

**Project:** ArteryVision AI  
**Domain:** Artificial Intelligence / Medical Image Analysis  
**Application Area:** Coronary Artery Segmentation and Stenosis Detection

## 📌 Disclaimer

This project is developed as an academic project to explore the application of deep learning and medical image processing for artery segmentation and stenosis analysis. It is intended for research and educational purposes and is **not a substitute for professional medical diagnosis**.
