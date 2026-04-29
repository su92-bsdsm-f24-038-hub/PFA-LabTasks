from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import re
import os

app = Flask(__name__)

# loading model, index and dataset
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

index = None
df = None

def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r'[^A-Za-z\s]', '', text)
        text = text.lower()
    else:
        text = ''
    return text

def load_data():
    global index, df

    if not os.path.exists('medical_faiss.index') or not os.path.exists('medical_qna.csv'):
        print("Index or CSV not found. Please run the notebook first.")
        return False

    index = faiss.read_index('medical_faiss.index')
    df = pd.read_csv('medical_qna.csv')
    print("Data loaded successfully!")
    return True

def search_answer(query):
    if index is None or df is None:
        return "Please run the notebook first to build the index."

    clean_query = clean_text(query)
    query_embedding = model.encode([clean_query])
    query_embedding = np.array(query_embedding).astype('float32')

    distances, indices = index.search(query_embedding, 1)

    best_idx = indices[0][0]
    best_distance = distances[0][0]

    # if distance is too high, the match is not relevant
    if best_distance > 2.5:
        return "Sorry, I couldn't find a relevant answer. Please try rephrasing your question."

    return df['answer'].iloc[best_idx]


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please type something!"})

    response = search_answer(user_message)
    return jsonify({"response": response})


if __name__ == "__main__":
    load_data()
    app.run(debug=True)
