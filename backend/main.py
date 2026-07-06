from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class LoanInput(BaseModel):
    age: int
    income: int
    loan_amount: int

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/predict")
def predict(data: LoanInput):
    return {
        "received_data": data,
        "result": "working"
    }