import streamlit as st
import pandas as pd
 
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")
 
# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
 
    for df in (seoul, yangpyeong):
        df["일시"] = pd.to_datetime(df["일시"])
        df.rename(columns={"기온(°C)": "기온"}, inplace=True)
 
    # 서울/양평 기온만 뽑아서 일시 기준으로 병합
    merged = pd.merge(
        seoul[["일시", "기온"]].rename(columns={"기온": "서울"}),
        yangpyeong[["일시", "기온"]].rename(columns={"기온": "양평"}),
        on="일시",
        how="inner",
    )
    merged["기온차"] = merged["서울"] - merged["양평"]
    merged["시간"] = merged["일시"].dt.hour
    merged["월"] = merged["일시"].dt.month
 
    return merged
 
 
try:
    data = load_data()
except FileNotFoundError as e:
    st.error(
        "CSV 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 "
        "이 앱과 같은 폴더에 있는지 확인해주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()
 
# -----------------------------
# 타이틀 & 설명
# -----------------------------
st.title("🌆 서울-양평 도시 열섬현상 분석")
st.write(
    "서울(도심)과 양평(비도심)의 2025년 시간별 기온 데이터를 비교하여 "
    "도시 열섬현상(Urban Heat Island)을 살펴봅니다."
)
 
# -----------------------------
# 요약 지표
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("연평균 서울 기온", f"{data['서울'].mean():.1f} °C")
col2.metric("연평균 양평 기온", f"{data['양평'].mean():.1f} °C")
col3.metric("연평균 기온차 (서울-양평)", f"{data['기온차'].mean():.2f} °C")
 
st.divider()
 
# -----------------------------
# ① 1년간 두 지역의 기온 변화 (선그래프)
# -----------------------------
st.subheader("① 1년간 두 지역의 기온 변화")
 
granularity = st.radio(
    "표시 단위 선택",
    ["시간별(원본)", "일별 평균", "월별 평균"],
    horizontal=True,
)
 
ts = data.set_index("일시")[["서울", "양평"]]
 
if granularity == "일별 평균":
    ts = ts.resample("D").mean()
elif granularity == "월별 평균":
    ts = ts.resample("MS").mean()
 
st.line_chart(ts)
 
st.divider()
 
# -----------------------------
# ② 시각(0~23시)별 평균 기온차 (막대그래프)
# -----------------------------
st.subheader("② 시각(0~23시)별 평균 기온차 (서울-양평)")
 
hourly_diff = data.groupby("시간")["기온차"].mean()
st.bar_chart(hourly_diff)
 
max_hour = hourly_diff.idxmax()
min_hour = hourly_diff.idxmin()
st.caption(
    f"기온차가 가장 큰 시각은 {max_hour}시 (+{hourly_diff[max_hour]:.2f}°C), "
    f"가장 작은(또는 음의) 시각은 {min_hour}시 ({hourly_diff[min_hour]:.2f}°C) 입니다."
)
 
st.divider()
 
# -----------------------------
# ③ 월(1~12월)별 평균 기온차 (막대그래프)
# -----------------------------
st.subheader("③ 월(1~12월)별 평균 기온차 (서울-양평)")
 
monthly_diff = data.groupby("월")["기온차"].mean()
st.bar_chart(monthly_diff)
 
max_month = monthly_diff.idxmax()
min_month = monthly_diff.idxmin()
st.caption(
    f"기온차가 가장 큰 달은 {max_month}월 (+{monthly_diff[max_month]:.2f}°C), "
    f"가장 작은 달은 {min_month}월 ({monthly_diff[min_month]:.2f}°C) 입니다."
)
 
st.divider()
st.caption("데이터 출처: 서울_기온.csv, 양평_기온.csv (2025년 시간별 기온 자료)")
