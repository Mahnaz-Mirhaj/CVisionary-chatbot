import faiss
import numpy as np
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Settings



embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")  # "BAAI/bge-small-en-v1.5"
documents = SimpleDirectoryReader("./data/DE").load_data()
Settings.chunk_size = 512
Settings.chunk_overlap = 50
embeddings = [embed_model.get_text_embedding(doc.text) for doc in documents]

embedding_dim = len(embeddings[0])
embedding_matrix = np.array(embeddings).astype(np.float32)

faiss_index = faiss.IndexFlatL2(embedding_dim)

faiss_index.add(embedding_matrix)
faiss.write_index(faiss_index, "faiss_index_de.index")

print("FAISS index built and saved!")

