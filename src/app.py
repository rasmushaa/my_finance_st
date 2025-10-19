import streamlit as st
from frontend import sidebar
import backend


# Main entry-point and the event-loop, that runs only once.
# Everyihg on this file is executed before all other Pages.

# Define all existing st.Page 'Pages' that are navigateable (required to do so),
# by the st.switch_page and st.page_link functions,
# but hide the default navigation,
# because that is dynamically changed in the code.


def init_backend():
    if 'backend' not in st.session_state:
        st.session_state['backend'] = backend

# Application Constants
st.set_page_config(page_title='My Finance')
st.logo('src/frontend/app_assets/logo.png', size='large')

all_pages = [
    st.Page('frontend/account/login.py', default=True),
    st.Page('frontend/account/logout.py'),
    st.Page('frontend/banking/file_input.py'),
    st.Page('frontend/banking/file_parsing.py'),
    st.Page('frontend/assets/uppload_file.py'),
    st.Page('frontend/admin/ai.py'),
    st.Page('frontend/admin/categories.py'),
    st.Page('frontend/admin/database.py'),
]

pg = st.navigation(
    all_pages,
    position='hidden'
)

init_backend()

sidebar.init_to_user_access_level() # Update the navigation accordingly to the user access level after each reload/page switch

pg.run() # Main Event Run


