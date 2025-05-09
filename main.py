import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline
import logging
import glob

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API")

# Initialize models and FAISS index
embedder = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # Embedding dimension for all-MiniLM-L6-v2
index = faiss.IndexFlatL2(dimension)
documents = []
metadata = []

# Initialize LLM
llm_pipeline = pipeline(
    "text-generation",
    model="distilgpt2",
    max_length=200,
    truncation=True
)
llm = HuggingFacePipeline(pipeline=llm_pipeline)

# Prompt template for RAG
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="Context: {context}\n\nQuestion: {question}\nAnswer:"
)

rag_chain = LLMChain(llm=llm, prompt=prompt_template)

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {str(e)}")
        return ""

def process_documents(directory="./documents"):
    global documents, metadata
    documents = []
    metadata = []
    
    # Supported file types
    file_types = ["*.pdf", "*.txt"]
    files = []
    for file_type in file_types:
        files.extend(glob.glob(os.path.join(directory, file_type)))
    
    for file_path in files:
        if file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:  # txt
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Simple chunking
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadata.append({
                "filename": os.path.basename(file_path),
                "chunk_id": i
            })
    
    # Generate embeddings
    embeddings = embedder.encode(documents, show_progress_bar=True)
    
    # Reset and populate FAISS index
    index.reset()
    index.add(np.array(embeddings, dtype=np.float32))
    
    logger.info(f"Processed {len(documents)} document chunks")

@app.on_event("startup")
async def startup_event():
    # Process documents on startup
    os.makedirs("./documents", exist_ok=True)
    process_documents()

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Embed the question
        question_embedding = embedder.encode([request.question])[0]
        
        # Search FAISS index
        distances, indices = index.search(
            np.array([question_embedding], dtype=np.float32),
            request.top_k
        )
        
        # Retrieve relevant chunks
        context = ""
        for idx in indices[0]:
            context += documents[idx] + "\n\n"
        
        # Generate answer
        response = rag_chain.run(
            context=context,
            question=request.question
        )
        
        return {
            "answer": response,
            "relevant_chunks": [
                {
                    "text": documents[idx],
                    "metadata": metadata[idx],
                    "distance": float(distances[0][i])
                }
                for i, idx in enumerate(indices[0])
            ]
        }
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


