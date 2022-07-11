import os
import discord
from keep_alive import keep_alive
from dict import *

kw_words = kw_en.keys()

my_secret = os.environ['TOKEN']

start_consonants = 'ptkbdgfscljwhm'
def split_compound(compound):
    pieces = []
    piece_start_index = 0 
    for i in range(1, len(compound)):
        if compound[i] in start_consonants + '\'':
            if compound[piece_start_index] == '\'':
                piece_start_index += 1
            pieces.append(compound[piece_start_index:i])
            piece_start_index = i
    pieces.append(compound[piece_start_index:])
    return pieces

def gloss_compound(compound):
  if compound[0] == "'":
    return '*' + compound + '*'
  else:
    pieces = split_compound(compound)
    return '-'.join([kw_en[i] for i in pieces])

client = discord.Client()

@client.event
async def on_ready():
  print('we have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  content = message.content
  if message.author == client.user:
    return

  if message.content.startswith('-g'):
    split = content.split(' ')
    reply = ''
    for i in split[1:]:
      try:
        reply = reply + ' ' + gloss_compound(i)
      except:
        reply = reply + ' ' + "???"
        await message.channel.send("You used a word that I don't know, hence the '???'")
    await message.channel.send(reply)
  if content.startswith('-s'):
    for i in content.split(' ')[1:]:
      await message.channel.send(kw_tr[i])
  
      
keep_alive()
client.run(my_secret)

  