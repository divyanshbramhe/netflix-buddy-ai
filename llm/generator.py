import os

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)

# =========================
# MODEL
# =========================

MODEL = "deepseek/deepseek-v4-flash:free"

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

        temperature=0.3,

        max_tokens=300
    )

    return response.choices[0].message.content
