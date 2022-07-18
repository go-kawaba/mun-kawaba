import traceback

import discord
from discord.ext import bridge, commands
from discord.utils import escape_markdown

from .cogs.kawaba import KawabaCog
from .logger import log

bot = bridge.Bot(command_prefix="/", intents=discord.Intents(messages=True))

### Cogs

bot.add_cog(KawabaCog(bot))


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
