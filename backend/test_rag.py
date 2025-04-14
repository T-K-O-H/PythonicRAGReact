import os
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt
import asyncio

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

class RetrievalAugmentedQAPipeline:
    def __init__(self, llm: ChatOpenAI, vector_db_retriever: VectorDatabase) -> None:
        self.llm = llm
        self.vector_db_retriever = vector_db_retriever

    async def arun_pipeline(self, user_query: str):
        context_list = self.vector_db_retriever.search_by_text(user_query, k=4)

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

async def test_rag_pipeline(text_path: str, test_query: str):
    print("1. Loading text file...")
    loader = TextFileLoader(text_path)
    documents = loader.load_documents()
    print(f"Loaded {len(documents)} documents")
    
    print("\n2. Splitting text...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_texts(documents)
    print(f"Split into {len(texts)} chunks")
    
    print("\n3. Creating vector database...")
    vector_db = VectorDatabase()
    vector_db = await vector_db.abuild_from_list(texts)
    print("Vector database created")
    
    print("\n4. Testing search...")
    results = vector_db.search_by_text(test_query, k=3)
    print(f"Found {len(results)} relevant chunks")
    for i, (text, score) in enumerate(results):
        print(f"\nChunk {i+1} (score: {score:.4f}):")
        print(text[:200] + "...")
    
    print("\n5. Testing full pipeline...")
    chat_openai = ChatOpenAI()
    pipeline = RetrievalAugmentedQAPipeline(
        vector_db_retriever=vector_db,
        llm=chat_openai
    )
    
    result = await pipeline.arun_pipeline(test_query)
    print("\nResponse:")
    print(result["response"])
    print("\nContext used:")
    for i, (text, score) in enumerate(result["context"]):
        print(f"\nContext {i+1} (score: {score:.4f}):")
        print(text[:200] + "...")

if __name__ == "__main__":
    # Test with our sample text file
    text_path = "test.txt"
    test_query = "What are the main applications of AI and ML?"
    
    asyncio.run(test_rag_pipeline(text_path, test_query)) 