class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "5483829443"
    sudo_users = "5483829443", "5483829443"
    GROUP_ID = "-1002025818174"
    TOKEN = "6807323573:AAF5PBWZ96QqCsveozwXPxgHAA3BpibU9FA"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "Your_waifu_Supports"
    UPDATE_CHAT = "Your_waifu_Supports"
    BOT_USERNAME = "@Character_CatcherXBot"
    CHARA_CHANNEL_ID = "-1002079290892"
    api_id = "28285623"
    api_hash = "2babec66ef08b3b8e1d49ce7bcf0e867"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
