from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
import openai
from typing import List, Dict, Any
import os
import asyncio


class ChatOpenAI:
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.async_client = AsyncOpenAI()
        self.client = OpenAI()

        if self.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. Please set it to your OpenAI API key."
            )
        openai.api_key = self.openai_api_key
        self.model_name = model_name

    async def agenerate(self, messages: List[Dict[str, str]]) -> str:
        chat_completion = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
        )

        return chat_completion.choices[0].message.content

    async def astream(self, messages: List[Dict[str, str]]):
        stream = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def generate(self, messages: List[Dict[str, str]]) -> str:
        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
        )

        return chat_completion.choices[0].message.content 