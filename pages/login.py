import os
import streamlit as st
import hashlib
from backend.credentials_api import CredentialsAPI


@st.cache_data
def st_wrapper_password_check(username, password_hash):
    api = CredentialsAPI()
    return api.username_and_password_match(username, password_hash)

@st.cache_data
def st_wrapper_init_user(username, password_hash):
    api = CredentialsAPI()
    return api.init_user(username, password_hash)

env = os.getenv('STREAMLIT_ENV')
env_siffix = '' if env=='prod' else ': STG' if env=='stg' else ': DEV' if env=='dev' else 'EnvVariable NotFound!' 
st.title(f'Data Workouts App{env_siffix}')

st.write('Please login')
username = st.text_input('Username')
password_hash = hashlib.sha256(st.text_input('Password', type='password').encode('utf-8')).hexdigest()

if st.button('Login', icon=":material/login:"):

    if st_wrapper_password_check(username, password_hash):
        st.success('Login successful')
        st.session_state['user'] = st_wrapper_init_user(username, password_hash)
        st.switch_page('pages/main_window.py')
    
    else:
        st.error('Password and Username do not match')