import joblib
import pandas as pd

# Load trained pipeline
MODEL_PATH = "models/loan_pipeline.pkl"
model = joblib.load(MODEL_PATH)

# Load the engineered dataset (NOT the raw dataset)
DATASET_PATH = "data/processed/loan_engineered.csv"

df = pd.read_csv(DATASET_PATH)

# Remove target column if it exists
if "Default" in df.columns:
    X = df.drop(columns=["Default"])
else:
    X = df

# Take one sample
sample = X.iloc[[0]]

print("=" * 50)
print("Sample Input")
print("=" * 50)
print(sample)

# Make prediction
prediction = model.predict(sample)

print("\nPrediction:")
print(prediction)

# Predict probability (if supported)
if hasattr(model, "predict_proba"):
    probability = model.predict_proba(sample)

    print("\nPrediction Probability:")
    print(probability)