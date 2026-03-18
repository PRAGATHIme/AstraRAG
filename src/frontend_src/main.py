import streamlit as st

pg = st.navigation([
    st.Page("app.py", title="Chat"),
    st.Page("login.py", title="Login", default=True),
    
])
pg.run()