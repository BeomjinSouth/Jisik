import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import hashlib
from email_validator import validate_email, EmailNotValidError

# 사용자 정보를 저장할 users.yaml 파일을 로드하거나 생성합니다.
def load_user_config():
    try:
        with open('users.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        config = {'credentials': {'usernames': {}}}
    return config

def save_user_config(config):
    with open('users.yaml', 'w') as file:
        yaml.dump(config, file)

def register_user():
    st.subheader('회원가입')
    email = st.text_input('이메일 주소')
    password = st.text_input('비밀번호', type='password')
    password_confirm = st.text_input('비밀번호 확인', type='password')
    if st.button('계정 등록'):
        # 이메일 유효성 검사
        try:
            validate_email(email)
        except EmailNotValidError as e:
            st.error('유효한 이메일 주소를 입력해주세요.')
            return
        if password != password_confirm:
            st.error('비밀번호가 일치하지 않습니다.')
            return
        config = load_user_config()
        if email in config['credentials']['usernames']:
            st.error('이미 등록된 이메일입니다.')
            return
        hashed_password = stauth.Hasher([password]).generate()[0]
        config['credentials']['usernames'][email] = {
            'email': email,
            'password': hashed_password
        }
        save_user_config(config)
        st.success('계정이 성공적으로 생성되었습니다. 로그인 해주세요.')
def login_user():
    st.subheader('로그인')
    email = st.text_input('이메일 주소')
    password = st.text_input('비밀번호', type='password')
    if st.button('로그인'):
        config = load_user_config()
        if email not in config['credentials']['usernames']:
            st.error('등록되지 않은 이메일입니다.')
            return
        hashed_password = config['credentials']['usernames'][email]['password']
        authenticator = stauth.Authenticate(
            {'usernames': {email: {'password': hashed_password}}},
            'cookie_name',
            'signature_key',
            cookie_expiry_days=30
        )
        # 매개변수를 위치 인자로 전달하고, 반환값을 두 개로 받습니다.
        name, authentication_status = authenticator.login('Login', 'main')
        if authentication_status:
            st.session_state['user'] = email
            st.success(f'환영합니다, {email}님!')
            st.experimental_rerun()
        elif authentication_status == False:
            st.error('이메일 또는 비밀번호가 일치하지 않습니다.')
        elif authentication_status == None:
            st.warning('로그인 정보를 입력해주세요.')

