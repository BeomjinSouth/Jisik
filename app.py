import streamlit as st
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

st.title("도우미 챗봇")

# 계정 생성 및 로그인 기능
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    with st.form(key="login_form"):
        st.write("계정이 없으신가요? 아래에서 생성해보세요.")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            # 로그인 인증 로직 추가 필요 (예: DB 확인)
            st.session_state["authenticated"] = True

        st.write("계정이 없으시다면 등록해주세요.")
        reg_email = st.text_input("등록할 이메일")
        reg_password = st.text_input("등록할 비밀번호", type="password")
        if st.form_submit_button("계정 등록"):
            # 계정 등록 로직 추가 필요 (예: DB에 저장)
            st.success("계정이 생성되었습니다. 로그인해주세요.")
else:
    # 기존 시스템 메시지 설정
    system_message = '''
    '''
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "system", "content": system_message}]

    st.write("원하는 문제를 생성해주세요.")

    # 문제 생성 섹션
    with st.form(key="question_form"):
        subject = st.selectbox("과목", ["영어", "수학", "과학"])
        category = st.selectbox("큰 카테고리", [])
        sub_category = st.selectbox("작은 카테고리", [])
        topic = st.text_input("생성하고 싶은 문제 주제")
        num_questions = st.number_input("문항 개수", min_value=1, max_value=10)
        difficulty = st.selectbox("난이도", ["쉬움", "중간", "어려움"])
        question_type = st.selectbox("문항 유형", ["논술형", "객관식"])
        
        # 카테고리 데이터 예시
        category_options = {
            "영어": {
                "문법": ["수동태", "현재완료", "관계대명사"],
                "독해": ["지문 해석", "어휘 문제"],
                "어휘": ["고급 어휘", "동의어"]
            },
            "수학": {
                "대수": ["방정식", "함수"],
                "기하": ["삼각형", "원"]
            },
            "과학": {
                "물리": ["역학", "전기"],
                "화학": ["화학 반응", "주기율표"]
            }
        }
        
        # 선택된 과목에 따라 카테고리 업데이트
        if subject:
            st.session_state.category_options = category_options[subject]
            category = st.selectbox("큰 카테고리", list(st.session_state.category_options.keys()))
            if category:
                sub_category = st.selectbox("작은 카테고리", st.session_state.category_options[category])

        if st.form_submit_button("생성하기"):
            # GPT를 이용해 문항 생성 로직
            st.session_state.messages.append({
                "role": "user", 
                "content": f"{subject} 과목에서 {category}의 {sub_category}에 대한 {topic} 주제의 {num_questions}개의 {difficulty} 난이도의 {question_type} 문제를 생성해주세요."
            })
            with st.chat_message("user"):
                st.markdown(st.session_state.messages[-1]["content"])

            with st.chat_message("assistant"):
                stream = client.chat_completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # 기존 챗봇 기능
    for idx, message in enumerate(st.session_state.messages):
        if idx > 0:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("문제에 대해 질문해주세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat_completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 평가하기 섹션
    if st.button("평가하기"):
        st.session_state.messages.append({
            "role": "user", 
            "content": "지금까지 생성한 문제와 대화 내용을 종합하여 평가해주세요."
        })
        with st.chat_message("user"):
            st.markdown(st.session_state.messages[-1]["content"])

        with st.chat_message("assistant"):
            stream = client.chat_completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
