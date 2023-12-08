import os
from dotenv import load_dotenv

env = load_dotenv("config.env")

if env:
    OWNER_ID = os.environ.get("OWNER_ID")
    sudo_users = list(map(int, os.environ.get("sudo_users", "").split()))
    GROUP_ID = os.environ.get("GROUP_ID")
    TOKEN = os.environ.get("TOKEN")
    mongo_url = os.environ.get("MONGODB_URL")
    if os.environ.get("PHOTO_URL") != None:
        PHOTO_URL = os.environ.get("PHOTO_URL") 
    else:
        PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT")
    UPDATE_CHAT = os.environ.get("UPDATE_CHAT")
    BOT_USERNAME = os.environ.get("BOT_USERNAME")
    CHARA_CHANNEL_ID = os.environ.get("CHARA_CHANNEL_ID")
    api_id = os.environ.get("api_id")
    api_hash = os.environ.get("api_hash")
else:
    OWNER_ID = 6765826972
    sudo_users = ["6765826972", "6046482147"]
    GROUP_ID = -100
    TOKEN = ""
    mongo_url = "mongodb://localhost:27017/"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "Collect_em_support"
    UPDATE_CHAT = "Collect_em_support"
    BOT_USERNAME = "Collect_Em_AllBot"
    CHARA_CHANNEL_ID = -100
    api_id = 123
    api_hash = ""