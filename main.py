import streamlit as st
import pandas as pd

st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")

st.title("🌆 서울과 양평의 도시 열섬현상 분석")
st.write("2025년 시간별 기온 데이터를 이용하여 서울과 양평의 기온을 비교합니다.")

# -------------------------
# 데이터 불러오기
# -------------------------
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

# 날짜 형식 변환
seoul["일시"] = pd.to_datetime(seoul["일시"])
yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

# 필요한 열만 선택
seoul = seoul[["일시", "기온(°C)"]]
yangpyeong = yangpyeong[["일시", "기온(°C)"]]

# 열 이름 변경
seoul.rename(columns={"기온(°C)": "서울"}, inplace=True)
yangpyeong.rename(columns={"기온(°C)": "양평"}, inplace=True)

# 데이터 병합
df = pd.merge(seoul, yangpyeong, on="일시")

# 기온차 계산
df["기온차"] = df["서울"] - df["양평"]

# 시간, 월 정보 추가
df["시간"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

# -------------------------
# 그래프 1
# -------------------------
st.header("① 1년간 서울과 양평의 기온 변화")

line_df = df.set_index("일시")[["서울", "양평"]]

st.line_chart(line_df)

# -------------------------
# 그래프 2
# -------------------------
st.header("② 시간대별 평균 기온차 (서울 - 양평)")

hour_diff = (
    df.groupby("시간")["기온차"]
      .mean()
      .reset_index()
      .set_index("시간")
)

st.bar_chart(hour_diff)

# -------------------------
# 그래프 3
# -------------------------
st.header("③ 월별 평균 기온차 (서울 - 양평)")

month_diff = (
    df.groupby("월")["기온차"]
      .mean()
      .reset_index()
      .set_index("월")
)

st.bar_chart(month_diff)

# -------------------------
# 데이터 보기
# -------------------------
with st.expander("데이터 보기"):
    st.dataframe(df)

st.markdown("---")
st.write("기온차 = 서울 기온 - 양평 기온")
st.write("기온차가 클수록 도시 열섬현상이 강하게 나타난 것으로 볼 수 있습니다.")
