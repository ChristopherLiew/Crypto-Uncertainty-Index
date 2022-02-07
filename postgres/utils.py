"""
SQLAlchemy related utils (DEBUG PD TO PG)
"""

import toml
import pandas as pd
import logging
from pathlib import Path
from sqlalchemy import create_engine
from rich.logging import RichHandler


# Config
pg_config = toml.load(Path() / "config" / "etl_config.toml")["postgres"]
pg_engine = create_engine(pg_config["default_local_uri"], echo=True)

# Logger Confog
FORMAT = "%(message)s"

logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%x]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")


def pd_to_pg(data: pd.DataFrame, table_name: str) -> None:
    """
    Inserts a pandas dataframe into a postgres table using
    the local default uri.

    Args:
        data (pd.DataFrame): Data.
        table_name (str): Name of Table in default PG Database.
    """
    num_rows_affected = data.to_sql(
        name=table_name, con=pg_engine, if_exists="append", index=False
    )
    log.info(f"Number of rows in {table_name} affected: {num_rows_affected}")
