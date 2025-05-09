```markdown
# RAG-Based Question-Answering Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on provided documents, implemented in Python and containerized with Docker.

## Setup Instructions

### Prerequisites
- Docker installed on your system
- Sample documents in PDF or TXT format

### Building the Docker Image
1. Clone the repository or copy the project files to a directory.
2. Place your documents in the `documents/` directory.
3. Build the Docker image:
   ```bash
   docker build -t rag-chatbot .
   ```

### Running the Container
Run the container, mapping port 8000:
```bash
docker run -d -p 8000:8000 -v $(pwd)/documents:/app/documents rag-chatbot
```

## API Usage
The API is available at `http://localhost:8000`.

### Endpoints
- **POST /ask**: Submit a question
  - Body: `{"question": "Your question here", "top_k": 3}`
  - Response: Answer and relevant document chunks
- **GET /health**: Check API status

### Example Request
```bash
curl -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the capital of France?", "top_k": 3}'
```

### Example Response
```json
{
  "answer": "The capital of France is Paris.",
  "relevant_chunks": [
    {
      "text": "France is a country in Europe. Its capital is Paris.",
      "metadata": {"filename": "france.txt", "chunk_id": 0},
      "distance": 0.123
    },
    ...
  ]
}
```

## Sample Documents
Place your documents in the `documents/` directory. Supported formats:
- PDF
- TXT

Example document (`sample.txt`):
```
France is a country in Europe. Its capital is Paris.
```

## Testing Script
```bash
# test.sh
curl -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the capital of France?", "top_k": 3}'
```

## Notes
- The system uses FAISS for vector search and Sentence Transformers for embeddings.
- DistilGPT2 is used as the LLM for simplicity; consider using a more powerful model for production.
- Documents are processed on startup; add new documents to the `documents/` directory and restart the container.
```


```x-shellscript
```bash
#!/bin/bash
curl -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the capital of France?", "top_k": 3}'
```
```

</xaiArtifact>