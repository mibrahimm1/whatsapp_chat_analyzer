from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_BASE_URL"] = st.secrets["OPENAI_BASE_URL"]


llm = ChatOpenAI(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.3,
    max_tokens=512,
    openai_api_key=openai_api_key,
    openai_api_base=openai_base_url
)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def whatsapp_df_to_documents(df):
    # Sorting by timestamp
    df = df.sort_values("timestamp")

    # Formatting Chat
    chat_lines = [
        f"[{row['timestamp']}] {row['user']}: {row['messege']}"
        for _, row in df.iterrows()
    ]

    full_chat_text = "\n".join(chat_lines)

    # Splitting into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " "]  # prioritize message boundaries
    )

    chunks = splitter.split_text(full_chat_text)

    # Creating Documents
    documents = [Document(page_content=chunk) for chunk in chunks]

    return documents

def count_tokens(text):
    return len(text.split())

def get_token_limited_docs(docs, max_tokens=12000):
    total = 0
    limited_docs = []
    for doc in docs:
        tokens = count_tokens(doc.page_content)
        if total + tokens > max_tokens:
            break
        total += tokens
        limited_docs.append(doc)
    return limited_docs


def create_vector_store(docs):
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 5})


def get_rag_chain(df):
    docs = whatsapp_df_to_documents(df)
    retriever = create_vector_store(docs)

    qa_chain = RetrievalQA.from_chain_type(
        llm= llm,
        retriever= retriever,
        chain_type= "stuff",
        return_source_documents=True
    )

    return qa_chain


def query_rag(chain, query, max_tokens = 12000):
    # Run retrieval step separately
    retrieved_docs = chain.retriever.get_relevant_documents(query)

    # Limit token usage
    limited_docs = get_token_limited_docs(retrieved_docs, max_tokens=max_tokens)

    result = chain.combine_documents_chain.run(input_documents=limited_docs, question=query)

    return {
        "result": result,
        "source_documents": limited_docs
    }



