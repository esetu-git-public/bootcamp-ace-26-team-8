import joblib
import pandas as pd

# Load the trained pipeline
MODEL_PATH = "models/loan_pipeline.pkl"
model = joblib.load(MODEL_PATH)

# --------------------------------------------------
# SAMPLE LOAN APPLICATION
# (Replace the field names below with the exact
# feature names used by your trained model.)
# --------------------------------------------------

sample_application = {
    "Age": 30,
    "Annual_Income": 75000,
    "Loan_Amount": 250000,
    "Credit_Score": 720,
    "Employment_Type": "Salaried",
    "Loan_Term": 36,
    "Existing_Debt": 50000,
    "Number_of_Dependents": 2,
    "Marital_Status": "Married",
    "Education": "Graduate"
}

# Convert to DataFrame
sample_df = pd.DataFrame([sample_application])

print("=" * 60)
print("Sample Loan Application")
print("=" * 60)
print(sample_df)

# Predict
prediction = model.predict(sample_df)

print("\n" + "=" * 60)
print("Prediction Result")
print("=" * 60)

if prediction[0] == 1:
    print("⚠️ Prediction: HIGH RISK (Likely to Default)")
else:
    print("✅ Prediction: LOW RISK (Not Likely to Default)")

# Predict Probability
if hasattr(model, "predict_proba"):
    probability = model.predict_proba(sample_df)

    print("\nPrediction Probability")

    print(f"Not Default : {probability[0][0]*100:.2f}%")
    print(f"Default     : {probability[0][1]*100:.2f}%")

print("\nDemo completed successfully.")