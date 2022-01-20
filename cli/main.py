"""
CLI commands for easy pipeline triggers and model training,
inference and analysis, etc.
"""

from typing import Optional
import typer

# App
app = typer.Typer()


# Test
@app.command()
def hello(name: Optional[str] = None):
    greet = "Welcome to the crypto-uncertainty-index CLI"
    if name:
        print(f"Hello {name}, {greet}")
    else:
        print(f"Hello Guest, {greet}")


#####################
## Data Extraction ##
#####################


#####################
## Data Processing ##
#####################


###################
## NLP Pipelines ##
###################
