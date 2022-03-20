"""
Convert TSV files to CSV and standardise column naming for Hugging Face
Models. (i.e. text and label)
"""

import pandas as pd
from pathlib import Path


# TSV File Paths
BIO_DATA = Path(
    "nlp/hedge_classifier/data/szeged_uncertainty_corpus/cleaned_datasets/train_test/bio/tsv"
)
WIKI_DATA = Path(
    "nlp/hedge_classifier/data/szeged_uncertainty_corpus/cleaned_datasets/train_test/wiki/tsv"
)


# Process
bio_data_fps = list(BIO_DATA.rglob("*.tsv"))
wiki_data_fps = list(WIKI_DATA.rglob("*.tsv"))


# BioScope Data
for fp in bio_data_fps:
    name = fp.stem
    data = pd.read_csv(
        fp,
        sep="\t",
        header=None,
    )
    data.columns = ["text", "label"]
    print(data.info())
    print(data.groupby(["label"]).count())
    data.to_csv(BIO_DATA / "csv" / f"{name}.csv", index=False)


# Wiki Data
for fp in wiki_data_fps:
    name = fp.stem
    data = pd.read_csv(
        fp,
        sep="\t",
        header=None,
    )
    data.columns = ["text", "label"]
    print(data.info())
    print(data.groupby(["label"]).count())
    data.to_csv(WIKI_DATA / "csv" / f"{name}.csv", index=False)
