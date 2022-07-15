from config import TOKEN

from .bot import bot
from .logger import setup_logging


def main():
    setup_logging()

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
