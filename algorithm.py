from atproto import Client, IdResolver, models

import os

class EngineerverseAlgorithm:
    def __init__(self, cursor, limit):
        self.client = Client()
        self.resolver = IdResolver()
        self.cursor = cursor
        self.limit = limit

    def authenticate(self):
        self.client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

    def publish_feed_generator(self):
        self.authenticate()
        
        # Create a properly formatted timestamp
        # Format: YYYY-MM-DDTHH:MM:SS.sssZ (note the 'Z' at the end indicating UTC)
        now = datetime.datetime.now(pytz.UTC)
        formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        # Trim microseconds to 3 decimal places
        formatted_time = formatted_time[:-4] + "Z"

        # Create the feed generator record
        self.client.com.atproto.repo.create_record({
            "repo": self.client.me.did,
            "collection": "app.bsky.feed.generator",
            "rkey": "Engineerverse",
            "record": {
                "$type": "app.bsky.feed.generator",
                "did": "did:web:cayyus-bskyfeed-gen.onrender.com",
                "displayName": "Engineerverse by Cayyus",
                "description": "Includes engineering content, programming and software development and other science and math related stuff",
                "createdAt": formatted_time
            }
        })

    def search_posts(self, q, limit=5):
        search = self.client.app.bsky.feed.search_posts(params={"q": q, "limit": limit})
        return search.posts

    def python_posts(self):
        self.authenticate()
        skip = 0
        if self.cursor:
            skip = int(self.cursor)
        
        # Example: Find posts with #python hashtag
        search_results = []
        
        try:
            queries = ["#engineering", "#programming", "#math", "#trump"]
            
            for query in queries:
                posts = self.search_posts(query, self.limit)
                
                for post in posts:
                    search_results.append(post.uri)
                
        except Exception as e:
            return 500, e
        
        # Format response according to protocol
        feed_items = [{"post": uri} for uri in search_results[:self.limit]]
        
        next_cursor = str(skip + self.limit) if len(search_results) >= self.limit else None
        
        response = {
            "feed": feed_items
        }
        
        if next_cursor:
            response["cursor"] = next_cursor
            
        return response
