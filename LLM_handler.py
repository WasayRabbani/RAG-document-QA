from gemini_client import get_client
from google.genai import types

class LLMHandler:
    def __init__(self,question,chunks):
        
        self.client=get_client()
        self.question=question
        self.chunks=chunks
        
    def make_chatbot(self):
        self.chat=self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction="""You are a helpful assistant that answers questions strictly based on the provided context from a document.
                Rules:
                1. Answer ONLY from the provided context.
                2. If the answer is not in the context, say: "I don't know based on the provided document."
                3. Keep answers concise and accurate.
                4. Do not make up any information."""))
        
        message = f"""Context:{self.chunks} Question: {self.question}"""
        
        response=self.chat.send_message(message)
        return response.text
        
        