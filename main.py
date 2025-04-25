from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from algorithm import EngineerverseAlgorithm

# Configuration
SERVICE_DID = "did:web:cayyus-bskyfeed-gen.onrender.com"  
SERVICE_HANDLE = "cayyus-bskyfeed-gen.onrender.com"
FEED_NAME = "Engineerverse by Cayyus"

app = FastAPI()

@app.get("/xrpc/app.bsky.feed.describeFeedGenerator")
async def describe_feed_generator():
    {
        "did": SERVICE_DID,
        "feeds": [
            {
            "uri": "at://{SERVICE_DID}/app.bsky.feed.generator/Engineerverse-by-Cayyus",
            "displayName": FEED_NAME,
            "description": "Includes engineering content, programming and software development and other science and math related stuff"
            }
        ]
    }

@app.get("/.well-known/did.json")
async def serve_did():
    return FileResponse("did.json", media_type="application/json")

@app.get("/xrpc/app.bsky.feed.getFeedSkeleton")
async def get_feed_skeleton(feed: str, limit: int = 20, cursor: str = None):
    algo = EngineerverseAlgorithm()
    algo.authenticate()

    skip = 0
    if cursor:
        skip = int(cursor)
    
    # Example: Find posts with #python hashtag
    search_results = []
    
    try:
        query = "#python"
        posts = algo.search_posts(query, limit)
        
        for post in posts:
            search_results.append(post.uri)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")
    
    # Format response according to protocol
    feed_items = [{"post": uri} for uri in search_results[:limit]]
    
    next_cursor = str(skip + limit) if len(search_results) >= limit else None
    
    response = {
        "feed": feed_items
    }
    
    if next_cursor:
        response["cursor"] = next_cursor
        
    return response
    
    
