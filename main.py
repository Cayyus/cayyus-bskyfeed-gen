from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
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


@app.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(request: Request):
    params = request.query_params
    feed_id = params.get("feed")
    limit = int(params.get("limit", 10))
    cursor = params.get("cursor", None)

    # Dummy placeholder post URIs (not real posts)
    dummy_posts = [
        {"post": "at://did:example:bob/app.bsky.feed.post/fake1"},
        {"post": "at://did:example:alice/app.bsky.feed.post/fake2"},
    ]

    return JSONResponse({
        "feed": [],
        "cursor": None  # add pagination later
    })
