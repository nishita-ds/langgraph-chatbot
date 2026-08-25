import streamlit as st 
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid 

# ******************************** utility functions *****************************
def generate_thread_id():
    return str(uuid.uuid4())
# def generate_thread_id():
#     thread_id = uuid.uuid4()

#     return thread_id

def generate_chat_title(message):
    words = message.strip().split()

    if len(words) <= 6:
        return message.strip()

    return " ".join(words[:6]) + "..."

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['chat_titles'][thread_id] = "New Chat"
    st.session_state['message_history'] = []

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state['thread_id'] = thread_id
#     add_thread(st.session_state['thread_id'])
#     st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']





# st.session_state -> dict -> do not erase content
# ***********************************Session Setup *********************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])

if st.session_state['thread_id'] not in st.session_state['chat_titles']:
    st.session_state['chat_titles'][st.session_state['thread_id']] = "New Chat"





# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()
    
# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = []
# add_thread(st.session_state['thread_id'])
    
    
    
#  ********************************** Sidebar UI **********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversation')


for thread_id in st.session_state['chat_threads'][::-1]:

    title = st.session_state['chat_titles'].get(
        thread_id,
        "New Chat"
    )

    if st.sidebar.button(
        title,
        key=f"chat_{thread_id}"
    ):

        st.session_state['thread_id'] = thread_id

        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append({
                'role': role,
                'content': msg.content
            })

        st.session_state['message_history'] = temp_messages

        st.rerun()






# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state['thread_id'] = thread_id
#         messages = load_conversation(thread_id)
        
#         temp_messages = []
        
#         for msg in messages:
#             if isinstance(msg,HumanMessage):
#                 role = 'user'
#             else:
#                 role = 'assistant'
                
#             temp_messages.append({'role':role,'content':msg.content})
            
#         st.session_state['message_history'] = temp_messages


    

# loading the conversation history
# ********************************** Main UI ***************************************


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")
if user_input:

    current_thread = st.session_state['thread_id']

    # Generate title from first user message
    if st.session_state['chat_titles'][current_thread] == "New Chat":

        st.session_state['chat_titles'][current_thread] = generate_chat_title(
            user_input
        )

    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })






# if user_input:
    
#     st.session_state['message_history'].append({'role':'user','content':user_input})
#     with st.chat_message('user'):
#         st.text(user_input)
        
        
    # response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)
    CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}
    # ai_message = response['messages'][-1].content
    # st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                 {'messages':[HumanMessage(content=user_input)]},config=CONFIG,
                 stream_mode='messages'
                
            )
        )
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})