# Artery Segmentation and Stenosis Detection Using Deep Learning

## Project Overview

This project focuses on developing a deep learning-based system for artery segmentation and stenosis detection using coronary angiography images.

The objective is to segment coronary arteries, identify potential narrowed regions, and support stenosis analysis through image processing and deep learning techniques.

## Dataset

**ARCADE – Automatic Region-based Coronary Artery Disease Diagnostics**

The dataset contains coronary angiography images and corresponding annotations for artery segmentation and stenosis-related analysis.

## Technologies Used

* Python
* PyTorch
* OpenCV
* NumPy
* Pandas
* Matplotlib
* Google Colab
* Deep Learning

## My Contributions

### Milestone 1 – Preliminary Medical Image Preprocessing

* Implemented image loading and validation using OpenCV.
* Applied image normalization.
* Implemented Gaussian Blur for noise reduction.
* Applied CLAHE for contrast enhancement.
* Visualized original and processed images.

### Dataset Exploration and Preparation

* Explored the ARCADE dataset structure.
* Inspected syntax and stenosis annotation JSON files.
* Examined polygon annotations and image information.
* Worked on image and mask preparation for segmentation experiments.

### Milestone 2 – Segmentation Model Development and Evaluation

* Implemented a baseline U-Net model.
* Implemented an Attention U-Net model.
* Trained and evaluated both models using PyTorch.
* Compared models using Dice Score, IoU, Precision, Recall, and Accuracy.
* Generated model comparison graphs, CSV results, and a performance report.

### Milestone 3 – Stenosis Detection Research

* Studied the stenosis detection pipeline.
* Explored stenosis candidate-region extraction.
* Studied the use of vessel segmentation, centerlines, and diameter measurements for identifying potential narrowed regions.

## Repository Structure

* `Milestone_1_Preprocessing/` – Preliminary image preprocessing work.
* `Dataset_Preparation/` – Dataset exploration and preparation.
* `Milestone_2_Segmentation/` – Segmentation models, evaluation, and reports.
* `Milestone_3_Stenosis_Research/` – Stenosis detection research notes.

## Note

The segmentation experiments and preliminary preprocessing prototype are academic development work. The results are experimental and are not clinically validated.
