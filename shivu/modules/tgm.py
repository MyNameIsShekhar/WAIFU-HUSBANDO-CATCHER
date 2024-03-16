import pyrogram 
from pyrogram import Client,filters,idle 
from telegraph import upload_file 
from shivu import shivuu
import os 
import io
from pyrogram.types import Message 


@shivuu.on_message(filters.command("tgm"))
async def graph(client:Client, message:Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("gib me smtg to generate graph.org ")
    if reply.media:
      try:
          x = await message.reply("Generating")
          path = await reply.download()
          semx = upload_file(path)
          for res in semx:
              url = "https://graph.org/" + res
          await x.edit(f'**Generated** \n({url}')
          os.remove(path)
      except Exception as e:
          await x.edit(f"Failed to generate {e}")
          os.remove(path) 
