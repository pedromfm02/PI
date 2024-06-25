from pydantic import BaseModel
class URL_Source(BaseModel): # class that defines atributes of URL source
    url: str
    paths: list[str]
    update_period: str | int
    description: str
    wait_time: int = 3 
    recursive: bool = False
      
class File_Source(BaseModel): # class that defines atributes of File source
    file_name: str
    file_path: str
    loader_type: str
    description: str

class Faq_Source(BaseModel): # class that defines atributes of Faq source
    question: str
    answer: str

class Question(BaseModel): # class that defines arguments for when the user asks a question
    prompt: str
    chat: list[str]