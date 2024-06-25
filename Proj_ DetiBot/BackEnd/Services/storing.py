#This file contains all the functions and calls to the other classes
#To execute the neccessary methods to store data.  
#In this file we have 2 classes: "Qstore" and "MySql".

from Services import File_Source, URL_Source, Faq_Source
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition,MatchValue
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from datetime import datetime, timedelta
import mysql.connector
from langchain_community.docstore.base import Document


QDRANT_URL = "http://qdrantdb:6333" #url="http://qdrantdb:6333" <- docker || local -> url="http://localhost:6333"
MYSQL_HOST = "mysqldb" #"mysqldb" <-docker || local -> "localhost"

#Defines class that provides methods to interact with Qdrant
class QStore:  

    def __init__(self):
       # Defines the embending model
       self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device':'cpu'},
            encode_kwargs = {
                'normalize_embeddings': True # keep True to compute cosine similarity
            }
        )
       
    # Function that indexes Faq Sources into Qdrant
    def index_faq(self, source:Faq_Source,meta):
        chunks = [Document(page_content=f"Pergunta: {source.question}\nResposta: {source.answer}",metadata={"source": {meta}})]
        index = Qdrant.from_documents(
            chunks,
            embedding=self.embeddings,
            url=QDRANT_URL,
            collection_name="db"
        )
        index.client.close()
        return {"response": "Successfull"}
 

    # Function that indexes the chunks of loaded sources
    def index_documents(self, chunks):
        index = Qdrant.from_documents(
            chunks,
            embedding=self.embeddings,
            url=QDRANT_URL,
            collection_name="db"
        )
        index.client.close()

    # Method that return the object retriever and the client connection that is used in querying.py
    def object_retriever(self):
        client = QdrantClient(url=QDRANT_URL)
        self.vector_store = Qdrant(client=client,embeddings=self.embeddings,collection_name="db")
        retriever = self.vector_store.as_retriever()
        return retriever, client
    
    #Method that deletes vectors according to their source
    def delete_vectors(self, payload_source):
        client = QdrantClient(url=QDRANT_URL)
        if client.collection_exists(collection_name="db"):
            delete_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.source",
                        match=MatchValue(value=payload_source),
                        )
                    ]
                )
            
            client.delete(collection_name="db", points_selector=delete_filter)
        client.close()

#Defines class that provides methods to interact with MySQL
class MySql:
    
    def __init__(self):
        
        # Connects to MySQL
        try:
            self.conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user="bot",
                password="pi2024",
                database="Detibot"
            )

            if self.conn.is_connected():
                print("Connected to MySQL database")

                # Perform database operations
                self.cursor = self.conn.cursor()

        except mysql.connector.Error as e:
            print("Error connecting to MySQL:", e)

    def insert_source(self,source):# inserts the source metadata accoring to it's type

        #FILE_SOURCE      
        if isinstance(source, File_Source): 
            insert_sql = (
                "INSERT INTO file_source "
                "(file_name,file_path, loader_type, descript) "
                "VALUES (%s, %s, %s, %s)"
            )
            params = (source.file_name,source.file_path, source.loader_type, source.description)
        
        #URL_SOURCE
        elif isinstance(source, URL_Source):
            Id = 0
            if source.update_period == "Daily":
                Id = 1
            elif source.update_period == 'Weekly':
                Id = 2
            elif source.update_period == 'Monthly':
                Id = 3
            elif source.update_period == 'Quarterly':
                Id = 4
            insert_sql = (
                "INSERT INTO url_source "
                "(url_link, paths, descript, wait_time, recursive_url,  update_period_str, update_period_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            params = (source.url, ','.join(source.paths), source.description, source.wait_time, source.recursive, source.update_period,Id)

        #FAQ_SOURCE
        elif isinstance(source,Faq_Source):
            faq_id = self.get("SELECT id FROM faq_source WHERE question = %s AND answer = %s",[source.question,source.answer])
            if faq_id == []:
                insert_sql = (
                    "INSERT INTO faq_source "
                    "(question,answer) "
                    "VALUES (%s, %s)"
                )
                params = (source.question,source.answer)
            else:
                return {"response": "This value already exists"}
        else:
            return "Invalid source type"

        try:
            self.cursor.execute(insert_sql,params) # maybe put here a logger and a try/ctach
            self.conn.commit()
        except mysql.connector.Error as e:
            error_message = str(e)
            #Here it verifies if the inserted source was already in the  database
            if "Duplicate entry" in error_message:
                return {"response": "This value already exists"}
            else:
                print("Error inserting to MySQL:", e)
                return {"response": "Error inserting to MySQL: " + str(e)}
        return {"response": True}

    #Saves the child urls and associate them with the parent Url
    def insert_child(self,childs:set,parent_link):
        parent_id = self.get("SELECT id FROM url_source WHERE url_link = %s",[parent_link])
        print(parent_id)
        for child in childs[1:]:
            insert_sql = (
                "INSERT INTO url_child_source "
                "(url_link,parent_id) "
                "VALUES (%s, %s)"
            )
            params = (child,parent_id[0][0])

            try:
                self.cursor.execute(insert_sql,params) # maybe put here a logger and a try/ctach
                self.conn.commit()
            except mysql.connector.Error as e:
                print("Error inserting to MySQL:", e)
                return {"response": "Error inserting to MySQL: " + str(e)}
        
        return {"response": True}


    # updates the period time in the update time table
    def update_time(self,idx): 
        update_sql = """
        UPDATE update_time SET update_period = %s WHERE id = %s
        """
        if idx >= 1 or idx <= 4:
            if idx == 1:
                time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=1)
            elif idx == 2:
                time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(weeks=1)
            elif idx == 3:
                time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(weeks=4)
            else:
                time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(weeks=16)
            
            self.cursor.execute(update_sql,[str(time.strftime('%Y-%m-%d %H:%M:%S')),idx])# maybe put here a logger and a try/ctach
            self.conn.commit()
            return str(time)
        else:
            return "invalid index"
    
    # funtion that does any type of query
    def get(self,query,arg):
        self.cursor.execute(query,arg)
        return self.cursor.fetchall()
    
# URL_SOURCE
    def list_url_sources(self):
        q = "SELECT * FROM url_source"
        try:
            self.cursor.execute(q)
            urlsource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "url": item[1],
                    "paths": item[2].split(','), 
                    "update_period": item[6],
                    "description": item[3],  
                    "wait_time": item[4],
                    "recursive": bool(item[5])
                }
                for item in urlsource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    def search_url_sources(self,search:str):
        q = """
            SELECT * FROM url_source 
            WHERE id LIKE %s OR
                  url_link LIKE %s OR
                  paths LIKE %s OR
                  wait_time LIKE %s OR
                  recursive_url LIKE %s OR
                  update_period_str LIKE %s OR
                  descript LIKE %s 
            """

        search_param = '%' + search + '%'
        params = (search_param,) * 7

        try:
            self.cursor.execute(q, params)
            urlsource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "url": item[1],
                    "paths": item[2].split(','), 
                    "update_period": item[6],
                    "description": item[3],  
                    "wait_time": item[4],
                    "recursive": bool(item[5])
                }
                for item in urlsource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    def delete_url_source(self, id):
        q = "DELETE FROM url_source WHERE id = %s"
        try:
            self.cursor.execute(q, (id,))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
    
    def delete_url_child_source(self, id):
        q = "DELETE FROM url_child_source WHERE parent_id = %s"
        try:
            self.cursor.execute(q, (id,))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")

    def update_url_source(self, id, source):
        self.delete_url_child_source(id)
        q = """
        UPDATE url_source 
        SET url_link = %s, paths = %s, descript = %s, wait_time = %s, recursive_url = %s, update_period_id = %s 
        WHERE id = %s
        """
        update_period_id = 0
        if source.update_period == "Daily":
            update_period_id = 1
        elif source.update_period == 'Weekly':
            update_period_id = 2
        elif source.update_period == 'Monthly':
            update_period_id = 3
        elif source.update_period == 'Quarterly':
            update_period_id = 4
        
        try:
            self.cursor.execute(q, (source.url, ','.join(source.paths), source.description, source.wait_time, source.recursive, update_period_id, id))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                return {"error": "ID not found"}
        except mysql.connector.Error as e:
            error_message = str(e)
            if "Duplicate entry" in error_message:
                return {"response": "This value already exists"}
            else:
                print("Error inserting to MySQL:", e)
                return {"response": "Error inserting to MySQL: " + str(e)}
        return {"response": True}


# FILE_SOURCE        
    def list_file_sources(self):
        q = "SELECT * FROM file_source"
        try:
            self.cursor.execute(q)
            filesource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "file_name": item[1],
                    "file_path": item[2], 
                    "description": item[4],  
                }
                for item in filesource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
    
    def search_file_sources(self,search:str):
        q = """
            SELECT * FROM file_source 
            WHERE id LIKE %s OR
                  file_name LIKE %s OR
                  descript LIKE %s OR
                  loader_type LIKE %s
            """
        search_param = '%' + search + '%'
        params = (search_param,) * 4

        try:
            self.cursor.execute(q, params)
            filesource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "file_name": item[1],
                    "file_path": item[2], 
                    "description": item[4],  
                }
                for item in filesource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    def delete_file_source(self, id):
        q = "DELETE FROM file_source WHERE id = %s"
        try:
            self.cursor.execute(q, (id,))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
    
    def update_file_source(self, id, source: File_Source):
        q = """
        UPDATE file_source 
        SET file_name = %s, file_path = %s, loader_type = %s, descript = %s 
        WHERE id = %s
        """        
        try:
            self.cursor.execute(q,(source.file_name, source.file_path, source.loader_type, source.description,id))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                return {"error": "ID not found"}
        except mysql.connector.Error as e:
            error_message = str(e)
            if "Duplicate entry" in error_message:
                return {"response": "This value already exists"}
            else:
                print("Error inserting to MySQL:", e)
                return {"response": "Error inserting to MySQL: " + str(e)}
        return {"response": True}


# FAQ_SOURCE 
    def list_faq_sources(self):
        q = "SELECT * FROM faq_source"
        try:
            self.cursor.execute(q)
            faqsource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "question": item[1],
                    "answer": item[2],  
                }
                for item in faqsource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    def search_faq_sources(self,search:str):
        q = """
            SELECT * FROM faq_source 
            WHERE id LIKE %s OR
                  question LIKE %s OR
                  answer LIKE %s 
            """
        search_param = '%' + search + '%'
        params = (search_param,) * 3

        try:
            self.cursor.execute(q, params)
            faqsource = self.cursor.fetchall()
            formatted_sources = [
                {
                    "id": item[0],
                    "question": item[1],
                    "answer": item[2],  
                }
                for item in faqsource
            ]
            return formatted_sources
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return []
        
    def delete_faq_source(self, id):
        q = "DELETE FROM faq_source WHERE id = %s"
        try:
            self.cursor.execute(q, (id,))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
    
    def update_faq_source(self, id, source: Faq_Source):
        faq_id = self.get("SELECT id FROM faq_source WHERE question = %s AND answer = %s",[source.question,source.answer])
        if faq_id == []:
            q = """
            UPDATE faq_source 
            SET question = %s, answer = %s 
            WHERE id = %s
            """        
            try:
                self.cursor.execute(q,(source.question, source.answer,id))
                self.conn.commit()
                if self.cursor.rowcount == 0:
                    return {"error": "ID not found"}
                return {"message": "Source updated successfully"}
            except mysql.connector.Error as e:
                print(f"Error executing query: {e}")
                return {"error": f"Error executing query: {e}"}
        return {"response": "This value already exists"} 
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

