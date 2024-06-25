#This class contains all the functions and calls to the other classes
#To execute the neccessary methods to load the source.

from Services.classes import URL_Source, File_Source
from Services.indexing import Indexing
from Services.storing import MySql

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader, CSVLoader, JSONLoader, UnstructuredHTMLLoader, TextLoader

from Services.seleniumLoader import SeleniumURLLoaderWithWait as urlLoader

db = MySql()
indexer = Indexing()
class Loading:

    # Manages the Loading Url Sources
    def url_loader(self, source: URL_Source):
        documents,childs=self.load_urls(source)
        if source.recursive:
            db.insert_child(childs,source.url)
        indexer.index(documents)
        return {"response": "Successfull"}
    
    # Manages the Loading File Sources
    def file_loader(self, source: File_Source):
        if source.loader_type == "application/pdf":
            documents = self.load_pdf(source)
        elif source.loader_type == "application/csv":
            documents = self.load_csv(source)
        elif source.loader_type == "application/docx":
            documents = self.load_docx(source)
        elif source.loader_type == "application/json":
            documents = self.load_csv(source)
        elif source.loader_type == "application/html":
            documents = self.load_json(source)
        else:
            documents = self.load_text(source)
        indexer.index(documents)
        return {"response": "Successfull"}
    
#------------------------- functions that loads diferent file extensions ---------------------------------    
    def load_csv(self, source:File_Source):
        loader = CSVLoader(file_path=source.file_path)
        return loader.load()
    
    def load_docx(self, source:File_Source):
        #%pip install --upgrade --quiet  docx2txt
        loader = Docx2txtLoader(file_path=source.file_path)
        return loader.load()
    
    def load_json(self, source:File_Source):
        loader = JSONLoader(file_path=source.file_path)
        return loader.load()
    
    def load_html(self, source:File_Source):
        loader = UnstructuredHTMLLoader(file_path=source.file_path)
        return loader.load()
    
    def load_text(self, source:File_Source):
        loader = TextLoader(file_path=source.file_path)
        return loader.load()
    
    def load_pdf(self, source:File_Source):
        loader = PyPDFLoader(file_path=source.file_path)
        return loader.load()

#------------------------- function that loads the Url ---------------------------------    
    def load_urls(self, source:URL_Source):
        loader = urlLoader(urls=[source.url], browser="chrome", headless=True)
        return loader.load(wait_time=source.wait_time, recursive=source.recursive, paths=source.paths)

    



