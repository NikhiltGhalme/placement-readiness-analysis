# Placement Readiness Analysis System

A full-stack ML-powered web application that predicts campus placement outcomes and salary packages for engineering students. Built with **FastAPI**, **scikit-learn**, and **Jinja2**.

## Overview

This system addresses a real problem in Indian engineering colleges: students don't know where they stand until it's too late. It combines rule-based assessment, statistical comparison against 1000+ student profiles, and 9 trained ML models to give actionable, data-driven placement guidance.

### Three Core Modules

| Module | Route | Purpose |
|---|---|---|
| **Readiness Checker** | `/readiness` | Interactive assessment across academics, technical skills, projects, and soft skills. Outputs a weighted readiness score, placement probability, estimated salary range, and personalized improvement plan. Compares the student against placed-student averages from the dataset. |
| **ML Analysis Dashboard** | `/analysis` | Runs a 7-phase ML pipeline: data loading, EDA (10 charts), preprocessing, classification (4 models), regression (5 models), summary, and PDF report generation. Produces 20 visualizations and a comprehensive academic report. |
| **Data Generator** | `/generator` | Generates synthetic placement datasets (100-10,000 records) with realistic correlations between skills and outcomes. Useful for experimentation and model retraining. |

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **ML/Data:** scikit-learn, pandas, NumPy, matplotlib, seaborn
- **Frontend:** Jinja2 templates, Tailwind CSS
- **Reports:** fpdf2 (PDF generation), openpyxl (Excel I/O)

## Project Structure

```
research/
├── webapp/
│   ├── app.py                  # FastAPI entry point, route registration
│   ├── config.py               # Paths: data, output, charts, reports
│   ├── routes/
│   │   ├── readiness.py        # /readiness — student assessment endpoints
│   │   ├── analysis.py         # /analysis  — ML pipeline endpoints (async with progress)
│   │   └── generator.py        # /generator — synthetic data generation endpoints
│   ├── services/
│   │   ├── readiness_checker.py    # Weighted scoring engine + dataset comparison
│   │   ├── ml_analysis.py          # 7-phase ML pipeline (4 classifiers, 5 regressors, 20 charts)
│   │   ├── data_generator.py       # Synthetic dataset generator with correlated outcomes
│   │   └── pdf_report.py           # Readiness PDF report builder
│   ├── templates/              # Jinja2 HTML templates
│   ├── static/                 # CSS, JS assets
│   └── output/                 # Generated charts, reports, datasets
├── generate_placement_data.py      # Standalone script — generated the initial dataset
├── placement_readiness_data.xlsx   # Primary dataset (1000 records, 26 features)
├── placement_analysis.py           # Standalone analysis script
├── placement_readiness_checker.py  # Standalone checker script
├── create_ppt.py                   # PPT generation script
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
git clone https://github.com/NikhiltGhalme/placement-readiness-analysis.git
cd placement-readiness-analysis
pip install -r webapp/requirements.txt
```

### Run the Application

```bash
python3 -m uvicorn webapp.app:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## ML Models Used

### Classification (Placed / Unplaced)

| Model | Purpose |
|---|---|
| Logistic Regression | Baseline linear classifier |
| Random Forest | Ensemble model, provides feature importance |
| SVM (RBF kernel) | Non-linear decision boundary |
| Gradient Boosting | Sequential ensemble, typically highest accuracy |

### Regression (Salary Prediction)

| Model | Purpose |
|---|---|
| Linear Regression | Baseline |
| Ridge Regression | L2 regularization to handle multicollinearity |
| Lasso Regression | L1 regularization for feature selection |
| Random Forest Regressor | Non-linear, robust to outliers |
| Gradient Boosting Regressor | Best overall performance on salary prediction |

## Dataset

The dataset contains **1000 synthetic student records** with 26 features spanning:

- **Academics:** CGPA, 10th/12th percentage
- **Technical:** DSA, OOPS, coding problems solved, languages, backend/frontend/DB, system design
- **Experience:** projects, internships, open source, full-stack project
- **Soft Skills:** communication, English fluency, interview confidence, mock interviews
- **Outcome:** placement status, salary package (LPA), company type

Placement outcomes are **correlated with skills** — not random. The generation formula weights DSA, CGPA, internships, and coding practice as the strongest predictors, reflecting real-world placement patterns.

## How the Scoring Works (Readiness Checker)

The readiness score is a weighted composite:

| Category | Weight | Key Factors |
|---|---|---|
| Academics | 25% | CGPA (50%), 12th % (25%), 10th % (25%) |
| Technical Skills | 30% | DSA (25%), Coding (25%), OOPS (15%), Languages (10%), Stack (25%) |
| Projects & Experience | 25% | Projects (30%), Internships (30%), Full-Stack (25%), Open Source (15%) |
| Soft Skills | 20% | Confidence (30%), Communication (30%), English (25%), Mock Interviews (15%) |

**Prediction thresholds:** >= 75 HIGH, >= 55 MODERATE, >= 35 LOW, < 35 VERY LOW

## Key Outputs

- **20 EDA & ML charts** (distribution, correlation, ROC, confusion matrix, feature importance, residuals)
- **Classification metrics** (accuracy, precision, recall, F1, AUC-ROC, cross-validation)
- **Regression metrics** (R-squared, MAE, RMSE, cross-validation R2)
- **Downloadable PDF reports** (individual readiness + full ML analysis)
- **Downloadable Excel datasets** (generated synthetic data)

## Author

- Nikhil Ghalme

## License

This project is for academic and educational purposes.
