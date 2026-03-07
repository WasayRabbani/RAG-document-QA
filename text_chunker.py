"""
Fixed size chunks 
500 characters = 1 chunk
Overlap = 50 characters
"""


"""
Here we will use langchain to make chunks of text. From it we will use RecursiveCharacterTextSplitter so that we make chunks of best size and also similar chinks could be related to each other

"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    def __init__(self,extracted_text):
        self.text=extracted_text
    
    def make_chunks(self):
        splitter=RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.text=" ".join(self.text)
        split_text=splitter.split_text(self.text)
        return split_text
    
    