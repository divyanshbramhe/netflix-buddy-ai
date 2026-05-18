import os

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(

    base_url="https://integrate.api.nvidia.com/v1",

    api_key=os.getenv("NVIDIA_API_KEY")

)

# =========================
# MODEL
# =========================

MODEL = "nvidia/nemotron-mini-4b-instruct"

# =========================
# GENERATE RESPONSE
# =========================

def generate_response(query, movies_df):

    if len(movies_df) == 0:

        return "No movies found in dataset."

    context = ""

    for _, row in movies_df.iterrows():

        context += f'''
TITLE: {row["Title"]}
YEAR: {row["release_year"]}
GENRE: {row["Genre"]}
RATING: {row["Rating"]}
OVERVIEW: {row["Overview"]}

-------------------
'''

    prompt = f"""
You are an AI movie recommendation assistant.

Use ONLY the provided movie dataset context.

Context:
{context}

User Query:
{query}

Instructions:
- Recommend movies naturally
- Be concise
- Mention ratings when useful
- Do NOT invent movies
- Only use movies from context
- Don't say based on available data

Answer:
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        top_p=0.7,
        max_tokens=3000,
        stream=False
    )

    return response.choices[0].message.content
