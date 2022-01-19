import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"

logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%x]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")
