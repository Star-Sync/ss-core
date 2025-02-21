from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/hello",
    tags=["hello"],
)


@router.get("/")
def hello():
    return {"message": "Hello, World!"}


@router.get(
    "/initdb",
    summary="Initialize the database",
    response_description="Database and tables created",
)
def initdb():
    from ..services.db import create_db_and_tables

    create_db_and_tables()
    return {"message": "Database and tables created"}
