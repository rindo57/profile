import os
import datetime
import requests

from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
API_ID = 10247139
API_HASH = "96b46175824223a33737657ab943fd6a"
OWNER = [7207726255]
app = Client(
    "rand_profile_pict",
    api_id=API_ID,
    api_hash=API_HASH
)

# Constants for Scheduler
HOUR = 22
MINUTE = 30
SECOND = 0
scheduler = AsyncIOScheduler()

def download_random_image():
    response = requests.get("https://picsum.photos/200/300", stream=True)
    if response.status_code == 200:
        with open("temp.jpg", "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return "temp.jpg"
    return None

def rand_command():
    current_time = datetime.datetime.utcnow()
    image_path = download_random_image()
    if image_path:
        app.set_profile_photo(photo=open(image_path, 'rb'))
        os.remove(image_path)
        print("Image modified on {}".format(current_time))
    else:
        print("Failed to fetch image.")

@app.on_message(filters.command("random") & filters.private & filters.user(Config.OWNER))
def manual_rand_command(client, message):
    current_time = datetime.datetime.utcnow()
    image_path = download_random_image()
    if image_path:
        app.set_profile_photo(photo=open(image_path, 'rb'))
        os.remove(image_path)
        print("Image modified on {}".format(current_time))
    else:
        print("Failed to fetch image.")

async def main():
    await app.start()  # Start Pyrogram client

    # Start scheduler after event loop is running
    scheduler.add_job(rand_command, 'interval', minutes=1)
    scheduler.start()

    print("Bot and scheduler started.")
    await idle()  # Keep the app running

from pyrogram.idle import idle

if __name__ == "__main__":
    asyncio.run(main())
