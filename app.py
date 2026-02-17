import streamlit as st
import os
import uuid
import time
from dotenv import load_dotenv
from core.loader import load_pdf
from core.splitter import split_documents
from core.vector_store import create_vector_store, load_vector_store
from core.rag_chain import get_rag_chain_with_memory_and_sources
from core.history import save_chat, load_chat, list_chats, delete_chat
from core.auth import verify_user, register_user
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
        background-color: #111F35;
        color: #FFFFFF;
    }
    
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 120px;
        max-width: 1000px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1626 !important;
        border-right: 1px solid rgba(138, 36, 75, 0.3);
    }
    
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* Sidebar Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(138, 36, 75, 0.5) !important;
        color: #FFFFFF !important;
        background-color: rgba(17, 31, 53, 0.8) !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton > button:hover {
        border-color: #F63049 !important;
        background-color: rgba(246, 48, 73, 0.1) !important;
        transform: translateY(-1px);
    }
    
    .new-chat-btn > div > button {
        background: linear-gradient(135deg, #F63049 0%, #D02752 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(246, 48, 73, 0.3);
        margin-top: 10px;
    }
    
    .new-chat-btn > div > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(246, 48, 73, 0.5);
    }

    /* Chat Messages Styling Enhancement */
    [data-testid="stChatMessage"] {
        background-color: rgba(27, 43, 69, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stChatMessageContent"] {
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }

    /* Source Tags */
    .source-tag {
        display: inline-block;
        background: rgba(138, 36, 75, 0.2);
        color: #F63049;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
        margin-top: 8px;
        font-weight: 600;
        border: 1px solid rgba(246, 48, 73, 0.3);
        backdrop-filter: blur(4px);
    }

    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(90deg, #FFFFFF 0%, #F63049 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(246, 48, 73, 0.4);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #F63049;
    }
    
    /* Input Area Styling */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid rgba(246, 48, 73, 0.2) !important;
        background-color: rgba(13, 22, 38, 0.9) !important;
        padding: 10px !important;
    }

    /* --- MOBILE RESPONSIVENESS UPDATES --- */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        [data-testid="stSidebar"] {
            width: 80vw !important;
        }
        
        [data-testid="stChatMessage"] {
            padding: 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        h1 {
            font-size: 1.8rem !important;
        }
        
        .stChatInputContainer {
            margin-bottom: 15px !important;
        }
        
        /* Fix tabs on mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 15px !important;
            font-size: 0.9rem !important;
        }
        
        /* Larger tap targets for sidebar activity */
        section[data-testid="stSidebar"] .stButton > button {
            padding: 0.7rem 0.5rem !important;
            margin-bottom: 5px !important;
        }
    }
    
    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem !important;
        }
        
        .source-tag {
            font-size: 0.75rem;
            padding: 3px 10px;
        }
        
        [data-testid="stSidebar"] {
            width: 90vw !important;
        }
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stChatMessage"] {
        animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP STATE ---
load_dotenv()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "process_complete" not in st.session_state:
    st.session_state.process_complete = os.path.exists("app_db")

if "username" not in st.session_state:
    st.session_state.username = None

# --- SIDEBAR ---
# --- MAIN INTERFACE ---
if not st.session_state.username:
    # Center login on mobile and desktop
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-top: 50px; margin-bottom: 30px;">
            <div style="
                width: 100px; 
                height: 100px; 
                background: linear-gradient(135deg, #F63049 0%, #8A244B 100%);
                border-radius: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 15px 35px rgba(246, 48, 73, 0.4);
                border: 2px solid #D02752;
                transform: rotate(-5deg);
            ">
                <span style="font-size: 50px; transform: rotate(5deg);">🧠</span>
            </div>
        </div>
        <h1 style="text-align: center; font-size: 2.5rem; margin-bottom: 5px;">AI Knowledge Hub</h1>
        <p style="text-align: center; color: rgba(255,255,255,0.6); margin-bottom: 40px;">Professional Document Intelligence Assistant</p>
    """, unsafe_allow_html=True)
    
    _, auth_col, _ = st.columns([1, 2, 1])
    with auth_col:
        st.markdown('<div style="background-color: rgba(13, 22, 38, 0.8); padding: 30px; border-radius: 20px; border: 1px solid rgba(246, 48, 73, 0.2);">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            l_user = st.text_input("Username", key="login_user")
            l_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Direct Login", use_container_width=True):
                success, message = verify_user(l_user, l_pass)
                if success:
                    st.session_state.username = l_user
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            r_user = st.text_input("New Username", key="reg_user")
            r_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Register Account", use_container_width=True):
                if r_user and r_pass:
                    success, message = register_user(r_user, r_pass)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (Logged In) ---
with st.sidebar:
    # Custom CSS Logo (Compact for sidebar)
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="
                width: 60px; 
                height: 60px; 
                background: linear-gradient(135deg, #F63049 0%, #8A244B 100%);
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 10px 20px rgba(246, 48, 73, 0.4);
                border: 2px solid #D02752;
            ">
                <span style="font-size: 30px;">🧠</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.title("Knowledge Hub")

    col_u1, col_u2 = st.columns([0.7, 0.3])
    with col_u1:
        st.write(f"👤 **{st.session_state.username}**")
    with col_u2:
        if st.button("Logout", help="Sign out"):
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    
    # New Chat Button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ Start New Session", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Conversations History
    st.subheader("Recent Activity")
    past_chats = list_chats(st.session_state.username)
    for chat in past_chats:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            active_style = "active-chat" if chat['id'] == st.session_state.chat_id else ""
            if st.button(f"📄 {chat['title'][:25]}...", key=f"chat_{chat['id']}", use_container_width=True):
                data = load_chat(chat['id'], st.session_state.username)
                if data:
                    st.session_state.chat_id = chat['id']
                    st.session_state.messages = data['messages']
                    st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat['id']}", help="Delete chat"):
                delete_chat(chat['id'])
                if st.session_state.chat_id == chat['id']:
                    st.session_state.chat_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun()

    st.markdown("---")
    
    # File Management
    st.subheader("Document Center")
    uploaded_files = st.file_uploader("Drop PDF files here (Max 500MB)", accept_multiple_files=True, type=['pdf'])
    
    if st.button("🚀 Process & Index Documents", use_container_width=True):
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_docs = []
            if not os.path.exists("temp_uploads"):
                os.makedirs("temp_uploads")
            
            total_files = len(uploaded_files)
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"📥 Extracting: {uploaded_file.name}...")
                file_path = os.path.join("temp_uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Update progress
                progress_bar.progress((i + 1) / (total_files * 2)) 
                
                # Load with Unstructured (OCR enabled)
                loader_docs = load_pdf(file_path)
                all_docs.extend(loader_docs)

            status_text.text("⚡ Analyzing tables and chunking text...")
            chunks = split_documents(all_docs)
            progress_bar.progress(0.8)
            
            status_text.text("💾 Persisting to Vector DB...")
            create_vector_store(chunks, persist_directory="app_db")
            
            progress_bar.progress(1.0)
            status_text.text("✅ Ingestion Complete!")
            st.session_state.process_complete = True
            time.sleep(1)
            status_text.empty()
            st.rerun()
        else:
            st.error("Please select a file first.")

# --- MAIN INTERFACE ---
st.title("🧠 AI Knowledge Assistant")
st.caption("Deep Document Analysis with Table & Image Recognition Support")

# Chat Container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                st.markdown("---")
                sources_html = "".join([f'<span class="source-tag">📍 {s}</span>' for s in message["sources"]])
                st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

# User Input area
if prompt := st.chat_input("Ask a specialized question..."):
    # UI: Add user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # UI: Assistant Thinking
    if not st.session_state.process_complete:
        with st.chat_message("assistant"):
            st.warning("No knowledge base found. Please upload documents in the sidebar.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing context and generating response..."):
                try:
                    # Prepare history
                    chat_history = []
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            chat_history.append(AIMessage(content=msg["content"]))

                    # Chain Call
                    rag_chain = get_rag_chain_with_memory_and_sources(persist_directory="app_db")
                    result = rag_chain({
                        "chat_history": chat_history,
                        "question": prompt
                    })
                    
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    
                    # Show Sources
                    if sources:
                        st.markdown("---")
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
                    st.error(f"Error during generation: {str(e)}")
