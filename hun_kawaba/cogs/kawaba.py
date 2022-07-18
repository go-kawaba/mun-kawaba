import aiohttp
from discord.ext import bridge, commands, pages, tasks
from thefuzz import process

import config

from ..logger import log
from ..morphemes import parse_sentence
from ..words import morpheme_list


class KawabaCog(commands.Cog):
    def __init__(self, bot: bridge.Bot):
        self.bot = bot
        self.word_data = {}
        self.populate_word_data.start()

    @tasks.loop(hours=1)
    async def populate_word_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://go-kawaba.github.io/diomawe/data.json"
            ) as response:
                response.raise_for_status()
                self.word_data = await response.json()

                log.info("Received diomawe JSON data!")
                log.debug(self.word_data)

    @bridge.bridge_command(
        description="Provides a naive gloss of a kawaba sentence.",
        guild_ids=config.TEST_GUILDS,
    )
    async def gloss(self, ctx: bridge.BridgeContext, *, sentence: str):
        words = parse_sentence(sentence)

        # Concatenating strings with the results we get from gloss_compound
        reply = ""
        errors = ""

        for word in words:
            if not word.loan_word and not word.invalid_word:
                try:
                    reply += "-".join(
                        [morpheme_list[morpheme] for morpheme in word.morphemes]
                    )
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

    @bridge.bridge_command(
        description="Searches for a word.", guild_ids=config.TEST_GUILDS
    )
    async def search(self, ctx: bridge.BridgeContext, text: str):
        baja = self.word_data["baja"]
        jacon = self.word_data["jacon"]

        # All words combined into one dictionary
        jace = baja | jacon

        matches: list[tuple[str, int]] = process.extractBests(
            text, jace.keys(), score_cutoff=80, limit=50
        )

        if not matches:
            await ctx.reply(f"Could not find word `{text}`.")
            return

        page_template = f"__Found {len(matches)} results__\n"

        reply_pages: list[pages.Page] = []

        # Go through each match 5 at a time and add them as a page
        while matches:
            page = page_template
            for _ in range(5):
                try:
                    match = matches.pop(0)
                    definition = jace[match[0]]["Definition"]
                    page += f"**{match[0]}** ({match[1]}%)\n> {definition}\n"
                except IndexError:
                    break

            reply_pages.append(pages.Page(page))

        # Create the paginator and send it
        paginator = pages.Paginator(reply_pages, show_indicator=True, author_check=True)
        await paginator.respond(ctx)

    @bridge.bridge_command(
        description="Sends information about this bot.", guild_ids=config.TEST_GUILDS
    )
    async def info(self, ctx: bridge.BridgeContext):
        await ctx.reply(
            "Hi, I am **hun kawaba**, a Discord bot for the kawaba language.\n"
            "> `/gloss [sentence]` provides a naive gloss of a kawaba sentence.\n"
            "> `/search [word]` fuzzy searches for a word.\n"
            "> `/info` shows you this message.\n"
        )
