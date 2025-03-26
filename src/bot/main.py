from framecho.btk import Bot

from config import DISCORD_TOKEN


def main():
    bot = Bot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
