# -*- coding: utf-8 -*-
"""GO_Preprocess.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15tY_KE7kr-ACJFmHaxeyw-Cuhq5BHUD8
"""

import numpy as np
import pandas as pd
from google.colab import drive
import requests
import os

"""Downloading the Dataset"""

base_url = 'https://storage.googleapis.com/gresearch/goemotions/data/full_dataset/'
file_names = ['goemotions_1.csv', 'goemotions_2.csv', 'goemotions_3.csv']
base_save_path = 'data/dataset/'


os.makedirs(base_save_path, exist_ok=True)

for file_name in file_names:

    url = base_url + file_name
    save_path = os.path.join(base_save_path, file_name)

    response = requests.get(url)
    response.raise_for_status()

  # Save the file
    with open(save_path, 'wb') as f:
        f.write(response.content)

    print(f'File downloaded and saved at {save_path}')

df1 = pd.read_csv('data/dataset/goemotions_1.csv')
df2 = pd.read_csv('data/dataset/goemotions_2.csv')
df3 = pd.read_csv('data/dataset/goemotions_3.csv')

df1.head(10)

df2.head(10)

df3.head(10)

df_combined = pd.concat([df1,df2,df3], ignore_index=True)
print("DF1 shape:", df1.shape)
print("DF2 shape:",df2.shape)
print("DF3 shape:",df3.shape)
print("combined DF:",df_combined.shape)

features = df_combined.columns.tolist()
print(features)

df_combined.drop(['id', 'author', 'subreddit', 'link_id', 'parent_id',
                  'created_utc', 'rater_id'], axis=1, inplace=True)
print("Shape:", df_combined.shape)

df_combined.head(10)

import matplotlib.pyplot as plt
value_counts = df_combined['example_very_unclear'].value_counts()
value_counts.plot(kind='bar')
plt.title('Histogram of True/False Classifications')
plt.xlabel('Classification')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.show()

df_combined = df_combined.loc[df_combined['example_very_unclear'] != True]
print("Shape:", df_combined.shape)

df_combined.drop_duplicates(inplace=True)
print("Shape:", df_combined.shape)

df_combined.drop('example_very_unclear', axis=1, inplace=True)
print("Shape:", df_combined.shape)

emotions_to_clear = ['admiration', 'amusement', 'caring', 'realization']
df_combined = df_combined[~(df_combined[emotions_to_clear] == 1).any(axis=1)]
print("Shape:", df_combined.shape)

df_combined.drop(emotions_to_clear, axis=1, inplace=True)

print("Shape:", df_combined.shape)

df_filtered = df_combined.drop(columns=['text'])
column_sums = df_filtered.sum()
column_sums.plot(kind='bar')
plt.title('Emotions Histogram')
plt.xlabel('Emotion')
plt.ylabel('sample quantity')
plt.xticks(rotation=45)
plt.show()
print(column_sums)

"""Lets downsample neutral"""

neutral_1_df = df_combined[df_combined['neutral'] == 1]
neutral_0_df = df_combined[df_combined['neutral'] == 0]
n_samples_to_keep = int(10000)

reduced_neutral_1_df = neutral_1_df.sample(n=n_samples_to_keep)
df_reduced = pd.concat([reduced_neutral_1_df, neutral_0_df])

approval_1_df = df_reduced[df_reduced['approval'] == 1]
approval_0_df = df_reduced[df_reduced['approval'] == 0]
n_samples_to_keep = int(10000)

reduced_approval_1_df = approval_1_df.sample(n=n_samples_to_keep)
df_reduced = pd.concat([reduced_approval_1_df, approval_0_df])
df_reduced_values = df_reduced.drop(columns=['text'])
column_sums = df_reduced_values.sum()
column_sums.plot(kind='bar')
plt.title('Emotions Histogram')
plt.xlabel('Emotion')
plt.ylabel('sample quantity')
plt.xticks(rotation=45)
plt.show()
print(column_sums)

"""Relabeling for a more balanced yet diverse distribution"""

df_reduced.loc[(df_reduced['nervousness'] == 1) | (df_reduced['embarrassment'] == 1), 'fear'] = 1
df_reduced.loc[(df_reduced['love'] == 1), 'joy'] = 1
df_reduced.loc[(df_reduced['relief'] == 1) | (df_reduced['pride'] == 1), 'optimism'] = 1
df_reduced.loc[(df_reduced['remorse'] == 1) | (df_reduced['grief'] == 1), 'sadness'] = 1
df_reduced.loc[(df_reduced['disgust'] == 1), 'disapproval'] = 1
df_reduced.loc[(df_reduced['excitement'] == 1), 'optimism'] = 1

df_reduced.drop(['nervousness','embarrassment', 'love', 'relief', 'pride',
                 'remorse', 'grief','desire','surprise', 'disgust','excitement'], axis=1, inplace=True)

print("Shape:", df_reduced.shape)

df_reduced.head(10)

disapproval_1_df = df_reduced[df_reduced['disapproval'] == 1]
disapproval_0_df = df_reduced[df_reduced['disapproval'] == 0]
n_samples_to_keep = int(12000)

reduced_disapproval_1_df = disapproval_1_df.sample(n=n_samples_to_keep)
df_reduced = pd.concat([reduced_disapproval_1_df, disapproval_0_df])

df_reduced_values = df_reduced.drop(columns=['text'])
df_balanced = df_reduced
column_sums = df_reduced_values.sum()
column_sums.plot(kind='bar')
plt.title('Emotions Histogram')
plt.xlabel('Emotion')
plt.ylabel('sample quantity')
plt.xticks(rotation=45)
plt.show()
print(column_sums)

"""Remove duplicates and find null values."""

df_unique = df_balanced
print("Shape:", df_balanced.shape)
print("Shape:", df_unique.shape)

df_unique_values = df_unique.drop(columns=['text'])
column_sums = df_unique_values.sum()
column_sums.plot(kind='bar')
plt.title('Emotions Histogram')
plt.xlabel('Emotion')
plt.ylabel('sample quantity')
plt.xticks(rotation=45)
plt.show()
print(column_sums)

nulls_per_column = df_unique.isnull().sum()
total_nulls = nulls_per_column.sum()
print("Nulls per column:\n", nulls_per_column)
print("\nTotal nulls in the DataFrame:", total_nulls)

import re

def clean_text(text):
	text = str(text).lower()  # Convert text to lowercase
	text = re.sub("[\[].*?[\]]", "", text)  # Remove text within square brackets
	text = re.sub(r"http\S+", "", text)  # Remove URLs
	text = re.sub(r"[^\w\s]", "", text)  # Remove non-alphanumeric characters (excluding spaces)
	text = re.sub(r"\d+", "", text)  # Remove digits
	return text

df_unique['cleaned_text'] = df_unique['text'].apply(clean_text)
df_clean = df_unique.drop(columns=['text'])
print(df_clean.head(20))

column_names = df_clean.columns
#column_names.remove('text')
print(column_names)
# Function to find the emotion label for a row
def find_emotion_label(row):
    for col in column_names:
        if row[col] == 1:
            return col  # Returns the name of the column where the value is 1
    return np.nan  # Returns NaN if no emotion column has a value of 1

# Apply the function to each row to create a new 'emotion_label' column
df_clean['emotion_label'] = df_clean.apply(find_emotion_label, axis=1)

df_clean.head()

df_labeled = df_clean[['cleaned_text','emotion_label']].copy()
df_labeled.head()

emotion_counts = df_labeled['emotion_label'].value_counts()

# Creating the histogram
plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
emotion_counts.plot(kind='bar')
plt.title('Distribution of Emotions')
plt.xlabel('Emotion')
plt.ylabel('Frequency')
plt.xticks(rotation=45)  # Rotate labels to make them readable
plt.show()

df_cleaned = df_labeled.dropna(subset=['emotion_label'])
df_cleaned.shape
null_count = df_cleaned['emotion_label'].isnull().sum()
print(f"Number of null values in 'emotion_label': {null_count}")

"""Processing functions"""

import spacy
nlp = spacy.load('en_core_web_sm')

def remove_stopwords(text):
    doc = nlp(text)
    text_wo_stopwords = ' '.join([token.text for token in doc if not token.is_stop])
    return text_wo_stopwords

def lemmas_tokens(text):
  doc = nlp(text)
  lemmas = ' '.join([token.lemma_ for token in doc])
  return lemmas

def tokenize(text):
    doc = nlp(text)
    tokens = [token.text for token in doc]
    return tokens

"""Already Preprocessed to the "processed.csv" file."""

# This cell takes a long time to apply lemmatization and Tokenization.
# Upload "processed.csv" file generated to the root of the environment.

df_cleaned['lemmas'] = df_cleaned['cleaned_text'].apply(lemmas_tokens)
df_cleaned['lemmas'] = df_cleaned['lemmas'].astype(str)
df_cleaned['tokens'] = df_cleaned['lemmas'].apply(tokenize)
file_name = '/content/processed.csv'
df_cleaned.to_csv(file_name, index=False)

df_preprocessed = pd.read_csv('processed.csv')
df_preprocessed.head(10)



#!pip --quiet install gensim

import gensim.downloader as api

word2vec_model = api.load('glove-twitter-200')

import numpy as np

def document_vector(model, doc_tokens):
    # Filter out tokens not in the model's vocabulary
    doc_tokens = [token for token in doc_tokens if token in model.key_to_index]

    if not doc_tokens:
        # Return a zero vector if the document contains no tokens in the model's vocabulary
        return np.zeros(model.vector_size)

    # Compute the average vector for the document
    return np.mean([model[token] for token in doc_tokens], axis=0)

df_preprocessed['doc_vector'] = df_preprocessed['tokens'].apply(lambda x: document_vector(word2vec_model, x))

df_vectorized = df_preprocessed
file_name = '/content/vectorized.csv'
df_vectorized.to_csv(file_name, index=False)

df_vectorized.head(10)

from sklearn.model_selection import train_test_split
X = df_preprocessed['doc_vector']
y = df_preprocessed['emotion_label']  # Target Variable
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    random_state=42, stratify=y)
print(f"Training set size: {len(X_train)}")
print(f"Testing set size: {len(X_test)}")