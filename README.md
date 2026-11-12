# ArteryVision AI

## Artery Segmentation and Stenosis Detection Using Advanced Deep Learning Techniques

ArteryVision AI is an AI-based medical image analysis project designed to process **CT Angiography (CTA)** images for artery segmentation and stenosis analysis.

The project uses deep learning techniques to identify artery regions from CTA images and provides a foundation for detecting and visualizing abnormal vessel narrowing (stenosis).

---

# Objectives

- Segment arteries from CTA images.
- Detect and localize possible stenosis regions.
- Estimate the percentage of vessel narrowing.
- Classify stenosis severity into mild, moderate, and severe categories.
- Generate visual outputs for artery and stenosis regions.
- Evaluate the AI model using standard performance metrics.
- Integrate the AI module with the complete ArteryVision AI application.

---

# AI/ML Module

The AI/ML module uses the **ARCADE dataset** for artery segmentation and stenosis-related analysis.

The overall AI workflow includes:

1. Dataset preparation
2. Image preprocessing
3. Artery mask preparation
4. Deep learning model training
5. Artery segmentation
6. Segmentation evaluation
7. Stenosis analysis
8. Stenosis visualization

---

# Dataset

## ARCADE Dataset

The project uses the **ARCADE (Artery and Carotid Artery Dataset)** for developing the artery segmentation and stenosis analysis components.

The dataset provides CTA images along with corresponding annotations that can be used for identifying artery structures and stenosis-related regions.

The dataset is organized into separate tasks for artery segmentation and stenosis analysis.

---

# Data Preprocessing

The preprocessing pipeline includes:

- Loading CTA images.
- Reading the corresponding annotation files.
- Validating image and annotation information.
- Converting annotations into suitable segmentation masks.
- Resizing/preparing images for model input.
- Normalizing image data.
- Preparing training and validation data.

The annotation information is processed to generate the required ground-truth masks for training.

---

# Artery Segmentation

The segmentation module is responsible for identifying artery regions from CTA images.

A **U-Net-based deep learning model** is used for artery segmentation.

### Model Architecture

The segmentation network contains:

- Convolutional layers
- Batch normalization
- ReLU activation
- Pooling layers
- Upsampling/transposed convolution
- Skip connections
- Output segmentation layer

The model learns to distinguish artery regions from the surrounding CTA image.

---

# Segmentation Training

The model is trained using the ARCADE training data.

The training pipeline includes:

```text
CTA Images
     ↓
Preprocessing
     ↓
Ground-Truth Masks
     ↓
U-Net Training
     ↓
Validation
     ↓
Best Model Checkpoint
```

The trained model is then used to generate predicted artery masks for unseen images.

---

# Segmentation Evaluation

The segmentation model is evaluated using standard metrics:

- **Dice Score**
- **Intersection over Union (IoU)**
- **Precision**
- **Recall**

These metrics help measure how accurately the model identifies the artery regions compared with the ground-truth annotations.

---

# Segmentation Results

The current ARCADE-based experiments produced the following results:

### U-Net

- Best validation Dice: **0.7498**
- Test Dice: **0.7109**
- Test IoU: **0.5515**
- Precision: **0.7117**
- Recall: **0.7101**

### Attention U-Net

- Best validation Dice: **0.7630**
- Test Dice: **0.7193**
- Test IoU: **0.5617**
- Precision: **0.7350**
- Recall: **0.7043**

The Attention U-Net showed a slight improvement in segmentation performance compared with the basic U-Net.

---

# Stenosis Detection and Analysis

## Overview

After obtaining the artery segmentation, the next stage is to analyze the segmented vessel structure for possible narrowing.

Stenosis refers to an abnormal narrowing of a blood vessel.

The stenosis module is designed to use the artery segmentation output to identify narrowed regions and estimate their severity.

---

## Stenosis Analysis Pipeline

```text
CTA Image
     ↓
Preprocessing
     ↓
Artery Segmentation
     ↓
Extract Artery Region
     ↓
Analyze Vessel Geometry
     ↓
Identify Narrowed Region
     ↓
Estimate Diameter
     ↓
Calculate Stenosis %
     ↓
Severity Classification
     ↓
Stenosis Visualization
```

---

# Stenosis Detection

The stenosis analysis focuses on identifying regions where the artery diameter becomes smaller than the normal/reference vessel diameter.

The planned analysis includes:

- Extracting the artery region from the segmentation mask.
- Identifying the vessel path.
- Detecting regions with reduced vessel diameter.
- Estimating the minimum vessel diameter.
- Comparing the narrowed diameter with a reference diameter.
- Identifying the approximate location of stenosis.

---

# Stenosis Percentage

The percentage of narrowing can be estimated using:

```text
Stenosis % = (1 - Narrowed Diameter / Reference Diameter) × 100
```

Where:

- **Reference Diameter** = estimated normal vessel diameter.
- **Narrowed Diameter** = minimum diameter measured at the suspected stenosis region.

The resulting percentage can be used for severity classification.

---

# Stenosis Severity Classification

The system is designed to classify detected narrowing into three categories:

| Stenosis Percentage | Severity |
|---|---|
| Less than 50% | Mild |
| 50% – 69% | Moderate |
| 70% or more | Severe |

These categories are intended for the project's academic analysis and can be adjusted according to the final methodology used.

---

# Stenosis Localization

The system aims to identify the approximate location of the stenotic region within the segmented artery.

The detected region can be highlighted on the CTA image to show where the narrowing occurs.

This allows the output to provide both:

- **Location of narrowing**
- **Estimated severity**

---

# Stenosis Visualization

The stenosis visualization module is designed to display:

- Original CTA image
- Artery segmentation
- Suspected stenosis region
- Highlighted narrowed area
- Estimated stenosis percentage
- Severity classification

Example workflow:

```text
Original CTA
     +
Artery Mask
     ↓
Identify Narrowed Region
     ↓
Highlight Stenosis
     ↓
Display Severity and Percentage
```

---

# Explainable AI

Explainability is included to make the AI output easier to understand.

The visualization can show:

- Where the artery was detected.
- Which region was identified as narrowed.
- The approximate stenosis location.
- The relationship between the original CTA image and the predicted region.

This provides visual evidence for the model's predictions instead of presenting only numerical results.

---

# AI Workflow

```text
ARCADE Dataset
      ↓
Data Preparation
      ↓
Image Preprocessing
      ↓
Annotation / Mask Preparation
      ↓
U-Net / Attention U-Net
      ↓
Artery Segmentation
      ↓
Segmentation Evaluation
      ↓
Vessel Structure Analysis
      ↓
Stenosis Detection
      ↓
Severity Classification
      ↓
Stenosis Visualization
```

---

# Project Structure

```text
ArteryVision-AI/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/
│
├── notebooks/
│
├── src/
│   ├── preprocessing/
│   ├── models/
│   ├── training/
│   ├── evaluation/
│   ├── stenosis/
│   └── visualization/
│
├── checkpoints/
│
├── experiments/
│
├── outputs/
│   ├── segmentation/
│   ├── reports/
│   └── visualizations/
│
└── documentation/
```

---

# Current AI/ML Progress

## Segmentation

- [x] ARCADE dataset preparation
- [x] CTA image preprocessing
- [x] Annotation processing
- [x] Segmentation mask generation
- [x] U-Net implementation
- [x] Attention U-Net implementation
- [x] Model training
- [x] Validation
- [x] Segmentation evaluation
- [x] Dice evaluation
- [x] IoU evaluation
- [x] Precision evaluation
- [x] Recall evaluation
- [x] Segmentation visualization

## Stenosis

## Stenosis

- [x] ARCADE stenosis annotations identified
- [x] Stenosis analysis workflow defined
- [x] Extract vessel geometry
- [x] Identify narrowed vessel regions
- [x] Estimate vessel diameter
- [x] Classify stenosis severity
- [ ] Calculate stenosis percentage
- [ ] Generate final stenosis visualization
- [ ] Integrate stenosis output with the application

---

# Future Work

- Improve artery segmentation performance.
- Develop robust vessel geometry extraction.
- Implement vessel centerline extraction.
- Estimate vessel diameter at different locations.
- Automate stenosis localization.
- Calculate stenosis percentage.
- Improve severity classification.
- Generate explainable stenosis visualizations.
- Integrate the AI module with the backend.
- Perform end-to-end testing with the complete ArteryVision AI application.
- Improve overall system reliability and usability.

---

# Disclaimer

This project is developed for **academic and research purposes**. The AI-generated segmentation and stenosis analysis are not intended to replace professional medical diagnosis or clinical decision-making.
