---
title: PythonicRAG
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# PythonicRAG

A RAG (Retrieval-Augmented Generation) application that allows you to upload PDF documents and ask questions about their content.

## Features

- Upload PDF documents
- Ask questions about the content
- Get AI-powered answers with relevant context
- Modern React frontend with Material UI
- FastAPI backend with vector search

## How to Use

1. Upload a PDF document (up to 2MB in size)
2. Wait for the document to be processed
3. Ask questions about the content
4. View the answers and relevant context

## Environment Variables

The following environment variables need to be set in the Hugging Face Space settings:

- `OPENAI_API_KEY`: Your OpenAI API key for the AI model

## Technical Details

- Frontend: React with Material UI
- Backend: FastAPI with vector search
- Database: Vector database for semantic search
- AI Model: OpenAI's GPT model

## Local Development

To run locally:

1. Clone the repository
2. Install dependencies:
   ```bash
   cd frontend && npm install
   cd ../backend && pip install -r requirements.txt
   ```
3. Set environment variables
4. Run the services:
   ```bash
   # Terminal 1 (Backend)
   cd backend && uvicorn main:app --host 0.0.0.0 --port 7860
   
   # Terminal 2 (Frontend)
   cd frontend && npm start
   ```

## License

MIT
