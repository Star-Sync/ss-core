from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import gs, hello, request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gs.router, prefix="/api/v1")
app.include_router(hello.router, prefix="/api/v1")
app.include_router(request.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
