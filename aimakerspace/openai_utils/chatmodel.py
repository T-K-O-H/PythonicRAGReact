from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class ChatOpenAI:
    def __init__(self, model_name: str = "gpt-4-1106-preview"):
        self.model_name = model_name
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI()
        self.async_client = AsyncOpenAI()

    def run(self, messages, text_only: bool = True, **kwargs):
        if not isinstance(messages, list):
            raise ValueError("messages must be a list")

        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, **kwargs
        )

        if text_only:
            return response.choices[0].message.content

        return response
    
    async def agenerate(self, messages, **kwargs):
        if not isinstance(messages, list):
            raise ValueError("messages must be a list")

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system" if i == 0 else "user", "content": msg} for i, msg in enumerate(messages)],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in agenerate: {str(e)}")
            raise
    
    async def astream(self, messages, **kwargs):
        if not isinstance(messages, list):
            raise ValueError("messages must be a list")

        stream = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
