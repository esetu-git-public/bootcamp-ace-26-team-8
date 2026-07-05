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

## Project Architecture

```
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

Clone the repository:

```bash
git clone <repository-url>
```

Navigate to the project folder:

```bash
cd bootcamp-ace-26-team-8
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

Install the required packages:

```bash
pip install -r requirements.txt
```
---

## How to Run

1. Clone the repository.
2. Install all required dependencies.
3. Place the dataset inside the `data/raw/` folder.
4. Open the preprocessing notebook and execute the cells.
5. Start the FastAPI backend.
6. Access the API through the browser or Swagger UI.
7. Submit borrower details to receive the loan default prediction.

---

## Future Scope

- Improve prediction accuracy using advanced machine learning algorithms.
- Deploy the application to a cloud platform.
- Develop a responsive web interface.
- Integrate Explainable AI (XAI) techniques.
- Support real-time loan prediction.
- Add authentication and user management.

---

## Project Methodology

This project follows the Agile Software Development Methodology. Development is carried out in multiple sprints, with continuous integration, code reviews, and incremental feature delivery through GitHub.
---

## Team Roles

- Business Owner
- Product Owner
- Scrum Master
- Team Lead
- Developer