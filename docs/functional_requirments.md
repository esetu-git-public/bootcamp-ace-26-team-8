Functional Requirements Document (FRD)
Project Name

Loan Default Prediction System

Introduction

The Loan Default Prediction System is a web-based application designed to help financial institutions predict whether a borrower is likely to default on a loan before loan approval. The system uses Machine Learning algorithms to analyze borrower information and assist loan officers in making informed lending decisions.

Purpose

This document defines the functional requirements of the Loan Default Prediction System for developers, testers, designers, stakeholders, and the Scrum team.

Scope

Secure authentication, borrower management, dataset upload, data preprocessing, loan default prediction, dashboard, reports, search and filtering, and audit logs.

User Roles

Administrator

Manage users
Upload datasets
Manage Machine Learning model
View reports
Monitor system activities

Loan Officer

Add borrower information
Update borrower details
Predict loan default
View prediction reports

Manager

View dashboards
Analyze prediction reports
Monitor loan statistics
Functional Requirements
FR-01 User Authentication

The system shall provide secure login using username/email and password.

FR-02 User Logout

The system shall securely terminate the user's session.

FR-03 Add Borrower Record

The system shall allow loan officers to enter borrower personal, financial, and loan information.

FR-04 Update Borrower Record

The system shall allow authorized users to edit borrower information before prediction.

FR-05 View Borrower Record

The system shall allow users to search and view borrower details.

FR-06 Upload Loan Dataset

The system shall allow the administrator to upload a loan dataset in CSV format with validation.

FR-07 Data Preprocessing

The system shall clean, validate, and preprocess borrower data before prediction.

FR-08 Predict Loan Default

The system shall analyze borrower information using the trained Machine Learning model and classify the applicant as:

Default
No Default
FR-09 Display Prediction Confidence

The system shall display the prediction confidence score (probability percentage).

FR-10 Dashboard

The system shall display statistics including:

Total Loan Applications
Total Predictions
Default Cases
No Default Cases
Prediction Accuracy (if available)
FR-11 Search and Filter

The system shall allow users to search and filter borrower records based on:

Applicant Name
Loan Status
Loan Amount
Prediction Result
Date
FR-12 Generate Reports

The system shall generate prediction reports that can be exported in PDF or CSV format.

FR-13 Audit Logs

The system shall record important user activities such as login, dataset upload, borrower updates, and prediction requests.
