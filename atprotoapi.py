from atproto import Client
from atproto import IdResolver

import os

client = Client()
resolver = IdResolver()

client.login(os.environ.get("BLUESKY_USERNAME"), os.environ.get("BLUESKY_PASSWORD"))

search = client.app.bsky.feed.search_posts(params={"q": "Python", "limit": 20})
for post in search.posts:
    print(post.record.text)
