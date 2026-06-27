from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import httpx

app = FastAPI()

@app.middleware("http")
async def rewrite_oi_prefix(request: Request, call_next):
    if request.url.path.startswith("/oi/"):
        request.scope["path"] = request.url.path[3:]
    return await call_next(request)

@app.post("/v1/models/pull")
async def pull():
    return {"status": "success"}

async def run_test():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/oi/v1/models/pull")
        print("Response:", resp.json())

if __name__ == "__main__":
    asyncio.run(run_test())
