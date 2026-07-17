import joblib
import pandas as pd

MODEL_PATH = "../models/loan_pipeline.pkl"

model = joblib.load(MODEL_PATH)

data = pd.DataFrame([
{
    "age":25,
    "credit_score":720,
    "dti_ratio":0.25,
    "education":"Bachelor's",
    "employment_type":"Full-time",
    "has_co_signer":"No",
    "has_dependents":"No",
    "has_mortgage":"No",
    "income":75000,
    "interest_rate":8.5,
    "loan_amount":15000,
    "loan_purpose":"Education",
    "loan_term":36,
    "marital_status":"Single",
    "months_employed":48,
    "num_credit_lines":4
},
{
    "age":45,
    "credit_score":540,
    "dti_ratio":0.52,
    "education":"High School",
    "employment_type":"Part-time",
    "has_co_signer":"Yes",
    "has_dependents":"Yes",
    "has_mortgage":"Yes",
    "income":32000,
    "interest_rate":18.5,
    "loan_amount":35000,
    "loan_purpose":"Business",
    "loan_term":72,
    "marital_status":"Married",
    "months_employed":15,
    "num_credit_lines":8
}
])

predictions = model.predict(data)
probabilities = model.predict_proba(data)

print("=" * 60)

for i in range(len(data)):
    print(f"Applicant {i+1}")
    print("Prediction :", predictions[i])
    print("Probability :", probabilities[i])
    print("-" * 60)