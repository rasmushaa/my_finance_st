import os
import streamlit as st
import hashlib
from backend.credentials_api import CredentialsAPI
#from frontend.utils import sidebar
from backend.user import User


# Utility functions
@st.cache_data
def st_wrapper_password_check(username, password_hash):
    api = CredentialsAPI()
    return api.username_and_password_match(username, password_hash)

@st.cache_data
def st_wrapper_init_user(username, password_hash):
    api = CredentialsAPI()
    return api.init_user(username, password_hash)

#sidebar.init_to_user_access_level()


# Dynamic Header, that indicates the ENVIRONMENT
env = os.getenv('STREAMLIT_ENV')
env_siffix = '' if env=='prod' else ': STG' if env=='stg' else ': DEV' if env=='dev' else 'EnvVariable NotFound!' 
col1, col2 = st.columns([3, 1])
col1.title(f'My Finance App{env_siffix}')
col2.image('frontend/assets/logo.png')

# User login input, that hashes the password
st.write('Please login')
username = st.text_input('Username')
password_hash = hashlib.sha256(st.text_input('Password', type='password').encode('utf-8')).hexdigest()

# Init the loging sequence
if st.button('Login', icon=":material/login:"):

    ##### OVERRIDE LOGIN FOR TESTING #####
    if username == 'admin': 
        st.session_state['user'] = User(id=1, name='AdminName', role='admin', is_logged_in=True) 
        st.switch_page('frontend/banking/process_file.py')
    elif username == 'user':
        st.session_state['user'] = User(id=2, name='UserName', role='user', is_logged_in=True) 
        st.switch_page('frontend/banking/process_file.py')
    else:
        st.rerun()

    if st_wrapper_password_check(username, password_hash):
        st.success('Login successful')
        st.session_state['user'] = st_wrapper_init_user(username, password_hash)
        st.switch_page('pages/main_window.py')
    
    else:
        st.error('Password and Username do not match')