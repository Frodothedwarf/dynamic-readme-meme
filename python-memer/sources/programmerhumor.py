import requests
from base import USER_AGENT_HEADERS
from bs4 import BeautifulSoup
from sources.base import MediaType, Meme, MemeBase


class ProgrammerHumorMeme(MemeBase):
    MEME_URL = "https://programmerhumor.io/hot"

    def fetch_meme(self) -> list[Meme]:
        response = requests.get(self.MEME_URL, headers=USER_AGENT_HEADERS)
        if not response.ok:
            return []

        soup = BeautifulSoup(response.content, features="html.parser")
        posts = soup.find("div", {"class": "posts"})
        post = posts.find("div", {"class": "post"})
        post_image = post.find("div", {"class": "post-image"})
        image = post_image.img
        image_src = image.attrs["src"]
        image_title = image.attrs["alt"]

        return [
            self.convert_to_object(
                image_src, MediaType.IMAGE, "programmerhumorio", image_title
            )
        ]

    def fetch_and_download_memes(self) -> None:
        programmer_humor_memes = self.fetch_meme()
        for meme in programmer_humor_memes:
            meme.download_image_and_convert()
