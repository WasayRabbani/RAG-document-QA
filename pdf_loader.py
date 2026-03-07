"""
1. PDF ka path lo
2. PDF kholo
3. Har page ka text nikalo
4. Sab pages ka text combine karo
5. Return karo     """


# import pdf_loader

from pypdf import PdfReader

class PDFLoader:
    
    def __init__(self,my_path):
     self.path=my_path
     
    def load_pdf(self):
        reader=PdfReader(self.path)
        pages=[]

page=PDFLoader()
page