import joblib

MODEL_PATH = "models/loan_pipeline.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
    print("Model Type:", type(model))
except Exception as e:
    print("❌ Failed to load model.")
    print(e)