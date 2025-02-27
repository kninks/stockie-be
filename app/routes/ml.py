from fastapi import APIRouter

router = APIRouter()

@router.get("/infer")
def infer():
    return {"message": "Inferencing model"}