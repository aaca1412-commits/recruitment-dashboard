import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. 頁面基本配置
st.set_page_config(
    page_title="國軍志願役招募數據儀表板",
    page_icon="🪖",
    layout="wide"
)

st.title("🪖 國軍志願役招募數據儀表板")
st.markdown("提供即時招募數據監控、合格率計算與多維度探索分析")
st.divider()

# 2. 載入資料與快取機制 (st.cache_data)
@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="工作表1")
    df["未報到原因"] = df["未報到原因"].fillna("已報到/無須紀錄")
    df["體檢不合格原因"] = df["體檢不合格原因"].fillna("體檢合格/無須紀錄")
    df["總體結果"] = df.apply(
        lambda row: "合格" if row.get("資審結果") == "合格" and row.get("體檢結果") == "合格" and row.get("報到狀態") == "已報到"else "不合格",
        axis=1
    )
    return df

df = load_data()

# 3. 側邊欄篩選器 (st.sidebar)
st.sidebar.header("🔍 資料篩選條件")

selected_team = st.sidebar.multiselect(
    "選擇班隊類別",
    options=df["班隊類別"].unique(),
    default=df["班隊類別"].unique()
)

selected_source = st.sidebar.multiselect(
    "選擇招獲來源",
    options=df["招獲來源"].unique(),
    default=df["招獲來源"].unique()
)

# 根據側邊欄條件過濾資料
filtered_df = df[
    (df["班隊類別"].isin(selected_team)) & 
    (df["招獲來源"].isin(selected_source))
]

# 4. 關鍵指標卡片 (KPI Cards)
st.subheader("📊 關鍵招募指標 (KPIs)")

total_applicants = len(filtered_df)
pass_applicants = (filtered_df["總體結果"] == "合格").sum()
pass_rate = (pass_applicants / total_applicants * 100) if total_applicants > 0 else 0
reported_count = (filtered_df["報到狀態"] == "已報到").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="總報名人數", value=f"{total_applicants} 人")
col2.metric(label="綜合合格人數", value=f"{pass_applicants} 人")
col3.metric(label="整體合格率", value=f"{pass_rate:.1f}%")
col4.metric(label="實際報到人數", value=f"{reported_count} 人")

st.divider()

# 5. 第 10 週：高階圖表與多維度探索分析 (Plotly)
st.subheader("📈 多維度探索分析")

# 第一排圖表：人數分布與合格率圓餅圖
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    team_counts = filtered_df["班隊類別"].value_counts().reset_index()
    team_counts.columns = ["班隊類別", "人數"]
    fig_team = px.bar(
        team_counts,
        x="班隊類別",
        y="人數",
        title="各班隊報名人數分布",
        color="班隊類別",
        text_auto=True
    )
    st.plotly_chart(fig_team, use_container_width=True)

with row1_col2:
    result_counts = filtered_df["總體結果"].value_counts().reset_index()
    result_counts.columns = ["總體結果", "人數"]
    fig_result = px.pie(
        result_counts,
        names="總體結果",
        values="人數",
        title="年度招募合格 / 不合格比例",
        color="總體結果",
        color_discrete_map={"合格": "#2ca02c", "不合格": "#d62728"},
        hole=0.4
    )
    st.plotly_chart(fig_result, use_container_width=True)

# 第二排圖表：招獲來源與未報到原因分析
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    source_counts = filtered_df["招獲來源"].value_counts().reset_index()
    source_counts.columns = ["招獲來源", "人數"]
    fig_source = px.bar(
        source_counts,
        x="人數",
        y="招獲來源",
        orientation="h",
        title="招獲來源統計分析",
        color="招獲來源",
        text_auto=True
    )
    st.plotly_chart(fig_source, use_container_width=True)

with row2_col2:
    unreported_df = filtered_df[filtered_df["報到狀態"] == "未報到"]
    if len(unreported_df) > 0:
        reason_counts = unreported_df["未報到原因"].value_counts().reset_index()
        reason_counts.columns = ["未報到原因", "人數"]
        fig_reason = px.pie(
            reason_counts,
            names="未報到原因",
            values="人數",
            title="未報到原因結構分析"
        )
        st.plotly_chart(fig_reason, use_container_width=True)
    else:
        st.info("目前無未報到資料")

st.divider()

# 6. 招募清單明細 (st.dataframe)
st.subheader("📋 招募測試資料明細")
st.dataframe(filtered_df, use_container_width=True)
