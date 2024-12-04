import requests
from dotenv import load_dotenv
from config import Config

load_dotenv()

IMGUR_CLIENT_ID = Config.IMGUR_CLIENT_ID

def upload_image_to_imgur(image_file):
    imgur_url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    response = requests.post(imgur_url, headers=headers, files={"image": image_file})

    if response.status_code != 200:
        raise Exception("Failed to upload image to Imgur.")

    return response.json()["data"]["link"], response.json()["data"]["deletehash"]

def delete_image_from_imgur(delete_hash):
    imgur_url = f"https://api.imgur.com/3/image/{delete_hash}"
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    response = requests.delete(imgur_url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to delete image from Imgur.")