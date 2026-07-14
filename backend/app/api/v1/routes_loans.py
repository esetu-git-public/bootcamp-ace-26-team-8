from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_loans():
    return {"message": "Loans route working 🚀"}