import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

# Gmail SMTP 설정
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email_to_user(user_email, evaluation):
    msg = MIMEMultipart()
    msg['From'] = st.secrets["email"]["gmail_user"]
    msg['To'] = user_email
    msg['Subject'] = '학습 평가 결과'

    body = f"안녕하세요,\n\n귀하의 학습 평가 결과입니다:\n\n{evaluation}\n\n감사합니다."
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(st.secrets["email"]["gmail_user"], st.secrets["email"]["gmail_app_password"])
    text = msg.as_string()
    server.sendmail(st.secrets["email"]["gmail_user"], user_email, text)
    server.quit()

def send_email_to_teacher(evaluation, chat_history):
    msg = MIMEMultipart()
    msg['From'] = st.secrets["email"]["gmail_user"]
    msg['To'] = st.secrets["email"]["teacher_email"]
    msg['Subject'] = '학생 대화 내역 및 평가 결과'

    chat_history_text = '\n'.join([f"{role}: {msg}" for role, msg in chat_history])
    body = f"안녕하세요,\n\n학생의 대화 내역과 평가 결과입니다:\n\n{chat_history_text}\n\n평가 결과:\n{evaluation}\n\n감사합니다."
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(st.secrets["email"]["gmail_user"], st.secrets["email"]["gmail_app_password"])
    text = msg.as_string()
    server.sendmail(st.secrets["email"]["gmail_user"], st.secrets["email"]["teacher_email"], text)
    server.quit()
