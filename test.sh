#!/bin/bash
curl -X POST http://localhost:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is the capital of France?", "top_k": 3}'
