from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from src.config import config
import logging
import os

logger = logging.getLogger(__name__)

class RAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        docs_dir = config.get('rag', {}).get('docs_dir', 'docs')
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            logger.warning(f"Created empty {docs_dir} directory as it did not exist")
        loader = DirectoryLoader(docs_dir)
        documents = loader.load()
        if not documents:
            logger.warning("No documents found in docs directory, using placeholder")
            self.vectorstore = FAISS.from_texts(["No documents available"], self.embeddings)
        else:
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            self.vectorstore = FAISS.from_documents(texts, self.embeddings)

    def retrieve(self, query):
        results = self.vectorstore.similarity_search(query, k=3)
        return [doc.page_content for doc in results]