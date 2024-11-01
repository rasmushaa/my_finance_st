import streamlit as st


st.title('You are at the Main Page!')


col1, col2, col3 = st.columns([1, 1, 10])

with col1:
    if st.button(label='', icon=":material/settings:"):
        st.switch_page('pages/menu.py')
        st.write('Testing')

with col2:
    st.button(label='', icon=":material/logout:")
    st.write('Testing')

with st.empty().container():
    st.write(st.session_state.user.id)
    st.write(st.session_state.user.name)
    st.write(st.session_state.user.role)
    st.write(st.session_state.user.is_logged_in)

st.button(label='s', icon=":material/settings:")