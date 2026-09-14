import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
2023년~2024년 기준 **365일간의 일별 박스오피스 TOP 10 데이터**를 기반으로 시간 흐름에 따른 다양한 영화 지표를 시각화합니다.
---
""")

# 2. 데이터 불러오기 및 전처리 (캐싱 처리)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # 날짜 열을 datetime 형태로 변환 (YYYYMMDD -> datetime)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 관객수 및 상영 횟수 등 수치형 데이터 확인/정리
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 구역 1: [개별 분석] 영화별 일관객수 변화
# -----------------------------------------------------------------------------
st.header("📌 Section 1. 영화별 일별 관객수 추이")

# 영화 목록 추출 (가나다순)
movie_list = sorted(df['영화명'].dropna().unique())

# 드롭다운 셀렉트박스
selected_movie = st.selectbox(
    "조회할 영화를 선택하세요:",
    options=movie_list,
    index=0 if len(movie_list) > 0 else None
)

if selected_movie:
    # 선택된 영화 데이터 필터링
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

    # 플롯리(Plotly) 선 그래프 생성
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<{selected_movie}> 일별 관객수 변화 추이",
        labels={'날짜': '상영 날짜', '일관객': '일일 관객수 (명)'},
        markers=True
    )

    # Hover format 및 스타일 지정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>",
        line=dict(width=2.5, color='#E50914'),
        marker=dict(size=6)
    )

    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객수 (명)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )

    # 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)

    # 그래프 해석/인사이트 작성 영역
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 2: [비교 분석] TOP 5 영화의 일별 관객수 비교
# -----------------------------------------------------------------------------
st.header("📌 Section 2. 기간 내 일관객 합계 TOP 5 영화 비교")

# 전체 기간 일관객 합계 상위 5개 영화 선출
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()

# 상위 5개 영화의 데이터 필터링
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

# 5개 영화 선 그래프 생성
fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="기간 내 일관객 합계 상위 5개 영화의 일별 관객수 비교",
    labels={'날짜': '상영 날짜', '일관객': '일일 관객수 (명)', '영화명': '영화 제목'}
)

# Hover format 및 범례 동작 설정
fig2.update_traces(
    hovertemplate="<b>영화:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객수 (명)",
    hovermode="x unified",
    legend_title_text="영화 제목 (클릭 시 토글)",
    margin=dict(l=40, r=40, t=60, b=40),
    template="plotly_white"
)

# 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 해석/인사이트 작성 영역
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 3: [전체 시장 분석] 일별 박스오피스 TOP 10 총 관객수 영역 그래프
# -----------------------------------------------------------------------------
st.header("📌 Section 3. 일별 박스오피스 TOP 10 총 관객수 추이")

# 날짜별 10위권 일관객 합계 계산
daily_total_df = df.groupby('날짜')['일관객'].sum().reset_index()

# 합계가 가장 컸던 상위 3일 구하기
top3_days = daily_total_df.nlargest(3, '일관객').sort_values('날짜')

# 영역 그래프(Area Chart) 생성
fig3 = px.area(
    daily_total_df,
    x='날짜',
    y='일관객',
    title="일별 박스오피스 10위권 관객 합계 추이 (최고 관객수 TOP 3일 표시)",
    labels={'날짜': '상영 날짜', '일관객': 'TOP 10 총 관객수 (명)'}
)

fig3.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>TOP 10 총 관객수:</b> %{y:,}명<extra></extra>",
    line=dict(color='#2E86C1', width=2),
    fillcolor='rgba(46, 134, 193, 0.3)'
)

# 상위 3일에 주석(Annotation) 추가
for idx, row in top3_days.iterrows():
    day_str = row['날짜'].strftime('%Y-%m-%d')
    audience_cnt = row['일관객']
    
    fig3.add_annotation(
        x=row['날짜'],
        y=audience_cnt,
        text=f"<b>TOP {top3_days.index.get_loc(idx)+1}위</b><br>{day_str}<br>({audience_cnt:,.0f}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#E74C3C',
        ax=0,
        ay=-45,
        bgcolor='#FADBD8',
        bordercolor='#E74C3C',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#78281F')
    )

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="TOP 10 총 관객수 (명)",
    hovermode="x unified",
    margin=dict(l=40, r=40, t=60, b=40),
    template="plotly_white"
)

# 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 해석/인사이트 작성 영역
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 4: [총 관객수 분석] 누적 관객수 TOP 10 영화 (가로 막대 그래프)
# -----------------------------------------------------------------------------
st.header("📌 Section 4. 기간 내 일관객 합계 TOP 10 영화")

# 영화별 일관객 합계 및 10위권 진입 일수 산출
movie_summary = df.groupby('영화명').agg(
    총관객수=('일관객', 'sum'),
    TOP10_진입일수=('날짜', 'count')
).reset_index()

# 총관객수 기준 상위 10개 영화 선택
top10_summary = movie_summary.nlargest(10, '총관객수').sort_values('총관객수', ascending=True)

# 가로 막대 그래프 생성
fig4 = px.bar(
    top10_summary,
    x='총관객수',
    y='영화명',
    orientation='h',
    title="기간 내 일관객 합계 TOP 10 영화 (10위권 진입 일수 포함)",
    labels={'총관객수': '기간 내 총 관객수 (명)', '영화명': '영화 제목'},
    text_auto=',.0f',
    color='총관객수',
    color_continuous_scale='Blues'
)

fig4.update_traces(
    customdata=top10_summary[['TOP10_진입일수']],
    hovertemplate="<b>영화명:</b> %{y}<br><b>기간 내 총 관객수:</b> %{x:,}명<br><b>TOP 10 진입 일수:</b> %{customdata[0]}일<extra></extra>",
    textposition='outside'
)

fig4.update_layout(
    xaxis_title="기간 내 총 관객수 (명)",
    yaxis_title="영화 제목",
    coloraxis_showscale=False,
    margin=dict(l=40, r=40, t=60, b=40),
    template="plotly_white"
)

# 그래프 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 해석/인사이트 작성 영역
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 5: [시즌/요일 분석] 월 x 요일별 일관객 합계 히트맵
# -----------------------------------------------------------------------------
st.header("📌 Section 5. 월 × 요일별 관객수 히트맵")

# 월 및 요일 컬럼 생성
df_heatmap = df.copy()
df_heatmap['월'] = df_heatmap['날짜'].dt.month.astype(str) + "월"
df_heatmap['요일'] = df_heatmap['날짜'].dt.day_name()

# 요일 한글 변환 매핑
day_map = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
}
df_heatmap['요일'] = df_heatmap['요일'].map(day_map)

# 월 및 요일 순서 지정
month_order = [f"{m}월" for m in range(1, 13)]
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 월 x 요일별 관객수 합계 피벗 테이블 생성
heatmap_pivot = df_heatmap.groupby(['월', '요일'])['일관객'].sum().reset_index()

# 피벗 테이블 재구성
pivot_table = heatmap_pivot.pivot(index='월', columns='요일', values='일관객')

# 순서 재정렬
pivot_table = pivot_table.reindex(index=[m for m in month_order if m in pivot_table.index],
                                  columns=[d for d in day_order if d in pivot_table.columns])

# 히트맵 생성
fig5 = px.imshow(
    pivot_table,
    labels=dict(x="요일", y="월", color="총 관객수 (명)"),
    x=pivot_table.columns,
    y=pivot_table.index,
    color_continuous_scale="Reds",
    aspect="auto",
    title="월 × 요일별 박스오피스 일관객 합계 히트맵"
)

# Hover format 설정
fig5.update_traces(
    hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>",
)

fig5.update_layout(
    xaxis_title="요일 (월~일)",
    yaxis_title="월",
    margin=dict(l=40, r=40, t=60, b=40),
    template="plotly_white"
)

# 그래프 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 해석/인사이트 작성 영역
st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 6: [추가 그래프 예시 구역]
# -----------------------------------------------------------------------------
st.header("📌 Section 6. (추후 그래프 추가 영역)")
st.caption("앞으로 추가할 시각화 그래프들이 이곳에 순차적으로 추가됩니다.")

with st.container():
    st.write("*(여기에 다음 그래프가 들어갈 자리입니다)*")
    st.info("💡 **이 그래프로 알 수 있는 것:** (이곳에 작성할 내용을 입력하세요.)")
