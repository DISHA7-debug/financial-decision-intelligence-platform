from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

from utils.pdf_utils import extract_pdf_text
from utils.chunking import chunk_text


PDF_FOLDER = "data/raw"


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

all_chunks = []
all_metadata = []


for filename in os.listdir(PDF_FOLDER):

    if not filename.endswith(".pdf"):
        continue

    pdf_path = os.path.join(
        PDF_FOLDER,
        filename
    )

    print(
        f"Processing {filename}"
    )

    text = extract_pdf_text(
        pdf_path
    )

    chunks = chunk_text(
        text
    )

    company = (
        filename
        .replace("_10k.pdf", "")
        .capitalize()
    )

    for chunk in chunks:

        all_chunks.append(
            chunk
        )

        all_metadata.append(
            {
                "company": company,
                "source": filename,
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
    "indexing/faiss_index/knowledge_base.index"
)

with open(
    "indexing/metadata/knowledge_base.pkl",
    "wb"
) as f:

    pickle.dump(
        all_metadata,
        f
    )

print(
    "\nKnowledge Base Built Successfully"
)