from fastapi import APIRouter
from schemas.user_schema import UserCreate, UserLogin

router = APIRouter()

@router.get("/")
def test():
    return {"message": "Auth working"}

@router.post("/register")
def register(user: UserCreate):
    return {
        "message": "User registered successfully",
        "data": user
    }

@router.post("/login")
def login(user: UserLogin):
    return {
        "message": "Login successful",
        "data": user
    }