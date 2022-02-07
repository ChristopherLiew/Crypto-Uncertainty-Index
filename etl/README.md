# Data Documentation
## Introduction
This documentation covers the various data sources pertaining to the construction of our Cryptocurrency Uncertainty Index. For details on data engineering pipelines / designs please refer to the main README.md in the ```root dir```.

### Components in the ```ETL``` directory:
* ```Extract``` - Extract functions and pipelines to pull data from various sources (APIs) and ingest them into databases (i.e. Elasticsearch or Postgres)
* ```Schema```- Contains schemas and dataclasses for constructing ES indices' mappings and PyDantic Classes for Vlidation.
* ```Raw Data Dump``` - Raw Extracted Data written out as ```.csv``` files, ```binaries``` and other compressed formates.

---
## Data Dictionary
* Please find the data dictionary for the cryptocurrency index [here](https://docs.google.com/spreadsheets/d/1O8ulP8rPCMWXDkvzuJ9BugfGTJiRSgo0XItg9Nrlp9w/edit?usp=sharing).

---
## Data Sources
### 1. Lexical Based Uncertainty Index
   * Reddit - Cryptocurrency Subreddits:
     a. r/Bitcoin
     b. r/Ethereum
