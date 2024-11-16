from fastapi import FastAPI

from .routers import gs, hello, request

app = FastAPI()

app.include_router(gs.router, prefix="/api/v1")
app.include_router(hello.router, prefix="/api/v1")
app.include_router(request.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
