import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from utils.auth import login_required
from utils.database import create_user, get_chat_history, get_user_by_username, init_db, save_chat
from utils.loader import ensure_path, extract_pdf_text, is_allowed_file, split_text_chunks
from utils.rag_pipeline import add_user_documents, answer_question

load_dotenv()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-this")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.before_request
def startup_checks():
    ensure_path(UPLOAD_DIR)


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    user = get_user_by_username(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"success": True, "redirect": url_for("dashboard")})


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return render_template("signup.html")

    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if len(username) < 3 or len(password) < 6:
        return jsonify({"success": False, "message": "Username must be 3+ chars and password 6+ chars."}), 400

    hashed_pw = generate_password_hash(password)
    if not create_user(username, hashed_pw):
        return jsonify({"success": False, "message": "Username already exists."}), 409

    return jsonify({"success": True, "redirect": url_for("login")})


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html", username=session.get("username", "User"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part provided."}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"success": False, "message": "Please select a PDF file."}), 400

    if not is_allowed_file(file.filename):
        return jsonify({"success": False, "message": "Only PDF files are allowed."}), 400

    filename = secure_filename(file.filename)
    user_id = session["user_id"]
    user_upload_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    ensure_path(user_upload_dir)

    file_path = os.path.join(user_upload_dir, filename)
    file.save(file_path)

    text = extract_pdf_text(file_path)
    if not text:
        return jsonify({"success": False, "message": "Could not extract text from PDF."}), 400

    chunks = split_text_chunks(text, source_name=filename)
    added = add_user_documents(user_id=user_id, chunks=chunks)

    return jsonify({"success": True, "message": f"Uploaded and indexed {filename} with {added} chunks.", "chunks": added})


@app.route("/ask", methods=["POST"])
@login_required
def ask_question():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"success": False, "message": "Question is required."}), 400

    user_id = session["user_id"]
    answer, sources = answer_question(user_id=user_id, question=question)
    save_chat(user_id=user_id, question=question, answer=answer)

    return jsonify({"success": True, "question": question, "answer": answer, "sources": sources})


@app.route("/history", methods=["GET"])
@login_required
def history():
    user_id = session["user_id"]
    chats = get_chat_history(user_id=user_id, limit=200)
    return jsonify({"success": True, "history": chats})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# initializing db and upload folder on startup
init_db()
ensure_path(UPLOAD_DIR)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
