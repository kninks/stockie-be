from fastapi import APIRouter

router = APIRouter()

@router.get("/predict")
def get_prediction():
    return {"message": "Predict stock price"}
