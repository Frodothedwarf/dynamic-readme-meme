from sources.reddit import RedditMeme
from image.downloader import download_image
from image.generator import add_title_above_file
from dotenv import load_dotenv

load_dotenv()

REDDIT_SUBREDDITS = [
    "ProgrammerHumor",
    "programminghumor",
    "funny",
    "memes",
    "dankmemes"
]

def main(*args, **kwargs):
    reddit = RedditMeme()

    for sub in REDDIT_SUBREDDITS:
        meme = reddit.fetch_meme(sub)
        pathTitle = meme.title.replace(" ", "")
        image = download_image(meme.media_url, f"./{pathTitle}.png")

        add_title_above_file(image, meme.title, f"{pathTitle}edited.png")



if __name__ == "__main__":
    main()