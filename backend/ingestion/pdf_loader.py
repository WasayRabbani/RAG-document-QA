'''
## PDF Ingestion Pipeline — Workflow

1. **Load PDF Files**  
   Accept a single PDF file or a directory containing multiple PDFs and open each file for processing.

2. **Extract Page Content**  
   Use `pypdf` to extract text from each page while preserving page numbers and document references.

3. **Extract Document and Page Metadata**  
   Collect available PDF metadata, including filename, document properties, page count, and relevant page-level information.

4. **Extract Tables Separately**  
   Use `pdfplumber` to extract tables independently from the body text, avoiding duplicate extraction of narrative content.

5. **Structure the Extracted Data**  
   Organize the extracted text, tables, and metadata into a consistent, page-wise JSON structure.

6. **Validate Extraction Results**  
   Check for missing pages, empty text, extraction errors, incomplete tables, and missing metadata. Record warnings where applicable.

7. **Process All Pages and Documents**  
   Repeat the extraction, structuring, and validation steps for every page in each PDF file.

8. **Save the Final JSON Output**  
   Save the structured data with document identifiers, filenames, page numbers, and table or paragraph references to support traceability and downstream RAG evaluation.
'''



from pathlib import Path
from pypdf import PdfReader
import pdfplumber

class PDFLoader:
    # constructor should load the pdf and it loads multiple pdfs
    def __init__(self, path: str):
        self.path=Path(path)

        if self.path.is_file():
            self.pdf_files=[self.path]
        else:
                  self.pdf_files=list(self.path.glob("*.pdf"))
        
        # for pdf in self.pdf_files:
        #     print(pdf.name) prints names of all pdfs ina folder
        # print(self.pdf_files[0]) Shows complete link to a pdf




    def extract_text(self):


        for pdf in self.pdf_files:
            reader=PdfReader(pdf)
            
            for page in reader.pages:
                text=page.extract_text()
                print(text)
           
    def extract_metadata(self):

      documents={}


        # Getting page level meta data
      for pdf in self.pdf_files:
            reader=PdfReader(pdf)


            documents[pdf.name]={
            "file_name":pdf.name,
            "pages":[]
         }
            
            for page_num,page in enumerate(reader.pages,start=1):
                text=page.extract_text() or ""
            
                metadata={
                   
                    "page_num":page_num,
                    "text":text,
                    "character_count":len(text)
                }
                documents[pdf.name]['pages'].append(metadata)
      return documents



    def extract_tables(self):
      documents={}
      for pdf in self.pdf_files:


            documents[pdf.name]={
               'file_name':pdf.name,
               'pages':{}
            }
            with pdfplumber.open(pdf) as file:
               for page_num,page in enumerate(file.pages,start=1):
                  tables=page.extract_tables()
                  if tables:
                     documents[pdf.name]['pages'][page_num]=[
                        {
                           'table_num':table_num,
                           'data':table
                        }
                        for table_num,table in enumerate(tables,start=1)
                     ]
      return documents
                     


      
obj=PDFLoader(r"/home/wasay-rabbani/Desktop/Test Pdfs")
# obj.extract_text()
# obj.extract_metadata()
print(obj.extract_tables())


