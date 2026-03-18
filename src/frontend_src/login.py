import sys
import os
import json
import hashlib
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st

USERS_FILE = r"C:\Users\shreyas.s1\Documents\capstone_project\users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        users = {"admin": hash_password("admin123")}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    users[username] = hash_password(password)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def verify_user(username, password):
    users = load_users()
    return users.get(username) == hash_password(password)

# ✅ initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ✅ redirect if already logged in
if st.session_state.logged_in:
    st.switch_page("app.py")

st.set_page_config(
    page_title="AstraRag - Login",
    page_icon="🤖",
    layout="centered",
)

st.markdown("""
<style>
            /* ===== HIDE NAVIGATION MENU ===== */
div[data-testid="stSidebarNav"] {
    display: none !important;
}
/* ===== AUTH BUTTONS ===== */
.auth-btn button {
    width: 100% !important;
    height: 42px !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    background-color: #7c3aed !important;
    color: white !important;
    border: none !important;
}
.auth-btn-secondary button {
    width: 100% !important;
    height: 42px !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    background-color: #374151 !important;
    color: white !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AstraRag")
st.markdown("#### Agentic RAG Chatbot")
st.markdown("---")

if not st.session_state.show_register:
    # ✅ LOGIN PAGE
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="auth-btn">', unsafe_allow_html=True)
        login_clicked = st.button("Login", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if login_clicked:
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome back, {username}!")
                time.sleep(0.5)
                st.switch_page("app.py")
            else:
                st.error("❌ Invalid username or password!")

    with col2:
        st.markdown('<div class="auth-btn-secondary">', unsafe_allow_html=True)
        register_clicked = st.button("Register instead", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if register_clicked:
            st.session_state.show_register = True
            st.rerun()

else:
    # ✅ REGISTER PAGE
    st.subheader("📝 Register")
    new_username = st.text_input("Choose Username", key="reg_user")
    new_password = st.text_input("Choose Password", type="password", key="reg_pass")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="auth-btn">', unsafe_allow_html=True)
        if st.button("Register", use_container_width=True):
            if not new_username or not new_password:
                st.error("❌ Please fill all fields!")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif new_username in load_users():
                st.error("❌ Username already exists!")
            else:
                save_user(new_username, new_password)
                st.success("✅ Account created! Please login.")
                st.session_state.show_register = False
                time.sleep(0.5)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="auth-btn-secondary">', unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)