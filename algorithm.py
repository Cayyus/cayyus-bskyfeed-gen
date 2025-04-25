from atproto import Client, IdResolver, models

import os

class EngineerverseAlgorithm:
    def __init__(self):
        self.client = Client()
        self.resolver = IdResolver()

    def authenticate(self):
        self.client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))

    def search_posts(self, q, limit=5):
        search = self.client.app.bsky.feed.search_posts(params={"q": q, "limit": limit})
        return search.posts
