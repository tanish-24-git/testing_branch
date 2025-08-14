from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from src.config import config
import logging

logger = logging.getLogger(__name__)

class RAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        loader = DirectoryLoader(config.get('rag', {}).get('docs_dir', 'docs'))
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)

    def retrieve(self, query):
        results = self.vectorstore.similarity_search(query, k=3)
        return [doc.page_content for doc in results]