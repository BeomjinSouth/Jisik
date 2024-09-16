import streamlit as st
import openai

def generate_questions():
    st.subheader('문제 생성')
    subjects = {
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

    subject = st.selectbox('과목 선택', list(subjects.keys()))
    category = st.selectbox('큰 카테고리 선택', list(subjects[subject].keys()))
    subcategory = st.selectbox('작은 카테고리 선택', subjects[subject][category])
    topic = st.text_input('생성하고 싶은 문제 주제')
    num_questions = st.number_input('문항 개수', min_value=1, max_value=10, value=1, step=1)
    difficulty = st.selectbox('난이도', ['쉬움', '보통', '어려움'])
    question_type = st.selectbox('문항 유형', ['논술형', '객관식'])

    if st.button('생성하기'):
        with st.spinner('문제를 생성하고 있습니다...'):
            prompt = f"{subject} 과목의 {category} 중 {subcategory}에 대한 {difficulty} 수준의 {question_type} 문제를 {num_questions}개 생성해줘. 주제는 '{topic}'이야."
            openai.api_key = st.secrets["api_keys"]["openai_api_key"]
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 문제 출제자입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            questions = response.choices[0].message.content
            st.session_state['questions'] = questions
            st.success('문제가 생성되었습니다.')
            st.write(questions)
