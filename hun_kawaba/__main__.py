import os

import discord
from dotenv import load_dotenv

from .words import kw_en, kw_tr

kw_words = kw_en.keys()

start_consonants = "ptkbdgfscljwhm"


def split_compound(compound):
    pieces = []
    piece_start_index = 0
    for i in range(1, len(compound)):
        if compound[i] in start_consonants + "'":
            if compound[piece_start_index] == "'":
                piece_start_index += 1
            pieces.append(compound[piece_start_index:i])
            piece_start_index = i
    pieces.append(compound[piece_start_index:])
    return pieces


def gloss_compound(compound):
    if compound[0] == "'":
        return "*" + compound + "*"
    else:
        pieces = split_compound(compound)
        return "-".join([kw_en[i] for i in pieces])


info = """Hi, I am **hun kawaba**, a discord bot for the kawaba language.\n\n> Provide a naive gloss of a kawaba sentence:  `-g [kawaba sentence]`\n\n> Search for a word: `-s [word]` (unfinished)\n\n> Show you this message: `-i` or `-info`"""


client = discord.Client()


@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    content = (
        message.content.replace("’", "'")
        .replace("‘", "'")
        .replace(",", "")
        .replace(".", "")
    )
    if message.author == client.user:
        return

    if message.content.startswith("-g"):
        split = content.split(" ")
        reply = ""
        for i in split[1:]:
            try:
                reply = reply + " " + gloss_compound(i)
            except Exception:
                reply = reply + " " + "???"
                await message.channel.send("I don't know the word `" + i + "`.")
        await message.channel.send("> " + reply)

    if content.startswith("-s"):
        for i in content.split(" ")[1:]:
            await message.channel.send(kw_tr[i])

    if content.startswith("-i"):
        await message.channel.send(info)


load_dotenv()

client.run(os.getenv("TOKEN"))
