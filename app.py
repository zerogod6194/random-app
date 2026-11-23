import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="열효율 정보 및 가이드",
    page_icon="⚡",
    layout="wide"
)

# 기기별 데이터 정의 (이미지 URL, 평균 기준 효율(%), 기본 소비전력(kW))
DEVICE_DATA = {
    "자동차": {
        "image": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 30.0,
        "power_kw": 50.0,
        "desc": "내연기관 및 하이브리드 차량 기준 평균 열효율: 약 25% ~ 38%"
    },
    "전자레인지": {
        "image": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 60.0,
        "power_kw": 1.0,
        "desc": "가정용 전자레인지 기준 평균 열효율: 약 55% ~ 65%"
    },
    "핸드폰": {
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 85.0,
        "power_kw": 0.02,
        "desc": "스마트폰 충전 및 구동 에너지 효율 기준: 약 80% ~ 90%"
    },
    "에어컨": {
        "image": "https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 75.0,
        "power_kw": 1.5,
        "desc": "인버터 냉방기 기준 환산 에너지 효율: 약 70% ~ 85%"
    }
}


# ---------------------------------------------------------
# 1. 열효율 계산 함수: calculate_energy(provide_e, useful_e)
# ---------------------------------------------------------
def calculate_energy(provide_e: float, useful_e: float):
    """공급받은 열(provide_e)과 유용하게 사용된 열(useful_e)로 열효율(effciency)과 등급을 계산합니다."""
    if provide_e <= 0:
        effciency = 0.0
    else:
        effciency = min((useful_e / provide_e) * 100.0, 100.0)

    effciency = round(effciency, 2)

    # 조건문을 이용한 에너지 효율등급(1~5등급) 산정
    if effciency >= 85.0:
        grade = 1
    elif effciency >= 70.0:
        grade = 2
    elif effciency >= 55.0:
        grade = 3
    elif effciency >= 40.0:
        grade = 4
    else:
        grade = 5

    return effciency, grade


def get_relative_efficiency(effciency: float, device_name: str) -> str:
    """동일 기기군
