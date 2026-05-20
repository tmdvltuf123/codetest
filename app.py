import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="AI 통합 추천 플랫폼", layout="wide")

# 데이터 로드 및 전처리 (도서)
@st.cache_data
def load_and_process_data():
    if os.path.exists("book_data.csv"):
        df = pd.read_csv("book_data.csv")
        df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2000)
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        df['popularity_score'] = (df['score'] * 10) - ((2026 - df['year']) * 0.5)
        df['popularity_score'] = df['popularity_score'].clip(lower=0)
        return df
    return None

def get_display_df(data):
    d = data[['title', 'artist', 'year', 'popularity_score']].copy()
    d.columns = ['제목', '크리에이터', '발행년도', '점수']
    return d

# --- UI 구성 ---
st.title("🚀 AI 콘텐츠 추천 플랫폼")

# 가장 상단에 3개의 큰 탭 배치
main_tab1, main_tab2, main_tab3 = st.tabs(["📚 도서", "🎵 음악 (준비중)", "🎬 영화 (준비중)"])

# 1. 도서 탭
with main_tab1:
    df = load_and_process_data()
    if df is not None:
        # 도서 내부 상세 탭
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🏆 전체 TOP 10", "📈 장르별 정밀 추천", "🎲 랜덤 발견"])
        
        with sub_tab1:
            st.header("🌟 도서 베스트셀러")
            st.dataframe(get_display_df(df.sort_values(by='popularity_score', ascending=False).head(10)), use_container_width=True)
        with sub_tab2:
            genre = st.selectbox("장르 선택", df['genre'].unique())
            st.dataframe(get_display_df(df[df['genre'] == genre].sort_values(by='popularity_score', ascending=False).head(10)), use_container_width=True)
        with sub_tab3:
            if st.button("추천 받기"):
                st.dataframe(get_display_df(df.sample(min(10, len(df)))), use_container_width=True)
    else:
        st.error("데이터 파일을 찾을 수 없습니다.")

# 2. 음악 탭
with main_tab2:
    st.info("🎵 음악 데이터는 곧 업데이트될 예정입니다.")

# 3. 영화 탭
with main_tab3:
    st.info("🎬 영화 데이터는 곧 업데이트될 예정입니다.")