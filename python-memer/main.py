from sources.reddit import RedditMeme
from sources.programmerhumor import ProgrammerHumorMeme
from dotenv import load_dotenv
from sources.base import MediaType
from datetime import datetime
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

REDDIT_MEDIA_TYPES = [
    MediaType.IMAGE,
    MediaType.GIF
]

def main(*args, **kwargs):
    programmer_humor = ProgrammerHumorMeme()
    reddit = RedditMeme()

    for subreddit in REDDIT_SUBREDDITS:
        memes = reddit.fetch_meme(subreddit, "day", REDDIT_MEDIA_TYPES)

        for meme in memes:
            pathTitle = meme.title.replace(" ", "")
            
            meme_og_path = f"./memes/reddit/{subreddit}/originals/{pathTitle}{datetime.today().strftime('%Y%m%d')}{meme.get_extension()}"
            meme_edited_path = f"./memes/reddit/{subreddit}/picked/todays_{meme.get_extension().replace('.', '')}{meme.get_extension()}"
            
            meme.download_image(meme_og_path, meme_edited_path)

    programmer_humor_memes = programmer_humor.fetch_meme()
    for meme in programmer_humor_memes:
        pathTitle = meme.title.replace(" ", "")

        meme_og_path = f"./memes/programmerhumor/originals/{pathTitle}{datetime.today().strftime('%Y%m%d')}{meme.get_extension()}"
        meme_edited_path = f"./memes/programmerhumor/picked/todays_{meme.get_extension().replace('.', '')}{meme.get_extension()}"

        meme.download_image(meme_og_path, meme_edited_path)

if __name__ == "__main__":
    main()