![Image](https://graph.org/file/9901c2070cea11d1aa194.jpg)

## WAIFU & HUSBANDO CATCHER 


![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)<br> [![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)<br>
[![Support Group!](https://img.shields.io/badge/Join%20Group-↗-green)](https://t.me/collect_em_support)


_**Available On Telegram As 
[Collect Em all](https://t.me/Collect_em_AllBot) and**_
_Ask for Help in our [Support Chat](https://t.me/Collect_em_support)_

## About The Repository
● This is an Open Source Implementation of Character Catcher Bot for Telegram
- For Example, Grab/Hunt/Protecc/Collect etc.. These Types of Bot You must have seen it on your telegram groups..
- This bot sends characters in group after every 100 Messages Of Groups Then any user can Guess that character's Name Using /guess Command.

- Now you can also deploy this type of bot. Using our source, we've used Python-Telegram-Bot V20.6 and Also lil bit Pyrogram. Enjoy!

## HOW TO UPLOAD CHARACTERS?

Format: 
```
/upload img_url character-name anime-name rarity-number
```
#### Example: 
```
/upload Img_url muzan-kibutsuji Demon-slayer 3
```



use Rarity Number accordingly rarity Map

| Number | Rarity     |
| ------ | -----------|
| 1 | ⚪️ Common   |
| 2 | 🟣 Rare     |
| 3 | 🟡 Legendary|
| 4 | 🟢 Medium   |


## USER COMMANDS
- `/guess` - Guess the character
- `/fav` - Add a character to favorites
- `/trade` - Trade a character with another user
- `/gift` - Gift a character to another user
- `/collection` - Boast your harem collection
- `/topgroups` - List the groups with biggest harem (globally)
- `/top` - List the users with biggest harem (globally)
- `/ctop` - List the users with biggest harem (current chat)
- `/changetime` - Change the frequency of character spawn
  
## SUDO USER COMMANDS..
- `/upload` - Add a new character to the database 
- `/delete` - Delete a character from the database 
- `/update` - Update stats of a character in the database 

## OWNER COMMANDS
- `/ping` - Pings the bot and sends a response
- `/stats` - Lists number or groups and users
- `/list` - Sends a document with list of all users that used the bot
- `/groups` - Sends a document with list of all groups that the bot has been in

## DEPLOYMENT METHODS

### Heroku
- Fork The Repository
- Go to [`config.py`](./shivu/config.py)
- Fill the All variables and Go to heroku. and deploy Your forked Repository

### Local Deploy/VPS
- Fill variables in [`config.py`](./shivu/config.py) 
- Open your VPS terminal (we're using Debian based) and run the following:
```bash
sudo apt-get update && sudo apt-get upgrade -y           

sudo apt-get install python3-pip -y          
sudo pip3 install -U pip

git clone https://github.com/<YourUsername>/WAIFU-HUSBANDO-CATCHER && cd WAIFU-HUSBANDO-CATCHER

pip3 install -U -r requirements.txt          

sudo apt install tmux && tmux          
python3 -m shivu
```       
 
## License
The Source is licensed under MIT, and hence comes with no Warranty whatsoever.

## Appreciation
If you appreciate this Code, make sure to star ✨ the repository.

## Developer Suggestions 
- Don't Use heroku. Deploy on Heroku is just for testing. Otherwise Bot's Inline will Work Too Slow.
- Use a reliable VPS provider
