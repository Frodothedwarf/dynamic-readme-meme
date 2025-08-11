import requests
from base import USER_AGENT_HEADERS

def download_image(url: str, str_path: str):
    image_response = requests.get(url, headers=USER_AGENT_HEADERS)
    if not image_response.ok:
        return None

    with open(str_path, "wb") as f:
        f.write(image_response.content)

    return str_path