from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFacePipeline
from typing import Literal,Annotated,TypedDict
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()


class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    

    
    
import os


from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

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
    messages=state['messages']
    response=model.invoke(messages)
    return {"messages":[response]}


graph=StateGraph(ChatState)

graph.add_node("chatnode",chat_node)

graph.add_edge(START,"chatnode")
graph.add_edge("chatnode",END)

checkpointer = InMemorySaver()
chatbot=graph.compile(checkpointer=checkpointer)


