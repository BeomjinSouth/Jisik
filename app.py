import streamlit as st
from authentication import login_user, register_user
from question_generation import generate_questions
from chat_interface import chat_interface

def main():
    st.title('AI 학습 플랫폼')
    menu = ['로그인', '회원가입']
    choice = st.sidebar.selectbox('메뉴', menu)
    if choice == '로그인':
        login_user()
    elif choice == '회원가입':
        register_user()
    else:
        st.subheader('메인 페이지')


if __name__ == '__main__':
    main()
