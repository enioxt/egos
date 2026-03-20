import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def build_logger(level: str, verbose: bool = False) -> logging.Logger:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("oracle-launcher")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if verbose else getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = RotatingFileHandler(logs_dir / "app.log", maxBytes=1_000_000, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
