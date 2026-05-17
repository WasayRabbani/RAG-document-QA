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
        system_instruction = """You are a technical document expert. Answer questions strictly using the provided context.
        Rules:
        1. Answer ONLY from the provided context. If not found, say: "I don't know based on the provided document."
        2. Give extremely concise answers (1-2 sentences max).
        3. TABLES & MATH: Pay close attention to numeric rows. If you see something like "2.3 x 10^19" or "2.3 ? 10 19", interpret it as scientific notation for training costs/FLOPs.
        4. List page numbers used as sources at the end (e.g., Sources: Page 7)."""

        # Format chunks with page numbers for the LLM
        # Use parent_text (larger context) if available, otherwise fall back to text
        formatted_context = ""
        seen_parents = set()  # Avoid sending duplicate parent chunks
        for chunk in self.chunks:
            context = chunk.get('parent_text', chunk['text'])
            # Deduplicate: if two children share the same parent, only send it once
            if context not in seen_parents:
                formatted_context += f"\n--- Page {chunk['page']} ---\n{context}\n"
                seen_parents.add(context)

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