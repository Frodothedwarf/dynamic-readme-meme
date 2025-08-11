from enum import Enum
from pathlib import Path
from image.downloader import download_image
from image.generator import add_title_above_file

class MediaType(Enum):
    IMAGE = ".png"
    GIF = ".gif"
    VIDEO = ".mp4"
    UNKNOWN = "unknown"

class Meme:
    title: str = ""
    media_url: str
    source: str

    media_type: MediaType

    def __init__(self, media_url: str, media_type: str, source: str, title: str = ""):
        self.title = title
        self.media_url = media_url
        self.media_type = MediaType(media_type)
        self.source = source
    
    def __str__(self):
        return f"Meme | {self.title} | {self.source}"

    def get_extension(self) -> str:
        return self.media_type.value
    
    def create_path(self, path: str) -> None:
        path = path.split("/")
        path.pop()
        path = "/".join(path)

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

    def download_image(self, og_path: str, edited_path: str) -> str:
        self.create_path(og_path)
        self.create_path(edited_path)

        image = download_image(self.media_url, og_path)
        if image is None:
            return None
        
        add_title_above_file(image, self.title, edited_path)

class MemeBase:
    def convert_to_object(self, media_url: str, media_type: str, source: str, title: str = ""):
        return Meme(
            title=title,
            media_url=media_url,
            media_type=media_type,
            source=source
        )