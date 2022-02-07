# Cryptocurrency Uncertainty Index

![](https://img.shields.io/badge/python-3.8.12-blue) ![](https://img.shields.io/badge/code--style-black-lightgrey) ![](https://img.shields.io/github/commit-activity/m/ChristopherLiew/Crypto-Uncertainty-Index?color=green) ![](https://img.shields.io/github/issues/ChristopherLiew/Crypto-Uncertainty-Index?color=red&style=plastic) 

## Overview
Constructing a cryptocurrency index based on news-media texts using NLP to measure cryptocurrency uncertainty for downstream time series analysis 
and forecasting of cryptocurrency volatility.

## Uncertainty Index Construction Approaches
1. Baseline Keyword Based Index ```(Lucey et al. 2021)```
1. Naive Keyword Based Index with Expanded Crypto Lexicon
2. Measuring Uncertainty using Linguistic Hedges & Language Models

## Set-Up
Some simple steps to setting up the repository for ETL, Modelling, etc.

### Dependencies & Venv
```zsh
brew install make  # OSX
make install  # Runs Brew and Poetry Installs
```

### Services
* ```Elasticsearch``` & ```Kibana``` - For easy text analysis and lookup of data
* ```Postgres``` - Storing of all other relational data (E.g. cryptocurrency indicies, macroeconomic indicators, etc.)

**Install**
```zsh
make build  # Build from docker-compose.yml
```
**Start Up**
```zsh
make run  # After starting up docker daemon
```
**Check Services' Health**
```zsh
make ps
make es-cluster-health # Check cluster health
```
**Shut down**
```zsh
make stop  # Stops docker containers
```

## DE, Modelling & Index Related Pipelines
### Data Extraction
1. **Subreddit Data Pull via PushshiftAPI**
* Extracts all subreddit comments and submissions data for a given list of ```subreddits``` over a period specified by ```start_date``` and ```end_date```. Note that data is extracted in batches by ```Year-Month``` to handle PushshiftAPI's (PMAW) connection drops / rate limits.
* Data is inserted into and analyzed by ```Elasticsearch``` under the ```reddit-crypto``` index by default and serialised locally in ```data/raw_data_dump/reddit``` as ```.pkl``` files.
* Using the CLI interface:
  ```zsh
  ucry-cli extract-reddit-cry-data --start-date 2014-01-01 --end-date 2021-12-31 ethereum ethtrader bitcoin ...
  ```
### NLP & Text Analysis
1. **Text Processing / Analysis of Raw Reddit Data**
* Uses ES' Reindex API to move and process existing raw data under ```reddit-crypto``` to the ```reddit-crypto-custom``` index using a ```Custom Analyzer``` to handle ```cryptocurrency``` and ```social-media``` specific terms and patterns. See ```es/custom_analyzers``` for details.

2. **Word Embedding Generation**
* Pipeline generates word embeddings using a specified pretrained ```word2vec``` model (E.g. FastText, GoogleWiki, HuggingFace) from subreddit data (using a specified ```index``` and ```field``` name) and stores it as ```embeddings``` in a elasticsearch index ```reddit-word-embeddings``` by default.

### Uncertainty Index Construction
3. **Baseline Uncertainty Index (Lucey's)**
* Uses ```Lucey et al. (2021)```'s methodology to construct a baseline cryptocurrency index using a simple predefined keyword set. Resulting numeric index values are inserted into the elasticsearch index ```ucry-baseline``` by default.
* Using the CLI interface:
  ```zsh
  ucry-cli build-ucry-lucey --start-date 2014-01-01 --end-date 2021-12-31 --granularity weekly --type price
  ```

## Appendix:
### Using In-Project poetry venv over cache
```zsh
poetry config virtualenvs.in-project true
poetry env remove python
poetry install
```

### Installing llvmlite on M1 Mac
```zsh
brew install cmake
arch -arm64 brew install llvm@11
# Check LLVM@11 version
LLVM_CONFIG="/opt/homebrew/Cellar/llvm@11/11.1.0_4/bin/llvm-config" arch -arm64 pip install llvmlite
```
To install BERTopic now
```zsh
# WARNING: Not tracked by Poetry
pip3 install -U bertopic
```

Make shortcut
```zsh
make install-bertopic
```

### ES DSL
* High level Elasticsearch API for Search
* Documentation [here](https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html)
