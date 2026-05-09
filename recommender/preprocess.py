import pandas as pd
import re


def clean_year(val):

    try:

        val = str(val).strip()

        match = re.search(r"(19|20)\d{2}", val)

        if match:
            return int(match.group())

    except:
        pass

    return None


MOOD_MAP = {
    "happy": ["comedy", "family", "animation"],
    "sad": ["comedy", "family", "feel good"],
    "romantic": ["romance"],
    "exciting": ["action", "adventure"],
    "scary": ["horror", "thriller"]
}


def preprocess_dataframe(df):

    cols = [
        "Title",
        "Genre",
        "Overview",
        "Tagline",
        "Original_Language",
        "Cast",
        "Director",
        "production_companies"
    ]

    for c in cols:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    df["release_year"] = df["release_year"].apply(clean_year)

    numeric_cols = [
        "Vote_Average",
        "Vote_Count",
        "Budget",
        "Revenue",
        "Runtime"
    ]

    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df