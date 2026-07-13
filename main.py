import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")

st.title("🌆 서울과 양평의 도시 열섬현상 분석")
st.write("2025년 시간별 기온 데이터를 이용하여 서울과 양평의 기온을 비교합니다.")

# 현재 폴더 확인(디버깅용)
st.write("현재 폴더:", os.getcwd())
st.write("현재 파일:", os.listdir("."))

# -------------------------
# 데이터 불러오기
# -------------------------
try:
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
except UnicodeDecodeError:
    # 혹시 GitHub에서 UTF-8로 저장된 경우 대비
    seoul = pd.read_csv("서울_기온.csv", encoding="utf-8")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="utf-8")
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()

# -------------------------
# 날짜 형식 변환
# -------------------------
seoul["일시"] = pd.to_datetime(seoul["일시"])
yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

# 필요한 열만 선택
seoul = seoul[["일시", "기온(°C)"]]
yangpyeong = yangpyeong[["일시", "기온(°C)"]]

# 열 이름 변경
seoul.rename(columns={"기온(°C)": "서울"}, inplace=True)
yangpyeong.rename(columns={"기온(°C)": "양평"}, inplace=True)

# -------------------------
# 데이터 병합
# -------------------------
df = pd.merge(seoul, yangpyeong, on="일시")

# 기온차 계산
df["기온차"] = df["서울"] - df["양평"]

# 시간, 월 정보 추가
df["시간"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

# -------------------------
# ① 1년간 기온 변화
# -------------------------
st.header("① 1년간 서울과 양평의 기온 변화")
st.line_chart(df.set_index("일시")[["서울", "양평"]])

# -------------------------
# ② 시간별 평균 기온차
# -------------------------
st.header("② 시각(0~23시)별 평균 기온차 (서울-양평)")
hour_diff = df.groupby("시간")["기온차"].mean()
st.bar_chart(hour_diff)

# -------------------------
# ③ 월별 평균 기온차
# -------------------------
st.header("③ 월별 평균 기온차 (서울-양평)")
month_diff = df.groupby("월")["기온차"].mean()
st.bar_chart(month_diff)

# -------------------------
# 데이터 보기
# -------------------------
with st.expander("병합된 데이터 보기"):
    st.dataframe(df)

st.markdown("---")
st.write("기온차 = 서울 기온 − 양평 기온")
st.write("양(+)의 값이 클수록 서울이 양평보다 더 따뜻하여 도시 열섬현상이 강한 것으로 해석할 수 있습니다.")
