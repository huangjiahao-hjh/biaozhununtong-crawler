#!/usr/bin/env python3
"""
标准通爬虫 - Streamlit Web 界面
"""

import io
import time
from typing import Dict, List

import pandas as pd
import streamlit as st
from scraper import (
    STD_TYPE_MAP,
    STD_STAGE_MAP,
    STD_STATE_MAP,
    FIELD_LABELS,
    fetch_multiple_keywords,
    get_search_total,
    write_excel,
)

# ── 页面配置 ──────────────────────────────────────────
st.set_page_config(
    page_title="标准通爬虫",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── 样式 ─────────────────────────────────────────────
st.markdown(
    """
<style>
    /* ── 全局 ── */
    .stApp {
        background: #fafafa;
    }
    #MainMenu {visibility: hidden;}

    ::-webkit-scrollbar {width: 4px; height: 4px;}
    ::-webkit-scrollbar-track {background: transparent;}
    ::-webkit-scrollbar-thumb {background: #d4d4d8; border-radius: 2px;}

    .main-container {max-width: 1400px; margin: 0 auto; padding: 0 0.5rem;}

    /* ── 顶部横幅 ── */
    .hero {
        background: #09090b;
        border-radius: 16px;
        padding: 2.8rem 3rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute; top: 0; right: 0; width: 50%; height: 100%;
        background: radial-gradient(ellipse at top right, rgba(99,102,241,0.12) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        font-size: 1.75rem; font-weight: 600;
        margin: 0 0 0.4rem 0;
        color: #fafafa;
        letter-spacing: -0.5px;
    }
    .hero p {
        font-size: 0.88rem; margin: 0;
        color: #71717a;
        font-weight: 400;
    }

    /* ── 侧边栏 ── */
    [data-testid="stSidebar"] {
        background: #fafafa !important;
        border-right: 1px solid #e4e4e7 !important;
    }

    /* ── 卡片 ── */
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.6rem 1.8rem;
        border: 1px solid #e4e4e7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }
    .card-title {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        font-size: 0.92rem; font-weight: 600;
        color: #09090b;
        margin-bottom: 1.2rem;
        display: flex; align-items: center; gap: 0.5rem;
        letter-spacing: -0.2px;
    }

    /* ── 主操作按钮 ── */
    div.stButton > button[kind="primary"] {
        background: #09090b !important;
        border: none !important;
        color: #fafafa !important;
        font-weight: 500 !important;
        height: 2.6rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
        font-size: 0.85rem !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #27272a !important;
    }

    /* ── 统计卡片 ── */
    .stat-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        border: 1px solid #e4e4e7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: all 0.15s ease;
    }
    .stat-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .stat-card .num {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        font-size: 1.6rem; font-weight: 700;
        color: #09090b;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .stat-card .label {
        font-size: 0.72rem; font-weight: 500;
        color: #a1a1aa; margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── 数据表格 ── */
    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        border: 1px solid #e4e4e7 !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] thead tr th {
        background: #fafafa !important;
        font-weight: 600 !important;
        color: #09090b !important;
        font-size: 0.75rem !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 1px solid #e4e4e7 !important;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    [data-testid="stDataFrame"] tbody tr:hover td {background: #f9f9fb !important;}
    [data-testid="stDataFrame"] tbody td {
        font-size: 0.82rem;
        padding: 0.5rem 1rem !important;
        border-bottom: 1px solid #f4f4f5 !important;
        color: #27272a;
    }

    /* ── Footer ── */
    .footer {
        text-align: center; padding: 2rem 0 0.5rem 0;
        color: #a1a1aa; font-size: 0.72rem; line-height: 1.8;
        margin-top: 2.5rem;
        position: relative;
    }
    .footer::before {
        content: "";
        display: block; width: 40px; height: 1px; margin: 0 auto 1.5rem;
        background: #e4e4e7;
    }

    /* ── 进度条 ── */
    div.stProgress > div > div > div > div {
        background: #09090b !important;
        border-radius: 2px;
    }

    /* ── 输入框 ── */
    div[data-testid="stTextInput"] input {
        border-radius: 8px !important;
        border: 1px solid #e4e4e7 !important;
        padding: 0.5rem 0.8rem !important;
        font-size: 0.88rem !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #09090b !important;
        box-shadow: 0 0 0 2px rgba(9,9,11,0.08) !important;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 8px !important;
        border: 1px solid #e4e4e7 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #09090b !important;
        box-shadow: 0 0 0 2px rgba(9,9,11,0.08) !important;
    }

    .stCaption {color: #a1a1aa; font-size: 0.78rem;}
</style>""",
    unsafe_allow_html=True,
)


# ── Session 状态 ─────────────────────────────────────
if "search_results" not in st.session_state:
    st.session_state.search_results = None
    st.session_state.search_summary = ""
    st.session_state.show_results_flag = False


# ── 多 Sheet Excel 导出 ─────────────────────────────
def make_multisheet_excel(sheet_dict: Dict[str, pd.DataFrame]) -> bytes:
    """生成多 Sheet Excel 文件的 bytes。"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheet_dict.items():
            # Excel sheet name 不能超 31 字符
            safe_name = sheet_name[:31]
            # 重命名列为中文
            df_renamed = df.rename(columns=FIELD_LABELS)
            df_renamed.to_excel(writer, sheet_name=safe_name, index=False)
    return output.getvalue()


# ── 统计卡片 ──────────────────────────────────────────
def show_stats(df: pd.DataFrame):
    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            f'<div class="stat-card"><div class="num">{len(df)}</div>'
            f'<div class="label">总条数</div></div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        cats = df["standard_category"].value_counts()
        label = " · ".join(f"{k} {v}" for k, v in cats.head(3).items())
        st.markdown(
            f'<div class="stat-card"><div class="num">{len(cats)}</div>'
            f'<div class="label">标准类别</div></div>',
            unsafe_allow_html=True,
        )
    with cols[2]:
        statuses = df["status"].value_counts()
        label = " · ".join(f"{k} {v}" for k, v in statuses.head(3).items())
        st.markdown(
            f'<div class="stat-card"><div class="num">{len(statuses)}</div>'
            f'<div class="label">实施状态</div></div>',
            unsafe_allow_html=True,
        )
    with cols[3]:
        keywords = df["keyword"].value_counts()
        st.markdown(
            f'<div class="stat-card"><div class="num">{len(keywords)}</div>'
            f'<div class="label">搜索关键词</div></div>',
            unsafe_allow_html=True,
        )


# ── Footer ────────────────────────────────────────────
FOOTER_HTML = """
<div class="footer">
    本工具仅用于标准信息查询与学习研究，请勿恶意爬取或攻击。<br>
    数据来源：标准通 (www.bzton.com)
</div>
"""


def show_footer():
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


# ── 结果展示 ──────────────────────────────────────────
def show_results(sheet_dict: Dict[str, pd.DataFrame], filename_base: str):
    """展示搜索结果"""
    if not sheet_dict:
        return

    # 合并所有 sheet 用于总览
    all_df = pd.concat(sheet_dict.values(), ignore_index=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-title">📊 检索结果（共 {len(all_df)} 条）</div>',
        unsafe_allow_html=True,
    )

    # ── 筛选 ──
    with st.expander("🔍 筛选结果", expanded=False):
        filter_cols = st.columns(4)
        filters = {}
        for i, col_name in enumerate(["standard_code", "standard_name", "status", "standard_category"]):
            if col_name in all_df.columns and all_df[col_name].nunique() > 1:
                vals = [""] + sorted(all_df[col_name].dropna().unique().tolist())
                filters[col_name] = filter_cols[i % 4].selectbox(
                    FIELD_LABELS.get(col_name, col_name), vals, key=f"filter_{col_name}"
                )

    filtered = all_df.copy()
    for col_name, val in filters.items():
        if val:
            filtered = filtered[filtered[col_name] == val]

    col_left, col_mid, col_right = st.columns([2, 1, 1])
    with col_left:
        st.caption(f"当前筛选后: {len(filtered)} 条")
    now = time.strftime("%Y%m%d_%H%M%S")
    with col_mid:
        # 多 Sheet Excel 下载
        excel_bytes = make_multisheet_excel(sheet_dict)
        st.download_button(
            "📥 下载 Excel",
            excel_bytes,
            f"{filename_base}_{now}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col_right:
        # CSV 下载
        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 下载 CSV",
            csv,
            f"{filename_base}_{now}.csv",
            "text/csv",
        )

    # 显示表格（中文表头）
    display_df = filtered.rename(columns=FIELD_LABELS)
    st.dataframe(display_df, use_container_width=True, height=500)

    with st.expander("📈 统计概览"):
        show_stats(filtered)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  主界面
# ══════════════════════════════════════════════════════

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ── 顶部横幅 ──
st.markdown(
    """
<div class="hero">
    <table width="100%"><tr>
        <td>
            <h1>标准通爬虫</h1>
            <p>标准通 (www.bzton.com) 标准信息批量抓取工具</p>
        </td>
    </tr></table>
</div>
""",
    unsafe_allow_html=True,
)


# ── 搜索区域 ──
st.markdown(
    '<div class="card"><div class="card-title">🔍 标准检索</div>',
    unsafe_allow_html=True,
)

# 关键词输入
keywords_input = st.text_area(
    "搜索关键词（多个关键词用逗号或换行分隔）",
    placeholder="例如：\n人工智能\n机器学习\n深度学习",
    height=120,
    help="每个关键词会分别搜索，然后合并去重结果",
)

st.markdown("<br>", unsafe_allow_html=True)

# 标准类型筛选
STD_TYPE_OPTIONS = {
    "": "全部",
    1100: "国家标准",
    1200: "行业标准",
    1300: "地方标准",
    1400: "团体标准",
    1500: "企业标准",
}

# 搜索参数
col1, col2 = st.columns(2)
with col1:
    page_size = st.number_input(
        "每页条数", min_value=10, max_value=100, value=20, step=10
    )
with col2:
    max_pages = st.number_input(
        "每个关键词最大页数（0=不限）",
        min_value=0, max_value=500, value=0, step=1,
        help="限制每个关键词的抓取页数以节省时间",
    )

st.markdown("<br>", unsafe_allow_html=True)

# 筛选条件
filter_cols = st.columns(3)
with filter_cols[0]:
    selected_types = st.multiselect(
        "标准类型（可多选，不选=全部）",
        options=list(STD_TYPE_OPTIONS.keys()),
        format_func=lambda x: STD_TYPE_OPTIONS.get(x, "全部"),
        default=[],
    )
with filter_cols[1]:
    selected_stages = st.multiselect(
        "标准阶段（可多选，不选=全部）",
        options=list(STD_STAGE_MAP.keys()),
        format_func=lambda x: STD_STAGE_MAP.get(x, x),
        default=[],
    )
with filter_cols[2]:
    selected_states = st.multiselect(
        "实施状态（可多选，不选=全部）",
        options=list(STD_STATE_MAP.keys()),
        format_func=lambda x: STD_STATE_MAP.get(x, str(x)),
        default=[],
    )

st.markdown("<br>", unsafe_allow_html=True)

# 搜索按钮
search_clicked = st.button("🚀 开始搜索", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ── 搜索逻辑 ──
if search_clicked:
    if not keywords_input.strip():
        st.warning("请输入至少一个关键词")
        st.stop()

    # 解析关键词
    keywords = []
    for line in keywords_input.strip().split("\n"):
        for kw in line.split(","):
            kw = kw.strip()
            if kw:
                keywords.append(kw)

    if not keywords:
        st.warning("请输入至少一个关键词")
        st.stop()

    # 标准类型过滤
    std_types = [t for t in selected_types if t] if selected_types else None
    std_stages = selected_stages if selected_stages else None
    std_states = selected_states if selected_states else None

    # 进度显示
    progress_bar = st.progress(0, text="准备中...")
    status_text = st.empty()

    def progress_callback(current, total, msg):
        if total > 0:
            progress_bar.progress(current / total, text=msg)
        else:
            status_text.info(msg)

    # 开始抓取
    start_time = time.time()
    results = fetch_multiple_keywords(
        keywords,
        page_size=page_size,
        max_pages=max_pages,
        std_types=std_types,
        std_states=std_states,
        std_stages=std_stages,
        progress_callback=progress_callback,
    )
    elapsed = time.time() - start_time

    # 清除进度显示
    progress_bar.empty()
    status_text.empty()

    if results:
        # 按标准类别分组
        sheet_dict: Dict[str, list] = {}
        for row in results:
            cat = row.get("standard_category", "其他")
            if cat not in sheet_dict:
                sheet_dict[cat] = []
            sheet_dict[cat].append(row)

        # 转为 DataFrame
        sheet_dict = {k: pd.DataFrame(v) for k, v in sheet_dict.items() if v}

        st.session_state.search_results = sheet_dict
        st.session_state.search_summary = f"关键词「{'、'.join(keywords[:3])}」"
        st.session_state.show_results_flag = True

        st.success(f"搜索完成！共获取 {len(results)} 条结果，耗时 {elapsed:.1f} 秒")
    else:
        st.warning("未找到匹配结果，请尝试其他关键词。")


# ── 显示结果 ──
if st.session_state.show_results_flag and st.session_state.search_results is not None:
    show_results(
        st.session_state.search_results,
        st.session_state.search_summary.replace(" ", "_"),
    )
elif st.session_state.search_results is not None and not st.session_state.show_results_flag:
    st.info(
        f"上次搜索结果：{st.session_state.search_summary}，"
        f"共 {sum(len(v) for v in st.session_state.search_results.values())} 条"
    )
    if st.button("📂 显示上次结果"):
        st.session_state.show_results_flag = True
        st.rerun()


# ── 使用说明 ──
with st.expander("📖 使用说明", expanded=False):
    st.markdown("""
    ### 功能特点

    1. **多关键词搜索**：支持同时输入多个关键词，分别搜索后合并去重
    2. **完整信息抓取**：抓取标准的详细信息，包括归口单位、起草单位、起草人等
    3. **多维度筛选**：支持按标准类型、标准阶段、实施状态筛选
    4. **多格式导出**：支持 Excel（按类别分 Sheet）和 CSV 格式

    ### 抓取字段

    | 字段 | 说明 |
    |------|------|
    | 超链接 | 标准详情页链接 |
    | 标准号 | 标准编号或计划号 |
    | 标准名称 | 标准中文名称 |
    | 标准类别 | 国家标准/行业标准/地方标准/团体标准/企业标准 |
    | 标准性质 | 强制性/推荐性/指导性技术文件 |
    | 主管部门 | 发布或批准部门 |
    | 归口单位 | 技术归口单位 |
    | 起草单位 | 主要起草和参与起草单位 |
    | 发布日期 | 标准发布日期 |
    | 实施日期 | 标准实施日期 |
    | 实施状态 | 现行/正在起草/正在批准等 |
    | TC编号 | 技术委员会编号 |
    | 起草人 | 参与起草的个人 |
    | ICS分类号 | 国际标准分类号 |
    | 标准摘要 | 标准内容简介 |
    | 目的和意义 | 立项阶段的目的和意义 |
    | 范围和主要技术内容 | 立项阶段的范围和主要技术内容 |

    ### 注意事项

    - 抓取速度受网络和服务器限制，大量数据需要较长时间
    - 建议先用少量页数测试，确认无误后再全量抓取
    - 请合理使用，避免对服务器造成过大压力
    """)


# ── Footer ──
show_footer()
st.markdown("</div>", unsafe_allow_html=True)
