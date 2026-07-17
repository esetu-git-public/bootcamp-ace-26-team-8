import joblib

MODEL_PATH = "../models/loan_pipeline.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("=" * 50)
    print("Model Loaded Successfully")
    print("=" * 50)
    print(type(model))
except Exception as e:
    print("Failed to load model")
    print(e)