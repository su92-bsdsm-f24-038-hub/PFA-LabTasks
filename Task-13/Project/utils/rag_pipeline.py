import os

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from openai import OpenAI

from utils.embeddings import get_embeddings_model


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
INDEX_ROOT = os.path.join(UPLOAD_DIR, "faiss")


def get_user_index_path(user_id):
    return os.path.join(INDEX_ROOT, f"user_{user_id}")


def to_documents(chunks):
    docs = []
    for item in chunks:
        doc = Document(page_content=item["page_content"], metadata=item.get("metadata", {}))
        docs.append(doc)
    return docs


def add_user_documents(user_id, chunks):
    if not chunks:
        return 0

    if not os.path.exists(INDEX_ROOT):
        os.makedirs(INDEX_ROOT)

    index_path = get_user_index_path(user_id)
    embeddings = get_embeddings_model()
    docs = to_documents(chunks)

    if os.path.exists(index_path):
        vectordb = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        vectordb.add_documents(docs)
    else:
        vectordb = FAISS.from_documents(docs, embeddings)

    vectordb.save_local(index_path)
    return len(docs)


def extractive_fallback(question, docs):
    if not docs:
        return "I could not find relevant information in your uploaded documents."

    snippets = []
    for doc in docs:
        if doc.page_content.strip():
            snippets.append(doc.page_content.strip())

    if not snippets:
        return "I could not find relevant information in your uploaded documents."

    # joining top 3 snipets
    joined = "\n\n".join(snippets[:3])
    return (
        "I could not access an online LLM provider, so here are the most relevant "
        "document excerpts to answer your question:\n\n"
        f"Question: {question}\n\n{joined}"
    )


def get_openai_answer(question, context_text):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "You are a business support AI assistant. Answer strictly from provided context. If details are missing from context, clearly say so."
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion:\n{question}"
            }
        ]
    )

    content = response.choices[0].message.content if response.choices else None
    if content:
        return content.strip()
    return None


def answer_question(user_id, question):
    index_path = get_user_index_path(user_id)

    if not os.path.exists(index_path):
        return "Please upload at least one PDF first so I can answer based on your documents.", []

    embeddings = get_embeddings_model()
    vectordb = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    retrived_docs = retriever.get_relevant_documents(question)

    context_text = "\n\n".join(doc.page_content for doc in retrived_docs)

    source_chunks = []
    for doc in retrived_docs:
        source_chunks.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "uploaded_document")
        })

    answer = get_openai_answer(question, context_text)
    if not answer:
        answer = extractive_fallback(question, retrived_docs)

    if not answer:
        answer = "I could not generate a response. Please try again."

    return answer, source_chunks
