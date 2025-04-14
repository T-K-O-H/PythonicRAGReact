from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from aimakerspace.text_utils import CharacterTextSplitter, TextFileLoader, PDFLoader
from aimakerspace.openai_utils.prompts import (
    UserRolePrompt,
    SystemRolePrompt,
)
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
import tempfile
import shutil
import os
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize application state
app.state.pipeline = None
app.state.vector_db = None
app.state.llm = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
text_splitter = CharacterTextSplitter()
system_template = """\
Use the following context to answer a users question. If you cannot find the answer in the context, say you don't know the answer."""
system_role_prompt = SystemRolePrompt(system_template)
user_prompt_template = """\
Context:
{context}

Question:
{question}
"""
user_role_prompt = UserRolePrompt(user_prompt_template)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

class RetrievalAugmentedQAPipeline:
    def __init__(self, llm: ChatOpenAI, vector_db_retriever: VectorDatabase) -> None:
        self.llm = llm
        self.vector_db_retriever = vector_db_retriever

    async def arun_pipeline(self, user_query: str):
        context_list = await self.vector_db_retriever.search_by_text(user_query, k=4)

        context_prompt = ""
        for context in context_list:
            context_prompt += context[0] + "\n"

        formatted_system_prompt = system_role_prompt.create_message()
        formatted_user_prompt = user_role_prompt.create_message(
            question=user_query, 
            context=context_prompt
        )

        response = await self.llm.agenerate([formatted_system_prompt, formatted_user_prompt])
        return {"response": response, "context": context_list}

class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_file_path = None
    try:
        print("Starting file upload process...")  # Debug log
        print(f"Received file: {file.filename}")  # Debug log
        
        # Create a temporary file with the correct extension
        suffix = f".{file.filename.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            print(f"Created temporary file: {temp_file_path}")  # Debug log
            print(f"File exists: {os.path.exists(temp_file_path)}")  # Debug log
            print(f"File size: {os.path.getsize(temp_file_path)}")  # Debug log

        # Create appropriate loader
        try:
            if file.filename.lower().endswith('.pdf'):
                print("Using PDF loader")  # Debug log
                loader = PDFLoader(temp_file_path)
            else:
                print("Using text file loader")  # Debug log
                raise HTTPException(status_code=400, detail="Only PDF files are supported")

            # Load and process the documents
            print("Loading documents...")  # Debug log
            documents = loader.load_documents()
            print(f"Loaded {len(documents)} documents")  # Debug log
            
            if not documents:
                raise ValueError("No text could be extracted from the document")
            
            # Split text into chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_texts(documents)
            print(f"Split into {len(texts)} text chunks")  # Debug log
            
            if not texts:
                raise ValueError("No text chunks were generated from the document")

        except Exception as e:
            print(f"Error processing document: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

        # Create vector store
        print("Creating vector database...")  # Debug log
        try:
            vector_db = VectorDatabase()
            print("VectorDatabase initialized")  # Debug log
            vector_db = await vector_db.abuild_from_list(texts)
            print("Vector database created successfully")  # Debug log
            app.state.vector_db = vector_db  # Store vector_db in application state
        except Exception as e:
            print(f"Error creating vector database: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Error creating vector database: {str(e)}")
        
        # Initialize chat model
        print("Initializing chat model...")  # Debug log
        try:
            chat_openai = ChatOpenAI()
            print("ChatOpenAI initialized")  # Debug log
            app.state.llm = chat_openai  # Store llm in application state
        except Exception as e:
            print(f"Error initializing chat model: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Error initializing chat model: {str(e)}")

        # Create pipeline
        print("Creating pipeline...")  # Debug log
        try:
            pipeline = RetrievalAugmentedQAPipeline(
                vector_db_retriever=vector_db,
                llm=chat_openai
            )
            print("Pipeline created successfully")  # Debug log
            app.state.pipeline = pipeline  # Store pipeline in application state
        except Exception as e:
            print(f"Error creating pipeline: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Error creating pipeline: {str(e)}")

        return {"message": "File processed successfully", "num_chunks": len(texts)}

    except Exception as e:
        print(f"Error in upload_file: {str(e)}")  # Debug log
        print(f"Error type: {type(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print("Temporary file cleaned up")  # Debug log
            except Exception as e:
                print(f"Error cleaning up temporary file: {str(e)}")  # Debug log

@app.post("/query")
async def query_document(request: QueryRequest):
    try:
        print("Starting query processing...")  # Debug log
        # Get the pipeline from application state
        pipeline = app.state.pipeline
        if not pipeline:
            print("No pipeline found in application state")  # Debug log
            # Try to recreate pipeline from stored components
            if app.state.vector_db and app.state.llm:
                print("Recreating pipeline from stored components")  # Debug log
                pipeline = RetrievalAugmentedQAPipeline(
                    vector_db_retriever=app.state.vector_db,
                    llm=app.state.llm
                )
                app.state.pipeline = pipeline
            else:
                raise HTTPException(status_code=400, detail="No document has been uploaded yet")

        print(f"Processing query: {request.query}")  # Debug log
        print(f"Pipeline state: {pipeline}")  # Debug log
        
        try:
            result = await pipeline.arun_pipeline(request.query)
            print(f"Query result: {result}")  # Debug log
            return result
        except Exception as pipeline_error:
            print(f"Pipeline error: {str(pipeline_error)}")  # Debug log
            print(f"Pipeline error type: {type(pipeline_error)}")  # Debug log
            import traceback
            print(f"Pipeline traceback: {traceback.format_exc()}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Pipeline error: {str(pipeline_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in query_document: {str(e)}")  # Debug log
        print(f"Error type: {type(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

class VectorDatabase:
    def __init__(self):
        print("Initializing VectorDatabase...")  # Debug log
        try:
            self.embedding_model = EmbeddingModel()
            print("EmbeddingModel initialized")  # Debug log
            self.embeddings = []
            self.texts = []
        except Exception as e:
            print(f"Error initializing VectorDatabase: {str(e)}")  # Debug log
            raise

    async def abuild_from_list(self, texts: List[str]):
        try:
            print(f"Building vector database from {len(texts)} texts")  # Debug log
            self.texts = texts
            print("Generating embeddings...")  # Debug log
            self.embeddings = await self.embedding_model.aembed_documents(texts)
            print(f"Generated {len(self.embeddings)} embeddings")  # Debug log
            return self
        except Exception as e:
            print(f"Error building vector database: {str(e)}")  # Debug log
            raise

    async def search_by_text(self, query: str, k: int = 4):
        try:
            print(f"Searching for query: {query}")  # Debug log
            query_embedding = await self.embedding_model.embed_query(query)
            print("Generated query embedding")  # Debug log
            
            # Calculate similarities
            similarities = []
            for i, embedding in enumerate(self.embeddings):
                similarity = self._cosine_similarity(query_embedding, embedding)
                similarities.append((self.texts[i], similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            print(f"Found {len(similarities)} matches")  # Debug log
            return similarities[:k]
        except Exception as e:
            print(f"Error in search_by_text: {str(e)}")  # Debug log
            raise

    def _cosine_similarity(self, a, b):
        try:
            import numpy as np
            a = np.array(a)
            b = np.array(b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except Exception as e:
            print(f"Error calculating cosine similarity: {str(e)}")  # Debug log
            raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 