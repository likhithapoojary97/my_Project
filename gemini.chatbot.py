import streamlit as st
import google.generativeai as genai
import os
import time
import joblib

genai.configure(api_key="AIzaSyAC3VUyMxsJ6az19WWIJiCGH1lADsWYW8c")


if 'chat_id' not in st.session_state:
    st.session_state.chat_id = None
if 'chat_title' not in st.session_state:
    st.session_state.chat_title = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'gemini_history' not in st.session_state:
    st.session_state.gemini_history = []

#create a chat id
new_chat_id = f'{time.time()}'
MODEL_ROLE = "ai"
AI_AVATAR_ICON = '🥰'

#create data directory
os.makedirs('database',exist_ok= True)

#load the past chats
try:
    past_chats: dict = joblib.load('database/past_chats_list')
except:
    past_chats = {}

#sidebar : chat selection

with st.sidebar:
    st.write('🌏PAST CHATS🌏')
    if st.session_state.chat_id is None:
        st.session_state.chat_id = st.selectbox('Pick a Past chat',
                                                options=[new_chat_id]+ list(past_chats.keys()),
                                                format_func=lambda x:past_chats.get(x,'New Chat'),
                                                placeholder= '_')
    else:
        st.session_state.chat_id = st.selectbox('Pick a Past Chat',
                                                options=[new_chat_id] + list(past_chats.keys()),
                                                format_func= lambda x: past_chats.get(x, 'New Chat' if x!= st.session_state.chat_id
                                                                                       else st.session_state.chat_title or 'Current_chat'),
                                                placeholder='_')
        st.session_state.chat_title = f'Chatsession-{st.session_state.chat_id}'

#load message history

try:
    st.session_state.messages = joblib.load(f'database{st.session_state.chat_id}-st_messages')
    st.session_state.gemini_history = joblib.load(f'database{st.session_state.chat_id}-gemini_messages')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []

#gimini model 
model = genai.GenerativeModel('models/gemini-2.0-flash')
st.session_state.model = model 
st.session_state.chat = model.start_chat(history=st.session_state.gemini_history)

st.write("# CHAT WITH GOOGLE AI🎓✅ - GEMINI")

for message in st.session_state.messages:
    with st.chat_message(name= message["role"],avatar= message.get('avatar')):
        st.markdown(message['content'])

#prompt 
if prompt := st.chat_input("Write Your Message Here only ai related questions if apart from that will bw asked simply say i don't know.....📍"):
    if st.session_state.chat_id not in past_chats:
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'database/past_chats_list')
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append(dict(role= "user", content = prompt))

    try:
        response = st.session_state.chat.send_message(prompt)
        response_text = response.text

    except Exception as e:
        response_text = f" Error: {e}"
    
    with st.chat_message(name = MODEL_ROLE, avatar= AI_AVATAR_ICON):
        st.markdown(response_text)

# store message and history 
    st.session_state.messages.append(dict(role = MODEL_ROLE ,content=response_text, avatar = AI_AVATAR_ICON))
    st.session_state.gemini_history = st.session_state.chat.history


#store on database (your local machine)
    joblib.dump(st.session_state.messages, f'database{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f"database{st.session_state.chat_id}-gemini_meesages")





 

