---
title: PythonicRAGReact
emoji: 📉
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: apache-2.0
---

# Pythonic RAG with React Frontend

This is a React version of the Pythonic RAG application that allows users to chat with their text files. The application uses a FastAPI backend for handling file uploads and queries, and a React frontend for the user interface.

## Features

- File upload support for text files
- Real-time chat interface
- Vector database for efficient text retrieval
- OpenAI integration for intelligent responses

## Architecture

The application consists of two main components:

1. Backend (FastAPI):
   - Handles file uploads
   - Processes text using RAG (Retrieval Augmented Generation)
   - Manages vector database
   - Integrates with OpenAI

2. Frontend (React):
   - Modern user interface
   - Real-time chat functionality
   - File upload component
   - Response streaming

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up environment variables:
   ```
   OPENAI_API_KEY=your_api_key
   ```

4. Run the application:
   ```bash
   # Backend
   uvicorn app:app --reload

   # Frontend
   npm start
   ```

## Deployment

The application is deployed on Hugging Face Spaces using Docker. The Dockerfile combines both frontend and backend services into a single container.

## License

Apache 2.0
