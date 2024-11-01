import streamlit as st


if 'menu_selection' not in st.session_state:
    st.session_state['menu_selection'] = None


st.title('Application Menu')

st.subheader('Account Settings')
with st.empty().container(border=True):
    if st.button(label='Profile info', icon=":material/person:", use_container_width=True):
        st.session_state['menu_selection'] = 1

    if st.button(label='Logout', icon=":material/logout:", use_container_width=True):
        st.session_state['menu_selection'] = 2


st.subheader('Application Settings')
with st.empty().container(border=True):
    if st.button(label='Manage users', icon=":material/person_add:", use_container_width=True):
        st.session_state['menu_selection'] = 3

    if st.button(label='Manage exercises', icon=":material/add_circle:", use_container_width=True):
        st.session_state['menu_selection'] = 4



with st.empty().container(border=False, height=10):
    pass

if st.session_state['menu_selection'] == 1:
    st.markdown(f"""**Account Information:** \\
                User name: **{st.session_state.user.name}** \\
                Account ID: **{st.session_state.user.id}** \\
                Role: **{st.session_state.user.role}**""")
    

if st.session_state['menu_selection'] == 4:
    workout_name = st.text_input('Name of the exercise', disabled=not st.session_state.user.is_admin())
    if st.button(label='Add exercise', icon=":material/add_circle:"):
        pass
    if st.button(label='Delete exercise', icon=":material/delete:"):
        pass


