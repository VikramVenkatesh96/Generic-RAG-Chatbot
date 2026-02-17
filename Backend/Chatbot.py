import os
import pandas as pd
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

MODEL_NAME = "all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = os.path.join("models", MODEL_NAME)

def load_embedding_model():
    if os.path.exists(LOCAL_MODEL_PATH):
        print("Loading model from local folder...")
        model = SentenceTransformer(LOCAL_MODEL_PATH)
    else:
        print("Model not found locally. Downloading...")
        model = SentenceTransformer(MODEL_NAME)
        model.save(LOCAL_MODEL_PATH)
        print("Model saved locally.")
    return model

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

class SimpleFAQBot:
    def __init__(self, csv_path, similarity_threshold=0.70):
        self.similarity_threshold = similarity_threshold
        self.df = pd.read_csv(csv_path)

        self.model = load_embedding_model()

        self.question_embeddings = self.model.encode(
            self.df['question'].tolist(),
            convert_to_numpy=True
        )

    def get_response(self, user_query):
        query_embedding = self.model.encode([user_query], convert_to_numpy=True)
        similarities = cosine_similarity(query_embedding, self.question_embeddings)[0]
        best_index = np.argmax(similarities)
        best_score = similarities[best_index]

        if best_score >= self.similarity_threshold:
            return self.df.iloc[best_index]['answer']
        else:
            return "I'm sorry but I can't help you here"

bot = SimpleFAQBot("Sample.csv")

@app.post("/chat")
def chat(query: Query):
    response = bot.get_response(query.message)
    return {"response": response}
