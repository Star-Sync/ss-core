from fastapi import FastAPI

from .routers import gs_mock, hello

app = FastAPI()

app.include_router(gs_mock.router)
app.include_router(hello.router)


@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
