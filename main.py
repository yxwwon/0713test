import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 데이터 비교")
st.markdown("### 도시 열섬현상(Urban Heat Island) 분석 웹앱")
st.write("본 웹앱은 서울(대도시)과 양평(교외 지역)의 2025년 시간별 기온 데이터를 비교하여 도시 열섬현상을 시각화합니다.")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    try:
        # 1, 3. 데이터 읽기 (같은 폴더 내 CSV 파일, encoding='cp949' 반영)
        seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
        
        # 2. 일시 컬럼을 datetime 형식으로 변환
        seoul_df['일시'] = pd.to_datetime(seoul_df['일시'])
        yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'])
        
        # 시간별 데이터에서 월, 시 정보 추출
        seoul_df['월'] = seoul_df['일시'].dt.month
        seoul_df['시'] = seoul_df['일시'].dt.hour
        
        yangpyeong_df['월'] = yangpyeong_df['일시'].dt.month
        yangpyeong_df['시'] = yangpyeong_df['일시'].dt.hour
        
        return seoul_df, yangpyeong_df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다. 파일명과 인코딩을 확인해주세요.\n오류 내용: {e}")
        return None, None

seoul, yangpyeong = load_data()

if seoul is not None and yangpyeong is not None:
    # '일시'를 기준으로 두 지역 데이터 병합 (시간 매칭)
    merged = pd.merge(
        seoul[['일시', '월', '시', '기온(°C)']], 
        yangpyeong[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    # 서울과 양평의 기온 차이 계산
    merged['기온차(서울-양평)'] = merged['기온(°C)_서울'] - merged['기온(°C)_양평']

    # 사이드바 요약 통계 정보 표시
    st.sidebar.header("📊 2025년 전체 요약")
    st.sidebar.metric("서울 평균 기온", f"{merged['기온(°C)_서울'].mean():.2f} °C")
    st.sidebar.metric("양평 평균 기온", f"{merged['기온(°C)_양평'].mean():.2f} °C")
    st.sidebar.metric("평균 기온차 (서울-양평)", f"{merged['기온차(서울-양평)'].mean():.2f} °C")

    # ① 1년간 두 지역의 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역의 기온 변화")
    st.write("2025년 전체 기간 동안의 서울과 양평의 기온 변화 추이입니다.")
    
    line_data = merged.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
    line_data.columns = ['서울 기온', '양평 기온']
    st.line_chart(line_data)  # 내장 대화형 선그래프

    # 가독성을 위해 하단 그래프는 2열 레이아웃으로 배치
    col1, col2 = st.columns(2)

    with col1:
        # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        st.write("하루 중 시간대별 평균 기온차입니다. (주로 밤과 새벽에 도시 열섬현상이 뚜렷하게 나타납니다.)")
        
        hour_diff = merged.groupby('시')['기온차(서울-양평)'].mean().reset_index()
        hour_diff = hour_diff.set_index('시')
        hour_diff.columns = ['평균 기온차 (°C)']
        st.bar_chart(hour_diff)  # 내장 대화형 막대그래프

    with col2:
        # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        st.write("계절 및 월별 도시 열섬현상의 강도 변화를 보여줍니다.")
        
        month_diff = merged.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        month_diff = month_diff.set_index('월')
        month_diff.columns = ['평균 기온차 (°C)']
        st.bar_chart(month_diff)  # 내장 대화형 막대그래프

    # 원본 데이터 확인 체크박스
    st.markdown("---")
    if st.checkbox("🔍 전처리 및 병합된 원본 데이터 확인하기"):
        st.dataframe(merged)
else:
    st.warning("웹앱을 실행하기 전에 같은 폴더 내에 '서울_기온.csv'와 '양평_기온.csv' 파일이 있는지 확인해주세요.")
