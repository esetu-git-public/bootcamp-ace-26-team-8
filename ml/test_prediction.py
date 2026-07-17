import joblib
import pandas as pd

# Load trained pipeline
MODEL_PATH = "models/loan_pipeline.pkl"
model = joblib.load(MODEL_PATH)

# Load engineered dataset (same format used during training)
DATASET_PATH = "data/processed/loan_engineered.csv"

df = pd.read_csv(DATASET_PATH)

# Separate features and target
X = df.drop(columns=["Default"])
y = df["Default"]

# Take the first sample
sample = X.iloc[[0]]
actual = y.iloc[0]

# Make prediction
prediction = model.predict(sample)[0]

# Prediction probability
if hasattr(model, "predict_proba"):
    probability = model.predict_proba(sample)[0]
    no_default_prob = probability[0] * 100
    default_prob = probability[1] * 100
else:
    no_default_prob = None
    default_prob = None

print("=" * 60)
print("LOAN DEFAULT PREDICTION TEST")
print("=" * 60)

print("\nSample Data:")
print(sample)

print("\nActual Value:")
print("Default" if actual == 1 else "No Default")

print("\nPredicted Value:")
print("Default" if prediction == 1 else "No Default")

if default_prob is not None:
    print("\nPrediction Probability")
    print(f"No Default Probability : {no_default_prob:.2f}%")
    print(f"Default Probability    : {default_prob:.2f}%")

print("\nResult Summary")
print("-" * 30)
print(f"Actual      : {'Default' if actual == 1 else 'No Default'}")
print(f"Predicted   : {'Default' if prediction == 1 else 'No Default'}")

if actual == prediction:
    print("Status      : ✅ Correct Prediction")
else:
    print("Status      : ❌ Incorrect Prediction")

print("=" * 60)