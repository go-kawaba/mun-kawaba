import traceback

import discord
from discord.ext import bridge, commands
from discord.utils import escape_markdown

import config

from .logger import log
from .morphemes import parse_sentence
from .words import kw_en

bot = bridge.Bot(command_prefix="/", intents=discord.Intents(messages=True))

### Commands


@bot.bridge_command(
    description="Provides a naive gloss of a kawaba sentence.",
    guild_ids=config.TEST_GUILDS,
)
async def gloss(ctx: commands.Context, *, sentence: str):
    words = parse_sentence(sentence)

    # Concatenating strings with the results we get from gloss_compound
    reply = ""
    errors = ""

    for word in words:
        if not word.non_word:
            try:
                reply += "-".join([kw_en[morpheme] for morpheme in word.morphemes])
            except KeyError as e:
                # If the compound is not present in the dictionary (should be impossible with regex?)
                reply += "???"
                errors += f"\nInvalid morpheme `{e.args[0]}`."
        else:
            reply += word.content
        reply += " "

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


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError):
        log.exception(
            f"""Exception from {ctx.command.qualified_name}!\n
                {"".join(traceback.format_exception(
                    type(error), error, error.__traceback__
                ))}"""
        )

        await ctx.send(
            f"""Exception from {ctx.command.qualified_name}!\n
            ```{escape_markdown("".join(
                    traceback.format_exception(
                        type(error), error, error.__traceback__
                    )
                )
             )}```"""
        )
