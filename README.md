# ArteryVision AI

## Artery Segmentation and Stenosis Detection Using Advanced Deep Learning Techniques

ArteryVision AI is an AI-based medical image analysis project designed to process **CT Angiography (CTA)** images for artery segmentation and stenosis analysis.

The project uses deep learning techniques to identify artery regions from CTA scans and provides a foundation for detecting and visualizing abnormal narrowing (stenosis).

---

## Objectives

- Segment arteries from 3D CTA images.
- Detect and analyze possible artery narrowing.
- Identify the location of stenosis.
- Estimate the severity of narrowing.
- Provide visual outputs for easier interpretation.
- Evaluate the AI model using standard segmentation metrics.
- Build a foundation for integration with the complete ArteryVision AI application.

---

# AI/ML Module

The current AI/ML implementation focuses on **3D artery segmentation using the ImageCAS dataset**.

The segmentation pipeline includes:

1. Dataset preparation
2. CT preprocessing
3. Ground-truth mask processing
4. 3D patch generation
5. 3D U-Net model training
6. Sliding-window inference
7. Threshold-based evaluation
8. Segmentation visualization

A stenosis analysis module is being developed on top of the artery segmentation output.

---

# Dataset

## ImageCAS Dataset

The project uses the **ImageCAS dataset**, which contains CTA images and corresponding artery segmentation labels.

For the current development and training pipeline:

- 200 CT scans were processed.
- 200 corresponding labels were processed.
- All selected CT images and labels passed the validation checks.

The dataset is handled in NIfTI format using **NiBabel**.

---

# Image Preprocessing

The preprocessing pipeline includes:

- Loading CT volumes using NiBabel.
- Checking image and label dimensions.
- Checking affine information.
- Clipping CT intensity values to approximately **-1000 to 1500 HU**.
- Normalizing CT intensity values.
- Converting artery labels into binary masks.
- Preparing the data for 3D deep learning.

The processed volumes are divided into smaller 3D patches for model training.

### Patch Size

```text
96 × 96 × 96
```

---

# Artery Segmentation

The segmentation model is a custom **3D U-Net** designed for volumetric CTA images.

### Model Architecture

The network contains:

- 3D convolutional layers
- Batch normalization
- ReLU activation
- Max pooling
- Transpose convolution
- Skip connections
- Two-class output

The model predicts the artery region from the input CTA volume.

### Training Configuration

The current training pipeline uses:

- Loss: Dice + Cross Entropy Loss
- Optimizer: AdamW
- Learning Rate: `1e-4`
- Weight Decay: `1e-5`
- Batch Size: `1`
- 3D patch size: `96 × 96 × 96`
- Mixed precision training
- GPU acceleration using Google Colab

---

# Inference

For inference, the trained 3D U-Net model is applied to the complete CTA volume using **MONAI sliding-window inference**.

### Inference Configuration

```text
ROI Size: 96 × 96 × 96
Overlap: 0.5
```

The sliding-window approach allows large 3D CTA volumes to be processed in smaller regions while maintaining the spatial information required for segmentation.

---

# Segmentation Evaluation

The segmentation output is evaluated using:

- Dice Score
- Intersection over Union (IoU)
- Precision
- Recall

Different probability thresholds are also tested to study the effect of threshold selection on the predicted artery masks.

### Thresholds Tested

```text
0.3
0.5
0.6
0.7
0.8
```

The results are stored in:

```text
validation_threshold_results.csv
```

---

# Segmentation Visualization

The project generates visual outputs to compare:

- Original CT image
- Ground-truth artery mask
- Predicted artery segmentation
- Ground-truth/prediction overlays
- Probability maps

These visualizations help verify whether the model is correctly identifying artery structures.

---

# Stenosis Detection and Analysis

## Overview

After artery segmentation, the predicted artery structures can be analyzed to identify regions where the vessel becomes abnormally narrow.

The stenosis module is intended to use the segmented artery region as the input for further analysis.

### Stenosis Analysis Pipeline

```text
CTA Image
    ↓
Preprocessing
    ↓
3D Artery Segmentation
    ↓
Extract Artery Region
    ↓
Analyze Vessel Geometry
    ↓
Identify Narrowing
    ↓
Estimate Stenosis Percentage
    ↓
Classify Severity
    ↓
Generate Stenosis Visualization
```

---

## Stenosis Detection

The stenosis analysis focuses on identifying abnormal narrowing within the segmented artery.

The planned analysis includes:

- Extracting the artery region from the segmentation mask.
- Identifying vessel narrowing along the artery.
- Comparing the narrowed region with a reference/normal vessel region.
- Estimating the percentage of narrowing.
- Identifying the approximate location of stenosis.

---

## Stenosis Percentage

The percentage of stenosis can be estimated using the relationship between the normal/reference vessel diameter and the minimum diameter at the narrowed region.

A commonly used representation is:

```text
Stenosis % = (1 - Narrowed Diameter / Reference Diameter) × 100
```

The reference diameter represents the estimated normal vessel diameter, while the narrowed diameter represents the vessel diameter at the suspected stenotic region.

---

## Stenosis Severity

The system is designed to classify detected narrowing into severity categories such as:

| Stenosis Percentage | Severity |
|---|---|
| < 50% | Mild |
| 50–69% | Moderate |
| ≥ 70% | Severe |

These thresholds can be adjusted according to the final clinical/reference methodology adopted for the project.

---

# Stenosis Visualization

The stenosis module is intended to provide visual indication of suspected narrowing.

The visualization can include:

- Original CTA slice
- Segmented artery
- Suspected stenotic region
- Highlighted narrowing area
- Stenosis percentage
- Severity classification

This will make the AI output easier to understand and interpret.

---

# Explainable AI

Explainability is included to make the AI predictions more understandable.

The project aims to provide visual evidence showing:

- Where the artery was detected.
- Which region was identified as abnormal.
- Where possible stenosis is located.
- How the predicted region relates to the original CTA image.

The visual overlays help users understand the model output rather than relying only on numerical predictions.

---

# Development Environment

The current AI/ML experiments are performed using **Google Colab** with GPU acceleration.

### Environment

```text
Platform: Google Colab
GPU: NVIDIA Tesla T4
Framework: PyTorch
Medical Image Processing: NiBabel
Deep Learning Utilities: MONAI
Numerical Processing: NumPy
Image Processing: OpenCV
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

# AI Workflow

```text
ImageCAS CTA Dataset
        ↓
Data Validation
        ↓
CT Preprocessing
        ↓
3D Patch Preparation
        ↓
3D U-Net Training
        ↓
Sliding-Window Inference
        ↓
Artery Segmentation
        ↓
Segmentation Evaluation
        ↓
Extract Artery Structure
        ↓
Stenosis Analysis
        ↓
Stenosis Visualization
```

---

# Current AI/ML Progress

### Completed

- [x] ImageCAS dataset preparation
- [x] CT and label validation
- [x] CT preprocessing
- [x] Intensity normalization
- [x] Binary mask preparation
- [x] 3D patch preparation
- [x] 3D U-Net implementation
- [x] Model training
- [x] GPU-based training in Google Colab
- [x] Sliding-window inference
- [x] Threshold-based evaluation
- [x] Dice, IoU, Precision and Recall evaluation
- [x] Segmentation visualization

### Stenosis Module

- [ ] Extract vessel geometry from segmentation
- [ ] Identify possible narrowing regions
- [ ] Estimate vessel diameter
- [ ] Calculate stenosis percentage
- [ ] Classify stenosis severity
- [ ] Generate stenosis visualization
- [ ] Integrate stenosis results with the application

---

# Future Work

The planned future improvements include:

- Improve segmentation performance using additional training data.
- Develop vessel centerline extraction.
- Improve vessel diameter estimation.
- Implement automated stenosis detection.
- Generate more detailed stenosis visualizations.
- Integrate the AI model with the backend API.
- Perform end-to-end testing with the complete application.
- Improve explainability of AI predictions.

---

# Disclaimer

This project is developed for **academic and research purposes**. The AI-generated segmentation and stenosis analysis should not be considered a substitute for professional medical diagnosis or clinical decision-making.
