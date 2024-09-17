import streamlit as st
import bcrypt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email_validator import validate_email, EmailNotValidError


def get_worksheet():
    # Google Sheets API와 Drive API 사용 범위 설정
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # st.secrets로부터 서비스 계정 정보를 불러옵니다
    creds_dict = st.secrets["gcp_service_account"]
    
    # Google Sheets 인증 정보 설정
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Google 스프레드시트 접근
    sheet = client.open_by_key('157IwlgSWvzxbqPoKZwTiRACc6kn1gh1EUOf3SI-JTyw')
    worksheet = sheet.sheet1  # 첫 번째 시트 사용
    return worksheet


def register_user():
    st.subheader('회원가입')
    email = st.text_input('이메일 주소')
    password = st.text_input('비밀번호', type='password')
    password_confirm = st.text_input('비밀번호 확인', type='password')
    if st.button('계정 등록'):
        # 이메일 유효성 검사
        try:
            validate_email(email)
        except EmailNotValidError:
            st.error('유효한 이메일 주소를 입력해주세요.')
            return
        if password != password_confirm:
            st.error('비밀번호가 일치하지 않습니다.')
            return
        
        # 스프레드시트에서 이메일 중복 체크
        worksheet = get_worksheet()
        emails = worksheet.col_values(1)  # A열의 이메일 목록
        if email in emails:
            st.error('이미 등록된 이메일입니다.')
            return
        
        # 비밀번호 해싱
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 스프레드시트에 사용자 정보 저장
        worksheet.append_row([email, hashed_password.decode('utf-8')])
        st.success('계정이 성공적으로 생성되었습니다. 로그인 해주세요.')

def login_user():
    st.subheader('로그인')
    email = st.text_input('이메일 주소')
    password = st.text_input('비밀번호', type='password')
    if st.button('로그인'):
        worksheet = get_worksheet()
        records = worksheet.get_all_records()
        user_found = False
        for record in records:
            if record['Email'] == email:
                user_found = True
                stored_password = record['Password'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    st.success(f'환영합니다, {email}님!')
                    st.session_state['user'] = email
                    st.rerun()
                else:
                    st.error('비밀번호가 일치하지 않습니다.')
                break
        if not user_found:
            st.error('등록되지 않은 이메일입니다.')
