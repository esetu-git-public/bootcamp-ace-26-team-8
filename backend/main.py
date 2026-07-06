from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
<<<<<<< HEAD
    return {"message": "Loan Default Prediction API is running"}
=======
    return {"message": "API is running"}

@app.post("/predict")
def predict():
    return {"result": "working"}
>>>>>>> 54b17fa0685ca1d58cdf6ac4777bf23b0ec9db1c
