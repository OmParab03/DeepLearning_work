from langchain.embeddings import init_embeddings
from typing import List

embed_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="dummy_api",
    check_embedding_ctx_length=False,
)

def embeddings(texts: List[str]) -> List[list[float]]:
    if not texts:
        return []
    return embed_model.embed_documents(texts)
