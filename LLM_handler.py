import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

class LLMHandler:
    def __init__(self, question, chunks):
  
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.question = question
        self.chunks = chunks
        self.model = "llama-3.3-70b-versatile"

    def make_chatbot(self):
        system_instruction = """You are a helpful assistant that answers questions strictly based on the provided context from a document.
        Rules:
        1. Answer ONLY from the provided context.
        2. If the answer is not in the context, say: "I don't know based on the provided document."
        3. Keep answers concise and accurate.
        4. Do not make up any information."""

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Context: {self.chunks} \n\nQuestion: {self.question}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )
        
        return response.choices[0].message.content