from sources.base import MemeBase, MediaType, Meme
from bs4 import BeautifulSoup
import requests
from base import USER_AGENT_HEADERS

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
            self.convert_to_object(image_src, MediaType.IMAGE, "ProgrammerHumor.io", image_title)
        ]