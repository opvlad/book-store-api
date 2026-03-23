from fastapi import APIRouter


router = APIRouter()


@router.get("/login")
async def login():
    pass


@router.post("/register")
async def register():
    pass