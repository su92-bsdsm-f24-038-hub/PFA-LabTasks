import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader


def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages).strip()


def split_text_chunks(text, source_name):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = splitter.split_text(text)

    result = []
    for chunk in chunks:
        if chunk.strip():
            result.append({
                "page_content": chunk,
                "metadata": {"source": source_name}
            })
    return result


def is_allowed_file(filename):
    return "." in filename and filename.lower().endswith(".pdf")


def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
