import argparse
import logging

from json import load
from sys import stdout
from base_bot import Bot

COGS_NAMES = [
    "cogs.astral.functions",
    "cogs.help.functions",
]


if __name__ == "__main__":

    logger: logging.Logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)

    FORMATTER = logging.Formatter(
        fmt="[%(asctime)s: %(levelname)s] [AstralLoader] %(message)s"
    )

    consoleHandler = logging.StreamHandler(stream=stdout)
    consoleHandler.setFormatter(FORMATTER)
    consoleHandler.setLevel(logging.INFO)

    logger.handlers = [consoleHandler]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug", help="enable debug and dev settings", action="store_true"
    )
    parser.add_argument("-c", "--config", type=str, help="config name in configs path")
    args = parser.parse_args()

    if args.config is not None:
        try:
            with open(f"./configs/{args.config}.json") as f:
                settings = load(f)
        except:
            logger.error("Unable to load config. Loads current")
            with open("./configs/astral_current.json") as f:
                settings = load(f)
    else:
        if not args.debug:
            with open("./configs/astral_current.json") as f:
                settings = load(f)

        else:
            with open("./configs/dev.json") as f:
                settings = load(f)

    if args.debug:
        debug = True

        logger.setLevel(logging.DEBUG)
        consoleHandler.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    else:
        debug = False

    logger.info(f"Token: {settings['token']}")
    logger.info(f"Database link: {settings['db_url']}")

    bot = Bot(COGS_NAMES, settings, debug=debug, bot_type="AstralBot")
    bot.run()
