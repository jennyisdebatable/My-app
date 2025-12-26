import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 앱 설정 (여고 감성 핑크 파스텔)
st.set_page_config(page_title="우리 반 마음 온도", page_icon="🪴")
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { background-color: #ffb7c5; color: white; border-radius: 20px; border: none; font-weight: bold; }
    .stProgress > div > div > div > div { background-color: #ffb7c5; }
    .log-item { background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #ffeff3; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 3. 데이터 저장소 초기화
if 'total_score' not in st.session_state:
    st.session_state.total_score = 50.0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 사이드바: 우리 반 상태 ---
st.sidebar.title("🏫 우리 반 어항")

temp = st.session_state.total_score
st.sidebar.metric("마음 온도", f"{temp:.1f} °C")
st.sidebar.progress(min(max(temp/100, 0.0), 1.0))

# 어항 시각화
fish_count = int(temp // 10)
fish_icon = "🐠" if temp < 80 else "🐳"
st.sidebar.write("### 🫧 우리 반 어항")
st.sidebar.write(fish_icon * max(1, fish_count))

if temp >= 80:
    st.sidebar.success("축하해요! 고래가 나타났어요! 🎉")

# --- 메인 화면 ---
st.title("🪴 우리반 배려 프로젝트")
st.write("오늘 우리 반을 위해 **실제로 실천한 배려**를 기록해 주세요.")

action = st.text_input("배려 행동 기록하기", placeholder="예: 친구에게 모르는 문제 알려주기, 복도에서 조용히 걷기")

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
                
                # 기록 추가
                curr_time = datetime.now().strftime("%H:%M")
                st.session_state.history.append({"time": curr_time, "action": action, "score": score_val})
                
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error("오류가 발생했습니다. 다시 시도해 주세요.")
    else:
        st.warning("행동을 먼저 입력해 주세요!")

# --- 하단 기록 (발자취 누적) ---
st.write("---")
st.subheader("📜 우리 반 배려 발자취")

if not st.session_state.history:
    st.write("아직 기록이 없어요. 따뜻한 첫 배려를 기록해 볼까요?")
else:
    # 역순 출력 루프 (여기가 에러가 났던 부분입니다!)
    for item in reversed(st.session_state.history):
        sign = "+" if item['score'] > 0 else ""
        st.markdown(f"""
        <div class="log-item">
            <b>[{item['time']}]</b> {item['action']} 
            <span style="color: #ff8fa3; font-weight: bold;">({sign}{item['score']}°C)</span>
        </div>
        """, unsafe_allow_html=True)
