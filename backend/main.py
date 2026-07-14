from fastapi import FastAPI
from app.api.v1 import routes_predictions

app = FastAPI()


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return {"message": "Backend is running successfully"}


app.include_router(
    routes_predictions.router,
    prefix="/api/v1/predictions",
    tags=["Predictions"]
)