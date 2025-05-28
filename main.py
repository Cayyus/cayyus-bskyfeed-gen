from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from algorithm import EngineerverseAlgorithm

# Configuration
SERVICE_DID = "did:web:cayyus-bskyfeed-gen.onrender.com"  # Your feed's DID
SERVICE_HANDLE = "cayyus-bskyfeed-gen.onrender.com"
FEED_NAME = "Engineerverse by Cayyus"

app = FastAPI()

@app.get("/xrpc/app.bsky.feed.describeFeedGenerator")
async def describe_feed_generator():
    return {
        "did": "did:web:cayyus-bskyfeed-gen.onrender.com",
        "feeds": [
            {
            "uri": "at://did:web:cayyus-bskyfeed-gen.onrender.com/app.bsky.feed.generator/Engineerverse-by-Cayyus",
            "displayName": FEED_NAME,
            "description": "Includes engineering content, programming and software development and other science and math related stuff"
            }
        ]
    }

@app.get("/.well-known/did.json")
async def serve_did():
    return FileResponse("did.json", media_type="application/json")

@app.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(feed: str, limit: int = 50, cursor: str = None):
    algo = EngineerverseAlgorithm(limit=limit, cursor=cursor)
    result = algo.curate_feed()

    if isinstance(result, tuple) and result[0] == 500:
        _, e = result
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

    return result
