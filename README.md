# Cryptocurrency Uncertainty Index

![](https://img.shields.io/badge/python-3.8.12-blue) ![](https://img.shields.io/badge/code--style-black-lightgrey) ![](https://img.shields.io/github/commit-activity/m/ChristopherLiew/Crypto-Uncertainty-Index?color=green) ![](https://img.shields.io/github/issues/ChristopherLiew/Crypto-Uncertainty-Index?color=red&style=plastic)

## Overview
Constructing a cryptocurrency index based on news-media texts using NLP to measure cryptocurrency uncertainty for downstream time series analysis
and forecasting of cryptocurrency volatility.

## Index Construction Approaches
1. Baseline Keyword Based Index ```(Lucey et al. 2021)```
2. Expanded Keyword Based Index with Latent Dirichlet Allocation recovered Topics
3. Hedge Based Uncertainty Index with BERTweet & Wiki Weasel 2.0


## Pipelines: Data Extraction, NLP Modelling & Indices Construction
### Data Extraction
1. **Subreddit Data Pull via PushshiftAPI**
* Extracts all subreddit comments and submissions data for a given list of ```subreddits``` over a period specified by ```start_date``` and ```end_date```. Note that data is extracted in batches by ```Year-Month``` to handle PushshiftAPI's (PMAW) connection drops / rate limits.
* Data is inserted into and analyzed by ```Elasticsearch``` under the ```reddit-crypto``` index by default and serialised locally in ```data/raw_data_dump/reddit``` as ```.pkl``` files.
* Using the CLI interface:
  ```zsh
  ucry-cli extract-reddit-cry-data --start-date 2014-01-01 --end-date 2021-12-31 ethereum ethtrader bitcoin ...
  ```
### Text Processing
1. **Text Processing / Analysis of Raw Reddit Data**
* Uses ES' Reindex API to move and process existing raw data under ```reddit-crypto``` to the ```reddit-crypto-custom``` index using a ```Custom Analyzer``` to handle ```cryptocurrency``` and ```social-media``` specific terms and patterns. See ```es/custom_analyzers``` for details.
* Using the CLI interface:
```zsh
ucry-cli es-reindex <SOURCE-INDEX> <DEST-INDEX> <DEST-MAPPING>
```

### NLP Tool Kit
1. **LDA Topic Modelling**
* Trains a LDA topic model using ```Gensim```'s Multicore LDA implementation optimized with variational Bayes.
* Using the CLI interface:
  ```zsh
  ucry-cli nlp-toolkit train-multi-lda <RAW-DATA-DIR> <GRAM-LEVEL> <NUM-TOPIC-RANGE> <NUM-TOPIC-STEP> <NUM-WORKERS> <CHUNKSIZE> <PASSES> <ALPHA> <ETA> ...
  ```

2. **Top2Vec Topic Modelling**
* Trains a Top2Vec topic model using joint word and document embeddings with the ```Doc2Vec``` algorithm (Default).
* Using the CLI interface:
  ```zsh
  ucry-cli nlp-toolkit train-t2v <DATA> <MIN-COUNT> <SPEED> <NUM-WORKERS> <EMBEDDING-MODEL> <HDB-MIN-CLUSTER-SIZE> <MODEL-SAVE-DIR> ...
  ```
3. **Finetune BERTweet Hedge Detector with Pop Based Training**
* Finetunes a ```Hugging Face``` model (```VinAI's BERTweet``` but can be changed) using SOTA Population Based Training with ```Ray Tune``` and logs models trained and hyperparam sweep with ```Weights & Biases```.
* Using the CLI interface:
  ```zsh
  ucry-cli nlp-toolkit pbt-hedge-clf <MODEL-NAME> <TRAIN-DATA-DIR> <MODEL-SAVE-DIR> <NUM-CPUS-PER-TRIAL> <NUM-GPUS-PER-TRIAL> <RAY-NUM-TRIALS> ...
  ```

### Uncertainty Index Construction
3. **Baseline Uncertainty Index (Lucey's)**
* Uses ```Lucey et al. (2021)```'s methodology to construct a baseline cryptocurrency index using a simple ```predefined keyword set```. Resulting numeric index values are inserted into the elasticsearch index ```ucry-baseline``` by default.
* Using the CLI interface:
  ```zsh
  ucry-cli build-ucry-lucey --start-date 2014-01-01 --end-date 2021-12-31 --granularity weekly --type price
  ```

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

**Make Commands**
```zsh
### Start Up Services ###
make build
make run

### Health Check ###
make ps
make es-cluster-health

### Shutdown ###
make stop  # Stops docker containers
```
