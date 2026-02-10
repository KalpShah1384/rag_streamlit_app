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
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1626 !important; /* Slightly darker navy for sidebar */
        border-right: 1px solid #8A244B;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* Sidebar Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid #8A244B !important;
        color: #FFFFFF !important;
        background-color: #111F35 !important;
    }
    
    .new-chat-btn > div > button {
        background: linear-gradient(135deg, #F63049 0%, #D02752 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(246, 48, 73, 0.3);
    }
    
    .new-chat-btn > div > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(246, 48, 73, 0.5);
    }

    /* Chat Messages */
    .chat-bubble {
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .user-bubble {
        background-color: #8A244B;
        border: 1px solid #D02752;
        margin-left: 15%;
        color: white;
    }
    
    .assistant-bubble {
        background-color: #1b2b45;
        border: 1px solid #8A244B;
        margin-right: 15%;
        color: #f0f0f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Source Tags */
    .source-tag {
        display: inline-block;
        background: linear-gradient(90deg, #D02752 0%, #8A244B 100%);
        color: #FFFFFF;
        padding: 4px 14px;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-right: 8px;
        margin-top: 8px;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #F63049 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: #F63049;
        border-radius: 10px;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #F63049 !important;
    }

    /* --- MOBILE RESPONSIVENESS --- */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        .source-tag {
            padding: 3px 8px;
            font-size: 0.7rem;
        }
        /* Make sidebar more compact on mobile if it overlays */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeIn 0.4s ease-out forwards;
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

# --- SIDEBAR ---
with st.sidebar:
    # Custom CSS Logo
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="
                width: 80px; 
                height: 80px; 
                background: linear-gradient(135deg, #F63049 0%, #8A244B 100%);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 10px 20px rgba(246, 48, 73, 0.4);
                border: 2px solid #D02752;
                transform: rotate(-10deg);
            ">
                <span style="font-size: 40px; transform: rotate(10deg);">🧠</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.title("Knowledge Hub")
    
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
    past_chats = list_chats()
    for chat in past_chats:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            active_style = "active-chat" if chat['id'] == st.session_state.chat_id else ""
            if st.button(f"📄 {chat['title'][:25]}...", key=f"chat_{chat['id']}", use_container_width=True):
                data = load_chat(chat['id'])
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
                    save_chat(st.session_state.chat_id, st.session_state.messages)
                    
                except Exception as e:
                    st.error(f"Error during generation: {str(e)}")
