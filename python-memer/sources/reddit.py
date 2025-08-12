import logging
import os

import praw
from praw.models import Submission
from sources.base import MediaType, Meme, MemeBase


class RedditMeme(MemeBase):
    SUBREDDITS = []
    MEDIA_TYPES = []

    def __init__(self):
        self.SUBREDDITS = [
            subreddit.strip()
            for subreddit in os.environ.get("REDDIT_SUBREDDITS").split(",")
        ]
        self.MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]

        logging.debug(
            f"Reddit Source: Fetching memes from subreddits; {self.SUBREDDITS}"
        )
        logging.debug(f"Reddit Source: Allowed MEDIA_TYPES; {self.MEDIA_TYPES}")

        self.reddit_client = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            user_agent=os.environ.get("REDDIT_USER_AGENT"),
        )

    def __str__(self):
        return "Reddit"

    def get_media_type(self, post: Submission) -> MediaType:
        if (
            post.url.endswith(".jpg")
            or post.url.endswith(".jpeg")
            or post.url.endswith(".png")
        ):
            return MediaType.IMAGE
        elif post.url.endswith(".gif"):
            return MediaType.GIF
        else:
            return MediaType.UNKNOWN

    def fetch_meme(self, subreddit: str, time_filter: str) -> list[Meme]:
        top_posts = self.reddit_client.subreddit(subreddit).top(
            time_filter=time_filter, limit=500
        )
        selected_posts = []

        for media_type in self.MEDIA_TYPES:
            selected_post = None

            for post in top_posts:
                post = self.reddit_client.submission(post)
                post_media_type = self.get_media_type(post)

                if post.over_18 is False and post_media_type == media_type:
                    selected_post = post
                    break

            if selected_post is not None:
                selected_posts.append(selected_post)
                continue

        converted_posts = []
        for post in selected_posts:
            converted_posts.append(
                self.convert_to_object(
                    title=post.title,
                    media_url=post.url,
                    media_type=self.get_media_type(post),
                    source=f"reddit/{subreddit}",
                )
            )

        return converted_posts

    def fetch_and_download_memes(self) -> None:
        for subreddit in self.SUBREDDITS:
            logging.info(f"⛏️ Looking into {subreddit}")
            memes = self.fetch_meme(subreddit, "day")

            logging.info(f"📚 Found {len(memes)} memes in {subreddit}")
            for meme in memes:
                meme.download_image_and_convert()
