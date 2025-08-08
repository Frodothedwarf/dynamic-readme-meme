import requests

def download_image(url: str, path: str):
    image_response = requests.get(url)
    if not image_response.ok:
        return None
    
    with open(path, "wb") as f:
        f.write(image_response.content)

    return path