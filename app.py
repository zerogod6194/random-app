"""
[ 열효율 정보 및 가이드 ]
기기별 열효율 계산 · 에너지 효율등급 · 동종 기기 비교 · 전기세 통지표

실행:  streamlit run app.py
"""

import streamlit as st

# ─────────────────────────────────────────────────────────────
# 1. 기준 데이터 (예시 기준값 — 화면의 '기준값 설정'에서 바꿀 수 있음)
# ─────────────────────────────────────────────────────────────
DEVICES = {
    "자동차": {
        "icon": "🚗",
        "power_kw": 7.0,      # 전기차 완속 충전기 기준 소비전력(kW)
        "avg_eff": 80.0,      # 같은 종류 기기의 평균 효율(%) 가정값
        "desc": "전기차 완속 충전(7 kW) 기준",
    },
    "전자레인지": {
        "icon": "🍱",
        "power_kw": 1.0,
        "avg_eff": 60.0,
        "desc": "가정용 전자레인지(1 kW) 기준",
    },
    "핸드폰": {
        "icon": "📱",
        "power_kw": 0.015,
        "avg_eff": 85.0,
        "desc": "스마트폰 충전기(15 W) 기준",
    },
    "에어컨": {
        "icon": "❄️",
        "power_kw": 1.8,
        "avg_eff": 75.0,
        "desc": "가정용 벽걸이·스탠드 에어컨(1.8 kW) 기준",
    },
}

DEFAULT_RATE = 120.0   # 전기요금 단가(원/kWh) 가정값
COMPARE_MARGIN = 5.0   # 평균 대비 ±5%p 이내면 '중'


# ─────────────────────────────────────────────────────────────
# 2. 계산 함수
# ─────────────────────────────────────────────────────────────
def calculate_energy(provide_e: float, useful_e: float) -> float:
    """열효율 계산기: effciency(%) = 유용하게 사용된 열 / 공급받은 열 × 100"""
    if provide_e <= 0:
        raise ValueError("공급받은 열은 0보다 커야 합니다.")
    if useful_e < 0:
        raise ValueError("유용하게 사용된 열은 0 이상이어야 합니다.")
    if useful_e > provide_e:
        raise ValueError("유용하게 사용된 열은 공급받은 열보다 클 수 없습니다. (에너지 보존)")
    effciency = useful_e / provide_e * 100
    return effciency


def get_energy_grade(effciency: float) -> int:
    """조건문으로 열효율(%)을 에너지 효율등급(1~5등급)으로 변환"""
    if effciency >= 80:
        grade = 1
    elif effciency >= 60:
        grade = 2
    elif effciency >= 40:
        grade = 3
    elif effciency >= 20:
        grade = 4
    else:
        grade = 5
    return grade


def compare_with_average(effciency: float, average: float) -> str:
    """같은 종류 기기의 평균 효율과 비교해 상 / 중 / 하 판정"""
    if effciency >= average + COMPARE_MARGIN:
        return "상"
    elif effciency >= average - COMPARE_MARGIN:
        return "중"
    else:
        return "하"


def calculate_electric(provide_e: float, useful_e: float, time: float,
                       power_kw: float = 1.0, rate: float = DEFAULT_RATE) -> dict:
    """전기세 계산기: time(시간) 동안 사용했을 때의 전력량 · 전기세 · 버려진 열 요금

    전기세(원) = 소비전력(kW) × 사용시간(h) × 단가(원/kWh)
    버려진 열 요금(원) = 전기세 × (1 − effciency / 100)
    """
    effciency = calculate_energy(provide_e, useful_e)
    usage_kwh = power_kw * time
    cost = usage_kwh * rate
    wasted_cost = cost * (1 - effciency / 100)
    return {"usage_kwh": usage_kwh, "cost": cost, "wasted_cost": wasted_cost}


def build_bill_table(provide_e: float, useful_e: float, selected_hours: int,
                     power_kw: float, rate: float) -> list:
    """반복문(for)으로 1시간 · 선택 시간 · 24시간 전기세 통지표 생성"""
    periods = [
        ("1시간", 1),
        (f"선택 시간 ({selected_hours}시간)", selected_hours),
        ("24시간", 24),
    ]
    rows = []
    for label, time in periods:
        bill = calculate_electric(provide_e, useful_e, time, power_kw, rate)
        rows.append(
            {
                "사용 시간": label,
                "사용 전력량 (kWh)": f"{bill['usage_kwh']:,.3f}",
                "전기세 (원)": f"{bill['cost']:,.0f}",
                "버려진 열 요금 (원)": f"{bill['wasted_cost']:,.0f}",
            }
        )
    return rows


# ─────────────────────────────────────────────────────────────
# 3. 기기 이미지 (직접 그린 SVG)
# ─────────────────────────────────────────────────────────────
def device_svg(device: str) -> str:
    art = {
        "자동차": """
            <rect x="30" y="92" width="180" height="38" rx="14" fill="#2563eb"/>
            <path d="M62 92 L82 58 H150 L176 92 Z" fill="#3b82f6"/>
            <path d="M88 64 H116 V90 H74 Z" fill="#dbeafe"/>
            <path d="M122 64 H147 L166 90 H122 Z" fill="#dbeafe"/>
            <circle cx="76" cy="132" r="19" fill="#1e293b"/><circle cx="76" cy="132" r="8" fill="#cbd5e1"/>
            <circle cx="166" cy="132" r="19" fill="#1e293b"/><circle cx="166" cy="132" r="8" fill="#cbd5e1"/>
            <rect x="198" y="100" width="12" height="8" rx="3" fill="#fde047"/>
            <rect x="30" y="100" width="8" height="8" rx="3" fill="#f87171"/>
        """,
        "전자레인지": """
            <rect x="28" y="42" width="184" height="104" rx="12" fill="#475569"/>
            <rect x="42" y="56" width="112" height="76" rx="8" fill="#0f172a"/>
            <rect x="50" y="64" width="96" height="60" rx="5" fill="#fbbf24" opacity="0.85"/>
            <ellipse cx="98" cy="112" rx="30" ry="5" fill="#fef3c7"/>
            <path d="M84 100 q4 -8 0 -16 M98 100 q4 -8 0 -16 M112 100 q4 -8 0 -16"
                  stroke="#fff7ed" stroke-width="3" fill="none" stroke-linecap="round"/>
            <rect x="166" y="58" width="34" height="16" rx="4" fill="#22d3ee"/>
            <circle cx="183" cy="96" r="11" fill="#cbd5e1"/>
            <rect x="170" y="118" width="26" height="9" rx="4" fill="#94a3b8"/>
            <rect x="44" y="146" width="18" height="7" rx="2" fill="#334155"/>
            <rect x="178" y="146" width="18" height="7" rx="2" fill="#334155"/>
        """,
        "핸드폰": """
            <rect x="80" y="14" width="80" height="152" rx="16" fill="#1e293b"/>
            <rect x="87" y="24" width="66" height="132" rx="9" fill="#60a5fa"/>
            <rect x="108" y="18" width="24" height="5" rx="2.5" fill="#0f172a"/>
            <rect x="96" y="40" width="20" height="20" rx="5" fill="#fde047"/>
            <rect x="124" y="40" width="20" height="20" rx="5" fill="#34d399"/>
            <rect x="96" y="68" width="20" height="20" rx="5" fill="#f472b6"/>
            <rect x="124" y="68" width="20" height="20" rx="5" fill="#f8fafc"/>
            <rect x="98" y="120" width="44" height="18" rx="4" fill="#0f172a" opacity="0.35"/>
            <rect x="101" y="123" width="28" height="12" rx="2" fill="#4ade80"/>
            <rect x="106" y="148" width="28" height="4" rx="2" fill="#f8fafc"/>
        """,
        "에어컨": """
            <rect x="26" y="34" width="188" height="62" rx="14" fill="#f8fafc" stroke="#cbd5e1" stroke-width="3"/>
            <rect x="40" y="76" width="160" height="9" rx="4" fill="#94a3b8"/>
            <rect x="40" y="46" width="110" height="5" rx="2.5" fill="#e2e8f0"/>
            <rect x="40" y="57" width="110" height="5" rx="2.5" fill="#e2e8f0"/>
            <circle cx="188" cy="54" r="5" fill="#22c55e"/>
            <path d="M66 108 q-10 14 0 28 q10 14 0 26" stroke="#38bdf8" stroke-width="5" fill="none" stroke-linecap="round"/>
            <path d="M120 108 q-10 14 0 28 q10 14 0 26" stroke="#38bdf8" stroke-width="5" fill="none" stroke-linecap="round"/>
            <path d="M174 108 q-10 14 0 28 q10 14 0 26" stroke="#38bdf8" stroke-width="5" fill="none" stroke-linecap="round"/>
        """,
    }
    return (
        '<svg viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;max-width:340px;height:auto;">' + art[device] + "</svg>"
    )


# ─────────────────────────────────────────────────────────────
# 4. 화면 구성
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="열효율 정보 및 가이드", page_icon="🔥", layout="wide")

st.markdown(
    """
    <style>
      .main-title {text-align:center; font-size:2.4rem; font-weight:800; margin:0 0 .2rem 0;}
      .sub-title  {text-align:center; opacity:.7; margin-bottom:1.6rem;}
      .card {border:1px solid rgba(128,128,128,.25); border-radius:16px; padding:1.2rem 1.4rem;
             background:rgba(128,128,128,.06);}
      .device-card {text-align:center;}
      .device-name {font-size:1.4rem; font-weight:700; margin-top:.4rem;}
      .result-line {font-size:1.15rem; margin:.55rem 0;}
      .result-line b {font-size:1.35rem; color:#ef4444;}
      .step {font-weight:700; font-size:1.05rem; margin:.9rem 0 .3rem 0;}
    </style>
    <div class="main-title">[ 열효율 정보 및 가이드 ]</div>
    <div class="sub-title">열효율 계산 · 에너지 효율등급 · 동종 기기 비교 · 전기세 통지표</div>
    """,
    unsafe_allow_html=True,
)

if "device" not in st.session_state:
    st.session_state.device = "자동차"
if "result" not in st.session_state:
    st.session_state.result = None

left, right = st.columns([3, 2], gap="large")

# ── 왼쪽: 입력 영역 ───────────────────────────────────────────
with left:
    st.markdown('<div class="step">① 기기 선택</div>', unsafe_allow_html=True)
    button_cols = st.columns(len(DEVICES))
    for col, name in zip(button_cols, DEVICES):
        selected = st.session_state.device == name
        if col.button(
            f"{DEVICES[name]['icon']} {name}",
            key=f"btn_{name}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.device = name
            st.session_state.result = None
            st.rerun()

    device = st.session_state.device
    info = DEVICES[device]

    st.markdown('<div class="step">② 열에너지 입력</div>', unsafe_allow_html=True)
    in1, in2 = st.columns(2)
    provide_e = in1.number_input("공급받은 열 E (J)", min_value=0.0, value=1000.0, step=10.0)
    useful_e = in2.number_input("유용하게 사용된 열 E (J)", min_value=0.0, value=600.0, step=10.0)

    st.markdown('<div class="step">③ 사용 시간</div>', unsafe_allow_html=True)
    hours = st.slider("몇 시간 사용하나요?", min_value=1, max_value=24, value=3, format="%d시간")

    with st.expander("⚙️ 기준값 설정 (소비전력 · 전기요금 단가 · 평균 효율)"):
        s1, s2, s3 = st.columns(3)
        power_kw = s1.number_input(
            "소비전력 (kW)", min_value=0.001, value=float(info["power_kw"]),
            step=0.1, format="%.3f", key=f"power_{device}",
        )
        rate = s2.number_input(
            "전기요금 단가 (원/kWh)", min_value=1.0, value=DEFAULT_RATE, step=10.0,
        )
        avg_eff = s3.number_input(
            f"{device} 평균 효율 (%)", min_value=1.0, max_value=100.0,
            value=float(info["avg_eff"]), step=1.0, key=f"avg_{device}",
        )
        st.caption(
            "기본값은 계산을 위한 예시 가정값입니다. "
            "실제 기기의 소비전력과 한국전력 요금표에 맞게 고쳐 쓰세요."
        )

    apply_clicked = st.button("✅ 적용", type="primary", use_container_width=True)

# ── 오른쪽: 선택한 기기 이미지 ────────────────────────────────
with right:
    st.markdown(
        f"""
        <div class="card device-card">
          {device_svg(device)}
          <div class="device-name">{info['icon']} {device}</div>
          <div style="opacity:.7">{info['desc']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── 적용 버튼 처리 ────────────────────────────────────────────
if apply_clicked:
    try:
        effciency = calculate_energy(provide_e, useful_e)
    except ValueError as error:
        st.session_state.result = None
        st.error(f"⚠️ {error}")
    else:
        st.session_state.result = {
            "device": device,
            "effciency": effciency,
            "grade": get_energy_grade(effciency),
            "level": compare_with_average(effciency, avg_eff),
            "avg_eff": avg_eff,
            "hours": hours,
            "power_kw": power_kw,
            "rate": rate,
            "bill": build_bill_table(provide_e, useful_e, hours, power_kw, rate),
        }

# ── 결과 출력 화면 ────────────────────────────────────────────
result = st.session_state.result
st.divider()

if result is None:
    st.info("값을 입력하고 **적용** 버튼을 누르면 아래에 결과가 표시됩니다.")
else:
    st.subheader("[ 결과 출력 화면 ]")
    res_left, res_right = st.columns([3, 2], gap="large")

    with res_left:
        st.markdown(
            f"""
            <div class="card">
              <div class="result-line">열효율은 <b>{result['effciency']:.1f}</b>퍼센트 입니다</div>
              <div class="result-line">에너지 효율등급은 <b>{result['grade']}</b> 등급입니다</div>
              <div class="result-line">타 같은 기기와 비교할 시, 에너지 효율성은 <b>[ {result['level']} ]</b> 입니다</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(result["effciency"] / 100, 1.0))
        m1, m2, m3 = st.columns(3)
        m1.metric("열효율", f"{result['effciency']:.1f} %")
        m2.metric("효율등급", f"{result['grade']} 등급")
        m3.metric(
            f"{result['device']} 평균 대비",
            result["level"],
            delta=f"{result['effciency'] - result['avg_eff']:+.1f} %p",
        )
        with st.expander("📘 계산 방법 보기"):
            st.markdown(
                """
                - **열효율(%)** = 유용하게 사용된 열 ÷ 공급받은 열 × 100
                - **효율등급** : 80% 이상 1등급 · 60% 이상 2등급 · 40% 이상 3등급 · 20% 이상 4등급 · 그 미만 5등급
                - **상 / 중 / 하** : 같은 종류 기기의 평균 효율보다 5%p 이상 높으면 상, ±5%p 이내면 중, 그보다 낮으면 하
                - **전기세(원)** = 소비전력(kW) × 사용 시간(h) × 단가(원/kWh)
                - **버려진 열 요금** = 전기세 × (1 − 열효율)
                """
            )

    with res_right:
        st.markdown(f"#### 🧾 전기세 통지표 — {result['device']}")
        st.table(result["bill"])
        st.caption(
            f"소비전력 {result['power_kw']:g} kW · 단가 {result['rate']:,.0f}원/kWh 기준 "
            "(기본요금·세금·누진제 제외)"
        )
