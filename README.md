# Cryptocurrency Uncertainty Index

![](https://img.shields.io/badge/python-3.8.12-blue) ![](https://img.shields.io/badge/code--style-black-lightgrey) ![](https://img.shields.io/github/commit-activity/m/ChristopherLiew/Crypto-Uncertainty-Index?color=green) ![](https://img.shields.io/github/issues/ChristopherLiew/Crypto-Uncertainty-Index?color=red&style=plastic) 

## Overview
Constructing a cryptocurrency index based on news-media texts using NLP to measure cryptocurrency uncertainty for downstream time series analysis 
and forecasting of cryptocurrency volatility.

## Uncertainty Index Construction Approaches
1. Naive Keyword Counts with Expanded Crypto Lexicon
2. Measuring Uncertainty using Linguistic Hedges & Language Models

## Set-Up
Some simple steps to setting up the repository for ETL, Modelling, etc.

### Poetry
**Install python dependencies**
```zsh
# Install poetry
brew install poetry

# Install deps from poetry.lock
poetry install  

# Refresh deps
poetry update 

# Activate venv
poetry shell 
```

### Docker
**Services**
* ```Elasticsearch``` & ```Kibana``` - For easy text analysis and lookup of data
* ```Postgres``` - Storing of all other relational data (E.g. cryptocurrency indicies, macroeconomic indicators, etc.)

**Start up**
```zsh
docker compose up # --build
docker ps
```
**Shut down**
```zsh
docker stop <container_id>
# OR
docker kill $(docker ps -q)
```

## DE, Modelling & Index Related Pipelines
### Data Extraction
1. Subreddit Data Pull
* Extracts all subreddit comments and submissions data for a given list of ```subreddits``` over a period specified by ```start_date``` and ```end_date```. Note that data is extracted in batches by ```Year-Month``` to handle PushshiftAPI's (PMAW) connection drops / rate limits.
* Data is inserted into ES under the ```reddit-crypto``` index by default and serialised locally in ```data/raw_data_dump/reddit``` as ```.pkl``` files.
* Using the CLI interface:
  ```zsh
  ucry-cli extract-reddit-cry-data --start-date 2014-01-01 --end-date 2021-12-31 ethereum ethtrader bitcoin ...
  ```

## Appendix:
### Using in project poetry venv
```zsh
poetry config virtualenvs.in-project true
poetry env remove python
poetry install
```

