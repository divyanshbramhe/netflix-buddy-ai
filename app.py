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

    answer = generate_response(q, movies)

    return {
        "question": q,
        "answer": answer

    }
