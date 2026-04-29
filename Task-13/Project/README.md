# RAG-Based AI Business Support and Customer Helpdesk

Production-ready Flask web application with:
- User authentication (signup/login/logout)
- PDF upload and parsing
- RAG retrieval using FAISS + LangChain
- AI answer generation using OpenAI (if configured), with robust fallback
- Per-user chat history in SQLite
- Neon black + dark-purple dashboard UI

## Project Structure

project/
- app.py
- requirements.txt
- .env.example
- templates/
  - login.html
  - signup.html
  - index.html
- static/
  - style.css
  - script.js
- uploads/
- database/
  - db.sqlite3 (created automatically)
- utils/
  - auth.py
  - loader.py
  - embeddings.py
  - rag_pipeline.py
  - database.py

## Setup

1. Open terminal in project root.
2. Install dependencies:
   - pip install -r requirements.txt
3. Create environment file:
   - copy .env.example .env
4. Set values in .env:
   - FLASK_SECRET_KEY to a strong random string
   - OPENAI_API_KEY optionally (for LLM-generated responses)

## Run

- python app.py
- Open http://127.0.0.1:5000

## Notes

- If OPENAI_API_KEY is not set, the app still works and returns grounded extractive answers from retrieved document chunks.
- Uploaded files and FAISS indexes are isolated per user.
- SQLite database and tables are auto-initialized on startup.
