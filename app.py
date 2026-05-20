import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="도서 추천 시스템", layout="wide")

# 1. 데이터 로드 및 전처리 (강력한 정제 로직 포함)
@st.cache_data
def load_and_process_data():
    df = pd.read_csv("book_data.csv")
    
    # 데이터를 숫자로 강제 변환 (문자열이 섞여 있어도 해결됨)
    # pd.to_numeric은 숫자가 아닌 데이터가 있으면 NaN으로 바꿉니다.
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2000)
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
    
    # 인기도 계산: 평점(80%) + 최신성(20%) 로직
    df['popularity_score'] = (df['score'] * 10) + ((df['year'] - 2020) * 0.5)
    
    return df

# 메인 UI
st.title(" 컨텐츠 추천 웹사이트")
st.markdown("---")

if os.path.exists("book_data.csv"):
    df = load_and_process_data()
    
    tab1, tab2, tab3 = st.tabs(["🏆 전체 TOP 10", "📈 장르별 인기 TOP 10", "🎲 장르별 랜덤 추천"])

    # 시스템 1) 전체 통합 TOP 10
    with tab1:
        st.header("🌟 전 장르 통합 베스트셀러")
        top10 = df.sort_values(by='popularity_score', ascending=False).head(10)
        # 소수점 점수까지 명확하게 확인 가능
        st.dataframe(top10[['title', 'artist', 'year', 'score', 'popularity_score', 'genre']], use_container_width=True)

    # 시스템 2) 장르별 인기 TOP 10
    with tab2:
        st.header("🔍 카테고리별 정밀 추천")
        selected_genre = st.selectbox("장르 선택", df['genre'].unique())
        genre_top = df[df['genre'] == selected_genre].sort_values(by='popularity_score', ascending=False).head(10)
        st.dataframe(genre_top[['title', 'artist', 'year', 'score', 'popularity_score']], use_container_width=True)

    # 시스템 3) 랜덤 추천
    with tab3:
        st.header("🎰 오늘의 우연한 발견")
        selected_genre_rnd = st.selectbox("장르 선택", df['genre'].unique(), key="rnd")
        if st.button("추천 받기"):
            random_books = df[df['genre'] == selected_genre_rnd].sample(min(10, len(df)))
            st.dataframe(random_books[['title', 'artist', 'year', 'score', 'popularity_score']], use_container_width=True)

    # 사이드바
    with st.sidebar:
        st.info("💡 **알고리즘 안내**\n평점과 최신성(2020년 기준) 가중치를 합산하여 인기도를 산정합니다.")
        st.write(f"현재 등록된 총 도서: {len(df)}권")

else:
    st.error("데이터 파일(`book_data.csv`)을 찾을 수 없습니다. `aladin.py`를 먼저 실행해주세요!")