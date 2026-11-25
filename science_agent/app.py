import os
import streamlit as st

from agents import Agent, Runner, SQLiteSession


# =========================================================
# 1. Page
# =========================================================

st.set_page_config(
    page_title="Technology Making Self Examination Helper",
    page_icon="🔬"
)
# 2. OpenAI API Key 설정 #
api_key = os.environ["OPENAI_ADMIN_KEY"]
# import Agent, Runner 했으므로 생략해도 됨

# =========================================================
# 2. Agent
# =========================================================

science_agent = Agent(
    name="Technology Making Self Examination Helper",

    instructions="""
    [ROLE]
    너는 중학교 기술 제작 실습 중 제작물의 오류를 자가 진단하도록 지원하는 도우미이다.

    [GOAL]
    학생이 오류가 난 공정 단계와 원인을 스스로 찾고, 교사 메뉴얼에 근거한 해결책을 직접 선택·수정하도록 도움

    [RULES]
    1. 먼저 오류 현상, 진행 중이던 공정 단계, 사용한 재료·장비를 확인한다. 정보가 부족하면 한 번에 하나씩 묻는다.
    2. 모든 피드백은 교사가 등록한 매뉴얼·유의사항에 근거하며, 근거가 된 항목을 함께 제시한다.
    3. 정답(원인이나 해결책)을 바로 알려주지 않는다. 학생이 스스로 답하도록 점검 질문을 먼저 던진다.
    4. 메뉴얼에 없는 내용을 임의로 추측하거나 외부 정보를 가져와 조언하지 않는다.
    5. 매뉴얼에서 근거를 찾지 못하면 추측하지 말고 "교사에게 확인이 필요하다"고 안내한다.
    6. 부상·장비 파손 등 안전과 관련된 오류는 진단을 멈추고 즉시 교사 호출을 안내한다.
    7. 학생의 수정안은 최대 3회까지 재평가하고, 이후에는 교사 검토로 넘긴다.


    [PROCESS]
    1. 상황 및 상태 확인 :  학생이 입력한 오류 현상, 현재 공정 단계, 사용 재료/장비 정보를 확인하고 부족한 점을 점검한다.  
    2. 자가 진단 질문 제시 : 교사 매뉴얼을 바탕으로 학생이 오류 원인을 스스로 되짚어볼 수 있는 단계별 점검 질문을 던진다.  
    3. 학생 답변 분석 : 학생이 제출한 원인 추정이나 수정안을 매뉴얼/유의사항 기준과 대조하여 분석한다.  
    4. 피드백 및 개선 방향 제안: 잘된 점과 수정이 필요한 부분을 매뉴얼 근거와 함께 안내하고 개선 방향을 안내한다.   
    5. 재평가 및 승인/이관: 학생의 수정안을 재평가(최대 3회)하며, 해결 시 완료하거나 필요 시 교사 검토(Handoff)로 넘긴다.  


    [OUTPUT]
    상황에 따라 다음을 제공한다.
    현재 상황 요약 및 분석: 학생이 입력한 공정 단계 및 오류 현상 정리  
    매뉴얼 기반 점검 포인트 (근거 포함): 피드백의 바탕이 된 교사 매뉴얼/유의사항 항목 명시
    개선 및 자가 진단 질문: 학생이 스스로 생각하게 만드는 1개의 점검 질문
    다음 행동 안내: 학생의 다음 입력 안내 또는 교사 검토(Handoff) 전환 안내
    """
)


# =========================================================
# 3. UI State
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# 4. Agent Session
# =========================================================

if "agent_session" not in st.session_state:

    st.session_state.agent_session = SQLiteSession(
        "student_session",
        "science_agent.db"
    )


# =========================================================
# 5. UI
# =========================================================

st.title("Technology Making Self Examination Helper")

st.caption(
    "학생이 스스로 기술 제작물을 "
    "자가 진단하도록 지원하는 AI Agent"
)


# =========================================================
# 6. Previous Messages
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# 7. User Input
# =========================================================

user_input = st.chat_input(
    "기술 제작물의 문제 현상을 입력하세요."
)


# =========================================================
# 8. Run Agent
# =========================================================

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    with st.chat_message("assistant"):

        with st.spinner("생각하고 있습니다..."):

            try:

                result = Runner.run_sync(
                    science_agent,
                    user_input,
                    session=st.session_state.agent_session
                )

                response = result.final_output

                st.markdown(response)

            except Exception as e:

                response = f"오류가 발생했습니다: {e}"

                st.error(response)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
