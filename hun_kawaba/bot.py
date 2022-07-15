from typing import List

import discord
from discord.ext import bridge, commands

import config

from .logger import log
from .words import kw_en

bot = bridge.Bot(command_prefix="/", intents=discord.Intents(messages=True))

### Commands


@bot.bridge_command(
    description="Provides a naive gloss of a kawaba sentence.",
    guild_ids=config.TEST_GUILDS,
)
async def gloss(ctx: commands.Context, *, arg: str):
    # I kept getting an error when trying to use *args here so we have to do this :(
    content = arg.split(" ")

    compounds = []

    for arg in content:
        compounds.append(
            # Getting rid of unnecessary characters and fixing mistakes
            arg.replace("’", "'")
            .replace("‘", "'")
            .replace(",", "")
            .replace(".", "")
        )

    # Concatenating strings with the results we get from gloss_compound
    reply = ""
    errors = ""

    for compound in compounds:
        try:
            reply += gloss_compound(compound) + " "
        except KeyError:
            # If the compound is not present in the dictionary
            reply += "??? "
            errors += f"\nInvalid word `{compound}`."

    await ctx.reply(f"> {reply}\n{errors}")


@bot.bridge_command(
    description="Sends information about this bot.", guild_ids=config.TEST_GUILDS
)
async def info(ctx: commands.Context):
    await ctx.reply(
        "Hi, I am **hun kawaba**, a Discord bot for the kawaba language.\n"
        "> `/gloss [sentence]` provides a naive gloss of a kawaba sentence.\n"
        "> `/search [word]` searches for a word (unimplemented)\n"
        "> `/info` shows you this message.\n"
    )


# search command not implemented yet


### Events


@bot.event
async def on_ready():
    log.info(f"Logged in successfully as {bot.user.name}#{bot.user.discriminator}")


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    # Removes the bot's message when the reaction is an X
    if reaction.message.author == bot.user:
        if reaction.emoji == "❌":
            await reaction.message.delete()


### Utilities


def split_compound(compound: str) -> List[str]:
    start_consonants = "ptkbdgfscljwhm"

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


def gloss_compound(compound: str):
    if compound == "'":
        return "*" + compound + "*"
    else:
        pieces = split_compound(compound)
        return "-".join([kw_en[i] for i in pieces])
