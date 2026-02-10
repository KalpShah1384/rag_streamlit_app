import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from core.loader import load_pdf
from core.splitter import split_documents
from core.vector_store import create_vector_store, load_vector_store
from core.rag_chain import get_rag_chain_with_memory
from core.history import save_chat, load_chat, list_chats, delete_chat
from langchain_core.messages import HumanMessage, AIMessage

# Page configuration
st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background-color: #38bdf8;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0ea5e9;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
    }
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .chat-message {
        padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; display: flex;
    }
    .chat-message.user {
        background-color: #1e293b; border: 1px solid #334155;
    }
    .chat-message.bot {
        background-color: #334155; border: 1px solid #475569;
    }
    .chat-message .avatar {
        width: 40px; height: 40px; border-radius: 50%; object-fit: cover;
    }
    .chat-message .message {
        margin-left: 1rem; color: #f1f5f9;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Chat List Styling */
    .chat-item {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
        background-color: #1e293b;
        border: 1px solid #334155;
        transition: all 0.2s;
    }
    .chat-item:hover {
        background-color: #334155;
    }
    .active-chat {
        background-color: #38bdf8 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# App State
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "process_complete" not in st.session_state:
    # Check if we already have a vector store
    st.session_state.process_complete = os.path.exists("app_db")

load_dotenv()

# Sidebar
with st.sidebar:
    st.title("🤖 Assistant")
    
    if st.button("➕ New Chat"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.subheader("Your Conversations")
    past_chats = list_chats()
    for chat in past_chats:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            btn_label = f"💬 {chat['title']}"
            is_active = chat['id'] == st.session_state.chat_id
            if st.button(btn_label, key=f"btn_{chat['id']}", help="Open this chat"):
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
    st.subheader("Document Ingestion")
    
    uploaded_files = st.file_uploader("Upload PDF documents", accept_multiple_files=True, type=['pdf'])
    
    if st.button("Process Documents"):
        if uploaded_files:
            with st.spinner("Processing..."):
                all_docs = []
                if not os.path.exists("temp_uploads"):
                    os.makedirs("temp_uploads")
                
                for uploaded_file in uploaded_files:
                    file_path = os.path.join("temp_uploads", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    loader_docs = load_pdf(file_path)
                    all_docs.extend(loader_docs)
                
                chunks = split_documents(all_docs)
                create_vector_store(chunks, persist_directory="app_db")
                st.session_state.process_complete = True
                st.success(f"✅ Indexed {len(chunks)} chunks!")
        else:
            st.error("Please upload at least one PDF.")

# Main Interface
st.title("🧠 AI Knowledge Assistant")
st.markdown("---")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    if not st.session_state.process_complete:
        with st.chat_message("assistant"):
            st.warning("Please upload and process documents first using the sidebar.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Searching and thinking..."):
                # Prepare history for LangChain
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    else:
                        chat_history.append(AIMessage(content=msg["content"]))

                # Get RAG Chain
                rag_chain = get_rag_chain_with_memory(persist_directory="app_db")
                
                # Invoke
                response = rag_chain.invoke({
                    "chat_history": chat_history,
                    "question": prompt
                })
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # PERSIST: Save the chat to disk after assistant response
                save_chat(st.session_state.chat_id, st.session_state.messages)

# Bottom padding
st.markdown("<br><br>", unsafe_allow_html=True)
