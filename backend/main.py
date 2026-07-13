from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}



@app.get("/")
def home():
    return {"message": "Backend is running successfully"}