import streamlit as st
import os
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from core.loader import load_pdf
from core.splitter import split_documents
from core.vector_store import create_vector_store, load_vector_store
from core.rag_chain import get_rag_chain_with_memory_and_sources
from core.history import save_chat, load_chat, list_chats, delete_chat
from langchain_core.messages import HumanMessage, AIMessage

# --- PAGE SETUP ---
st.set_page_config(
    page_title="AI Knowledge Assistant PRO",
    page_icon="🧠",
    layout="wide",
)

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    /* Main Layout */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 100px;
        max-width: 1100px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #161B22 100%) !important;
        border-right: 1px solid rgba(246, 48, 73, 0.15);
    }
    
    /* Premium Headers */
    .main-title {
        background: linear-gradient(90deg, #FFFFFF 0%, #F63049 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -1px;
    }

    /* Sidebar Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(246, 48, 73, 0.3) !important;
        color: #FFFFFF !important;
        background-color: rgba(246, 48, 73, 0.05) !important;
        padding: 0.6rem 1.2rem !important;
    }
    
    .stButton > button:hover {
        border-color: #F63049 !important;
        background-color: rgba(246, 48, 73, 0.15) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(246, 48, 73, 0.2);
    }
    
    .new-chat-btn > div > button {
        background: linear-gradient(135deg, #F63049 0%, #8A244B 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(246, 48, 73, 0.3);
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        backdrop-filter: blur(10px);
    }
    
    .user-msg { border-left: 4px solid #F63049 !important; }
    .assistant-msg { border-left: 4px solid #38BDF8 !important; }

    /* Source Tags */
    .source-tag {
        display: inline-block;
        background: rgba(246, 48, 73, 0.1);
        color: #F63049;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-top: 6px;
        font-weight: 600;
        border: 1px solid rgba(246, 48, 73, 0.2);
    }

    /* Input Area */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(246, 48, 73, 0.2) !important;
        background-color: #0D1117 !important;
    }

    /* Animations */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage { animation: slideUp 0.4s ease-out forwards; }
    </style>
    """, unsafe_allow_html=True)

# --- APP STATE & SESSION TIMEOUT ---
load_dotenv()

# Initialize activity tracker
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

# Check for timeout (1 hour = 3600 seconds)
if time.time() - st.session_state.last_activity > 3600:
    st.session_state.clear()
    st.session_state.last_activity = time.time()
    st.info("Session reset due to 1 hour of inactivity.")
    st.rerun()

st.session_state.last_activity = time.time()

# Default user for history (since login is removed)
if "username" not in st.session_state:
    st.session_state.username = "Guest_User"

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if Qdrant is configured
QDRANT_READY = os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY")

if "process_complete" not in st.session_state:
    st.session_state.process_complete = False

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="
                width: 70px; height: 70px; 
                background: linear-gradient(135deg, #F63049 0%, #8A244B 100%);
                border-radius: 20px; margin: 0 auto;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 10px 20px rgba(246, 48, 73, 0.3);
                border: 2px solid rgba(255,255,255,0.1);
            ">
                <span style="font-size: 35px;">🧠</span>
            </div>
            <h2 style="margin-top: 15px; color: white;">Knowledge Hub</h2>
            <p style="font-size: 0.8rem; color: #8B949E;">Cloud-Powered RAG System</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Session Info
    st.caption(f"🆔 Session: `{st.session_state.chat_id[:8]}...`")
    
    # New Chat Button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ Start New Session", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Activity Monitoring
    st.subheader("Document Center")
    if not QDRANT_READY:
        st.error("⚠️ Qdrant Cloud not configured. Please set QDRANT_URL and QDRANT_API_KEY in .env")
    
    uploaded_files = st.file_uploader("Upload PDF Documents", accept_multiple_files=True, type=['pdf'])
    
    if st.button("🚀 Index to Qdrant Cloud", use_container_width=True, disabled=not QDRANT_READY):
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_docs = []
            temp_dir = "temp_uploads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            total_files = len(uploaded_files)
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"📥 Processing: {uploaded_file.name}...")
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                progress_bar.progress((i + 1) / (total_files * 2)) 
                
                try:
                    loader_docs = load_pdf(file_path)
                    all_docs.extend(loader_docs)
                    # Cleanup local file after loading
                    os.remove(file_path)
                except Exception as e:
                    st.error(f"Error loading {uploaded_file.name}: {str(e)}")

            status_text.text("⚡ Optimizing & Splitting...")
            chunks = split_documents(all_docs)
            progress_bar.progress(0.8)
            
            status_text.text("💾 Syncing with Qdrant Cloud...")
            try:
                create_vector_store(chunks)
                st.session_state.process_complete = True
                progress_bar.progress(1.0)
                status_text.text("✅ Sync Complete!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Cloud Storage Error: {str(e)}")
                if "quota" in str(e).lower():
                    st.warning("API Quota hit. Please wait a moment or check your Google Cloud Console.")
        else:
            st.error("Please select a file first.")

    st.markdown("---")
    
    # Recent Activity
    st.subheader("Global History")
    past_chats = list_chats(st.session_state.username)
    for chat in past_chats:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(f"📄 {chat['title'][:20]}...", key=f"chat_{chat['id']}", use_container_width=True):
                data = load_chat(chat['id'], st.session_state.username)
                if data:
                    st.session_state.chat_id = chat['id']
                    st.session_state.messages = data['messages']
                    st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat['id']}"):
                delete_chat(chat['id'])
                st.rerun()

# --- MAIN INTERFACE ---
st.markdown('<h1 class="main-title">AI Knowledge Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8B949E; margin-bottom: 2rem;">Cloud-Synchronized Document Intelligence & Specialized RAG</p>', unsafe_allow_html=True)

# Chat Display
for message in st.session_state.messages:
    msg_class = "user-msg" if message["role"] == "user" else "assistant-msg"
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            sources_html = "".join([f'<span class="source-tag">📍 {s}</span>' for s in message["sources"]])
            st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

# User Input
if prompt := st.chat_input("Analyze document content..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.process_complete:
        with st.chat_message("assistant"):
            st.warning("Knowledge base is empty. Please upload documents in the sidebar to begin analysis.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Retrieving from Cloud & Synthesizing..."):
                try:
                    # Prepare history
                    chat_history = []
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            chat_history.append(AIMessage(content=msg["content"]))

                    # Chain Call
                    rag_chain = get_rag_chain_with_memory_and_sources()
                    result = rag_chain({
                        "chat_history": chat_history,
                        "question": prompt
                    })
                    
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    
                    if sources:
                        sources_html = "".join([f'<span class="source-tag">📍 {s}</span>' for s in sources])
                        st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

                    # Persist
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    save_chat(st.session_state.chat_id, st.session_state.messages, st.session_state.username)
                    
                except Exception as e:
                    err_msg = str(e)
                    if "quota" in err_msg.lower():
                        st.error("🛑 Embedding API Quota hit. Try again in 60 seconds.")
                    else:
                        st.error(f"Generation Error: {err_msg}")
