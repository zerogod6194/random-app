import random

import streamlit as st

st.set_page_config(page_title="오늘의 점심 메뉴 추천", page_icon="🎲")

st.title("🎲 오늘의 점심 메뉴 추천")
st.write("버튼을 누르면 랜덤으로 점심 메뉴를 골라 드려요!")

menus = ["짜장면", "마라탕", "제육볶음", "돈까스", "떡볶이", "햄버거", "초밥"]

with st.expander("메뉴 목록 보기"):
    st.write(", ".join(menus))

if st.button("🍽️ 메뉴 추천받기"):
    selected_menu = random.choice(menus)
    st.success(f"🎯 오늘의 추천 메뉴: **{selected_menu}**")
    st.balloons()
