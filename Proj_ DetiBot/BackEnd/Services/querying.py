#This class contains all the functions and calls to the other classes
#To execute the neccessary methods to load the source provided in the
#'loader' method.
#from llama_index.core import SimpleDirectoryReader

from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import PromptTemplate
import textwrap
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain


from Services.storing import QStore
qstore = QStore()

class Query: 

    def __init__(self):
        
        #Defines connection with the ollama server and what LLM it uses
        self.llm = Ollama(model="llama3", temperature=0,base_url="http://ollama:11434") # ,base_url="http://ollama:11434" <- docker || local -> sem o ,base_url="http://ollama:11434"
        
    # Formats list of messages in the chat into the format "message_id: {count}, message: {message}\n ..." for the LLM to be able to take into account the chat history
    def format_history(self, chat_history):
        history = ""
        count = 0
        for message in chat_history:
            history += f"message_id: {count}, message: {message}\n"
            count += 1
        return history

    #Function that processes the question and returns the answer
    def queries(self, question, language,chat):
        #gets retriever object and client connection with Qdrant
        retriever, client = qstore.object_retriever()
        
        history = self.format_history(chat)
        
        #Defines 2 diferent prompt templates to answer only in english or portuguese, 
        # as well as a set o rules and instructions for how to answer and what to take into account when the LLM generates the answer.
        if language == "en":
            template = """
                ### System:
                Always answer in english.
                The following information is your only source of truth, only answer the question with the provided context, if you are unable to answer from that, tell the user “I’m having trouble finding an answer for you"
                You are an respectful and honest assistant. You have to answer the user's questions using only the context \
                provided to you. If you don't know the answer, just say you don't know. Don't try to make up an answer.
                Only use infromation from history if the user input ask you to.
                ### History:
                {history}
                ### Context:
                {context}
                ### User:
                {input}
                ### Response:
                """
        elif language == "pt":
            template = """

                ### System:
                Always answer in portuguese.
                The following information is your only source of truth, only answer the question with the provided context, if you are unable to answer from that, tell the user “I’m having trouble finding an answer for you"
                You are an respectful and honest assistant. You have to answer the user's questions using only the context \
                provided to you. If you don't know the answer, just say you don't know. Don't try to make up an answer.
                Only use infromation from history if the user input ask you to.
                ### History:
                {history}
                ### Context:
                {context}
                ### User:
                {input}
                ### Response:
                """


        # Creating the prompt from the template which we created before
        prompt = PromptTemplate.from_template(template)
        
        #Creats the chain that will in turn return an answer.
        qa_chain = create_stuff_documents_chain(self.llm, prompt)
        chain = create_retrieval_chain(retriever, qa_chain)
        input_data = {
            'input': question,
            'history': history,  # add history to input data
            'context': ""
        }
        
        text = chain.invoke(input_data)
        client.close()
        response = textwrap.fill(text['answer'])
        return {"query": response}