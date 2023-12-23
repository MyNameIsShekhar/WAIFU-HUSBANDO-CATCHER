class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = ""
    sudo_users = "", ""
    GROUP_ID = -100
    TOKEN = ""
    mongo_url = ""
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "Collect_em_support"
    UPDATE_CHAT = "Collect_em_support"
    BOT_USERNAME = "Collect_Em_AllBot"
    CHARA_CHANNEL_ID = ""
    api_id = ""
    api_hash = ""

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
