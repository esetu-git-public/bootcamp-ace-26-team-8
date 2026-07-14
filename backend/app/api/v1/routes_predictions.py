from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_any_role, AuthenticatedUser
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse
from app.services.prediction_service import run_prediction, PredictionServiceError


router = APIRouter()


@router.get("/")
def get_predictions():
    return {"message": "Predictions route working 🚀"}


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    user: AuthenticatedUser = Depends(require_any_role),
):
    try:
        return run_prediction(payload)

    except PredictionServiceError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate a prediction at this time.",
        )