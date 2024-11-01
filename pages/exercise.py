import streamlit as st


st.title('You are at the Main Page!')

with st.empty().container(height=50):
    st.write(st.session_state.user.id)
    st.write(st.session_state.user.name)
    st.write(st.session_state.user.role)
    st.write(st.session_state.user.is_logged_in)