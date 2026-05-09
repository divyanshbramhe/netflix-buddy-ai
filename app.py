from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import re

# =========================
# APP
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv("data/movies.csv")

df = df.fillna("")

df = df.astype(str)

# =========================
# LOWERCASE HELPER COLUMNS
# =========================

df["title_lower"] = df["Title"].str.lower()

df["genre_lower"] = df["Genre"].str.lower()

df["overview_lower"] = df["Overview"].str.lower()

df["language_lower"] = df["Original_Language"].str.lower()

# =========================
# ROOT
# =========================

@app.get("/")
def home():

    return {
        "message": "Netflix Buddy API Running",
        "movies": len(df)
    }

# =========================
# HELPERS
# =========================

def extract_year(query):

    match = re.search(r"(19\d{2}|20\d{2})", query)

    if match:
        return match.group()

    return None


def extract_rating(query):

    match = re.search(
        r"(?:more than|above|greater than)\s*(\d+(\.\d+)?)",
        query
    )

    if match:
        return float(match.group(1))

    return None


def detect_mood(query):

    query = query.lower()

    if any(word in query for word in [
        "sad",
        "depressed",
        "upset",
        "lonely"
    ]):
        return "feel_good"

    if any(word in query for word in [
        "scary",
        "horror",
        "ghost",
        "thriller"
    ]):
        return "horror"

    if any(word in query for word in [
        "romantic",
        "love"
    ]):
        return "romance"

    return None

# =========================
# MAIN API
# =========================

@app.get("/ask")
def ask(q: str):

    query = q.lower().strip()

    # =========================
    # MOVIE INFO SEARCH
    # =========================

    info_keywords = [
        "tell me about",
        "overview",
        "about movie",
        "plot"
    ]

    if any(k in query for k in info_keywords):

        cleaned = query

        for k in info_keywords:
            cleaned = cleaned.replace(k, "")

        cleaned = cleaned.strip()

        exact = df[df["title_lower"] == cleaned]

        if len(exact) > 0:

            row = exact.iloc[0]

            return {
                "answer": f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 Overview:
{row['Overview']}
"""
            }

        partial = df[
            df["title_lower"].str.contains(
                cleaned,
                na=False
            )
        ]

        if len(partial) > 0:

            row = partial.iloc[0]

            return {
                "answer": f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 Overview:
{row['Overview']}
"""
            }

        return {
            "answer": "Movie not found in dataset."
        }

    # =========================
    # FILTERING
    # =========================

    filtered = df.copy()

    # genre filtering

    genres = [
        "action",
        "thriller",
        "horror",
        "romance",
        "comedy",
        "drama",
        "crime",
        "adventure",
        "animation",
        "family",
        "fantasy",
        "mystery",
        "war",
        "history",
        "sci-fi",
        "science fiction"
    ]

    for genre in genres:

        if genre in query:

            search_genre = genre

            if genre == "science fiction":
                search_genre = "sci-fi"

            filtered = filtered[
                filtered["genre_lower"].str.contains(
                    search_genre,
                    na=False
                )
            ]

    # year filtering

    year = extract_year(query)

    if year:

        filtered = filtered[
            filtered["release_year"] == year
        ]

    # rating filtering

    rating = extract_rating(query)

    if rating:

        filtered["Vote_Average"] = pd.to_numeric(
            filtered["Vote_Average"],
            errors="coerce"
        )

        filtered = filtered[
            filtered["Vote_Average"] >= rating
        ]

    # language filtering

    if "bollywood" in query or "hindi" in query:

        filtered = filtered[
            filtered["language_lower"].str.contains(
                "hi",
                na=False
            )
        ]

    # mood filtering

    mood = detect_mood(query)

    if mood == "feel_good":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "comedy|family|animation|adventure",
                regex=True,
                na=False
            )
        ]

    elif mood == "horror":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "horror|thriller",
                regex=True,
                na=False
            )
        ]

    elif mood == "romance":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "romance",
                na=False
            )
        ]

    # =========================
    # SORTING
    # =========================

    filtered["Vote_Average"] = pd.to_numeric(
        filtered["Vote_Average"],
        errors="coerce"
    )

    filtered = filtered.sort_values(
        by="Vote_Average",
        ascending=False
    )

    # =========================
    # FINAL RESPONSE
    # =========================

    if len(filtered) == 0:

        return {
            "answer": "No matching movies found."
        }

    top_movies = filtered.head(5)

    answer = ""

    for _, row in top_movies.iterrows():

        answer += f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 {row['Overview']}

-----------------------------------

"""

    return {
        "answer": answer
    }
