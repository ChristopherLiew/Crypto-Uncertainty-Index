"""
Creates tables specified in Models for Crypto Currency
Analysis.
"""

import toml
from pathlib import Path
import click_spinner
from sqlalchemy import create_engine
from models.models import Base
from utils import log


def init_db():
    pg_config = toml.load(Path() / "config" / "etl_config.toml")["postgres"]
    pg_engine = create_engine(pg_config["default_local_uri"], echo=True)
    Base.metadata.create_all(pg_engine)


if __name__ == "__main__":

    log.info("Initialising Postgres Database ...")

    with click_spinner.spinner():
        init_db()

    log.info("Crypto Postgres Database Initialised!")
