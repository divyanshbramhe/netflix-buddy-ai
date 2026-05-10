import pandas as pd

# =========================
# LOAD CSV
# =========================

df = pd.read_csv("/Users/apple/Downloads/Project/data/9000plus_clean.csv")

# =========================
# CONVERT DATE COLUMN
# =========================

df["movie_release_date"] = pd.to_datetime(
    df["movie_release_date"],
    format="%d/%m/%y",
    errors="coerce"
)

# =========================
# CREATE RELEASE YEAR COLUMN
# =========================

df["release_year"] = df["movie_release_date"].dt.year

# =========================
# OPTIONAL:
# CONVERT YEAR TO INTEGER
# =========================

df["release_year"] = (
    df["release_year"]
    .fillna(0)
    .astype(int)
)

# =========================
# SAVE UPDATED CSV
# =========================

df.to_csv("/Users/apple/Downloads/Project/data/movies_updated.csv", index=False)

# =========================
# DONE
# =========================

print("✅ release_year column created successfully")
print(df[["movie_release_date", "release_year"]].head())