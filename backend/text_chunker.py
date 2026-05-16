"""
Smart Chunking Strategy:
1. Scan each page for "table-like" regions (rows of numbers/short columns)
2. Extract those as a single preserved chunk with a clear label
3. Run regular RecursiveCharacterTextSplitter on remaining prose text
4. Combine both into the final chunk list
"""

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self, extracted_pages):
        # extracted_pages is a list of {"text": ..., "page": ...}
        self.pages = extracted_pages
    
    def _is_table_line(self, line: str) -> bool:
        """
        Heuristic: A line is "table-like" if it contains multiple
        numeric values or tab/multi-space separated short tokens.
        """
        stripped = line.strip()
        if not stripped:
            return False
        # Count numeric tokens (integers, floats, percentages)
        numeric_tokens = re.findall(r'\b\d+\.?\d*\b', stripped)
        total_tokens = stripped.split()
        # If >30% of tokens are numbers AND line has >= 3 tokens, it's table-like
        if len(total_tokens) >= 3 and len(numeric_tokens) >= 2:
            return True
        return False

    def _extract_tables(self, text: str, page_num: int):
        """
        Walk through the lines of a page and group consecutive
        table-like lines into a single preserved chunk.
        Returns (table_chunks, remaining_text).
        """
        lines = text.split('\n')
        table_chunks = []
        remaining_lines = []
        
        buffer = []  # accumulate consecutive table lines
        
        for line in lines:
            if self._is_table_line(line):
                buffer.append(line)
            else:
                if buffer:
                    # We have a complete table block — save it
                    table_text = "[TABLE DATA]\n" + "\n".join(buffer)
                    table_chunks.append({"text": table_text, "page": page_num})
                    buffer = []
                remaining_lines.append(line)
        
        # Don't forget the last buffer
        if buffer:
            table_text = "[TABLE DATA]\n" + "\n".join(buffer)
            table_chunks.append({"text": table_text, "page": page_num})
        
        return table_chunks, "\n".join(remaining_lines)

    def chunking(self):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len
        )
        
        final_chunks = []
        
        for page in self.pages:
            # 1. Extract table blocks first (preserved as single chunks)
            table_chunks, remaining_text = self._extract_tables(
                page["text"], page["page"]
            )
            final_chunks.extend(table_chunks)
            
            # 2. Chunk the remaining prose text normally
            if remaining_text.strip():
                prose_chunks = splitter.split_text(remaining_text)
                for chunk in prose_chunks:
                    final_chunks.append({
                        "text": chunk,
                        "page": page["page"]
                    })
                
        return final_chunks
