"""
1. PDF ka path lo
2. PDF kholo
3. Har page ka text nikalo
4. Sab pages ka text combine karo
5. Return karo"""

from pypdf import PdfReader
import logging

class PDFLoader:
    def __init__(self, pdf_link):
        self.pdf = pdf_link

    def load_pdf(self):
        try:
            loaded_pdf = PdfReader(self.pdf)
            
            if loaded_pdf.is_encrypted:
                raise ValueError(f"Error: {self.pdf} is encrypted.")

            pages_data = [] # List of dicts: {"text": str, "page": int}

            for i, page in enumerate(loaded_pdf.pages):
                try:
                    text = page.extract_text()
                    if text:
                        # We store 1-based page numbers for users
                        pages_data.append({"text": text.strip(), "page": i + 1})
                except Exception as e:
                    logging.warning(f"Could not extract text from page {i+1}: {e}")
                    continue
            
            if not pages_data:
                raise ValueError("No text could be extracted.")
                
            return pages_data

        except Exception as e:
            logging.error(f"Failed to load PDF {self.pdf}: {e}")
            raise e


# link = r"sample.pdf"
# p1 = PDFLoader(link)

# print(p1.load_pdf())
