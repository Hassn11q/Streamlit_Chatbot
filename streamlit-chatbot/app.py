#imports
from openai import OpenAI 
import os 
import streamlit as st 
from dotenv import load_dotenv 
import shelve


#load the .env file
load_dotenv()

st.title('CHATGPT-APP')
st.image(image = '/Users/hassn-/Desktop/streamlit-chatbot/Images/ChatGPT.jpg'  , width = 500)

user_avatar = '👤'
bot_avatar = '🤖'

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

# Ensure openai model is intialized in session state 
if 'openai_model' not in st.session_state:
    st.session_state['openai_model'] = 'gpt-3.5-turbo'

# load the history from shelve file 
def load_chat_history():
    with shelve.open('history.db') as db:
        return db.get('messages' , [])

# save the history in shelve file
def save_chat_history(messages):
    with shelve.open('history.db') as db:
        db['messages'] = messages


# initialize the chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = load_chat_history()

# sidebar with button delete chat history 
with st.sidebar:
    if st.button('Delete Chat History'):
        st.session_state.messages = []
        save_chat_history([])

for message in st.session_state.get('messages' , []):
    avatar = user_avatar if message['role'] == 'user' else bot_avatar
    with st.chat_message(message['role'] , avatar = avatar):
        st.markdown(message['content'])
                    
if prompt := st.chat_input('How can i Help You ?'):
    st.session_state.messages.append({'role' : 'user' , 'content' : prompt})
    with st.chat_message('user', avatar = user_avatar):
        st.markdown(prompt)

    with st.chat_message('assistant' , avatar = bot_avatar):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model = st.session_state['openai_model'] , 
            messages = st.session_state['messages'],
            max_tokens = 2048,
            stream = True , ):
            full_response += response.choices[0].delta.content or ''
            message_placeholder.markdown(full_response + '|')
        message_placeholder.markdown(full_response)
    st.session_state['messages'].append({'role' : 'assistant' , 'content' : full_response})
