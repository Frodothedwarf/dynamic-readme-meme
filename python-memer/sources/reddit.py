import os
import praw
from sources.base import MemeBase

class RedditMeme(MemeBase):
    def __init__(self):
        self.reddit_client = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            user_agent=os.environ.get("REDDIT_USER_AGENT"),
        )

    def fetch_meme(self, subreddit: str):
        top_posts = self.reddit_client.subreddit(subreddit).top(time_filter="day")
        selected_post = None

        for post in top_posts:
            post = self.reddit_client.submission(post)

            if post.over_18 is False and post.url.startswith("https://i.redd.it"):
                selected_post = post
                break

        if selected_post is None:
            return None

        return self.convert_to_object(
            title=selected_post.title,
            media_url=selected_post.url,
            media_type="image",
            source=f"Reddit r/{subreddit}"
        )
