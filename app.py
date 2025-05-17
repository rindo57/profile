import requests
import time
import os
import asyncio
from pyrogram import Client
from PIL import Image, ImageOps
from pyrogram.errors import FloodWait

# Replace with your Telegram API credentials
API_ID = 10247139  # your api_id
API_HASH = "96b46175824223a33737657ab943fd6a"

IMG_PATH = "temp_profile.jpg"
IMAGE_API_URL = "https://any-anime-api.vercel.app/v1/anime/png/1"

app = Client("auto_profile_pic_session", api_id=API_ID, api_hash=API_HASH)

def get_png_image_url():
    try:
        response = requests.get(IMAGE_API_URL)
        data = response.json()
        return data["images"][0]
    except Exception as e:
        print("❌ Failed to fetch image URL:", e)
        return None

def download_and_prepare_image(image_url, path, size=(512, 512)):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            print(f"❌ Failed to download image, status code: {response.status_code}")
            return False

        with open(path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        img = Image.open(path).convert("RGB")
        img = ImageOps.fit(img, size, Image.LANCZOS, centering=(0.5, 0.5))
        img.save(path, "JPEG")
        return True
    except Exception as e:
        print("❌ Image processing error:", e)
        return False

async def update_name_based_on_status():
    while True:
        try:
            me = await app.get_me()
            current_name = me.first_name
            user = await app.get_users(me.id)
            status = user.status
            
            new_name = "Ken 🟢" if status == "online" else "Ken 🔴"
            
            if current_name != new_name:
                try:
                    await app.update_profile(first_name=new_name)
                    print(f"✅ Name updated to: {new_name} (Status: {status})")
                except FloodWait as e:
                    print(f"⚠️ Flood wait: {e.x} seconds")
                    await asyncio.sleep(e.x)
                except Exception as e:
                    print(f"❌ Error updating name: {e}")
        except Exception as e:
            print(f"❌ Error checking status: {e}")
        
        await asyncio.sleep(10)  # Check every 10 seconds

async def update_profile_picture():
    while True:
        print("🔄 Fetching new PNG anime image...")
        image_url = get_png_image_url()

        if image_url and download_and_prepare_image(image_url, IMG_PATH):
            try:
                await app.set_profile_photo(photo=IMG_PATH)
                print("✅ Profile picture updated.")
            except FloodWait as e:
                print(f"⚠️ Flood wait: {e.x} seconds")
                await asyncio.sleep(e.x)
            except Exception as e:
                print("❌ Telegram error:", e)
        else:
            print("❌ Failed to update profile picture.")

        await asyncio.sleep(900)  # Wait for 15 minutes (900 seconds)

async def main():
    await app.start()
    print("✅ Logged in as", (await app.get_me()).first_name)
    
    # Create tasks for both functions
    status_task = asyncio.create_task(update_name_based_on_status())
    pp_task = asyncio.create_task(update_profile_picture())
    
    # Wait for both tasks to complete (they won't, since they're infinite loops)
    await asyncio.gather(status_task, pp_task)

# Run the main function
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n👋 Stopping the bot...")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    if app.is_connected:
        app.stop()
    print("✅ Bot stopped successfully")
