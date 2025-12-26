import streamlit as st
from openai import OpenAI

# 1. AI 연결 (Streamlit 비밀 설정을 통해 키를 가져옴)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🌱 바른 마음 프로젝트 : 우리 반 윤리 대시보드")
st.write("당신의 행동이 공동체에 미칠 영향을 AI(벤담의 7척도)가 분석합니다.")

# 2. 사용자 입력
action = st.text_input("무엇을 하려고 하나요?", placeholder="예: 빈 교실 불 끄기")

if st.button("바른 마음 분석하기"):
    if action:
        # ChatGPT에게 분석 요청
        with st.spinner('AI 벤담이 분석 중...'):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "너는 벤담의 7척도 전문가야. 행동을 분석해서 각 항목 점수(1-10)와 최종 권고안을 한글로 알려줘."},
                    {"role": "user", "content": f"'{action}'을 분석해줘."}
                ]
            )
            result = response.choices[0].message.content
            st.info(result)
            st.success("분석 완료! 이 결과는 데이터에 반영됩니다.")
    else:
        st.warning("행동을 입력해주세요!")
