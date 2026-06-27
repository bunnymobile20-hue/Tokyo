from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

class OIRewriteMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/oi/"):
            scope["path"] = "/" + scope["path"][4:]
            if "raw_path" in scope:
                scope["raw_path"] = scope["path"].encode("ascii")
        await self.app(scope, receive, send)

app.add_middleware(OIRewriteMiddleware)

@app.get("/v1/models/pull")
async def pull():
    return {"status": "success"}

client = TestClient(app)
print(client.get("/oi/v1/models/pull").json())
