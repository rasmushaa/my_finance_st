import streamlit as st
from frontend.utils import valid_user_state

valid_user_state()


st.subheader('Expenditure Categories')
st.write(st.session_state['api']['categories'].get_expenditure_categories())


st.subheader('Asset Categories')
st.write(st.session_state['api']['categories'].get_asset_categories())