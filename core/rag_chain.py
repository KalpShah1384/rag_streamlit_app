from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from core.vector_store import load_vector_store
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time

def format_docs(docs):
    """Formats a list of documents into a single string for context."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain(persist_directory: str = "faiss_db"):
    """Creates and returns a RAG chain."""
    
    # 1. Load the vector store and set up the retriever
    vector_store = load_vector_store(persist_directory)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # 2. Define the LLM (using the verified Gemini model)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # 3. Define the RAG Prompt
    template = """You are an AI Knowledge Assistant. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and professional.

Context:
{context}

Question: {question}

Helpful Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)

    # 4. Build the LCEL Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def get_rag_chain_with_sources(persist_directory: str = "faiss_db"):
    """
    Creates a chain that returns both the answer and the source documents.
    This uses a more manual approach to return sources.
    """
    vector_store = load_vector_store(persist_directory)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    template = """You are an AI Knowledge Assistant. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and professional.

Context:
{context}

Question: {question}

Helpful Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)

    def retrieve_and_format(query):
        docs = retriever.invoke(query)
        context = format_docs(docs)
        return context, docs

    # Manual chain execution to capture docs
    def invoke_chain(query):
        context, docs = retrieve_and_format(query)
        # Use prompt and llm separately or via pipe
        response = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": query})
        return {
            "answer": response,
            "sources": [doc.metadata.get("source", "Unknown") for doc in docs],
            "chunks": [doc.page_content for doc in docs]
        }

    return invoke_chain

def get_rag_chain_with_memory(persist_directory: str = "faiss_db"):
    """
    Creates a RAG chain that handles conversation history.
    """
    vector_store = load_vector_store(persist_directory)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # Contextualize question prompt
    # This helps in handling follow-up questions by re-writing them based on history
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    
    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

    # RAG prompt
    qa_system_prompt = """You are an AI Knowledge Assistant. Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know, don't try to make up an answer. \
Keep the answer concise and professional.

Context:
{context}"""

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    def contextualized_question(input: dict):
        if input.get("chat_history"):
            return contextualize_q_chain
        else:
            return input.get("question")

    rag_chain = (
        RunnablePassthrough.assign(
            context=contextualized_question | retriever | format_docs
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
def get_rag_chain_with_memory_and_sources(persist_directory: str = "faiss_db"):
    """
    Creates a RAG chain that handles conversation history AND returns sources.
    """
    vector_store = load_vector_store(persist_directory)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # 1. Contextualize Question
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

    # 2. QA Prompt
    qa_system_prompt = """You are an AI Knowledge Assistant. Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know, don't try to make up an answer. \
Keep the answer concise and professional.

Context:
{context}"""

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    
    qa_chain = qa_prompt | llm | StrOutputParser()

    # 3. Custom Invoke Function with Robust Retry Logic
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=15),
    )
    def invoke_chain(input_data):
        question = input_data["question"]
        chat_history = input_data.get("chat_history", [])
        
        standalone_question = question
        # Reformulate question if history exists
        if chat_history:
            try:
                standalone_question = contextualize_q_chain.invoke({
                    "chat_history": chat_history,
                    "question": question
                })
                # If AI returned something empty or invalid, fallback
                if not standalone_question or len(standalone_question.strip()) < 2:
                    standalone_question = question
            except Exception:
                standalone_question = question
            
        # Retrieve docs (Embedding call happens here)
        try:
            docs = retriever.invoke(standalone_question)
        except Exception as e:
            # If the reformulated question crashes the embedding engine, 
            # try one last time with the raw original question
            if chat_history:
                docs = retriever.invoke(question)
            else:
                raise e
                
        context = format_docs(docs)
        
        # Generate Answer
        answer = qa_chain.invoke({
            "context": context,
            "chat_history": chat_history,
            "question": question
        })
        
        return {
            "answer": answer,
            "sources": list(set([doc.metadata.get("source", "Unknown") for doc in docs])),
            "chunks": [doc.page_content for doc in docs]
        }

    return invoke_chain
