from enum import Enum

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"

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

class MemeBase:
    def convert_to_object(self, media_url: str, media_type: str, source: str, title: str = ""):
        return Meme(
            title=title,
            media_url=media_url,
            media_type=media_type,
            source=source
        )