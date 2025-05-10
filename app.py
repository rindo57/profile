
import requests
import time
import os
from pyrogram import Client

# Replace with your Telegram API credentials
API_ID =10247139   # your api_id
API_HASH = "96b46175824223a33737657ab943fd6a"

# Temporary image path
IMG_PATH = "temp_profile.jpg"

app = Client("auto_profile_pic_session", api_id=API_ID, api_hash=API_HASH)

def download_image(url: str, path: str):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download image, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Download error: {e}")
        return False

with app:
    print("Logged in as", app.get_me().first_name)
    while True:
        print("Fetching new profile picture...")
        if download_image("https://pic.re/image/", IMG_PATH):
            try:
                app.set_profile_photo(photo=IMG_PATH)
                print("✅ Profile photo updated successfully.")
            except Exception as e:
                print("❌ Error setting profile photo:", e)
        else:
            print("❌ Failed to download new image.")

        # Wait for 60 seconds
        time.sleep(60)
