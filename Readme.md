# ArteryVision – My Research & Development Contributions

**Project:** ArteryVision – Coronary Artery Segmentation and Stenosis Detection  
**My Working Branch:** [Soumita Mukherjee](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL/tree/Soumita)
**Repository:** [Team_3_Segmentation_Artery_DL](https://github.com/springboardmentor15742s-oss/Team_3_Segmentation_Artery_DL)

---

## 1. Overview

ArteryVision is a deep-learning-based medical imaging research project focused on coronary artery segmentation, vessel structure analysis, and stenosis detection using medical imaging data.

My contribution focuses on dataset exploration, image preprocessing, segmentation experiments, vessel structure analysis, stenosis detection, model integration, and testing.

The work combines Python-based research notebooks, PyTorch models, image-processing techniques, and integration with the ArteryVision application.

## 2. My Contributions

### 2.1 Project Initialization
- Prepared the project environment and initialized the research workflow.
- Organized the development process and supporting resources.
- Set up the required Python libraries and deep-learning dependencies.

**Notebook:** `01_Project_Initialization.ipynb`

### 2.2 Dataset Exploration and EDA
- Explored the available medical imaging dataset.
- Examined image properties and dataset characteristics.
- Investigated the data distribution and relevant image information.
- Prepared the dataset for subsequent preprocessing and segmentation experiments.

**Notebook:** `02_Dataset_EDA.ipynb`

### 2.3 Medical Image Preprocessing
- Worked on preprocessing medical images for deep-learning applications.
- Prepared normalized image representations.
- Organized image inputs for model processing.
- Worked on preprocessing workflows to improve consistency in model inputs.

**Notebook:** `03_Image_Preprocessing.ipynb`

### 2.4 Artery Segmentation
- Worked on deep-learning-based coronary artery segmentation.
- Explored U-Net-based segmentation architectures.
- Worked with trained model checkpoints for segmentation experiments.
- Examined segmentation outputs and model predictions.

**Notebook:** `01_Artery_Segmentation(4).ipynb`

### 2.5 Vessel Structure Analysis
- Worked on identifying and analyzing coronary vessel structures.
- Explored vessel segmentation outputs and structural characteristics.
- Studied the relationship between artery regions and their segmentation masks.

**Notebook:** `02_Vessel_Structure_Analysis(3).ipynb`

### 2.6 Stenosis Detection and Explainable AI
- Worked on U-Net-based stenosis detection experiments.
- Integrated the stenosis model checkpoint into the project workflow.
- Explored stenosis-region localization and prediction outputs.
- Worked with Explainable AI (XAI) visualization to understand model predictions.
- Examined prediction masks and research-based severity estimates.

**Notebook:** `03_Stenosis_Detection_Explainable_AI(4).ipynb`

### 2.7 Model Integration
- Worked with trained PyTorch model checkpoints.
- Added the stenosis model checkpoint `stenosis_unet_v2.pth`.
- Added the segmentation implementation file `src/segmentation.py`.
- Worked on connecting model-related components with the existing application structure.

### 2.8 Testing and Reporting
- Performed testing of the project workflow.
- Checked preprocessing and model-related components.
- Examined prediction outputs and stored analysis results.
- Worked on evaluation and reporting activities.

**Notebook:** `04_Milestone4_Testing_Reporting.ipynb`

## 3. Models and Technologies

### Deep Learning Models
- U-Net
- Attention U-Net
- Multiclass U-Net
- Stenosis U-Net

### Technologies Used

| Category | Technologies |
|---|---|
| Programming | Python |
| Deep Learning | PyTorch |
| Numerical Computing | NumPy |
| Image Processing | Pillow, medical image processing libraries |
| Data Analysis | Jupyter Notebook |
| Backend | FastAPI |
| Frontend | React, Vite |
| Database | PostgreSQL |
| API Testing | FastAPI Swagger UI |
| Version Control | Git and GitHub |

## 4. Repository Contribution Structure

```text
Team_3_Segmentation_Artery_DL/
│
├── notebooks/
│   ├── 01_Project_Initialization.ipynb
│   ├── 02_Dataset_EDA.ipynb
│   ├── 03_Image_Preprocessing.ipynb
│   ├── 04_Milestone4_Testing_Reporting.ipynb
│   ├── 01_Artery_Segmentation(4).ipynb
│   ├── 02_Vessel_Structure_Analysis(3).ipynb
│   └── 03_Stenosis_Detection_Explainable_AI(4).ipynb
│
├── src/
│   └── segmentation.py
│
├── models/
│   └── stenosis/
│       └── stenosis_unet_v2.pth
│
└── README.md
```

*The structure above represents the intended organization of my contribution files.*

## 5. Local Environment and Testing

The project environment was configured and tested locally.

Environment verification included:

- Python 3.13.5
- PyTorch 2.6.0+cpu
- NumPy 2.5.5
- Successful import verification of the required Python libraries.
- Backend API documentation access through FastAPI Swagger UI when the backend server was running.

The application was also tested through its deployed frontend.

## 6. Research Outputs

The research workflow covers:

- Dataset exploration and preprocessing.
- Coronary artery segmentation experiments.
- Vessel structure analysis.
- Stenosis detection experiments.
- Prediction-mask inspection.
- Explainable AI visualization.
- Model evaluation and reporting.

Model outputs are experimental research results and are not clinically validated diagnostic measurements.

## 7. Conclusion

Through this contribution, I worked across the medical image-processing and deep-learning research pipeline, from dataset exploration and preprocessing to segmentation, vessel structure analysis, stenosis detection, model integration, and testing.

This work contributes to the development of ArteryVision as a research-oriented coronary imaging workspace and supports further experimentation with deep-learning-based medical image analysis.

---
