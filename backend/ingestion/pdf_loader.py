"""
PDF Loader — Hybrid Strategy:
- Uses pypdf for text extraction (proven to work correctly)
- Uses pdfplumber ONLY for structured table detection
- Applies math symbol repair for broken scientific notation
"""

import re
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

class PDFLoader:
    def __init__(self, pdf_link):
        self.pdf = pdf_link

    def _clean_text(self, text: str) -> str:
        """Fix common PDF character encoding issues for math and tables."""
        if not text:
            return ""
        replacements = {
            "·": "*",
            "×": "x",
            "−": "-",
            "–": "-",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix scientific notation: "10 19" or "10?19" → "10^19"
        text = re.sub(r'(\d)\s*[·\?\*×]\s*10\s*(\d{2})', r'\1 x 10^\2', text)
        return text

    def _should_check_for_tables(self, text: str) -> bool:
        """Fast check to see if a page likely contains a table before running slow extraction."""
        if not text:
            return False
        
        # Keywords that usually signal a table
        table_markers = ["Table ", "TABLE ", "Index", "Summary", "%", "Total"]
        if any(marker in text for marker in table_markers):
            return True
            
        # Or if the page has a high density of numbers
        numbers = re.findall(r'\d+', text)
        if len(numbers) > 15: # High number count usually means data
            return True
            
        return False

    def _format_table_row(self, headers: list, row: list) -> str:
        """Helper to format a single table row into a readable text format."""
        pairs = []
        for h, v in zip(headers, row):
            val = str(v).strip().replace('\n', ' ') if v else ''
            if val:
                pairs.append(f"{h}: {val}" if h else val)
        return " | ".join(pairs)

    def load_pdf(self):
        try:
            reader = PdfReader(self.pdf)
            total_pages = len(reader.pages)
            logger.info(f"Starting extraction of {total_pages} pages...")

            pages_data = []

            # We'll open pdfplumber once to keep it ready
            import pdfplumber
            with pdfplumber.open(self.pdf) as plumber_pdf:
                for i, page in enumerate(reader.pages):
                    page_num = i + 1
                    
                    if page_num % 10 == 0:
                        logger.info(f"  → Processing page {page_num}/{total_pages}...")

                    try:
                        # 1. Fast text extraction using pypdf
                        raw_text = page.extract_text()
                        if not raw_text:
                            continue
                        
                        cleaned_text = self._clean_text(raw_text.strip())
                        table_rows = []

                        # 2. ONLY run slow table extraction if the page looks like it has a table
                        if self._should_check_for_tables(raw_text):
                            plumber_page = plumber_pdf.pages[i]
                            tables = plumber_page.extract_tables()
                            
                            if tables:
                                for table in tables:
                                    if not table or len(table) < 2:
                                        continue
                                    headers = [str(h).strip().replace('\n', ' ') if h else '' for h in table[0]]
                                    # Basic sanity check on headers
                                    if any(h and not h.isspace() for h in headers):
                                        for row in table[1:]:
                                            if not row: continue
                                            formatted = self._format_table_row(headers, row)
                                            if formatted:
                                                table_rows.append("[TABLE ROW] " + formatted)

                        # 3. Combine
                        if table_rows:
                            combined = "\n".join(table_rows) + "\n\n" + cleaned_text
                        else:
                            combined = cleaned_text
                        
                        pages_data.append({"text": combined, "page": page_num})
                        
                    except Exception as e:
                        logger.warning(f"Skipping page {page_num} due to error: {e}")
                        continue
            
            if not pages_data:
                raise ValueError("No text could be extracted.")
                
            logger.info(f"Successfully extracted {len(pages_data)} pages.")
            return pages_data

        except Exception as e:
            logger.error(f"Failed to load PDF {self.pdf}: {e}")
            raise e




""" The main function of this file is to upload A PDF to app and we have to extract all of the data from this PDF so for that purpose we are using libraries Pypdf and PDF Plumber pypdf is used for text because it is exceptionally fast and not good with tables on the other hand we are using pipe lumber for pages that are having tables because it is good with tables but it is slow So first thing is when we extract all of the data we use by PDF and if on any page we encounter a table we switch to PDF plumber once the data has been retrieved clean the data in Cleaning we clean math functions and some scientific notations Then we use another function that's main purpose is to check page hash table if page has a table then we switch to pipe number and another function is used to make sure that the data extracted from the table has its semantic meaning restored Then we have the main function that loads my whole PDF
"""
