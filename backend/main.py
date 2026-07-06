from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Loan Default Prediction API",
    description="API for predicting whether a borrower is likely to default on a loan.",
    version="1.0.0"
)

class LoanInput(BaseModel):
age: int
income: int
loan_amount: int

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

@app.post("/predict")
def predict(data: LoanInput):
return {
"received_data": data,
"result": "working"
}
