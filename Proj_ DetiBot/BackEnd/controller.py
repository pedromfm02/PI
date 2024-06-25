from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from Services import Query,Loading,MySql,URL_Source,File_Source,QStore,Faq_Source,Question


app = FastAPI()
procurador = Query()
load = Loading()
db = MySql()
qstore = QStore()
UPLOAD_FOLDER = "./uploads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can also use [""] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"]  # Allows all headers
)




@app.get("/detibot")
async def root():
    return "This is the api for DETIBOT"
#---------------------- endpoints that returns an answer given a prompt--------------------------- 
@app.post("/detibot/en")
async def QuestionEn(payload: Question):
    response = procurador.queries(payload.prompt, "en", payload.chat)
    return response["query"]

@app.post("/detibot/pt")
async def QuestionPt(payload: Question):
    response = procurador.queries(payload.prompt, "pt", payload.chat)
    return response["query"]

#-------------------------enpoints that list every row of a table in mysql--------------------------
@app.get("/detibot/url_sources")
async def listUrlSources():
    return db.list_url_sources()

@app.get("/detibot/file_sources")
async def listFileSources():
    return db.list_file_sources()

@app.get("/detibot/faq_sources")
async def listFaqSources():
    return db.list_faq_sources()

#------------------------ endpoints to apply a search bar in each table of sources-------------------
@app.get("/detibot/Search_url_sources/{search}")
async def searchUrlSources(search:str):
    return db.search_url_sources(search)

@app.get("/detibot/Search_file_sources/{search}")
async def searchFileSources(search:str):
    return db.search_file_sources(search)

@app.get("/detibot/Search_faq_sources/{search}")
async def searchFaqSources(search:str):
    return db.search_faq_sources(search)

#------------------------ endpoints that post the diferent type of sources in the system-----------------
@app.post("/detibot/insert_filesource")
async def SourceFile(file: UploadFile = File(...), descript: str = Form(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    source = File_Source(file_name=file.filename,file_path=file_location,loader_type=file.content_type,description=descript)
    #inserts the source object into the db
    response = db.insert_source(source)
    if response["response"] is True:
        #loads the new source object
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        load_response = load.file_loader(source)
        os.remove(file_location)

        return load_response
    else:
        return response   

@app.post("/detibot/insert_urlsource")
async def SourceUrl(source: URL_Source):
    #inserts the source object into the db
    response = db.insert_source(source)
    if response["response"] is True:
        #loads the new source object
        return load.url_loader(source)
    else:
        return response   

@app.post("/detibot/insert_faqsource")
async def SourceFaq(source: Faq_Source):
    #inserts the source object into the db
    response = db.insert_source(source)
    if response["response"] is True:
        sourceId = db.get("SELECT id FROM faq_source WHERE question = %s",[source.question])
        #loads the new source object
        meta = str(sourceId[0][0]) + source.question
        return qstore.index_faq(source,meta)
    else:
        return response   

#------------------------ endpoints to delete sources in the system------------------------------
@app.delete("/detibot/delete_urlsource/{id}")
async def deleteUrlSource(id: int):
    current_source = db.get("SELECT url_link FROM url_source WHERE id = %s",[id])

    child_links = db.get("SELECT url_link FROM url_child_source WHERE parent_id = %s",[id])

    qstore.delete_vectors(current_source[0][0])
    for link in child_links:
        qstore.delete_vectors(link[0])

    db.delete_url_source(id)


@app.delete("/detibot/delete_filesource/{id}")
async def deleteFileSource(id: int):
    current_source = db.get("SELECT file_path FROM file_source WHERE id = %s",[id])
    
    if not current_source:
        raise HTTPException(status_code=404, detail="File source not found")
    qstore.delete_vectors(current_source[0][0])
    db.delete_file_source(id)
    return {"detail": "File deleted successfully"}

@app.delete("/detibot/delete_faqsource/{id}")
async def deleteFaqSource(id: int):
    current_source = db.get("SELECT question FROM faq_source WHERE id = %s",[id])
    qstore.delete_vectors(str(id)+current_source[0][0])
    db.delete_faq_source(id)

#------------------------ endpoints to update sources in the system------------------------------
@app.put("/detibot/update_urlsource/{id}")
async def updateUrlSource(id: int,source: URL_Source):
    current_source = db.get("SELECT url_link FROM url_source WHERE id = %s",[id])

    if current_source:

        child_links = db.get("SELECT url_link FROM url_child_source WHERE parent_id = %s",[id])

        qstore.delete_vectors(current_source[0][0])
        if child_links:
            for link in child_links:
                qstore.delete_vectors(link[0])

        db.update_url_source(id, source)
        return load.url_loader(source)
    else:
        response = db.insert_source(source)
        if response["response"] is True:
            #loads the new source object
            return load.url_loader(source)
        else:
            return response   


@app.put("/detibot/update_filesource/{id}")
async def updateFileSource(id: int,file: UploadFile = File(...), descript: str = Form(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    current_source = db.get("SELECT file_path FROM file_source WHERE id = %s",[id])
    if not current_source:
        raise HTTPException(status_code=404, detail="File source not found")

    qstore.delete_vectors(current_source[0][0])
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    updated_source = File_Source(file_name=file.filename,file_path=file_location,loader_type=file.content_type,description=descript)
    db.update_file_source(id, updated_source)
    loader_response = load.file_loader(updated_source)
    os.remove(file_location)
    return loader_response

@app.put("/detibot/update_faqsource/{id}")
async def updateFaqSource(id: int,source: Faq_Source):
    current_source = db.get("SELECT question FROM faq_source WHERE id = %s",[id])
    qstore.delete_vectors(str(id)+current_source[0][0])
    db.update_faq_source(id, source)
    qstore.index_faq(source,str(id)+current_source[0][0])
