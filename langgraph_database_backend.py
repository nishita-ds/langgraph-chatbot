from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from typing import Literal,Annotated,TypedDict
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

import os

load_dotenv()


class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    task="text-generation",
    provider="auto",
    max_new_tokens=1500,
    temperature=0.2,
    repetition_penalty=1.1,
    top_p=0.9
)

model = ChatHuggingFace(llm=llm)
def chat_node(state:ChatState) -> ChatState:
    messages = state['messages']
    response = model.invoke(messages)

    print("RESPONSE:", response)
    print("CONTENT:", response.content)

    return {"messages":[response]}


conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph=StateGraph(ChatState)
graph.add_node("chatnode",chat_node)
graph.add_edge(START,"chatnode")
graph.add_edge("chatnode",END)


chatbot=graph.compile(checkpointer=checkpointer)

# Extract number of threads
def retrieve_all_threads():
    all_threads =set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return(list(all_threads))




# # test
# CONFIG = {'configurable':{'thread_id':'thread-1'}}
# response = chatbot.invoke(
#     {'messages':[HumanMessage(content='what is my name?')]},
#     config=CONFIG
# )
# print(response)