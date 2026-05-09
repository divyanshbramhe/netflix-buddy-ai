# recommender/engine.py

import pandas as pd
import faiss
import pickle
import requests
import numpy as np

from recommender.query_parser import (
    extract_year,
    extract_genre,
    extract_language,
    extract_rating,
    detect_mood
)

from recommender.preprocess import preprocess_dataframe

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("data/movies.csv")

df = preprocess_dataframe(df)

# =========================
# LOAD FAISS
# =========================

index = faiss.read_index("indexes/movie_index.faiss")

docs = pickle.load(
    open("indexes/docs.pkl", "rb")
)

# =========================
# EMBEDDING
# =========================

def get_embedding(text):

    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    data = response.json()

    return data["embedding"]

# =========================
# EXACT TITLE SEARCH
# =========================

def exact_title_search(query):

    q = query.lower()

    for _, row in df.iterrows():

        title = str(row["Title"]).lower().strip()

        # ignore tiny titles
        if len(title) < 3:
            continue

        if f" {title} " in f" {q} ":
            return row

    return None

# =========================
# STRUCTURED SEARCH
# =========================

def structured_search(query):

    result = df.copy()

    year = extract_year(query)

    genre = extract_genre(query)

    lang = extract_language(query)

    rating = extract_rating(query)

    mood = detect_mood(query)

    # =========================
    # GENRE FILTER
    # =========================

    if genre:

        result = result[
            result["Genre"].str.contains(
                genre,
                case=False,
                na=False
            )
        ]

    # =========================
    # YEAR FILTER
    # =========================

    if year:

        result = result[
            result["release_year"] == year
        ]

    # =========================
    # LANGUAGE FILTER
    # =========================

    if lang:

        result = result[
            result["Original_Language"]
            .str.contains(
                lang,
                case=False,
                na=False
            )
        ]

    # =========================
    # RATING FILTER
    # =========================

    if rating:

        result = result[
            result["Vote_Average"] >= rating
        ]

    # =========================
    # MOOD FILTER
    # =========================

    if mood:

        if mood == "happy":

            result = result[
                result["Genre"].str.contains(
                    "Comedy|Family|Animation",
                    case=False,
                    na=False
                )
            ]

        elif mood == "romance":

            result = result[
                result["Genre"].str.contains(
                    "Romance",
                    case=False,
                    na=False
                )
            ]

        elif mood == "scary":

            result = result[
                result["Genre"].str.contains(
                    "Horror|Thriller",
                    case=False,
                    na=False
                )
            ]

    # =========================
    # SORTING
    # =========================

    result = result.sort_values(
        by=[
            "Vote_Average",
            "Vote_Count"
        ],
        ascending=False
    )

    return result.head(5)

# =========================
# SEMANTIC SEARCH
# =========================

def semantic_search(query, k=5):

    emb = np.array([
        get_embedding(query)
    ]).astype("float32")

    _, idx = index.search(emb, k)

    return df.iloc[idx[0]]

# =========================
# MAIN RECOMMENDER
# =========================

def recommend(query):

    # =========================
    # 1. EXACT TITLE
    # =========================

    exact = exact_title_search(query)

    if exact is not None:

        return pd.DataFrame([exact])

    # =========================
    # 2. STRUCTURED FILTERING
    # =========================

    structured = structured_search(query)

    if len(structured) > 0:

        return structured

    # =========================
    # 3. SEMANTIC FALLBACK
    # =========================

    return semantic_search(query)