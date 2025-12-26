import streamlit as st
from openai import OpenAI
import random

# 1. 앱 설정 및 스타일 (여고 감성 핑크/파스텔 톤)
st.set_page_config(page_title="바른 마음 프로젝트", page_icon="🪴")
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { background-color: #ffb7c5; color: white; border-radius: 20px; border: none; }
    .stProgress > div > div > div > div { background-color: #ffb7c5; }
    </style>
    """, unsafe_allow_name_checked=True)

# 2. AI 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 3. 데이터 보존 (앱이 켜져있는 동안 점수 유지)
if 'total_score' not in st.session_state:
    st.session_state.total_score = 50  # 시작 온도: 50도
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 사이드바: 우리 반 상태 ---
st.sidebar.title("🏫 우리 반 마음 대시보드")
st.sidebar.write("### 현재 마음 온도")

# 온도에 따른 귀여운 이모지 변화
temp = st.session_state.total_score
if temp >= 80: status_msg, fish_icon = "우리 반은 지금 훈훈한 바다! 🌊", "🐳"
elif temp >= 40: status_msg, fish_icon = "살기 적당한 미지근한 물이에요 ☀️", "🐠"
else: status_msg, fish_icon = "물이 차가워요.. 배려가 필요해요! ❄️", "🐡"

st.sidebar.metric("마음 온도", f"{temp:.1f} °C")
st.sidebar.progress(min(max(temp/100, 0.0), 1.0))
st.sidebar.write(status_msg)

# 어항 시각화 (물고기 숫자로 표현)
fish_count = int(temp // 10)
st.sidebar.write("### 🫧 우리 반 어항")
st.sidebar.write(fish_icon * fish_count)

# --- 메인 화면 ---
st.title("🪴 바른 마음 프로젝트")
st.write("오늘 친구나 공동체를 위해 **실제로 한 행동**을 적어주세요!")

action = st.text_input("어떤 배려를 실천했나요?", placeholder="예: 급식실에서 뒷사람 위해 의자 넣어주기, 교실 불 끄기 등")

if st.button("배려 기록하기 ✨"):
    if action:
        with st.spinner('AI가 배려 점수를 계산 중...'):
            try:
                # AI에게 벤담의 7척도 기반 점수 산출 요청
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "너는 학급 공동체 전문가야. 사용자가 실천한 행동을 벤담의 7척도로 분석해. '공동체 기여도'를 -5에서 +5 사이의 숫자로 딱 하나 정하고, 그 이유를 다정하게 한 문장으로 말해줘. 형식은 [점수: 숫자] 메시지 로 해줘."},
                        {"role": "user", "content": f"행동: {action}"}
                    ]
                )
                result_text = response.choices[0].message.content
                
                # 점수 추출 및 업데이트
                score_val = float(result_text.split('[점수:')[1].split(']')[0])
                st.session_state.total_score += score_val
                st.session_state.history.append(f"{action} ({'+' if score_val>0 else ''}{score_val})")
                
                # 결과 표시
                st.balloons()
                st.success(f"**기록 완료!** {result_text.split(']')[1]}")
                st.write(f" 우리 반 마음 온도가 **{score_val}도** 변했습니다!")
                
            except Exception as e:
                st.error("앗, 에러가 발생했어요! 다시 시도해봐요.")
    else:
        st.warning("행동을 먼저 입력해 주세요!")

# --- 하단 기록 ---
with st.expander("📜 오늘 우리 반의 발자취"):
    for item in reversed(st.session_state.history):
        st.write(f"- {item}")
