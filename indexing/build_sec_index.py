import os
import pickle
import faiss
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

from nodes.node0_sec import (
    run_sec_ingestion
)

from utils.chunking import (
    chunk_text
)


COMPANIES = [
    "Apple",
    "Microsoft",
    "Nvidia",
    "Tesla",
    "Amazon"
]

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

all_chunks = []
all_metadata = []

for company in COMPANIES:

    print(
        f"Processing {company}"
    )

    filing_text = (
        run_sec_ingestion(
            company
        )
    )

    chunks = chunk_text(
        filing_text
    )

    for chunk in chunks:

        all_chunks.append(
            chunk
        )

        all_metadata.append(
            {
                "company": company,
                "source": "SEC_10K",
                "text": chunk
            }
        )

print(
    f"\nTotal Chunks: {len(all_chunks)}"
)

embeddings = model.encode(
    all_chunks,
    show_progress_bar=True
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    np.array(
        embeddings,
        dtype=np.float32
    )
)

faiss.write_index(
    index,
    "indexing/faiss_index/sec_knowledge_base.index"
)

with open(
    "indexing/metadata/sec_knowledge_base.pkl",
    "wb"
) as f:

    pickle.dump(
        all_metadata,
        f
    )

print(
    "\nSEC Knowledge Base Built"
)