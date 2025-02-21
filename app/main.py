from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from pygelf import GelfTcpHandler
from .routers import gs, hello, request, ground_station
import logging

logger = logging.getLogger()

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
app.include_router(request.router, prefix="/api/v1")  # type: ignore
app.include_router(ground_station.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    logger.info("Root endpoint")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Star Sync API")
