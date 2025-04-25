from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/xrpc/app.bsky.feed.describeFeedGenerator")
async def describe_feed_generator():
    return {
        "did": "did:web:cayyus-bskyfeed-gen.onrender.com",
        "feeds": [
            {
            "uri": "at://did:web:cayyus-bskyfeed-gen.onrender.com/app.bsky.feed.generator/my-feed",
            "displayName": "Engineerverse by Cayyus"
            }
        ]
    }


@app.get("/.well-known/did.json")
async def serve_did():
    return FileResponse("did.json", media_type="application/json")
