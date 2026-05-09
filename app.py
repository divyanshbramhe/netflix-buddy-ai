from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

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

# lowercase helper columns

df["title_lower"] = df["Title"].str.lower()

# lowercase helper columns

df["title_lower"] = df["Title"].astype(str).str.lower()

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
# SEARCH MOVIE
# =========================

@app.get("/ask")
def ask(q: str):

    query = q.lower().strip()

    # exact match

    exact = df[df["title_lower"] == query]

    if len(exact) > 0:

        row = exact.iloc[0]

        return {
            "answer": f"""
🎬 {row['Title']} ({row['release_year']})

⭐ Rating: {row['Vote_Average']}

🎭 Genre: {row['Genre']}

📝 {row['Overview']}
"""
        }

    # partial match

    partial = df[
        df["title_lower"].str.contains(query, na=False)
    ]

    if len(partial) > 0:

        results = partial.head(5)

        answer = ""

        for _, row in results.iterrows():

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

    return {
        "answer": "Movie not found in dataset."
    }
