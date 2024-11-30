import os
import streamlit as st
import hashlib
from frontend.utils import init_random_captcha_color,  validate_captcha_color


# Dynamic Header, that indicates the ENVIRONMENT
env = os.getenv('STREAMLIT_ENV')
env_siffix = '' if env=='prod' else ': STG' if env=='stg' else ': DEV' if env=='dev' else 'EnvVariable NotFound!' 
col1, col2 = st.columns([3, 1])
col1.title(f'My Finance App{env_siffix}')
col2.image('frontend/app_assets/logo.png')


# User login input, that hashes the password
st.write('Please login')
username = st.text_input('Username')
password_hash = hashlib.sha256(st.text_input('Password', type='password').encode('utf-8')).hexdigest()


# Random color captcha
target_color_name, target_rgb = init_random_captcha_color(draw_new_color=False)
st.markdown(f'<p style="color:{target_color_name.lower()};">Pick a {target_color_name} color</p>', unsafe_allow_html=True)
user_hex_color = st.color_picker('Captcha').lstrip('#')
user_rgb_color = tuple(int(user_hex_color[i:i+2], 16) for i in (0, 2, 4))


# Init the loging sequence
if st.button('Login', icon=":material/login:"):

    validate_captcha_color(user_rgb_color, target_rgb, draw_new_color_if_failed=True)

    if st.session_state['api']['credentials'].username_and_password_match(username, password_hash):
        st.success('Login successful')
        st.session_state['user'] = st.session_state['api']['credentials'].init_user(username, password_hash)
        st.switch_page('frontend/banking/file_input.py')
    
    else:
        st.error('Password and Username do not match')