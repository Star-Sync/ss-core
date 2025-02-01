from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler, GelfHttpHandler, GelfHttpsHandler
import logging
import http.client
import json

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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(GelfUdpHandler(host='localhost', port=12201))

def test():
    conn = http.client.HTTPConnection("localhost", 12201)
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "version": "1.1",
        "host": "example.org",
        "short_message": "A short message",
        "level": 5,
        "_some_info": "foo"
    }

    json_data = json.dumps(data)
    conn.request("POST", "/gelf", body=json_data, headers=headers)
    response = conn.getresponse()

    print(response.status)
    print(response.read().decode())

@app.get("/")
async def root():
    test()
    return {"message": "Hello FastAPI!"}
