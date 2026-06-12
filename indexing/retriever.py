import faiss
import pickle
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

index = faiss.read_index(
    "indexing/faiss_index/sec_knowledge_base.index"
)

with open(
    "indexing/metadata/sec_knowledge_base.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)


def retrieve(
    query: str,
    company: str = None,
    top_k: int = 5
):

    query_embedding = model.encode(
        [query]
    )

    distances, indices = index.search(
        np.array(
            query_embedding,
            dtype=np.float32
        ),
        50
    )

    results = []

    for idx in indices[0]:

        chunk = metadata[idx]

        if (
            company
            and chunk["company"].lower()
            != company.lower()
        ):
            continue

        results.append(
            chunk
        )

        if len(results) >= top_k:
            break

    return results