from chromadb import PersistentClient
from models import embeddings

db = PersistentClient(path="./Assignment_11-RAG")
collection = db.get_or_create_collection("resume")


def add_resume(resume_id, resume_text, embedings, metadata):
    ids = [f"{resume_id}__chunk__{i}" for i in range(len(resume_text))]

    collection.add(
        ids=ids,
        documents=resume_text,
        embeddings=embedings,
        metadatas=metadata
    )


def query_search(query, top_k=5):
    query_vector = embeddings([query])[0]

    return collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )


def delete_resume(resume_id):
    collection.delete(where={"resume_id": resume_id})


def get_all_resumes(limit=100):
    return collection.get(limit=limit)
