"""
Smart Chunking Strategy:
1. Detect [TABLE ROW] entries (from pdf_loader's pdfplumber) → each as its own chunk
2. Everything else goes through Parent-Child chunking:
   - Parent: 2000 chars (sent to LLM for full context)
   - Child: 500 chars (used for precise FAISS search)
   - Each child gets a CONTEXT PREFIX from its parent's first sentence
     so even pure-number children are searchable
"""

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self, extracted_pages):
        self.pages = extracted_pages

    def _extract_context_prefix(self, parent_text: str) -> str:
        """
        Extract the first meaningful sentence/heading from a parent chunk.
        This gets prepended to every child so numeric-only children
        become searchable (e.g., "Table 3: Variations on the Transformer...").
        """
        # Try to get the first sentence (up to first period followed by space)
        match = re.match(r'^(.+?\.)\s', parent_text, re.DOTALL)
        if match:
            prefix = match.group(1).strip()
            # Keep it short — max 120 chars
            if len(prefix) > 120:
                prefix = prefix[:120] + "..."
            return f"[Context: {prefix}] "
        
        # Fallback: first line
        first_line = parent_text.split('\n')[0].strip()
        if first_line and len(first_line) > 5:
            if len(first_line) > 120:
                first_line = first_line[:120] + "..."
            return f"[Context: {first_line}] "
        
        return ""

    def chunking(self):
        # PARENT splitter: large chunks for rich context
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len
        )

        # CHILD splitter: small chunks for precise search
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len
        )

        final_chunks = []

        for page in self.pages:
            text = page["text"]
            page_num = page["page"]

            # 1. Extract pre-formatted [TABLE ROW] lines (from pdfplumber)
            lines = text.split('\n')
            table_rows = []
            prose_lines = []

            for line in lines:
                if line.strip().startswith("[TABLE ROW]"):
                    table_rows.append(line.strip())
                else:
                    prose_lines.append(line)

            # Each [TABLE ROW] becomes its own self-contained chunk
            for row in table_rows:
                final_chunks.append({
                    "text": row,
                    "parent_text": row,
                    "page": page_num
                })

            # 2. Parent-Child chunking for ALL remaining text
            remaining_text = "\n".join(prose_lines)
            if remaining_text.strip():
                parent_chunks = parent_splitter.split_text(remaining_text)

                for parent_text in parent_chunks:
                    # Extract a context prefix from the parent's first sentence
                    context_prefix = self._extract_context_prefix(parent_text)
                    children = child_splitter.split_text(parent_text)

                    for child_text in children:
                        # Prepend the context prefix to the child's search text
                        # so pure-number chunks become findable
                        searchable_text = context_prefix + child_text

                        final_chunks.append({
                            "text": searchable_text,  # Used for SEARCH (has context)
                            "parent_text": parent_text,  # Used for LLM (full context)
                            "page": page_num
                        })

        return final_chunks
