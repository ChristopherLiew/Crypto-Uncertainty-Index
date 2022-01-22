"""
CLI commands for easy pipeline triggers and model training,
inference and analysis, etc.
"""

from typing import Optional
import typer
from pipelines.data_engineering import (
    crypto_text_data_extraction_pipeline
)

# App
app = typer.Typer()


# Test
@app.command()
def main(name: Optional[str] = None):
    greet = "Welcome to the crypto-uncertainty-index CLI"
    if name:
        print(f"Hello {name}, {greet}")
    else:
        print(f"Hello Guest, {greet}")


#####################
## Data Extraction ##
#####################
app.add_typer(
    crypto_text_data_extraction_pipeline.app,
    name="extract-reddit-crypto-data",
    help="""Extracts subreddit data and inserts into ES
         and serialises into pickle vis Pushshift API."""
)


#####################
## Data Processing ##
#####################



###################
## NLP Pipelines ##
###################
