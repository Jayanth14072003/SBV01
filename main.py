import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

api_id = config.get("credentials", "api_id")
api_hash = config.get("credentials", "api_hash")
bot_token = config.get("credentials", "bot_token")
SB_key = config.get("credentials", "pdisk_key")


# Select a server
def select_server():
    server_url = "https://streambits.net/api/upload/server"
    params = {"key": "749yn5bi434hvl9r22m"}
    response = requests.get(server_url, params=params)
    try:
        server_data = response.json()
        upload_url = server_data["result"]
        print(upload_url)
        return upload_url
    except ValueError:
        print("Error parsing server response JSON:", response.text)
        exit(1)


# Check if the file extension is supported
def is_supported_file(file_name):
    supported_extensions = (".mp4", ".mov", ".avi", ".mkv")
    return file_name.lower().endswith(supported_extensions)


# Step 2: Upload a file
async def handle_video(client: Client, message: Message):
    upload_url = select_server()

    if message.video or message.document:
        file_info = message.video or message.document
        file_path = await client.download_media(file_info)
        print(file_info)
        print(file_path)
        if not is_supported_file(file_path):
            return "Sorry, only video files (MP4, MOV, AVI, MKV) are supported. Please upload a video file."

        file_obj = open(file_path, 'r+b')
        upload_data = {
            "key": "749yn5bi434hvl9r22m",
            "file": (os.path.basename(file_path), file_obj),
            "fld_id": 0
        }
        response = requests.get(upload_url, params=upload_data)
        print(response)
        try:
            upload_result = response.json()[0]
            print(upload_result)
            file_code = upload_result["filecode"]
            file_url = f"https://streambits.net/{file_code}"
            return file_url
        except ValueError:
            print("Error parsing upload response JSON:", response.text)
            return "Error occurred during file upload."
        finally:
            if 'file_obj' in locals():
                # Close and delete the file
                file_obj.close()
                #os.remove(file_path)

    elif message.text:
        url = message.text.strip()
        if not url.startswith("http"):
            return "Invalid URL format. Please provide a valid URL."
        upload_url = "https://streambits.net/api/upload/url"
        params = {
            "key": "749yn5bi434hvl9r22m", 
            "url": url, 
            "fld_id": 0
            }

        response = requests.get(upload_url, params=params)
        try:
            upload_result = response.json()
            file_code = upload_result["result"]["filecode"]
            file_url = f"https://streambits.net/{file_code}"
            return file_url
        except ValueError:
            print("Error parsing upload response JSON:", response.text)
            return "Error occurred during file upload."
    else:
        return "Invalid file format or URL. Please send a video file or a valid URL."


app = Client("my_bot", api_id=3393749, api_hash="a15a5954a1db54952eebd08ea6c68b71", bot_token="5872747581:AAH7_XPCOCEVfbgUhepjJWlcOmj8wjDTjBk")

@app.on_message(filters.command("start"))
async def handle_start_command(client: Client, message: Message):
    instructions = (
        "Welcome to the File Upload Bot!\n\n"
        "Please send a video file or a remote URL to upload it to streambits.net.\n"
        "Only video files (MP4, MOV, AVI, MKV) are supported."
    )
    await message.reply_text(instructions)


@app.on_message(filters.video | filters.document | filters.text)
async def handle_message(client: Client, message: Message):
    if message.text and message.text.startswith("/"):
        # Ignore commands other than the start command
        return
    await message.reply_text(await handle_video(client, message), quote=True)


app.run()
