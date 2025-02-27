from fastapi import APIRouter

router = APIRouter()

@router.get("/get")
async def test_db():
    return {"message": "get"}

@router.get("/post")
async def get_data():
    return {"message": "post"}