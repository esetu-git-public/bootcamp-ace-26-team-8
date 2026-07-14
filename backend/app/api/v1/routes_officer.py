from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_officer():
    return {"message": "Officer route working 🚀"}