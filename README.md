# bootcamp-ace-26-team-8

# Bootcamp by ACE Students Team 8

# Loan Default Prediction

## Project Overview

Loan Default Prediction is a Machine Learning project developed to predict whether a borrower is likely to default on a loan. The system analyzes customer and loan-related information and classifies the borrower as either likely to default or not default. This project follows the Agile methodology with incremental development through multiple sprints.

---

## Problem Statement

Financial institutions face significant losses due to loan defaults. Manually assessing loan applications can be time-consuming and inconsistent. This project aims to develop a machine learning model that predicts loan default risk using historical borrower data, enabling faster and more reliable lending decisions.

---

## Business Objectives

- Reduce financial losses caused by loan defaults.
- Improve the loan approval process.
- Assist financial institutions in making data-driven decisions.
- Increase the efficiency and consistency of risk assessment.
- Build an accurate binary classification model for loan default prediction.

---

## Dataset

- **Project:** Loan Default Prediction
- **Problem Type:** Binary Classification
- **Source:** Kaggle Loan Default Dataset
- **Target Variable:** Loan Default (0 = No Default, 1 = Default)

The dataset contains borrower information such as demographic details, financial information, loan details, and repayment history.

---

## Project Workflow

1. Customer Registration
2. Customer Login
3. Loan Application Submission
4. Loan Officer Reviews Application
5. Machine Learning Model Predicts Loan Default Risk
6. Loan Approval or Rejection
7. Customer Views Application Status

---

## Tech Stack

### Programming Language
- Python

### Machine Learning
- Scikit-learn
- Pandas
- NumPy

### Data Visualization
- Matplotlib
- Seaborn

### Backend
- FastAPI

### Development Environment
- Jupyter Notebook
- Visual Studio Code

### Version Control
- Git
- GitHub

---
## Installation

### Clone the Repository

```bash
git clone <repository-url>
```

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend

```bash
python backend/main.py
```

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```



## Project Architecture

```text
User
   │
   ▼
Frontend
   │
   ▼
FastAPI Backend
   │
   ▼
Machine Learning Model
   │
   ▼
Prediction Result
```

---

## Installation

```bash
git clone <repository-url>
cd bootcamp-ace-26-team-8
python -m venv venv
pip install -r requirements.txt
```

---

## How to Run

1. Clone the repository.
2. Install the dependencies.
3. Place the dataset inside `data/raw/`.
4. Run the preprocessing notebook.
5. Start the FastAPI backend.
6. Open Swagger UI.
7. Test the prediction API.

---

## Future Scope

- Improve prediction accuracy.
- Deploy to cloud.
- Build a frontend.
- Add Explainable AI.
- Support real-time predictions.
- Add authentication.

---

## Project Methodology

This project follows the Agile Software Development Methodology with multiple sprints, continuous integration, and code reviews.

---

## Team Roles

- Business Owner
- Product Owner
- Scrum Master
- Team Lead
- Developer

---

## Team Members

Business Owner                  : Sai Kumar
Product Owner                   : Deekshith
Developer                       : Manikanta
Scrum Master                    : Renuka
Team Lead                       : Varshitha
Backend Developer               : Renuka
ML Engineer                     : Deekshith
Frontend Developer              : Manikanta
Database & Integration          : Sai Kumar
 
 -----

 ## Future Enhancements

- Deploy the application to the cloud.
- Improve prediction accuracy using advanced ML algorithms.
- Add email notifications.
- Build an admin dashboard.
- Implement real-time analytics.