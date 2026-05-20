import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="AI 통합 추천 플랫폼", layout="wide")

# 1. 데이터 로드 및 정교한 점수 계산
@st.cache_data
def load_and_process_data(file_name):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        
        # 데이터 타입 보정
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        df['salesPoint'] = pd.to_numeric(df['salesPoint'], errors='coerce').fillna(0)
        
        # 1) 평점 정규화 (5점 만점 * 10 = 50점 만점)
        norm_score = df['score'] * 10
        
        # 2) 판매지수 정규화 (로그 스케일 적용 후 50점 만점)
        log_val = np.log1p(df['salesPoint'])
        log_max = np.log1p(464853) 
        
        # 50점을 넘으면 50점으로 고정
        norm_sales = (log_val / log_max) * 50
        norm_sales = norm_sales.clip(upper=50)
        
        # 3) 최종 합산
        df['popularity_score'] = norm_score + norm_sales
        
        return df
    return None

# 데이터 출력 포맷팅 (제목 길이 제한)
def get_display_df(data):
    d = data[['title', 'artist', 'genre', 'year', 'popularity_score']].copy()
    
    # 제목이 30자가 넘으면 자르고 '...' 붙이기
    d['title'] = d['title'].apply(lambda x: str(x)[:30] + '...' if len(str(x)) > 30 else x)
    
    d.columns = ['제목', '크리에이터', '장르', '발행년도', '점수']
    d['점수'] = d['점수'].round(1)
    return d

# 데이터프레임 렌더링 설정 (빨간 막대 제거)
def show_dataframe(df):
    st.dataframe(
        df,
        width='stretch', 
        hide_index=True,
        column_config={
            "제목": st.column_config.TextColumn("제목", width="large"),
            "크리에이터": st.column_config.TextColumn("크리에이터", width="medium"),
            "장르": st.column_config.TextColumn("장르", width="small"),
            "발행년도": st.column_config.NumberColumn("발행년도", format="%d"),
            # [수정] ProgressColumn 대신 NumberColumn을 사용하여 숫자만 출력
            "점수": st.column_config.NumberColumn("점수", format="%.1f")
        }
    )

# --- UI 구성 ---
st.title("🚀 AI 콘텐츠 추천 플랫폼")

main_tab1, main_tab2, main_tab3 = st.tabs(["📚 도서", "🎬 영화", "🎵 음악 (준비중)"])

# 도서 탭
with main_tab1:
    df_book = load_and_process_data("book_data.csv")
    if df_book is not None:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🏆 전체 TOP 10", "📈 장르별 정밀 추천", "🎲 랜덤 발견"])
        
        with sub_tab1:
            show_dataframe(get_display_df(df_book.sort_values(by='popularity_score', ascending=False).head(10)))
        with sub_tab2:
            genre = st.selectbox("장르 선택", df_book['genre'].unique())
            show_dataframe(get_display_df(df_book[df_book['genre'] == genre].sort_values(by='popularity_score', ascending=False).head(10)))
        with sub_tab3:
            if st.button("추천 받기"):
                show_dataframe(get_display_df(df_book.sample(min(10, len(df_book)))))
    else:
        st.error("도서 데이터를 찾을 수 없습니다.")

# 영화 탭
with main_tab2:
    df_movie = load_and_process_data("movie_data.csv")
    if df_movie is not None:
        st.header("🎬 인기 영화 추천")
        show_dataframe(get_display_df(df_movie.sort_values(by='popularity_score', ascending=False).head(10)))
    else:
        st.info("영화 데이터가 없습니다. `tmdb.py`를 먼저 실행하세요.")

with main_tab3:
    st.info("🎵 음악 데이터는 곧 업데이트될 예정입니다.")