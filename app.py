import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="AI 통합 추천 플랫폼", layout="wide")

# 1. 데이터 로드 및 정교한 점수 계산
@st.cache_data
def load_and_process_data():
    if os.path.exists("book_data.csv"):
        df = pd.read_csv("book_data.csv")
        
        # 데이터 타입 보정
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        df['salesPoint'] = pd.to_numeric(df['salesPoint'], errors='coerce').fillna(0)
        
        # 1) 평점 정규화 (10점 만점을 100점 만점으로 환산)
        norm_score = df['score'] * 10
        
        # 2) 판매지수 정규화 (로그 스케일 적용 후 0~100점 변환)
        # 판매지수는 격차가 크므로 로그를 씌워야 균형 잡힌 점수가 나옵니다.
        log_sales = np.log1p(df['salesPoint'])
        norm_sales = (log_sales / log_sales.max()) * 100
        
        # 3) 최종 점수 (평점 50% + 판매지수 50% 합산)
        df['popularity_score'] = (norm_score * 0.5) + (norm_sales * 0.5)
        
        return df
    return None

# 데이터 출력 포맷팅 (크리에이터 명칭 적용)
def get_display_df(data):
    d = data[['title', 'artist', 'year', 'popularity_score']].copy()
    d.columns = ['제목', '크리에이터', '발행년도', '점수']
    d['점수'] = d['점수'].round(1) # 소수점 첫째 자리까지 표시
    return d

# --- UI 구성 ---
st.title("🚀 AI 콘텐츠 추천 플랫폼")

main_tab1, main_tab2, main_tab3 = st.tabs(["📚 도서", "🎵 음악 (준비중)", "🎬 영화 (준비중)"])

with main_tab1:
    df = load_and_process_data()
    if df is not None:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🏆 전체 TOP 10", "📈 장르별 정밀 추천", "🎲 랜덤 발견"])
        
        with sub_tab1:
            st.header("🌟 통합 베스트셀러")
            st.dataframe(get_display_df(df.sort_values(by='popularity_score', ascending=False).head(10)), use_container_width=True)
        with sub_tab2:
            genre = st.selectbox("장르 선택", df['genre'].unique())
            st.dataframe(get_display_df(df[df['genre'] == genre].sort_values(by='popularity_score', ascending=False).head(10)), use_container_width=True)
        with sub_tab3:
            if st.button("추천 받기"):
                st.dataframe(get_display_df(df.sample(min(10, len(df)))), use_container_width=True)
    else:
        st.error("데이터 파일(`book_data.csv`)을 찾을 수 없습니다. `aladin.py`를 먼저 실행하세요.")

with main_tab2:
    st.info("🎵 음악 데이터는 곧 업데이트될 예정입니다.")

with main_tab3:
    st.info("🎬 영화 데이터는 곧 업데이트될 예정입니다.")