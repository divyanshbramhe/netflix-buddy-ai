from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recommender.engine import recommend

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
# ROOT
# =========================

@app.get("/")

def home():

    return {
        "message": "Netflix Buddy API Running"
    }

# =========================
# ASK ENDPOINT
# =========================

@app.get("/ask")

def ask(q: str):

    result = recommend(q)

    return result
