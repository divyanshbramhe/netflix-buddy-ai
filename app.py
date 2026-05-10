from fastapi import FastAPI
from recommender.engine import recommend
from llm.generator import generate_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": "Netflix Buddy is running"
    }


@app.get("/ask")
def ask(q: str):

    movies = recommend(q)

    if not movies:

        return {
            "question": q,
            "answer": "No matching movies found."
        }

    try:

        answer = generate_response(q, movies)

    except Exception as e:

        print("LLM ERROR:", e)

        answer = str(movies[:5])

    return {
        "question": q,
        "answer": answer
    }
