import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (데이터 시각화 시 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows용 (Mac은 'AppleGothic' 사용)
plt.rcParams['axes.unicode_minus'] = False

# 페이지 제목 설정
st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")
st.title("🏙️ 서울 vs 🌲 양평 기온 데이터 비교")
st.markdown("### 서울(대도시)과 양평(교외)의 기온 차이를 통해 도시 열섬현상을 살펴봅니다.")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 파일 읽기 (cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    
    # 분석에 필요한 월(Month), 시각(Hour) 파생변수 생성
    seoul['월'] = seoul['일시'].dt.month
    seoul['시각'] = seoul['일시'].dt.hour
    yangpyeong['월'] = yangpyeong['일시'].dt.month
    yangpyeong['시각'] = yangpyeong['일시'].dt.hour
    
    return seoul, yangpyeong

try:
    seoul_df, yp_df = load_data()
    
    # 두 데이터의 기온을 '일시' 기준으로 결합 (동일 시간대 비교용)
    merged_df = pd.merge(
        seoul_df[['일시', '월', '시각', '기온(°C)']], 
        yp_df[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    # 기온 차이 계산 (서울 - 양평)
    merged_df['기온차(서울-양평)'] = merged_df['기온(°C)_서울'] - merged_df['기온(°C)_양평']

    # --- ① 1년간 두 지역의 기온 변화 (선그래프) ---
    st.subheader("① 1년간 두 지역의 기온 변화")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(merged_df['일시'], merged_df['기온(°C)_서울'], label='서울', color='coral', alpha=0.7)
    ax1.plot(merged_df['일시'], merged_df['기온(°C)_양평'], label='양평', color='teal', alpha=0.7)
    ax1.set_ylabel("기온 (°C)")
    ax1.set_xlabel("날짜")
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig1)

    # 레이아웃을 위해 좌우 2분할 컬럼 생성
    col1, col2 = st.columns(2)

    # --- ② 시각별 평균 기온차 (막대그래프) ---
    with col1:
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        hour_diff = merged_df.groupby('시각')['기온차(서울-양평)'].mean()
        
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        hour_diff.plot(kind='bar', ax=ax2, color='orangered', alpha=0.8)
        ax2.set_xlabel("시각 (0~23시)")
        ax2.set_ylabel("평균 기온차 (°C)")
        ax2.axhline(0, color='black', linewidth=0.8, linestyle='-')
        ax2.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig2)
        st.caption("💡 주로 야간과 새벽 시간에 서울의 기온이 양평보다 확연히 높은 열섬현상이 관측됩니다.")

    # --- ③ 월별 평균 기온차 (막대그래프) ---
    with col2:
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        month_diff = merged_df.groupby('월')['기온차(서울-양평)'].mean()
        
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        month_diff.plot(kind='bar', ax=ax3, color='crimson', alpha=0.8)
        ax3.set_xlabel("월 (1~12월)")
        ax3.set_ylabel("평균 기온차 (°C)")
        ax3.axhline(0, color='black', linewidth=0.8, linestyle='-')
        ax3.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig3)
        st.caption("💡 대도시의 인공열 및 콘크리트 축열 영향으로 사계절 내내 서울이 더 따뜻하게 나타납니다.")

except FileNotFoundError as e:
    st.error("⚠️ 데이터를 찾을 수 없습니다. 같은 폴더에 '서울_기온.csv'와 '양평_기온.csv' 파일이 있는지 확인해주세요.")
