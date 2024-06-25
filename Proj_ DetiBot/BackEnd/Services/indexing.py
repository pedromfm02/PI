#This class contains the function and calls class Qstore
#To the split in chunks the loaded data and index it   
#Into the vector store.

from langchain_text_splitters import RecursiveCharacterTextSplitter
from Services.storing import QStore

qstore = QStore()
class Indexing:

    def __init__(self,size=256,overlap=25):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)

    def index(self, documents):
        chunks = self.text_splitter.split_documents(documents)
        qstore.index_documents(chunks)
        return {"Indexing": "Successfull"}
