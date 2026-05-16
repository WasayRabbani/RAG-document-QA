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
        1. Answer ONLY from the provided context. If the answer is not in the context, say: "I don't know based on the provided document."
        2. Give extremely concise answers. Keep your response to 1-2 sentences maximum, straight to the point. Do not add fluff or introductory phrases.
        3. At the end of your answer, you MUST list the page numbers used as sources (e.g., Sources: Page 1, Page 5)."""

        # Format chunks with page numbers for the LLM
        formatted_context = ""
        for chunk in self.chunks:
            formatted_context += f"\n--- Page {chunk['page']} ---\n{chunk['text']}\n"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Context: {formatted_context} \n\nQuestion: {self.question}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )
        
        return response.choices[0].message.content