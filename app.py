import os
from openai import OpenAI

# OpenAI API 키 설정
openai_client = OpenAI(api_key=os.getenv("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"))

import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ChatVectorDBChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

def setup_pdf_qa(pdf):
    st.session_state.pdf = pdf
    loader = PyPDFLoader(pdf)
    pdf_doc = loader.load_and_split()
    return pdf_doc

def setup_qa_chain(pdf_doc):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    persist_directory = './persist_directory/'
    embedding = OpenAIEmbeddings(client=openai_client)
    all_splits = text_splitter.split_documents(pdf_doc)
    vectordb = Chroma.from_documents(all_splits, embedding=embedding, persist_directory=persist_directory)
    vectordb.persist()
    pdf_qa = ChatVectorDBChain.from_llm(ChatOpenAI(temperature=0, model_name="gpt-4", client=openai_client), vectordb)
    return pdf_qa

def main():
    st.header("PDF와 Q&A 💬")

    pdf = st.text_input("PDF 파일 경로를 입력하세요:")

    if st.button("PDF 로드"):
        st.session_state.pdf_doc = setup_pdf_qa(pdf)
        st.write("PDF가 로드되었습니다!")

    query = st.text_input("PDF에 대해 질문하세요:")

    if query:
        pdf_qa = setup_qa_chain(st.session_state.pdf_doc)
        result = pdf_qa({"question": query, "chat_history": []})
        st.write(result["answer"])

if __name__ == '__main__':
    main()
