from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import re

# -------------------- Initialize FastAPI --------------------
app = FastAPI()

# -------------------- Pydantic Model --------------------
class QueryRequest(BaseModel):
    query: str

# -------------------- Duration Extraction --------------------
def extract_duration_from_text(text):
    text = text.lower()
    match = re.search(r'(?:under|less than|below|max(?:imum)?(?: duration of)?|upto|up to)\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return None

# -------------------- Load Data --------------------
df = pd.read_csv("cleaned_shl_assessments.csv")
df['duration'] = df['duration'].astype(int)
df['clean_text'] = df['name'].fillna('') + ' ' + df['description'].fillna('')

# -------------------- Load Model & Prep --------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
corpus_embeddings = model.encode(df["clean_text"].tolist(), show_progress_bar=False)
tokenized = [doc.lower().split() for doc in df["clean_text"]]
bm25 = BM25Okapi(tokenized)

# -------------------- API Endpoint --------------------
@app.post("/recommend")
def recommend_assessments(request: QueryRequest):
    query = request.query
    query_embedding = model.encode([query])
    cosine_scores = cosine_similarity(query_embedding, corpus_embeddings)[0]

    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    # Normalize
    bm25_norm = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores) + 1e-8)
    cosine_norm = (cosine_scores - np.min(cosine_scores)) / (np.max(cosine_scores) - np.min(cosine_scores) + 1e-8)

    final_score = 0.5 * bm25_norm + 0.5 * cosine_norm
    df["final_score"] = final_score

    # Time constraint
    max_duration = extract_duration_from_text(query)
    if max_duration is not None:
        df_filtered = df[df['duration'] <= max_duration]
    else:
        df_filtered = df

    results = df_filtered.sort_values("final_score", ascending=False).head(10)
    
    return results[["name", "url", "duration", "test_type", "remote_testing_support"]].to_dict(orient="records")
