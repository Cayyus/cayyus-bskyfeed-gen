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

    def curate_feed(self):
        self.authenticate()
        
        # Define our search queries
        queries = ["#engineering", "#programming", "#math", "#trump"]
        
        # Parse cursor if provided
        current_query_index = 0
        last_post_index = 0
        
        if self.cursor:
            try:
                # Decode cursor - assuming format "queryIndex:postIndex"
                cursor_parts = self.cursor.split(":")
                current_query_index = int(cursor_parts[0])
                last_post_index = int(cursor_parts[1])
            except (ValueError, IndexError):
                # If cursor parsing fails, start from beginning
                current_query_index = 0
                last_post_index = 0
        
        search_results = []
        next_cursor = None
        
        try:
            # Start from where we left off
            for i in range(current_query_index, len(queries)):
                query = queries[i]
                
                # Get posts for this query
                posts = self.search_posts(query, 25)  # Get more than needed to have buffer for next page
                
                # Skip posts we've already sent (only matters for the first query in this request)
                start_index = last_post_index if i == current_query_index else 0
                
                # Add posts to results
                for j in range(start_index, len(posts)):
                    search_results.append(posts[j].uri)
                    
                    # If we have enough posts, prepare cursor and break
                    if len(search_results) >= self.limit:
                        # Set cursor to continue from next post in current query
                        next_cursor = f"{i}:{j+1}"
                        break
                
                # If we've collected enough posts, break out of the query loop too
                if len(search_results) >= self.limit:
                    break
                    
                # If we've processed all posts in this query, move to next query
                if i < len(queries) - 1:
                    # Next query, starting from the beginning
                    next_cursor = f"{i+1}:0"
                
        except Exception as e:
            return 500, e
        
        # Format response according to protocol
        feed_items = [{"post": uri} for uri in search_results[:self.limit]]
        
        response = {
            "feed": feed_items
        }
        
        if next_cursor:
            response["cursor"] = next_cursor
            
        return response
