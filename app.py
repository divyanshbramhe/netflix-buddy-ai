from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv("data/movies.csv")

# =========================
# ROOT
# =========================

@app.get("/")
def home():

    return {
        "message": "Dataset loaded successfully",
        "movies": len(df)
    }
