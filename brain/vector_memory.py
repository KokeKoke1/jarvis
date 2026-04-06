import faiss
import numpy as np
import json
import os
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
HISTORY_FILE = "memory/history.json"

client = OpenAI()  # Podłącz swoje API OpenAI lub Claude API

class VectorMemory:
    def __init__(self, dim=1536):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, text, meta=None):
        embedding = self.get_embedding(text)
        self.index.add(np.array([embedding], dtype='float32'))
        self.metadata.append(meta or {"text": text})
        self.save()

    def query(self, text, k=5):
        if self.index.ntotal == 0:
            return []
        embedding = self.get_embedding(text)
        D, I = self.index.search(np.array([embedding], dtype='float32'), k)
        return [self.metadata[i] for i in I[0] if i < len(self.metadata)]

    def get_embedding(self, text):
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return np.array(resp.data[0].embedding, dtype='float32')

    def save(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        data = {
            "meta": self.metadata,
            "index": self.index_to_list()
        }
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                self.metadata = data.get("meta", [])
                self.list_to_index(data.get("index", []))

    def index_to_list(self):
        if self.index.ntotal > 0:
            return self.index.reconstruct_n(0, self.index.ntotal).tolist()
        return []

    def list_to_index(self, arr):
        if arr:
            embeddings = np.array(arr, dtype='float32')
            self.index.add(embeddings)

# Singleton
MEMORY = VectorMemory()
MEMORY.load()