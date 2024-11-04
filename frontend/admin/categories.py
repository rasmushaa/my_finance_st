import streamlit as st



def f1():
    print('f1')

def f2():
    print('f2')

st.title('Edit Categories')
st.button('Button', on_click=f1)
f2()
print('end\n\n')