from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Loan Default Prediction API is running"}