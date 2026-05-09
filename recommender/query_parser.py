import re

GENRES = [
    "action",
    "thriller",
    "horror",
    "comedy",
    "romance",
    "sci-fi",
    "science fiction",
    "drama",
    "biopic",
    "crime",
    "animation"
]

MOODS = {
    "sad": "happy",
    "depressed": "happy",
    "lonely": "feel good",
    "romantic": "romance",
    "scared": "horror"
}

LANGUAGE_MAP = {
    "bollywood": "hi",
    "hindi": "hi",
    "hollywood": "en"
}


def extract_year(query):

    match = re.search(r"(19|20)\d{2}", query)

    if match:
        return int(match.group())

    return None


def extract_genre(query):

    q = query.lower()

    for g in GENRES:
        if g in q:
            return g

    return None


def extract_language(query):

    q = query.lower()

    for k, v in LANGUAGE_MAP.items():
        if k in q:
            return v

    return None


def extract_rating(query):

    match = re.search(r"more than (\d+(\.\d+)?)", query.lower())

    if match:
        return float(match.group(1))

    return None


def detect_mood(query):

    q = query.lower()

    for k, v in MOODS.items():
        if k in q:
            return v

    return None