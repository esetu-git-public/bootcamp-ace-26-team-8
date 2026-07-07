from fastapi import FastAPI

app = FastAPI(
    title="Loan Default Prediction API",
    description="API for predicting whether a borrower is likely to default on a loan.",
    version="1.0.0"
)

@app.get("/")
def welcome():
    return {
        "message": "Loan Default Prediction API is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "API is running successfully."
    }
def home():
    return {"message": "Loan Default Prediction API is running"}