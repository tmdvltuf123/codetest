import streamlit as st
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="콘텐츠 통합 추천 플랫폼", layout="wide")


GENRE_TO_MOOD_TAGS = {
    "액션": {"긴장감"},
    "스릴러": {"긴장감", "몰입"},
    "SF": {"신비", "몰입"},
    "판타지": {"신비"},
    "코미디": {"유쾌함"},
    "드라마": {"감성", "몰입"},
    "로맨스": {"감성", "힐링"},
    "공포": {"긴장감"},
    "미스터리": {"긴장감", "몰입"},
    "애니메이션": {"유쾌함", "힐링"},

    "소설": {"몰입", "감성"},
    "경제/경영": {"동기부여"},
    "자기계발": {"동기부여"},
    "인문": {"몰입"},
    "사회": {"몰입"},
    "과학": {"신비"},
    "역사": {"몰입"},
    "에세이": {"감성", "힐링"},
    "IT/컴퓨터": {"동기부여"},
}

DISPLAY_MOOD_TO_TAG = {
    "감성적인": "감성",
    "긴장감 있는": "긴장감",
    "유쾌한": "유쾌함",
    "몰입감 있는": "몰입",
    "신비로운": "신비",
    "동기부여가 되는": "동기부여",
    "힐링되는": "힐링",
}


KEYWORD_TO_MOOD_TAGS = {
    "범죄": {"긴장감"},
    "모험": {"신비"},
    "멜로": {"감성"},
    "사랑": {"감성"},
    "k-pop": {"유쾌함"},
    "록": {"몰입"},
    "발라드": {"감성"},
    "힙합": {"몰입"},
    "재즈": {"힐링"},
}

if "show_persona_survey" not in st.session_state:
    st.session_state.show_persona_survey = False

if "persona_answers" not in st.session_state:
    st.session_state.persona_answers = {}

if "expanded_movie_plots" not in st.session_state:
    st.session_state.expanded_movie_plots = {}

if "random_recommendations" not in st.session_state:
    st.session_state.random_recommendations = {}


@st.cache_data
def load_and_process_data(file_name, file_mtime):
    file_path = BASE_DIR / file_name
    if file_path.exists():
        df = pd.read_csv(file_path)

        if file_name == "movie_data.csv" and "title" in df.columns:
            # 한국어/영어/숫자/기본 문장부호로만 구성된 제목만 유지
            title_pattern = re.compile(r"^[A-Za-z0-9가-힣\s\-:,.!?\'\"()&/]+$")
            df = df[df["title"].astype(str).str.match(title_pattern, na=False)].copy()

        # salespoint 높은 순으로 top10 정렬하는 코드에요
        df['salesPoint'] = pd.to_numeric(df['salesPoint'], errors='coerce').fillna(0)

        return df
    return None


def get_display_df(data):
    d = data[['title', 'genre', 'year']].copy()
    
    d.columns = ['제목', '장르', '발행년도']
    return d


def get_book_display_df(data):
    d = data[['coverUrl', 'title', 'genre', 'year']].copy()
    d.columns = ['표지', '제목', '장르', '발행년도']
    return d


def get_music_display_df(data):
    d = data[['artworkUrl', 'title', 'genre', 'year']].copy()
    d.columns = ['앨범', '제목', '장르', '발행년도']
    return d


def get_movie_display_df(data):
    d = data[['posterUrl', 'title', 'genre', 'year']].copy()
    if 'overview' in data.columns:
        d['overview'] = data['overview'].fillna('').astype(str)
    else:
        d['overview'] = ''
    d.columns = ['포스터', '제목', '장르', '발행년도', '줄거리']
    return d


def show_dataframe(df):
    st.dataframe(
        df,
        width='stretch', 
        hide_index=True,
        column_config={
            "제목": st.column_config.TextColumn("제목", width="large"),
            "장르": st.column_config.TextColumn("장르", width="small"),
            "발행년도": st.column_config.NumberColumn("발행년도", format="%d")
        }
    )
    


def show_book_cards(df):
    rows = [df.iloc[i:i+5] for i in range(0, len(df), 5)]

    for row_df in rows:
        cols = st.columns(5)

        for col, (_, row) in zip(cols, row_df.iterrows()):
            with col:
                if pd.notna(row["표지"]):
                    st.image(row["표지"],width=200)
                else:
                    st.image("image/no_image.png", width=200)
                st.markdown(f"**{row['제목']}**")
                st.caption(row["장르"])
                st.caption(str(row["발행년도"]))


def show_music_cards(df):
    rows = [df.iloc[i:i+5] for i in range(0, len(df), 5)]

    for row_df in rows:
        cols = st.columns(5)

        for col, (_, row) in zip(cols, row_df.iterrows()):
            with col:
                st.image(row["앨범"], width=200)
                st.markdown(f"**{row['제목']}**")
                st.caption(row["장르"])
                st.caption(str(row["발행년도"]))
    
    


def show_movie_cards(df, key_prefix="movie"):

    rows = [df.iloc[i:i+5] for i in range(0, len(df), 5)]
    card_index = 0

    for row_df in rows:
        cols = st.columns(5)

        for col, (_, row) in zip(cols, row_df.iterrows()):
            with col:
                st.image(row["포스터"], width=200)
                st.markdown(f"**{row['제목']}**")
                st.caption(row["장르"])
                st.caption(str(row["발행년도"]))

                title = str(row.get("제목", ""))
                year = row.get("발행년도", "")
                movie_key = f"{title}::{year}"
                button_key = f"{key_prefix}_plot_btn_{card_index}_{movie_key}"

                is_open = st.session_state.expanded_movie_plots.get(movie_key, False)
                button_label = "줄거리 닫기" if is_open else "줄거리 보기"

                if st.button(button_label, key=button_key, use_container_width=True):
                    st.session_state.expanded_movie_plots[movie_key] = not is_open
                    st.rerun()

                if st.session_state.expanded_movie_plots.get(movie_key, False):
                    overview = str(row.get("줄거리", "")).strip()
                    if not overview:
                        overview = "줄거리 정보가 없습니다."
                    st.info(overview)

                card_index += 1

        


def get_unique_genres(df):
    genre_series = df['genre'].dropna().astype(str)
    split_genres = genre_series.str.split(',')
    return sorted({g.strip() for genres in split_genres for g in genres if g.strip()})


def has_genre(genre_text, selected_genre):
    genre_list = [g.strip() for g in str(genre_text).split(',') if g.strip()]
    return selected_genre in genre_list


def render_recommendation_tabs(df, content_key):
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([" 전체 TOP 10", " 장르별 정밀 추천", " 랜덤 발견"])

    with sub_tab1:
        top10 = df.sort_values(by='salesPoint', ascending=False).head(10)
        if content_key == "book" and "coverUrl" in df.columns:
            show_book_cards(get_book_display_df(top10))
        elif content_key == "music":
            show_music_cards(get_music_display_df(top10))
        elif content_key == "movie" and "posterUrl" in df.columns:
            show_movie_cards(get_movie_display_df(top10), key_prefix=f"{content_key}_top")
        else:
            show_dataframe(get_display_df(top10))

    with sub_tab2:
        # if문에서는 영화는 genre 데이터 자체가 복수값이므로, 장르 선택 시 해당 장르가 포함된 영화들을 필터링
        if content_key == "movie":
            genre_options = get_unique_genres(df)
            genre = st.selectbox("장르 선택", genre_options, key=f"genre_{content_key}")
            filtered_df = df[df['genre'].apply(lambda x: has_genre(x, genre))].sort_values(by='salesPoint', ascending=False).head(10)
            if "posterUrl" in df.columns:
                show_movie_cards(get_movie_display_df(filtered_df), key_prefix=f"{content_key}_genre")
            else:
                show_dataframe(get_display_df(filtered_df))
        # else문에서는 book과 music은 genre가 단일값이므로 기존 방식으로 필터링
        else:
            genre = st.selectbox("장르 선택", df['genre'].dropna().unique(), key=f"genre_{content_key}")
            filtered_df = df[df['genre'] == genre].sort_values(by='salesPoint', ascending=False).head(10)
            if content_key == "book" and "coverUrl" in df.columns:
                show_book_cards(get_book_display_df(filtered_df))
            elif content_key == "music":
                show_music_cards(get_music_display_df(filtered_df))
            else:
                show_dataframe(get_display_df(filtered_df))

    with sub_tab3:
        if st.button("추천 받기", key=f"random_{content_key}"):
            random_df = df.sample(min(10, len(df)))
            st.session_state.random_recommendations[content_key] = random_df.to_dict("records")

        random_records = st.session_state.random_recommendations.get(content_key)
        if random_records:
            random_df = pd.DataFrame(random_records)
            if content_key == "book" and "coverUrl" in random_df.columns:
                show_book_cards(get_book_display_df(random_df))
            elif content_key == "music":
                show_music_cards(get_music_display_df(random_df))
            elif content_key == "movie" and "posterUrl" in random_df.columns:
                show_movie_cards(get_movie_display_df(random_df), key_prefix=f"{content_key}_random")
            else:
                show_dataframe(get_display_df(random_df))


def get_file_mtime(file_name):
    file_path = BASE_DIR / file_name
    return file_path.stat().st_mtime if file_path.exists() else 0


def get_persona_recommendations(df, answers):
    if df is None or df.empty:
        return pd.DataFrame()

    rec_df = df.copy()

    def to_numeric_column(frame, column_name):
        if column_name in frame.columns:
            return pd.to_numeric(frame[column_name], errors="coerce").fillna(0)
        return pd.Series([0] * len(frame), index=frame.index, dtype="float64")

    rec_df["salesPoint"] = to_numeric_column(rec_df, "salesPoint")
    rec_df["score"] = to_numeric_column(rec_df, "score")
    rec_df["year"] = to_numeric_column(rec_df, "year")

    selected_moods = {
    DISPLAY_MOOD_TO_TAG[m]
    for m in answers.get("선호분위기", [])
    if m in DISPLAY_MOOD_TO_TAG
}
    def build_user_mood_tags(moods):
       return set(moods)

    def extract_item_mood_tags(genre_text, title_text):
        text = f"{genre_text} {title_text}".lower()
        tags = set()

        for genre_name, mood_set in GENRE_TO_MOOD_TAGS.items():
            if genre_name.lower() in text:
                tags.update(mood_set)

        for keyword, mood_set in KEYWORD_TO_MOOD_TAGS.items():
            if keyword in text:
                tags.update(mood_set)

         # 태그로 장르명이나 제목에서 추출된 단어를 태그로 활용하는 방법을 사용함
        if not tags:
            tags.add("기본")
        return tags

    user_mood_tags = build_user_mood_tags(selected_moods)

    def genre_match_score(genre_text, title_text):
        if not user_mood_tags:
            return 0.5

        item_tags = extract_item_mood_tags(genre_text, title_text)
        matched = user_mood_tags.intersection(item_tags)
        return len(matched) / max(len(user_mood_tags), 1)

    if "genre" in rec_df.columns:
        rec_df["genre_match"] = rec_df.apply(
            lambda row: genre_match_score(row.get("genre", ""), row.get("title", "")),
            axis=1,
        )
    else:
        rec_df["genre_match"] = 0.0
    rec_df["popularity_score"] = rec_df["salesPoint"].rank(pct=True)
    rec_df["rating_score"] = rec_df["score"].rank(pct=True)
    rec_df["freshness_score"] = rec_df["year"].rank(pct=True)

    weights = {
        "genre": 0.4,
        "popularity": 0.2,
        "rating": 0.2,
        "freshness": 0.2,
    }

    if answers.get("작품성향") == "인기작 위주":
        weights["popularity"] += 0.2
        weights["freshness"] -= 0.1
        weights["rating"] -= 0.1
    elif answers.get("작품성향") == "새로운 작품 위주":
        weights["freshness"] += 0.2
        weights["popularity"] -= 0.1
        weights["rating"] -= 0.1

    important = answers.get("중요기준")
    if important == "평점":
        weights["rating"] += 0.2
        weights["genre"] -= 0.1
        weights["freshness"] -= 0.1
    elif important == "최신성":
        weights["freshness"] += 0.2
        weights["genre"] -= 0.1
        weights["rating"] -= 0.1
    elif important in ["줄거리(주제)", "분위기"]:
        weights["genre"] += 0.2
        weights["popularity"] -= 0.1
        weights["freshness"] -= 0.1

    
    for key in weights:
        weights[key] = max(weights[key], 0.05)

    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}

    rec_df["persona_score"] = (
        rec_df["genre_match"] * weights["genre"]
        + rec_df["popularity_score"] * weights["popularity"]
        + rec_df["rating_score"] * weights["rating"]
        + rec_df["freshness_score"] * weights["freshness"]
    )

    return rec_df.sort_values(by="persona_score", ascending=False).head(10)


def render_persona_recommendations(answers):
    df_book = load_and_process_data("book_data.csv", get_file_mtime("book_data.csv"))
    df_movie = load_and_process_data("movie_data.csv", get_file_mtime("movie_data.csv"))
    df_music = load_and_process_data("music_data.csv", get_file_mtime("music_data.csv"))

    rec_book = get_persona_recommendations(df_book, answers)
    rec_movie = get_persona_recommendations(df_movie, answers)
    rec_music = get_persona_recommendations(df_music, answers)

    st.markdown("#### 설문 기반 맞춤 추천 결과")

    result_tab1, result_tab2, result_tab3 = st.tabs([" 도서 추천", " 영화 추천", " 음악 추천"])

    with result_tab1:
        if not rec_book.empty:
            if "coverUrl" in rec_book.columns:
                show_book_cards(get_book_display_df(rec_book))
            else:
                show_dataframe(get_display_df(rec_book))
        else:
            st.info("도서 추천 결과를 만들 수 없습니다.")

    with result_tab2:
        if not rec_movie.empty:
            if "posterUrl" in rec_movie.columns:
                show_movie_cards(get_movie_display_df(rec_movie), key_prefix="persona_movie")
            else:
                show_dataframe(get_display_df(rec_movie))
        else:
            st.info("영화 추천 결과를 만들 수 없습니다.")

    with result_tab3:
        if not rec_music.empty:
            show_music_cards(get_music_display_df(rec_music))
        else:
            st.info("음악 추천 결과를 만들 수 없습니다.")


title_col, button_col = st.columns([6, 1])
with title_col:
    st.title("콘텐츠 통합 추천 플랫폼")

with button_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("사용자 맞춤 추천 콘텐츠 설문", use_container_width=True):
        st.session_state.show_persona_survey = not st.session_state.show_persona_survey


if st.session_state.show_persona_survey:
    with st.container(border=True):
        st.subheader("사용자 맞춤 추천 콘텐츠 설문")
        with st.form("persona_survey_form"):
            q2 = st.multiselect(
                "1. 어떤 분위기의 콘텐츠를 선호하시나요? (복수선택 가능)",
                [
                    "감성적인",
                    "긴장감 있는",
                    "유쾌한",
                    "몰입감 있는",
                    "신비로운",
                    "동기부여가 되는",
                    "힐링되는",
                ],
                key="survey_q2",
            )

            q3 = st.radio(
                "2. 인기작과 새로운 작품 중 무엇을 더 선호하나요?",
                ["인기작 위주", "반반", "새로운 작품 위주"],
                index=None,
                key="survey_q3",
            )

            q4 = st.radio(
                "3. 콘텐츠를 고를 때 가장 중요한 기준은?",
                ["평점", "줄거리(주제)", "분위기", "최신성"],
                index=None,
                key="survey_q4",
            )

            submitted = st.form_submit_button("설문 저장", type="primary")
            if submitted:
                if None in [q3, q4]:
                    st.warning("2, 3번 문항을 모두 선택해주세요.")
                else:
                    st.session_state.persona_answers = {
                        "선호분위기": q2,
                        "작품성향": q3,
                        "중요기준": q4,
                    }
                    st.success("설문 결과가 저장되었습니다.")

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("설문 다시 하기", use_container_width=True):
                st.session_state.persona_answers = {}
                for key in ["survey_q2", "survey_q3", "survey_q4"]:
                    st.session_state.pop(key, None)
                st.rerun()

        with action_col2:
            if st.button("설문 종료", use_container_width=True):
                st.session_state.show_persona_survey = False
                st.rerun()

        if st.session_state.persona_answers:
            st.caption(f"현재 저장된 설문: {st.session_state.persona_answers}")
            render_persona_recommendations(st.session_state.persona_answers)

if not st.session_state.show_persona_survey:
    main_tab1, main_tab2, main_tab3 = st.tabs([" 도서", " 영화", " 음악"])

    with main_tab1:
        df_book = load_and_process_data("book_data.csv", get_file_mtime("book_data.csv"))
        if df_book is not None:
            render_recommendation_tabs(df_book, "book")
        else:
            st.error("도서 데이터를 찾을 수 없습니다.")


    with main_tab2:
        df_movie = load_and_process_data("movie_data.csv", get_file_mtime("movie_data.csv"))
        if df_movie is not None:
            render_recommendation_tabs(df_movie, "movie")
        else:
            st.error("영화 데이터를 찾을 수 없습니다.")

    with main_tab3:
        df_music = load_and_process_data("music_data.csv", get_file_mtime("music_data.csv"))
        if df_music is not None:
            render_recommendation_tabs(df_music, "music")   
        else:
            st.error("음악 데이터를 찾을 수 없습니다.")