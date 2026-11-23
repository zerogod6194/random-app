import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="열효율 정보 및 가이드",
    page_icon="⚡",
    layout="wide"
)

# 기기별 데이터 정의 (이미지 URL, 평균 기준 효율(%), 평균 소비전력(kW))
# 외부 이미지 링크가 깨질 경우를 대비해 안정적인 Unsplash 고화질 이미지 및 아이콘 활용
DEVICE_DATA = {
    "자동차": {
        "image": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 30.0,      # 내연기관 평균 열효율 기준 (%)
        "power_kw": 50.0,     # 주행 평균 환산 출력 (kW)
        "desc": "내연기관 및 하이브리드 차량 기준 평균 열효율: 약 25% ~ 38%"
    },
    "전자레인지": {
        "image": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 60.0,      # 마이크로파 가열 평균 효율 (%)
        "power_kw": 1.0,      # 1000W
        "desc": "가정용 전자레인지 기준 평균 열효율: 약 55% ~ 65%"
    },
    "핸드폰": {
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 85.0,      # 배터리 충전 및 회로 전력 효율 (%)
        "power_kw": 0.02,     # 20W 고속충전 기준
        "desc": "스마트폰 충전 및 구동 에너지 효율 기준: 약 80% ~ 90%"
    },
    "에어컨": {
        "image": "https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?auto=format&fit=crop&w=600&q=80",
        "avg_eff": 75.0,      # 인버터 히트펌프 환산 효율 (%)
        "power_kw": 1.5,      # 1500W
        "desc": "인버터 냉방기 기준 환산 에너지 효율: 약 70% ~ 85%"
    }
}

# ---------------------------------------------------------
# 1. 파이썬 함수 구문: 열효율 및 등급 계산 함수 (조건문 활용)
# ---------------------------------------------------------
def calculate_thermal_efficiency(supplied_e: float, useful_e: float, device_name: str):
    """공급받은 열E와 유용하게 사용된 열E를 바탕으로 열효율, 에너지 효율등급, 상대적 효율성을 계산합니다."""
    if supplied_e <= 0:
        return 0.0, 5, "하"

    # 열효율(%) = (유용하게 사용된 열 / 공급받은 열) * 100
    efficiency = (useful_e / supplied_e) * 100
    efficiency = min(efficiency, 100.0)  # 물리적 한계 100% 상한 보정

    # 조건문을 이용한 에너지 효율등급(1~5등급) 산정
    if efficiency >= 85.0:
        grade = 1
    elif efficiency >= 70.0:
        grade = 2
    elif efficiency >= 55.0:
        grade = 3
    elif efficiency >= 40.0:
        grade = 4
    else:
        grade = 5

    # 타 같은 기기(평균 효율)와 비교한 상대적 효율성 [상, 중, 하] 판별
    avg_eff = DEVICE_DATA[device_name]["avg_eff"]
    if efficiency >= avg_eff + 5.0:
        relative_perf = "상"
    elif efficiency >= avg_eff - 5.0:
        relative_perf = "중"
    else:
        relative_perf = "하"

    return round(efficiency, 2), grade, relative_perf


# ---------------------------------------------------------
# 2. 파이썬 함수 구문: 전기세 계산 및 통지표 생성 함수 (for 반복문 활용)
# ---------------------------------------------------------
def generate_electricity_bill(device_name: str, selected_hours: int, efficiency: float):
    """선택한 시간, 1시간, 24시간 사용량에 따른 전기세 통지표 데이터를 for문으로 생성합니다."""
    base_power_kw = DEVICE_DATA[device_name]["power_kw"]
    
    # 효율이 낮을수록 동일한 작업을 위해 더 많은 전력을 소모한다고 가정한 보정 계수
    eff_factor = (DEVICE_DATA[device_name]["avg_eff"] / efficiency) if efficiency > 0 else 1.5
    actual_power_kw = base_power_kw * eff_factor

    # 한국전력 주택용 저압 평균 단가 근사치 적용 (kWh당 약 150원 기준 + 기본료/부가세 반영 계수)
    unit_price_krw = 155.0

    # 반복문(for)으로 비교할 시간 목록 정의
    time_cases = [
        ("1시간 사용", 1),
        (f"선택한 시간 ({selected_hours}시간)", selected_hours),
        ("24시간 (1일 연속)", 24)
    ]

    bill_records = []
    for label, hours in time_cases:
        consumed_kwh = actual_power_kw * hours
        estimated_cost = int(round(consumed_kwh * unit_price_krw))
        
        bill_records.append({
            "구분": label,
            "사용 시간": f"{hours} 시간",
            "예상 전력량 (kWh)": f"{consumed_kwh:.2f} kWh",
            "예상 전기요금 (원)": f"{estimated_cost:,} 원"
        })

    return pd.DataFrame(bill_records)


# ---------------------------------------------------------
# UI 구성 영역
# ---------------------------------------------------------

# 세션 상태 초기화 (기본 선택 기기: 자동차)
if "selected_device" not in st.session_state:
    st.session_state.selected_device = "자동차"

# 최상단 제목
st.title("⚡ [ 열효율 정보 및 가이드 ]")
st.markdown("기기의 열에너지 효율을 계산하고 동일 기기군 대비 효율 등급 및 예상 전기요금을 분석합니다.")
st.divider()

# 상단 영역: 왼쪽(기기 버튼 선택 및 에너지 입력) / 오른쪽(선택된 기기 이미지 출력)
col_left, col_right = st.columns([1.3, 1], gap="large")

with col_left:
    st.subheader("1. 분석할 기기 선택")
    
    # 4가지 기기 버튼 형식 배치
    btn_cols = st.columns(4)
    devices = ["자동차", "전자레인지", "핸드폰", "에어컨"]
    
    for idx, device in enumerate(devices):
        # 현재 선택된 버튼은 primary 스타일로 강조
        btn_type = "primary" if st.session_state.selected_device == device else "secondary"
        if btn_cols[idx].button(device, use_container_width=True, type=btn_type):
            st.session_state.selected_device = device
            st.rerun()

    st.info(f"📌 **{st.session_state.selected_device}** 선택됨 — {DEVICE_DATA[st.session_state.selected_device]['desc']}")

    st.subheader("2. 열에너지(E) 및 사용 시간 입력")
    input_col1, input_col2 = st.columns(2)
    
    with input_col1:
        supplied_energy = st.number_input(
            "공급받은 열 E (kJ 또는 J)",
            min_value=1.0,
            max_value=1000000.0,
            value=1000.0,
            step=50.0,
            help="기기에 투입된 총 열에너지를 입력하세요."
        )
    
    with input_col2:
        useful_energy = st.number_input(
            "유용하게 사용된 열 E (kJ 또는 J)",
            min_value=0.0,
            max_value=1000000.0,
            value=650.0,
            step=50.0,
            help="실제 목적에 맞게 변환되어 사용된 에너지를 입력하세요."
        )

    usage_hours = st.slider(
        "사용 시간 설정 (시간)",
        min_value=1,
        max_value=24,
        value=5,
        step=1
    )

    # 적용 버튼
    apply_btn = st.button("✅ 적용하기", type="primary", use_container_width=True)

with col_right:
    current_device = st.session_state.selected_device
    st.subheader(f"선택된 기기: {current_device}")
    st.image(
        DEVICE_DATA[current_device]["image"],
        caption=f"[{current_device}] 표준 작동 모델",
        use_container_width=True
    )

st.divider()

# ---------------------------------------------------------
# 결과 출력 화면 (적용 버튼을 눌렀을 때 실행)
# ---------------------------------------------------------
if apply_btn:
    if useful_energy > supplied_energy:
        st.error("⚠️ 오류: 유용하게 사용된 열 E는 공급받은 열 E보다 클 수 없습니다. (열역학 제1법칙 위배)")
    else:
        eff_percent, eff_grade, rel_status = calculate_thermal_efficiency(
            supplied_energy, useful_energy, st.session_state.selected_device
        )
        bill_df = generate_electricity_bill(
            st.session_state.selected_device, usage_hours, eff_percent
        )

        # 하단 좌측: 요구사항 텍스트 출력 / 하단 우측: 전기세 통지표 표 출력
        res_left, res_right = st.columns([1, 1.2], gap="large")

        with res_left:
            st.subheader("[결과 출력 화면]")
            
            # 지정된 문구 포맷 정확히 반영
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 24px; border-radius: 12px; border-left: 6px solid #ff4b4b; color: #111111;">
                <p style="font-size: 19px; margin-bottom: 12px;">
                    열효율은 <b>{eff_percent}%</b> 입니다
                </p>
                <p style="font-size: 19px; margin-bottom: 12px;">
                    에너지 효율등급은 <b>{eff_grade} 등급</b>입니다
                </p>
                <p style="font-size: 19px; margin-bottom: 0;">
                    타 같은 기기와 비교할 시, 에너지 효율성은 <b>[ {rel_status} ]</b> 입니다
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 추가 시각적 지표 (Metric)
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("계산된 열효율", f"{eff_percent}%")
            m_col2.metric("효율 등급", f"{eff_grade}등급")
            m_col3.metric("동종 기기 대비", rel_status)

        with res_right:
            st.subheader("🧾 전기세 통지표 (사용 시간별 비교)")
            st.caption(f"※ {st.session_state.selected_device} 기준 평균 소비전력 및 계산된 열효율({eff_percent}%)이 반영된 예상 요금입니다.")
            
            # 표 형태로 출력
            st.dataframe(
                bill_df,
                use_container_width=True,
                hide_index=True
            )
