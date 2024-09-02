import streamlit as st
import sqlite3
import hashlib
from openai import OpenAI

# 데이터베이스 설정
conn = sqlite3.connect('users.db')  # SQLite 데이터베이스 파일을 생성하고 연결합니다.
c = conn.cursor()

# 사용자 테이블 생성 (이메일과 패스워드를 저장)
c.execute('''CREATE TABLE IF NOT EXISTS users
             (email TEXT PRIMARY KEY, password TEXT)''')

# 학습 이력 테이블 생성 (이메일과 피드백을 저장)
c.execute('''CREATE TABLE IF NOT EXISTS learning_history
             (email TEXT, feedback TEXT)''')

# 비밀번호 해싱 함수 (SHA-256 알고리즘 사용)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 계정 생성 함수
def create_account(email, password):
    c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hash_password(password)))
    conn.commit()

# 로그인 확인 함수
def login(email, password):
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hash_password(password)))
    return c.fetchone()

# GPT API 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # API 키를 환경 변수에서 불러옵니다.

st.title("교육용 챗봇 시스템")

# 세션 상태 초기화
if "email" not in st.session_state:
    st.session_state["email"] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# 계정 생성 및 로그인 UI
if st.session_state["email"]:
    st.success(f"로그인 성공: {st.session_state['email']}")
else:
    st.header("계정 생성")
    email = st.text_input("이메일")
    password = st.text_input("패스워드", type="password")
    if st.button("계정 등록"):
        create_account(email, password)
        st.success("계정이 생성되었습니다. 이제 로그인해 주세요.")

    st.header("로그인")
    email = st.text_input("로그인 이메일", key="login_email")
    password = st.text_input("로그인 패스워드", type="password", key="login_password")
    if st.button("로그인"):
        if login(email, password):
            st.session_state["email"] = email
            st.success("로그인 성공")
        else:
            st.error("로그인 실패")

# 문항 생성 UI
if st.session_state["email"]:
    st.header("문항 생성")

    subject = st.selectbox("과목", ["영어", "수학", "과학"])
    categories = {
        "영어": {"문법": ["수동태", "현재완료", "관계대명사"], "독해": ["지문 해석", "어휘 문제"], "어휘": ["고급 어휘", "동의어"]},
        "수학": {"대수": ["방정식", "함수"], "기하": ["삼각형", "원"]},
        "과학": {"물리": ["역학", "전기"], "화학": ["화학 반응", "주기율표"]}
    }

    main_category = st.selectbox("큰 카테고리", list(categories[subject].keys()))
    sub_category = st.selectbox("작은 카테고리", categories[subject][main_category])

    topic = st.text_input("문제 주제")
    num_questions = st.number_input("문항 개수", min_value=1, max_value=10)
    difficulty = st.selectbox("난이도", ["쉬움", "중간", "어려움"])
    question_type = st.selectbox("문항 유형", ["논술형", "객관식"])

    if st.button("생성하기"):
        with st.spinner("문항 생성 중..."):
            # OpenAI API를 사용하여 문항 생성
            response = client.chat.completions.create(
                model="gpt-4o",  # 사용할 GPT 모델
                messages=[{
                    "role": "user",
                    "content": f"{subject} 과목의 {main_category}에서 {sub_category}에 대한 {difficulty} 수준의 {question_type} 문제를 {num_questions}개 생성해줘."
                }],
                stream=True  # 결과를 스트리밍 방식으로 가져옴
            )

            # 결과를 스트림으로 처리
            questions = st.write_stream(response)
            st.session_state["questions"] = questions  # 생성된 문제를 세션에 저장

# 채팅 UI
if st.session_state.get("questions"):
    st.header("GPT와 대화하기")

    user_input = st.text_input("여기에 채팅 내용을 입력하세요", key="chat_input")
    
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state["messages"].append({"role": "assistant", "content": response})
    
    if st.button("평가하기"):
        with st.spinner("평가 중..."):
            # 사용자의 답변 및 태도에 대한 평가 요청 메시지 작성
            evaluation_context = "지금까지의 대화 및 생성된 문제에 대한 사용자의 답변 및 태도는 다음과 같습니다:\n\n"
            for i, message in enumerate(st.session_state["messages"], 1):
                if message["role"] == "user":
                    evaluation_context += f"{i}. {message['content']}\n"

            evaluation_context += "\n이 답변에 대해 평가를 진행해 주세요. 답변의 정확성, 태도, 그리고 개선이 필요한 점에 대해 피드백을 제공해 주세요."

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state["messages"] + [{"role": "user", "content": evaluation_context}],
                stream=True,
            )
            response_content = st.write_stream(response)

            # 학습 이력을 데이터베이스에 저장
            c.execute('INSERT INTO learning_history (email, feedback) VALUES (?, ?)',
                      (st.session_state["email"], response_content))
            conn.commit()

            st.success("평가 결과를 이메일로 전송했습니다.")
