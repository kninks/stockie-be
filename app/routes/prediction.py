from fastapi import APIRouter

router = APIRouter()


@router.get("/predict")
def get_prediction():
    result = {}
    return {"message": "Predict stock price"}
