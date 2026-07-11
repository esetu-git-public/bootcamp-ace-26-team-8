import joblib
import pandas as pd

# Load model
MODEL_PATH = "models/loan_pipeline.pkl"
model = joblib.load(MODEL_PATH)

# Create a NEW sample loan application
sample = {
    "Age": 30,
    "Income": 85000,
    "LoanAmount": 200000,
    "CreditScore": 760,
    "MonthsEmployed": 60,
    "NumCreditLines": 5,
    "InterestRate": 8.5,
    "LoanTerm": 36,
    "DTIRatio": 0.25,
    "Education": "Bachelor's",
    "EmploymentType": "Full-time",
    "MaritalStatus": "Married",
    "HasMortgage": "No",
    "HasDependents": "Yes",
    "LoanPurpose": "Home",
    "HasCoSigner": "Yes",
}

# ---------- Feature Engineering ----------

sample["Income_was_outlier"] = 0
sample["LoanAmount_was_outlier"] = 0
sample["InterestRate_was_outlier"] = 0
sample["DTIRatio_was_outlier"] = 0

sample["LoanToIncomeRatio"] = sample["LoanAmount"] / sample["Income"]

sample["EmploymentStabilityRatio"] = (
    sample["MonthsEmployed"] / sample["Age"]
)

score = sample["CreditScore"]

if score < 580:
    band = "Poor"
elif score < 670:
    band = "Fair"
elif score < 740:
    band = "Good"
elif score < 800:
    band = "Very Good"
else:
    band = "Excellent"

sample["CreditScoreBand"] = band

sample_df = pd.DataFrame([sample])

print("=" * 60)
print("Sample Loan Application")
print("=" * 60)
print(sample_df)

prediction = model.predict(sample_df)

print("\nPrediction")

if prediction[0] == 1:
    print("⚠️ Default Risk")
else:
    print("✅ No Default Risk")

if hasattr(model, "predict_proba"):
    probability = model.predict_proba(sample_df)

    print("\nPrediction Probability")
    print(f"No Default : {probability[0][0]*100:.2f}%")
    print(f"Default    : {probability[0][1]*100:.2f}%")