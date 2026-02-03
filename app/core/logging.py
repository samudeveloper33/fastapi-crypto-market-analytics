import logging

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
