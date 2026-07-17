import joblib
import pandas as pd

MODEL_PATH = "ml/models/loan_pipeline.pkl"

model = joblib.load(MODEL_PATH)

sample = pd.DataFrame([{
    "age": 41,
    "credit_score": 615,
    "dti_ratio": 0.41,
    "education": "High School",
    "employment_type": "Part-time",
    "has_co_signer": "No",
    "has_dependents": "Yes",
    "has_mortgage": "No",
    "income": 54000,
    "interest_rate": 15.2,
    "loan_amount": 22000,
    "loan_purpose": "Business",
    "loan_term": 60,
    "marital_status": "Single",
    "months_employed": 30,
    "num_credit_lines": 6
}])

prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0]

print("=" * 50)
print("Prediction :", prediction)
print("Probability:", probability)
print("Probability of Default :", probability[1])
print("Probability of Non-Default :", probability[0])
print("=" * 50)