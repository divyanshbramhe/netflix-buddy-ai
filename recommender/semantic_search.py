import pandas as pd
import numpy as np
import faiss
import pickle
import requests
from tqdm import tqdm
from recommender.preprocess import preprocess_dataframe
import os

os.makedirs("indexes", exist_ok=True)

CSV_PATH = "data/movies.csv"


df = pd.read_csv(CSV_PATH)
df = preprocess_dataframe(df)


def build_text(row):

    return f"""
TITLE: {row['Title']}
GENRE: {row['Genre']}
OVERVIEW: {row['Overview']}
TAGLINE: {row['Tagline']}
CAST: {row['Cast']}
DIRECTOR: {row['Director']}
"""


texts = []
embeddings = []


for _, row in tqdm(df.iterrows(), total=len(df)):

    text = build_text(row)

    texts.append(text)

    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    emb = response.json()["embedding"]

    embeddings.append(emb)


embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, "indexes/movie_index.faiss")

pickle.dump(texts, open("indexes/docs.pkl", "wb"))

np.save("indexes/embeddings.npy", embeddings)

print("Index created")
