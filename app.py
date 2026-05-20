import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="콘텐츠 통합 추천 플랫폼", layout="wide")


@st.cache_data
def load_and_process_data(file_name):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        
        
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        df['salesPoint'] = pd.to_numeric(df['salesPoint'], errors='coerce').fillna(0)
        
       
        norm_score = df['score'] * 10
        
       
        log_val = np.log1p(df['salesPoint'])
        log_max = np.log1p(464853) 
        
        
        norm_sales = (log_val / log_max) * 50
        norm_sales = norm_sales.clip(upper=50)
        
       
        df['popularity_score'] = norm_score + norm_sales
        
        return df
    return None


def get_display_df(data):
    d = data[['title', 'artist', 'genre', 'year', 'popularity_score']].copy()
    
  
    d['title'] = d['title'].apply(lambda x: str(x)[:30] + '...' if len(str(x)) > 30 else x)
    
    d.columns = ['제목', '크리에이터', '장르', '발행년도', '점수']
    d['점수'] = d['점수'].round(1)
    return d


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
            "점수": st.column_config.NumberColumn("점수", format="%.1f")
        }
    )


st.title("콘텐츠 통합 추천 플랫폼")

main_tab1, main_tab2, main_tab3 = st.tabs([" 도서", " 영화 (준비중)", " 음악 (준비중)"])


with main_tab1:
    df_book = load_and_process_data("book_data.csv")
    if df_book is not None:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs([" 전체 TOP 10", " 장르별 정밀 추천", " 랜덤 발견"])
        
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


with main_tab2:
    df_movie = load_and_process_data("movie_data.csv")
    if df_movie is not None:
        st.header(" 인기 영화 추천")
        show_dataframe(get_display_df(df_movie.sort_values(by='popularity_score', ascending=False).head(10)))
    else:
        st.info("영화 데이터가 없습니다. `tmdb.py`를 먼저 실행하세요.")

with main_tab3:
    st.info(" 음악 데이터는 곧 업데이트될 예정입니다.")