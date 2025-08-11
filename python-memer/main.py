from dotenv import load_dotenv
from sources.base import MediaType
from sources.programmerhumor import ProgrammerHumorMeme
from sources.reddit import RedditMeme

load_dotenv()

REDDIT_SUBREDDITS = [
    "blunderyears",
    "BreadStapledToTrees",
    "cringepics",
    "CrappyDesign",
    "dankmemes",
    "disneyvacation",
    "facepalm",
    "funny",
    "gifs",
    "holdmybeer",
    "iamverysmart",
    "Jokes",
    "memes",
    "MildlyVandalised",
    "nocontextpics",
    "PerfectTiming",
    "ProgrammerHumor",
    "programminghumor",
    "trippinthroughtime",
]

REDDIT_MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]


def main(*args, **kwargs):
    """
    The main function that should contain all sources, and download memes for all sources.
    """

    programmer_humor = ProgrammerHumorMeme()
    reddit = RedditMeme(subreddits=REDDIT_SUBREDDITS, media_types=REDDIT_MEDIA_TYPES)

    reddit.fetch_and_download_memes()
    programmer_humor.fetch_and_download_memes()


if __name__ == "__main__":
    main()
