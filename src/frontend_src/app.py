import sys
import os
import subprocess
import shutil
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import requests
import speech_recognition as sr
from src.frontend_src.config.frontend_settings import Settings

setting = Settings()

# ✅ redirect to login if not logged in
if not st.session_state.get("logged_in"):
    st.switch_page("src/frontend_src/login.py")

DOCS_DIR = r"C:\Users\shreyas.s1\Documents\capstone_project\docs_dir"
VECTOR_STORE_DIR = r"C:\Users\shreyas.s1\Documents\capstone_project\doc_vector_store"

st.set_page_config(
    page_title='AstraRag',
    page_icon="🤖",
    layout="centered",
)
st.markdown("""
<style>
            
            /* ===== HIDE NAVIGATION MENU ===== */
div[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ===== HEARD BOX ===== */
.heard-box {
    position: fixed;
    bottom: 160px;
    left: 50%;
    transform: translateX(-50%);
    width: 50%;
    text-align: center;
    background: #1f1f2e;
    border-radius: 12px;
    padding: 12px;
    color: white;
    font-size: 15px;
    border-left: 4px solid #7c3aed;
    z-index: 9999;
}

/* ===== LISTENING BOX ===== */
.listening-box {
    position: fixed;
    bottom: 160px;
    left: 50%;
    transform: translateX(-50%);
    width: 50%;
    text-align: center;
    background: #1f1f2e;
    border-radius: 12px;
    padding: 12px;
    color: #ef4444;
    font-size: 15px;
    border-left: 4px solid #ef4444;
    z-index: 9999;
}

/* push chat content above fixed elements */
.main .block-container {
    padding-bottom: 200px;
}

/* ===== SIDEBAR BUTTON - stays normal in sidebar ===== */
div[data-testid="stSidebar"] div[data-testid="stButton"] button {
    position: static !important;
    bottom: auto !important;
    right: auto !important;
    width: 100% !important;
    height: auto !important;
    font-size: 14px !important;
    background-color: #7c3aed !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    color: white !important;
    transform: none !important;
}

/* ===== MIC BUTTON - fixed in main area only ===== */
div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button {
    position: fixed !important;
    bottom: 60px !important;
    right: calc(50% - 430px) !important;
    z-index: 9999 !important;
    background-color: #3d3d3d !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    width: 44px !important;
    height: 44px !important;
    font-size: 18px !important;
    cursor: pointer !important;
    padding: 0 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button:hover {
    background-color: #555555 !important;
}

div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button:active {
    transform: scale(0.95) !important;
}

</style>
""", unsafe_allow_html=True)

st.title("AstraRag - Agentic RAG Chatbot")

# ✅ initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "trained" not in st.session_state:
    st.session_state.trained = False
if "trained_file" not in st.session_state:
    st.session_state.trained_file = None
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "listening" not in st.session_state:
    st.session_state.listening = False

# ✅ speech recognition function
def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return "⚠️ No speech detected. Please try again."
    except sr.UnknownValueError:
        return "⚠️ Could not understand audio. Please try again."
    except sr.RequestError:
        return "⚠️ Speech service unavailable. Check internet."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ✅ sidebar

st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.get('username', '')}**")

# ✅ logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.chat_history = []
    st.switch_page("login.py")

# ✅ clear history button
if st.sidebar.button("🗑️ Clear My Chat History"):
    st.session_state.chat_history = []

st.sidebar.markdown("---")
st.sidebar.title("📁 Upload Documents")
if st.session_state.trained_file:
    st.sidebar.info(f"📄 Currently trained on: **{st.session_state.trained_file}**")

uploaded_file = st.sidebar.file_uploader(
    "Upload a .txt file to add to the knowledge base",
    type=["txt"]
)

if uploaded_file is not None:
    save_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"✅ '{uploaded_file.name}' uploaded!")

    if st.session_state.trained_file != uploaded_file.name:
        if st.sidebar.button("🔄 Train on Uploaded File"):
            with st.sidebar.status("Training on your file...", expanded=True) as status:
                try:
                    st.sidebar.write("🗑️ Step 1: Clearing old knowledge base...")
                    time.sleep(0.5)
                    if os.path.exists(VECTOR_STORE_DIR):
                        # ✅ kill only port 8000 backend, not all python
                        subprocess.run(
                            ["powershell", "-Command",
                            "Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"],
                            capture_output=True
                        )
                        time.sleep(1)
                        shutil.rmtree(VECTOR_STORE_DIR)
                    st.sidebar.write("✅ Step 1: Old knowledge base cleared!")
                    st.sidebar.write("📄 Step 2: Loading your documents...")
                    time.sleep(0.5)

                    process = subprocess.Popen(
                        [r"C:\Users\shreyas.s1\Documents\capstone_project\env\Scripts\python.exe",
                         "-m", "src.rag_doc_ingestion.ingest_docs"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=r"C:\Users\shreyas.s1\Documents\capstone_project"
                    )

                    st.sidebar.write("✅ Step 2: Documents loaded!")
                    st.sidebar.write("✂️ Step 3: Splitting into chunks...")

                    for line in process.stdout:
                        if "parsed" in line.lower():
                            st.sidebar.write(f"✅ Step 3: {line.strip()}")
                        elif "building" in line.lower():
                            st.sidebar.write("🔢 Step 4: Converting text to vectors...")
                        elif "completed successfully" in line.lower():
                            st.sidebar.write("✅ Step 4: Vectors created!")
                            st.sidebar.write("🗄️ Step 5: Saving to knowledge base...")
                            time.sleep(0.5)
                            st.sidebar.write("✅ Step 5: Knowledge base saved!")

                    process.wait()
                    if process.returncode == 0:
                        st.session_state.trained = True
                        st.session_state.trained_file = uploaded_file.name

                        # ✅ restart backend automatically
                       # ✅ restart backend and wait until it's actually ready
                        st.sidebar.write("🚀 Step 6: Restarting backend...")
                        subprocess.Popen(
                            [r"C:\Users\shreyas.s1\Documents\capstone_project\env\Scripts\python.exe",
                            "-m", "src.backend_src.main"],
                            cwd=r"C:\Users\shreyas.s1\Documents\capstone_project"
                        )

                        # ✅ wait until backend is actually accepting connections
                        import socket
                        for _ in range(20):  # try for 20 seconds
                            time.sleep(1)
                            try:
                                s = socket.create_connection(("localhost", 8000), timeout=1)
                                s.close()
                                break  # backend is up!
                            except OSError:
                                st.sidebar.write("⏳ Waiting for backend...")

                        st.sidebar.write("✅ Step 6: Backend is ready!")
                        status.update(label="🎉 Training Complete!", state="complete")
                    else:
                        status.update(label="❌ Training Failed!", state="error")
                except Exception as e:
                    status.update(label="❌ Training Failed!", state="error")
                    st.sidebar.error(f"❌ Error: {e}")
    else:
        st.sidebar.success(f"✅ Already trained on '{uploaded_file.name}'!")

# ✅ display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("role") == "assistant":
            sources = message.get("sources", [])
            tool_used = message.get("tool_used")
            rationale = message.get("rationale")
            if sources:
                st.markdown(f"**sources:** {', '.join(sources)}")
            with st.expander("show details (tool & rationale)"):
                st.markdown(f"**tool used:** {tool_used if tool_used else 'N/A'}")
                st.markdown(f"**rationale:** {rationale if rationale else 'N/A'}")



# ✅ real streamlit mic button - styled via CSS to sit next to chat input
mic_clicked = st.button("🎙️", key="mic_btn", help="Click to speak")

if mic_clicked:
    st.markdown('<div class="listening-box">🔴 Listening... Speak now!</div>',
                unsafe_allow_html=True)
    spoken_text = recognize_speech()
    if not spoken_text.startswith("⚠️"):
        st.session_state.voice_text = spoken_text
        st.rerun()
    else:
        st.warning(spoken_text)

# ✅ chat input
user_prompt = st.chat_input("Ask chatbot ....")

# ✅ use voice if available
if st.session_state.voice_text and not user_prompt:
    user_prompt = st.session_state.voice_text
    st.session_state.voice_text = ""

# ✅ handle prompt
if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    payload = {"chat_history": st.session_state.chat_history}

    try:
        response = requests.post(setting.CHAT_ENDPOINT_URL, json=payload)
        response.raise_for_status()
        response_json = response.json()
        assistant_response = response_json.get("answer", "(NO response)")
        tool_used = response_json.get("tool_used", "N/A")
        rationale = response_json.get("rationale", "N/A")
        sources = response_json.get("sources", [])
    except Exception as e:
        assistant_response = f"Error: {e}"
        tool_used = "N/A"
        rationale = "N/A"
        sources = []

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": assistant_response,
        "tool_used": tool_used,
        "rationale": rationale,
        "sources": sources
    })

    with st.chat_message("assistant"):
        st.markdown(assistant_response)
        if sources:
            st.markdown(f"**sources:** {', '.join(sources)}")
        with st.expander("show details (tool & rationale)"):
            st.markdown(f"**tool used:** {tool_used}")
            st.markdown(f"**rationale:** {rationale}")