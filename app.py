import streamlit as st
from authentication import register_user, login_user
from question_generation import generate_questions
from chat_interface import chat_interface

def main():
    st.title('AI 학습 플랫폼')
    if 'user' not in st.session_state:
        menu = ['로그인', '회원가입']
        choice = st.sidebar.selectbox('메뉴', menu)
        if choice == '로그인':
            login_user()
        elif choice == '회원가입':
            register_user()
    else:
        st.sidebar.success(f"로그인됨: {st.session_state['user']}")
        menu = ['문제 생성', '채팅', '로그아웃']
        choice = st.sidebar.selectbox('메뉴', menu)
        if choice == '문제 생성':
            generate_questions()
        elif choice == '채팅':
            chat_interface()
        elif choice == '로그아웃':
            st.session_state.pop('user')
            st.experimental_rerun()

if __name__ == '__main__':
    main()
