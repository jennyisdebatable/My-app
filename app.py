import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 앱 설정 (여고 감성 파스텔 핑크)
st.set_page_config(page_title="우리 반 마음 온도", page_icon="🪴")
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { background-color: #ffb7c5; color: white; border-radius: 20px; border: none; font-weight: bold; }
    .stProgress > div > div > div > div { background-color: #ffb7c5; }
    .log-item { background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #ffeff3; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 연결 (OpenAI API Key)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 3. 데이터 저장소 초기화
if 'total_score' not in st.session_state:
    st.session_state.total_score = 50.0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 사이드바: 우리 반 상태 (온도별 멘트 로직 적용) ---
st.sidebar.title("🏫 우리 반 대시보드")

temp = st.session_state.total_score
st.sidebar.metric("마음 온도", f"{temp:.1f} °C")
st.sidebar.progress(min(max(temp/100, 0.0), 1.0))

# [중요] 온도에 따른 멘트 및 아이콘 변화
if temp >= 80:
    status_msg = "우리 반은 지금 훈훈한 바다! 🌊"
    fish_icon = "🐳"
elif temp >= 40:
    status_msg = "살기 적당한 미지근한 물이에요 ☀️"
    fish_icon = "🐠"
else:
    status_msg = "물이 차가워요.. 배려가 필요해! ❄️"
    fish_icon = "🐡"

st.sidebar.write(f"### {status_msg}")
st.sidebar.write("### 🫧 우리 반 어항")
fish_count = int(temp // 10)
st.sidebar.write(fish_icon * max(1, fish_count))

if temp >= 80:
    st.sidebar.success("축하해요! 고래가 나타났어요! 🎉")

# --- 메인 화면 ---
st.title("🪴 바른 마음 프로젝트")
st.write("오늘 우리 반을 위해 **실제로 실천한 배려**를 기록해 주세요.")

action = st.text_input("배려 행동 기록하기", placeholder="예: 친구에게 간식을 나눠줬다, 복도에서 조용히 걸었다")

if st.button("마음 온도 올리기 ✨"):
    if action:
        with st.spinner('AI 분석 중...'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "너는 학급 공동체 전문가야. 행동을 분석해 '공동체 기여도'를 -5에서 +5 사이 숫자로 결정해. 답변은 반드시 [점수: 숫자] 메시지 형식으로 해줘."},
                        {"role": "user", "content": f"행동: {action}"}
                    ]
                )
                result_text = response.choices[0].message.content
                
                # 점수 파싱 및 누적
                score_val = float(result_text.split('[점수:')[1].split(']')[0])
                st.session_state.total_score += score_val
                
                # 기록 추가 (시간 포함)
                curr_time = datetime.now().strftime("%H:%M")
                st.session_state.history.append({"time": curr_time, "action": action, "score": score_val})
                
                st.balloons()
                st.rerun() # 즉시 반영
                
            except Exception as e:
                st.error("오류가 발생했습니다. API 키나 결제 상태를 확인해 주세요.")
    else:
        st.warning("행동을 먼저 입력해 주세요!")

# --- 하단 기록 (발자취 누적) ---
st.write("---")
st.subheader("📜 우리 반 배려 발자취")

if not st.session_state.history:
    st.write("아직 기록이 없어요. 따뜻한 첫 배려를 기록해 볼까요?")
else:
    # 에러가 났던 하단부 문법 수정 완료
    for item in reversed(st.session_state.history):
        sign = "+" if item['score'] > 0 else ""
        st.markdown(f"""
        <div class="log-item">
            <b>[{item['time']}]</b> {item['action']} 
            <span style="color: #ff8fa3; font-weight: bold;">({sign}{item['score']}°C)</span>
        </div>
        """, unsafe_allow_html=True)
