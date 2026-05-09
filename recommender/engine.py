import pandas as pd
import re
from difflib import get_close_matches

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv("data/movies.csv")

# =========================
# CLEAN DATA
# =========================

df.fillna("", inplace=True)

# =========================
# LOWERCASE HELPER COLUMNS
# =========================

df["title_lower"] = df["Title"].astype(str).str.lower()

df["genre_lower"] = df["Genre"].astype(str).str.lower()

df["overview_lower"] = df["Overview"].astype(str).str.lower()

df["language_lower"] = df["Original_Language"].astype(str).str.lower()

df["director_lower"] = df["Director"].astype(str).str.lower()

df["cast_lower"] = df["Cast"].astype(str).str.lower()

# =========================
# QUERY PARSER
# =========================

def extract_year(query):

    match = re.search(r"(19\d{2}|20\d{2})", query)

    if match:
        return int(match.group())

    return None


def extract_rating(query):

    match = re.search(r"(?:more than|above|greater than)\s*(\d+(\.\d+)?)", query)

    if match:
        return float(match.group(1))

    return None


# =========================
# MOOD DETECTION
# =========================

def detect_mood(query):

    query = query.lower()

    if any(word in query for word in [
        "sad",
        "depressed",
        "upset",
        "lonely",
        "crying"
    ]):
        return "feel good"

    if any(word in query for word in [
        "scared",
        "horror",
        "ghost",
        "thriller"
    ]):
        return "horror"

    if any(word in query for word in [
        "romantic",
        "love",
        "relationship"
    ]):
        return "romance"

    if any(word in query for word in [
        "funny",
        "comedy",
        "laugh"
    ]):
        return "comedy"

    return None


# =========================
# TITLE SEARCH
# =========================

def find_movie(query):

    query = query.lower().strip()

    # exact match

    exact = df[df["title_lower"] == query]

    if len(exact) > 0:
        return exact

    # partial match

    partial = df[
        df["title_lower"].str.contains(query, na=False)
    ]

    if len(partial) > 0:
        return partial.head(5)

    # fuzzy match

    titles = df["title_lower"].tolist()

    close = get_close_matches(query, titles, n=1, cutoff=0.7)

    if close:

        fuzzy = df[df["title_lower"] == close[0]]

        return fuzzy

    return pd.DataFrame()


# =========================
# MAIN RECOMMENDER
# =========================

def recommend(query):

    query_lower = query.lower()

    # =========================
    # 1. MOVIE INFO REQUEST
    # =========================

    info_keywords = [
        "tell me about",
        "overview",
        "about movie",
        "story of",
        "plot of"
    ]

    if any(k in query_lower for k in info_keywords):

        cleaned = query_lower

        for k in info_keywords:
            cleaned = cleaned.replace(k, "")

        cleaned = cleaned.strip()

        result = find_movie(cleaned)

        if len(result) == 0:

            return {
                "answer": "Movie not found in dataset."
            }

        row = result.iloc[0]

        answer = f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 Overview:
{row['Overview']}
"""

        return {
            "answer": answer
        }

    # =========================
    # 2. FILTERING
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
        "sci-fi",
        "science fiction",
        "crime",
        "adventure",
        "animation",
        "family",
        "fantasy",
        "mystery",
        "war",
        "history"
    ]

    for genre in genres:

        if genre in query_lower:

            if genre == "science fiction":
                genre = "sci-fi"

            filtered = filtered[
                filtered["genre_lower"].str.contains(
                    genre,
                    na=False
                )
            ]

    # language filtering

    if "bollywood" in query_lower or "hindi" in query_lower:

        filtered = filtered[
            filtered["language_lower"].str.contains(
                "hi",
                na=False
            )
        ]

    if "english" in query_lower:

        filtered = filtered[
            filtered["language_lower"].str.contains(
                "en",
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

        filtered = filtered[
            filtered["Vote_Average"] >= rating
        ]

    # mood filtering

    mood = detect_mood(query)

    if mood == "feel good":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "comedy|family|animation|adventure",
                na=False,
                regex=True
            )
        ]

    elif mood == "horror":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "horror|thriller",
                na=False,
                regex=True
            )
        ]

    elif mood == "romance":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "romance",
                na=False
            )
        ]

    elif mood == "comedy":

        filtered = filtered[
            filtered["genre_lower"].str.contains(
                "comedy",
                na=False
            )
        ]

    # =========================
    # 3. SORTING
    # =========================

    filtered = filtered.sort_values(
        by="Vote_Average",
        ascending=False
    )

    # =========================
    # 4. FINAL RESPONSE
    # =========================

    if len(filtered) == 0:

        return {
            "answer": "No matching movies found in dataset."
        }

    top_movies = filtered.head(5)

    response = ""

    for _, row in top_movies.iterrows():

        response += f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 {row['Overview']}

-----------------------------------

"""

    return {
        "answer": response
    }
