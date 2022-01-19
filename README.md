# Cryptocurrency Uncertainty Index

![](https://img.shields.io/github/commit-activity/m/ChristopherLiew/Crypto-Uncertainty-Index?color=green) ![](https://img.shields.io/github/issues/ChristopherLiew/Crypto-Uncertainty-Index?color=red&style=plastic)

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


## Appendix:
### Using in project poetry venv
```zsh
poetry config virtualenvs.in-project true
poetry env remove python
poetry install
```

