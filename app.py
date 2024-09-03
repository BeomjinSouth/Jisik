import streamlit as st
from utils import print_messages, StreamHandler
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import os

st.set_page_config(page_title="ChatGPT", page_icon="🦜")
st.title("🦜 ChatGPT")

# API KEY 설정
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 메시지 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 채팅 데이터를 저장할 store 세션 상태 생성
if "store" not in st.session_state:
    st.session_state["store"] = dict()

# 사이드바 설정
with st.sidebar:
    session_id = st.text_input("Session ID", value="abc123")
    
    clear_btn = st.button("대화로그 초기화")
    if clear_btn:
        st.session_state["messages"] = []
        st.experimental_rerun()

# 이전 대화로그를 출력하는 코드
print_messages()

# 세션 ID를 기반으로 세션 기록을 반환하는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:  # 세션 ID가 store에 없는 경우
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]

# 사용자 입력 처리
if user_input := st.chat_input("메시지를 입력해 주세요."):
    # 사용자가 입력한 내용 처리
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

    # AI의 답변 생성
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())

        # LLM을 사용하여 AI의 답변을 생성
        llm = ChatOpenAI(streaming=True, callbacks=[stream_handler])

        # 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "질문에 짧고 간결하게 답변해 주세요."),
            ]
        )

        # 대화 기록을 변수로 사용, history가 MessageHistory 의 key가 됨
        chain = prompt | llm

        chain_with_memory = RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
            chain,  # 실행할 Runnable 객체
            get_session_history,  # 세션 기록을 가져오는 함수
            input_messages_key="question",  # 사용자 질문의 키
            history_messages_key="history",  # 기록 메시지의 키
        )

        # 답변 생성 및 세션 ID 설정
        response = chain_with_memory.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        # 생성된 답변을 세션 상태에 저장
        st.session_state["messages"].append(
            ChatMessage(role="assistant", content=response.content)
        )
