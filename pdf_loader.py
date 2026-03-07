"""
1. PDF ka path lo
2. PDF kholo
3. Har page ka text nikalo
4. Sab pages ka text combine karo
5. Return karo     """



from pypdf import PdfReader

class PDFLoader:
    def __init__(self,pdf_link):   #Constructor to automatically give link of pdf
        self.pdf=pdf_link
    
    def load_pdf(self):
        
        loaded_pdf=PdfReader(self.pdf)  # loads pdf from link
        
        extracted_text=[]                # makes a list where we will extract all text of pdf
        
        for pages in loaded_pdf.pages:  # load all pages from pdf using .pages property
            extracted_text.append(pages.extract_text())  # saves text from every page to list
        
        return extracted_text  # return all extracted text



link=r"D:\IDM Files\sample.pdf"
p1=PDFLoader(link)

print(p1.load_pdf())
