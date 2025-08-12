import requests
from ..base import USER_AGENT_HEADERS


def download_image(url: str, str_path: str):
    """
    Function for downloading the image from a url.
    Supports the normal .jpeg, .jpg, .png, .gif urls.
    """

    image_response = requests.get(url, headers=USER_AGENT_HEADERS)
    if not image_response.ok:
        return None

    with open(str_path, "wb") as f:
        f.write(image_response.content)

    return str_path
