import logging

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename="logs/bot.log",
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]",
        datefmt="%d/%m/%Y %I:%M:%S",
        encoding="utf-8",
        filemode="a",
    )
