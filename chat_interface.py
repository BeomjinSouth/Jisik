import streamlit as st
from openai import OpenAI
import sqlite3
import datetime
from email_sender import send_email_to_user, send_email_to_teacher

# 데이터베이스 연결
conn = sqlite3.connect('user_data.db', check_same_thread=False)
c = conn.cursor()

# 테이블 생성
def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (user TEXT, timestamp TEXT, role TEXT, message TEXT)''')
    conn.commit()

def chat_interface():
    create_table()
    st.subheader('채팅')

    if 'questions' not in st.session_state:
        st.warning('먼저 문제를 생성해주세요.')
        return
    else:
        st.write('### 생성된 문제')
        st.write(st.session_state['questions'])

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    user_input = st.text_input('입력')

    col1, col2, col3 = st.columns(3)
    with col1:
        ask = st.button('질문하기')
    with col2:
        discuss = st.button('얘기하기')
    with col3:
        evaluate = st.button('평가하기')

    if ask and user_input:
        # GPT에게 힌트를 요청하는 로직
        prompt = f"학생이 질문했습니다: '{user_input}'. 이에 대해 힌트를 제공해주세요."
        openai.api_key = st.secrets["api_keys"]["openai_api_key"]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 친절한 선생님입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        st.session_state['chat_history'].append(('user', user_input))
        st.session_state['chat_history'].append(('assistant', answer))
        st.write('**GPT:**', answer)
        # 대화 내역을 데이터베이스에 저장
        save_chat_history(st.session_state['user'], 'user', user_input)
        save_chat_history(st.session_state['user'], 'assistant', answer)

    elif discuss and user_input:
        # 일반적인 대화를 진행하는 로직
        prompt = f"학생과 대화를 진행하세요. 학생의 말: '{user_input}'"
        openai.api_key = st.secrets["api_keys"]["openai_api_key"]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 친절한 대화 상대입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        st.session_state['chat_history'].append(('user', user_input))
        st.session_state['chat_history'].append(('assistant', answer))
        st.write('**GPT:**', answer)
        # 대화 내역 저장
        save_chat_history(st.session_state['user'], 'user', user_input)
        save_chat_history(st.session_state['user'], 'assistant', answer)
    elif evaluate:
        if len(st.session_state['chat_history']) == 0:
            st.warning('대화 내역이 없습니다.')
            return
        # 평가를 진행하는 로직
        # 전체 대화 내용을 기반으로 평가
        chat_history_text = '\n'.join([f"{role}: {msg}" for role, msg in st.session_state['chat_history']])
        prompt = f"학생과의 대화 내용입니다:\n{chat_history_text}\n\n학생의 답변을 다양한 측면에서 평가하고 피드백을 제공해주세요."
        openai.api_key = st.secrets["api_keys"]["openai_api_key"]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 엄격하지만 공정한 평가자입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        evaluation = response.choices[0].message.content
        st.write('**평가 결과:**', evaluation)
        # 이메일 전송
        send_email_to_user(st.session_state['user'], evaluation)
        send_email_to_teacher(evaluation, st.session_state['chat_history'])
        st.success('평가 결과가 이메일로 전송되었습니다.')
        # 학습 데이터 분석 및 피드백
        analyze_progress(st.session_state['user'])

def save_chat_history(user, role, message):
    timestamp = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO chat_history (user, timestamp, role, message) VALUES (?, ?, ?, ?)", (user, timestamp, role, message))
    conn.commit()

def analyze_progress(user):
    c.execute("SELECT message FROM chat_history WHERE user=? AND role='assistant'", (user,))
    evaluations = [row[0] for row in c.fetchall()]
    if len(evaluations) >= 2:
        if len(evaluations[-1]) > len(evaluations[-2]):
            st.write('이전보다 더 좋아졌어요!')
        else:
            st.write('더 노력해봐요!')
