# app.py
import streamlit as st
import sqlite3
import hashlib
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DB_FILE = "users.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            gender TEXT,
            phone TEXT,
            profile_image TEXT
        )''')

init_db()

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, pw, name, gender, phone):
    hashed_pw = hash_pw(pw)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                     (email, hashed_pw, name, gender, phone, ""))

def login_user(email, pw):
    hashed_pw = hash_pw(pw)
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?",
                           (email, hashed_pw))
        return cur.fetchone()

def update_user(email, name, gender, phone, image_path):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''UPDATE users
                        SET name = ?, gender = ?, phone = ?, profile_image = ?
                        WHERE email = ?''',
                     (name, gender, phone, image_path, email))

def get_user(email):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()

st.title("🚲 Bike Sharing App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

menu = st.sidebar.selectbox("메뉴", ["홈", "로그인", "회원가입", "사용자 정보", "EDA", "로그아웃"])

if menu == "홈":
    st.subheader("📌 프로젝트 개요")
    st.markdown("자전거 수요 데이터를 분석하는 웹앱입니다.")

elif menu == "회원가입":
    st.subheader("📝 회원가입")
    email = st.text_input("이메일")
    pw = st.text_input("비밀번호", type="password")
    name = st.text_input("이름")
    gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
    phone = st.text_input("전화번호")
    if st.button("회원가입"):
        try:
            register_user(email, pw, name, gender, phone)
            st.success("회원가입 성공! 로그인 해주세요.")
        except:
            st.error("이미 존재하는 계정이거나 오류가 발생했습니다.")

elif menu == "로그인":
    st.subheader("🔐 로그인")
    email = st.text_input("이메일")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        user = login_user(email, pw)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("로그인 성공")
        else:
            st.error("로그인 실패")

elif menu == "사용자 정보" and st.session_state.logged_in:
    user = get_user(st.session_state.user_email)
    st.subheader("👤 사용자 정보 수정")
    name = st.text_input("이름", value=user[2])
    gender = st.selectbox("성별", ["선택 안함", "남성", "여성"], index=["선택 안함", "남성", "여성"].index(user[3]))
    phone = st.text_input("전화번호", value=user[4])
    uploaded = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
    image_path = user[5]
    if uploaded:
        image_path = os.path.join(UPLOAD_FOLDER, f"{user[0].replace('@','_')}.jpg")
        with open(image_path, "wb") as f:
            f.write(uploaded.read())
        st.image(image_path, width=150)
    elif user[5]:
        st.image(user[5], width=150)
    if st.button("수정 저장"):
        update_user(user[0], name, gender, phone, image_path)
        st.success("수정 완료")

elif menu == "EDA":
    st.subheader("📊 EDA - 자전거 대여 분석")
    uploaded = st.file_uploader("CSV 파일 업로드 (train.csv)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded, parse_dates=['datetime'])
        df['hour'] = df['datetime'].dt.hour
        df['dayofweek'] = df['datetime'].dt.dayofweek
        st.write(df.head())
        st.bar_chart(df['hour'].value_counts().sort_index())
        st.bar_chart(df['dayofweek'].value_counts().sort_index())
        st.line_chart(df[['temp', 'humidity']])

elif menu == "로그아웃":
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.success("로그아웃 되었습니다.")
