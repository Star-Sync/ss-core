from fastapi import APIRouter

router = APIRouter(
    prefix="/hello",
    tags=["hello"],
)


@router.get("/db")
def initdb():
    from ..services.db import create_db_and_tables
    create_db_and_tables()
    return {"message": "Database and tables created"}


@router.get("/")
def hello():
    return {"message": "Hello, World!"}
