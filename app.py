
import requests
import time
import os
from pyrogram import Client
from PIL import Image
# Replace with your Telegram API credentials
API_ID =10247139   # your api_id
API_HASH = "96b46175824223a33737657ab943fd6a"

# Temporary image path
IMG_PATH = "temp_profile.jpg"

app = Client("auto_profile_pic_session", api_id=API_ID, api_hash=API_HASH)

def download_and_resize_image(url: str, path: str, size=(512, 512)):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)

            img = Image.open(path)
            img = img.convert("RGB")
            img = img.resize(size, Image.LANCZOS)
            img.save(path, "JPEG")
            return True
        else:
            print(f"Failed to download image, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Image processing error: {e}")
        return False

with app:
    print("Logged in as", app.get_me().first_name)
    while True:
        print("Fetching and resizing new profile picture...")
        if download_and_resize_image("https://pic.re/image/", IMG_PATH):
            try:
                app.set_profile_photo(photo=IMG_PATH)
                print("✅ Profile photo updated successfully.")
            except Exception as e:
                print("❌ Error setting profile photo:", e)
        else:
            print("❌ Failed to process new image.")

        time.sleep(60)
