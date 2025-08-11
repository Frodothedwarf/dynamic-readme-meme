import re
import unicodedata
from datetime import datetime
from enum import Enum
from pathlib import Path

from image.downloader import download_image
from image.generator import add_title_above_file


class MediaType(Enum):
    """
    Should contain all possible media types that can be downloaded from all sources.
    Value should be the extension.
    """

    IMAGE = ".png"
    GIF = ".gif"
    VIDEO = ".mp4"
    UNKNOWN = "unknown"


class Meme:
    """
    Meme class that contains all default settings for the meme.
    """

    title: str = ""
    media_url: str
    source: str

    media_type: MediaType

    def __init__(self, media_url: str, media_type: str, source: str, title: str = ""):
        self.title = title
        self.media_url = media_url
        self.media_type = MediaType(media_type)
        self.source = source

    def __str__(self) -> str:
        return f"Meme | {self.title} | {self.source}"

    def prepare_title_for_path(self, title):
        title = unicodedata.normalize("NFKD", title)
        title = title.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]", "", title.lower())

    def get_extension(self) -> str:
        """
        Should be able to get the extension of the media.
        """
        return self.media_type.value

    def create_path(self, path: str) -> None:
        """
        Creates the path for the media.
        """

        path = path.split("/")
        path.pop()
        path = "/".join(path)

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

    def download_image(self, og_path: str, edited_path: str) -> str:
        """
        Creates both og path and edited path, and downloads the media + edits with the title on top.
        """

        self.create_path(og_path)
        self.create_path(edited_path)

        image = download_image(self.media_url, og_path)
        if image is None:
            return None

        add_title_above_file(image, self.title, edited_path)

    def download_image_and_convert(self):
        """
        Base function for downloading the media and converts it.
        """

        image_extension = self.get_extension()
        path_title = self.prepare_title_for_path(self.title)

        og_path = f"./memes/{self.source}/originals/{path_title}{datetime.today().strftime('%Y%m%d')}{image_extension}"
        edited_path = f"./memes/{self.source}/picked/todays_{image_extension.replace('.', '')}{image_extension}"

        self.download_image(og_path, edited_path)


class MemeBase:
    """
    Base class for sources, contains all functions that should be available to the function.
    """

    def convert_to_object(
        self, media_url: str, media_type: str, source: str, title: str = ""
    ):
        """
        Helper function for converting the media into a meme class.
        """

        return Meme(
            title=title, media_url=media_url, media_type=media_type, source=source
        )

    def fetch_and_download_memes(self):
        """
        Helper function for downloading the meme and in the way the source requires, and calls `donwload_image_and_convert()` from the Meme class.
        """
        raise NotImplementedError
