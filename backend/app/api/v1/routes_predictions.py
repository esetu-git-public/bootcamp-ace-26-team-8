from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_predictions():
    return {"message": "Predictions route working 🚀"}