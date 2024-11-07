from fastapi import FastAPI

from .routers import gs_mock, hello

app = FastAPI()

app.include_router(gs_mock.router, prefix="/api/v1")
app.include_router(hello.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
