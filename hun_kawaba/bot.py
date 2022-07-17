import traceback

import discord
from discord.ext import bridge, commands, pages
from discord.utils import escape_markdown
from thefuzz import process

import config

from .logger import log
from .morphemes import parse_sentence
from .words import kw_en, kw_tr

bot = bridge.Bot(command_prefix="/", intents=discord.Intents(messages=True))

### Commands


@bot.bridge_command(
    description="Provides a naive gloss of a kawaba sentence.",
    guild_ids=config.TEST_GUILDS,
)
async def gloss(ctx: bridge.BridgeContext, *, sentence: str):
    words = parse_sentence(sentence)

    # Concatenating strings with the results we get from gloss_compound
    reply = ""
    errors = ""

    for word in words:
        if not word.loan_word and not word.invalid_word:
            try:
                reply += "-".join([kw_en[morpheme] for morpheme in word.morphemes])
            except KeyError as e:
                # If the compound is not present in the dictionary
                # (should be impossible with the regex?)
                reply += "???"
                errors += f"\nInvalid morpheme `{e.args[0]}`."
        else:
            reply += word.content

        if word.invalid_word:
            if not word.loan_word:
                errors += f"\nInvalid word `{word.content}`."

        reply += " "

    await ctx.reply(f"> {reply}\n{errors}")


@bot.bridge_command(description="Searches for a word.", guild_ids=config.TEST_GUILDS)
async def search(ctx: bridge.BridgeContext, text: str):
    matches: list[tuple[str, int]] = process.extractBests(
        text, kw_tr.keys(), score_cutoff=80, limit=50
    )

    if not matches:
        await ctx.reply(f"Could not find word `{text}`.")
        return

    page_template = f"__Found {len(matches)} results__\n"

    reply_pages: list[pages.Page] = []

    # Go through each match 5 at a time and add them as a page
    while matches:
        page = page_template
        for i in range(5):
            try:
                match = matches.pop(0)
                page += f"**{match[0]}** ({match[1]}%)\n> {kw_tr[match[0]]}\n"
            except IndexError:
                break

        reply_pages.append(pages.Page(page))

    # Create the paginator and send it
    paginator = pages.Paginator(reply_pages, show_indicator=True, author_check=True)
    await paginator.respond(ctx)


@bot.bridge_command(
    description="Sends information about this bot.", guild_ids=config.TEST_GUILDS
)
async def info(ctx: bridge.BridgeContext):
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
