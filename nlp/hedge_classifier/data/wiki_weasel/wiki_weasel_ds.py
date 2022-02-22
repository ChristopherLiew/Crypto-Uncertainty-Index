import pandas as pd
from pathlib import Path

root = Path('nlp/hedge_classifier/data/wiki_weasel')
test_certain = root / 'test_wikiweasel_certain_sentences.txt'
test_uncertain = root / 'test_wikiweasel_uncertain_sentences.txt'
train_certain = root / 'train_wikiweasel_certain_sentences.txt'
train_uncertain = root / 'train_wikiweasel_uncertain_sentences.txt'

# Certain = 0 and Uncertain = 1
RENAME_MAP = {0: 'text'}

# Test
test_certain_list = []
with open(test_certain, 'r') as f:
    lines = f.readlines()
    test_certain_list.extend({'text': line, 'label': 0} for line in lines)

test_certain_df = pd.DataFrame(test_certain_list)


test_uncertain_list = []
with open(test_uncertain, 'r') as f:
    lines = f.readlines()
    test_uncertain_list.extend({'text': line, 'label': 1} for line in lines)

test_uncertain_df = pd.DataFrame(test_uncertain_list)

# Train
train_certain_list = []
with open(train_certain, 'r') as f:
    lines = f.readlines()
    train_certain_list.extend({'text': line, 'label': 0} for line in lines)

train_certain_df = pd.DataFrame(train_certain_list)

train_uncertain_list = []
with open(train_uncertain, 'r') as f:
    lines = f.readlines()
    train_uncertain_list.extend({'text': line, 'label': 1} for line in lines)

train_uncertain_df = pd.DataFrame(train_uncertain_list)

# Concat
test_df = pd.concat([test_certain_df, test_uncertain_df], axis=0)
train_df = pd.concat([train_certain_df, train_uncertain_df], axis=0)

# Write
test_df.to_csv(root / 'test.csv', index=False)
train_df.to_csv(root / 'train.csv', index=False)
