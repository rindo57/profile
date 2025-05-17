import requests
import asyncio
import time
from pyrogram import Client
from PIL import Image, ImageOps
from pyrogram.errors import FloodWait
from pyrogram.enums import UserStatus

# Telegram API credentials
API_ID = 10247139
API_HASH = "96b46175824223a33737657ab943fd6a"

IMG_PATH = "temp_profile.jpg"
IMAGE_API_URL = "https://any-anime-api.vercel.app/v1/anime/png/1"

class ProfileUpdater:
    def __init__(self):
        self.app = Client("auto_profile_pic_session", api_id=API_ID, api_hash=API_HASH)
        self.running = True
        self.last_pic_update = 0
        self.last_status = None

    def get_png_image_url(self):
        try:
            response = requests.get(IMAGE_API_URL)
            return response.json()["images"][0]
        except Exception as e:
            print(f"❌ Failed to fetch image URL: {e}")
            return None

    def download_and_prepare_image(self, image_url):
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code != 200:
                return False

            with open(IMG_PATH, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            img = Image.open(IMG_PATH).convert("RGB")
            img = ImageOps.fit(img, (512, 512), Image.LANCZOS)
            img.save(IMG_PATH, "JPEG")
            return True
        except Exception as e:
            print(f"❌ Image processing error: {e}")
            return False

    async def update_name(self):
        try:
            me = await self.app.get_me()
            user = await self.app.get_users(me.id)
            
            # Determine new status
            new_status = user.status
            new_name = "Ken 🟢" if new_status == UserStatus.ONLINE else "Ken 🟡"
            
            # Only update if status changed
            if new_status != self.last_status:
                await self.app.update_profile(first_name=new_name)
                print(f"✅ Name updated to: {new_name} (Status: {new_status})")
                self.last_status = new_status
                
        except FloodWait as e:
            print(f"⚠️ Flood wait: {e.x} seconds")
            await asyncio.sleep(e.x)
        except Exception as e:
            print(f"❌ Error updating name: {e}")

    async def update_profile_pic(self):
        print("🔄 Fetching new PNG anime image...")
        image_url = self.get_png_image_url()

        if image_url and self.download_and_prepare_image(image_url):
            try:
                await self.app.set_profile_photo(photo=IMG_PATH)
                print("✅ Profile picture updated.")
                self.last_pic_update = time.time()
            except FloodWait as e:
                print(f"⚠️ Flood wait: {e.x} seconds")
                await asyncio.sleep(e.x)
            except Exception as e:
                print(f"❌ Telegram error: {e}")
        else:
            print("❌ Failed to update profile picture.")

    async def run_updates(self):
        while self.running:
            try:
                # Update name based on status
                await self.update_name()
                
                # Update profile pic every 15 minutes (900 seconds)
                if time.time() - self.last_pic_update >= 900:
                    await self.update_profile_pic()
                
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ Update error: {e}")
                await asyncio.sleep(30)

    async def run(self):
        await self.app.start()
        me = await self.app.get_me()
        print(f"✅ Logged in as {me.first_name}")
        
        # Initialize status tracking
        user = await self.app.get_users(me.id)
        self.last_status = user.status
        
        try:
            # Initial profile pic update
            await self.update_profile_pic()
            
            # Start the update loop
            await self.run_updates()
        except KeyboardInterrupt:
            print("\n👋 Stopping the bot...")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            if await self.app.is_connected():
                await self.app.stop()
            print("✅ Bot stopped successfully")

async def main():
    updater = ProfileUpdater()
    await updater.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
