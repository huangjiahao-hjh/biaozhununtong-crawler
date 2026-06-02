#!/usr/bin/env python3
"""
标准通爬虫 - 核心模块
从 www.bzton.com 抓取标准信息
"""

import csv
import re
import sys
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests

# ── 常量配置 ──────────────────────────────────────────
BASE_URL = "https://www.bzton.com"
API_BASE = f"{BASE_URL}/prod-api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/search",
}

# 标准类型映射
STD_TYPE_MAP = {
    1000: "国际标准",
    1100: "国家标准",
    1200: "行业标准",
    1300: "地方标准",
    1400: "团体标准",
    1500: "企业标准",
    3: "法律法规",
    4: "行业动态",
}

# 标准阶段映射
STD_STAGE_MAP = {
    "00": "预研阶段",
    "10": "立项阶段",
    "20": "起草阶段",
    "30": "征求意见阶段",
    "40": "审查阶段",
    "50": "批准阶段",
    "60": "出版阶段",
    "90": "复审阶段",
    "95": "废止阶段",
}

# 标准状态映射
STD_STATE_MAP = {
    6: "即将实施",
    7: "现行",
    8: "废止",
}

# 输出字段名
FIELDNAMES = [
    "keyword",           # 搜索关键词
    "hyperlink",         # 超链接
    "standard_code",     # 标准号
    "standard_name",     # 标准名称
    "standard_category", # 标准类别
    "guikou_unit",       # 归口单位
    "drafting_units",    # 起草单位
    "status",            # 实施状态
    "ics",               # ICS分类号
    "purpose",           # 目的和意义
    "scope",             # 范围和主要技术内容
]

# 中文字段名映射
FIELD_LABELS = {
    "keyword": "关键词",
    "hyperlink": "超链接",
    "standard_code": "标准号",
    "standard_name": "标准名称",
    "standard_category": "标准类别",
    "guikou_unit": "归口单位",
    "drafting_units": "起草单位",
    "status": "实施状态",
    "ics": "ICS分类号",
    "purpose": "目的和意义",
    "scope": "范围和主要技术内容",
}


# ── 网络请求 ──────────────────────────────────────────
def _request(method: str, url: str, max_retries: int = 3, **kwargs) -> Optional[requests.Response]:
    """发送 HTTP 请求，支持自动重试"""
    if "headers" not in kwargs:
        kwargs["headers"] = HEADERS
    for attempt in range(1, max_retries + 1):
        try:
            kwargs.setdefault("timeout", 30)
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < max_retries:
                time.sleep(attempt * 1.5)
            else:
                print(f"请求失败: {e}", file=sys.stderr)
    return None


def _request_json(method: str, url: str, max_retries: int = 3, **kwargs) -> Optional[Dict]:
    """发送请求并返回 JSON 响应"""
    resp = _request(method, url, max_retries=max_retries, **kwargs)
    if resp is None:
        return None
    try:
        return resp.json()
    except Exception:
        return None


# ── 工具函数 ──────────────────────────────────────────
def extract_tc_code(text: str) -> str:
    """从归口单位名称中提取 TC 编号"""
    if not text:
        return ""
    # 匹配 TCxxx 或 TCxxx/SCxxx 格式
    match = re.search(r"TC\d+(?:/SC\d+)?", text, re.I)
    return match.group(0).upper() if match else ""


def parse_std_category(category_str: str) -> Tuple[str, str]:
    """
    解析标准分类字符串，返回 (标准性质, ICS分类号)

    示例输入: "国内标准/国家级标准/GB/T-推荐性国家标准,ICS分类/35.信息技术..."
    """
    if not category_str:
        return "", ""

    std_nature = ""
    ics = ""

    # 提取标准性质
    if "强制性" in category_str:
        std_nature = "强制性"
    elif "推荐性" in category_str:
        std_nature = "推荐性"
    elif "指导性" in category_str:
        std_nature = "指导性技术文件"

    # 提取 ICS 分类号
    ics_match = re.search(r"ICS分类/([^,]+)", category_str)
    if ics_match:
        ics = ics_match.group(1).strip()

    return std_nature, ics


def get_std_type_name(std_type: int) -> str:
    """获取标准类型名称"""
    return STD_TYPE_MAP.get(std_type, "其他")


def build_hyperlink(std_id: int) -> str:
    """构建标准详情页链接"""
    return f"{BASE_URL}/standard/stdReader/{std_id}"


# ── 搜索 API ──────────────────────────────────────────
def search_standards(
    keyword: str,
    page_num: int = 1,
    page_size: int = 10,
    std_types: List[int] = None,
    std_states: List[int] = None,
    std_stages: List[str] = None,
) -> Optional[Dict]:
    """
    搜索标准

    Args:
        keyword: 搜索关键词
        page_num: 页码
        page_size: 每页数量
        std_types: 标准类型过滤
        std_states: 标准状态过滤
        std_stages: 标准阶段过滤

    Returns:
        API 响应数据
    """
    url = f"{API_BASE}/standard/dmsTopic/open/getFullTextPageList"
    payload = {
        "pageNum": page_num,
        "pageSize": page_size,
        "sortField": "release_date",
        "sortWay": "desc",
        "searchRange": "full",
        "stdTypes": std_types or [],
        "stdStates": std_states or [],
        "stdStages": std_stages or [],
        "searchType": None,
        "unitNames": None,
        "personNames": None,
        "searchValue": keyword,
    }
    return _request_json("post", url, json=payload)


def get_search_total(keyword: str, page_size: int = 10) -> int:
    """获取搜索结果总数"""
    data = search_standards(keyword, page_num=1, page_size=page_size)
    if not data or "data" not in data or data["data"] is None:
        return 0
    return data["data"].get("total", 0)


# ── 详情页 API ──────────────────────────────────────────
def get_std_detail(std_id: int) -> Optional[Dict]:
    """获取标准详情"""
    url = f"{API_BASE}/standard/dmsTopic/open/{std_id}"
    return _request_json("get", url)


def get_participate_info(std_id: int, std_stages: List[int] = None) -> Optional[List[Dict]]:
    """
    获取标准参与信息（归口单位、起草单位、起草人等）

    Args:
        std_id: 标准ID
        std_stages: 标准阶段列表，如 [50, 60] 表示批准和现行阶段

    Returns:
        参与信息列表
    """
    url = f"{API_BASE}/standard/dmsParticipate/open/getStdParticipateInfo"
    payload = {
        "stdId": std_id,
        "stdStages": std_stages or [50, 60],
    }
    result = _request_json("post", url, json=payload)
    if not result or "data" not in result or result["data"] is None:
        return []
    return result["data"]


def parse_participate_info(participate_list: List[Dict]) -> Dict[str, str]:
    """
    解析参与信息，提取归口单位、主管部门、起草单位、起草人等

    Returns:
        包含各字段的字典
    """
    result = {
        "charge_dept": "",      # 主管部门
        "guikou_unit": "",      # 归口单位
        "drafting_units": "",   # 起草单位
        "draft_staff": "",      # 起草人
    }

    if not participate_list:
        return result

    charge_depts = []
    guikou_units = []
    drafting_units = []
    draft_staffs = []

    for item in participate_list:
        participate_type = item.get("participateTypeLabel", "")
        participant_type = item.get("participantTypeLabel", "")
        name = item.get("participantName", "")

        if not name:
            continue

        # 归口单位
        if participate_type == "归口" and participant_type == "单位":
            if name not in guikou_units:
                guikou_units.append(name)

        # 主管部门（发布/批准部门）
        if participate_type in ["发布", "批准"] and participant_type == "部门":
            if name not in charge_depts:
                charge_depts.append(name)

        # 主要起草单位
        if participate_type == "主要起草" and participant_type == "单位":
            if name not in drafting_units:
                drafting_units.append(name)

        # 起草单位（非主要）
        if participate_type == "起草" and participant_type == "单位":
            if name not in drafting_units:
                drafting_units.append(name)

        # 起草人
        if participate_type == "起草" and participant_type == "个人":
            if name not in draft_staffs:
                draft_staffs.append(name)

    result["charge_dept"] = "；".join(charge_depts) if charge_depts else ""
    result["guikou_unit"] = "；".join(guikou_units) if guikou_units else ""
    result["drafting_units"] = "；".join(drafting_units) if drafting_units else ""
    result["draft_staff"] = "；".join(draft_staffs) if draft_staffs else ""

    return result


def extract_tc_from_guikou(guikou_unit: str) -> str:
    """从归口单位中提取 TC 编号"""
    return extract_tc_code(guikou_unit)


# ── 阶段信息 API ──────────────────────────────────────────
def get_stage_data(std_uuid: str, std_stage: str = "10") -> Optional[Dict]:
    """
    获取标准阶段信息（立项阶段数据包含目的意义和范围主要技术内容）

    Args:
        std_uuid: 标准UUID
        std_stage: 阶段代码，"10" 表示立项阶段

    Returns:
        阶段数据
    """
    url = f"{API_BASE}/standard/dmsTopic/open/getStageData"
    payload = {
        "stdUuid": std_uuid,
        "stdStage": std_stage,
    }
    return _request_json("post", url, json=payload)


def get_active_stages(std_uuid: str) -> List[str]:
    """
    获取标准有参与数据的活跃阶段列表

    Args:
        std_uuid: 标准UUID

    Returns:
        有参与数据的阶段代码列表，如 ["10", "20"]
    """
    url = f"{API_BASE}/standard/dmsTopic/open/getActiveStageByStdUuid"
    payload = {"stdUuid": std_uuid}
    result = _request_json("post", url, json=payload)

    if not result or "data" not in result or result["data"] is None:
        return []

    # 返回 count > 0 的阶段
    active_stages = []
    for item in result["data"]:
        if item.get("count", 0) > 0:
            active_stages.append(item["stdStage"])
    return active_stages


def get_purpose_and_scope(std_uuid: str) -> Tuple[str, str]:
    """
    获取目的意义和范围主要技术内容

    Args:
        std_uuid: 标准UUID

    Returns:
        (目的意义, 范围和主要技术内容)
    """
    if not std_uuid:
        return "", ""

    data = get_stage_data(std_uuid, "10")  # 立项阶段
    if not data or "data" not in data or data["data"] is None:
        return "", ""

    stage_data = data["data"]
    purpose = stage_data.get("purposeSignificance", "") or ""
    scope = stage_data.get("scopeTechnicalContent", "") or ""

    return purpose, scope


# ── 主要抓取逻辑 ──────────────────────────────────────
def fetch_single_keyword(
    keyword: str,
    page_size: int = 20,
    max_pages: int = 0,
    std_types: List[int] = None,
    std_states: List[int] = None,
    std_stages: List[str] = None,
    progress_callback=None,
) -> List[Dict]:
    """
    抓取单个关键词的所有标准

    Args:
        keyword: 搜索关键词
        page_size: 每页数量
        max_pages: 最大页数，0 表示不限制
        std_types: 标准类型过滤
        std_states: 标准状态过滤
        std_stages: 标准阶段过滤
        progress_callback: 进度回调函数 callback(current, total, message)

    Returns:
        标准信息列表
    """
    results = []
    page_num = 1
    total = 0

    while True:
        # 搜索列表页
        data = search_standards(
            keyword, page_num=page_num, page_size=page_size,
            std_types=std_types, std_states=std_states, std_stages=std_stages
        )

        if not data or "data" not in data or data["data"] is None:
            break

        rows = data["data"].get("rows", [])
        total = data["data"].get("total", 0)

        if not rows:
            break

        # 处理每条标准
        for i, row in enumerate(rows):
            std_id = row.get("stdId")
            if not std_id:
                continue

            # 进度回调
            if progress_callback:
                current = (page_num - 1) * page_size + i + 1
                progress_callback(
                    current, total,
                    f"正在处理 {keyword}... {current}/{total}"
                )

            # 获取目的意义和范围主要技术内容
            std_uuid = row.get("stdUuid", "")
            purpose, scope = get_purpose_and_scope(std_uuid)

            # 获取参与信息（详情页）
            # 先用默认阶段 [50, 60] 查询
            participate_info = get_participate_info(std_id)
            # 如果为空，尝试用活跃阶段查询（适用于立项、起草等早期阶段）
            if not participate_info and std_uuid:
                active_stages = get_active_stages(std_uuid)
                if active_stages:
                    participate_info = get_participate_info(std_id, std_stages=active_stages)
            detail = parse_participate_info(participate_info)

            # 解析标准分类
            std_category_str = row.get("stdCategory", "")
            _, ics = parse_std_category(std_category_str)

            # 构建标准信息
            std_info = {
                "keyword": keyword,
                "hyperlink": build_hyperlink(std_id),
                "standard_code": row.get("stdNo") or row.get("planNo") or "",
                "standard_name": row.get("stdName", ""),
                "standard_category": get_std_type_name(row.get("stdType", 0)),
                "guikou_unit": detail["guikou_unit"],
                "drafting_units": detail["drafting_units"],
                "status": row.get("stdStatus", ""),
                "ics": ics,
                "purpose": purpose,
                "scope": scope,
            }

            results.append(std_info)

            # 请求间隔，避免被限制
            time.sleep(0.5)

        # 检查是否还有下一页
        if max_pages and page_num >= max_pages:
            break
        if page_num * page_size >= total:
            break

        page_num += 1
        time.sleep(1)  # 翻页间隔

    return results


def fetch_multiple_keywords(
    keywords: List[str],
    page_size: int = 20,
    max_pages: int = 0,
    std_types: List[int] = None,
    std_states: List[int] = None,
    std_stages: List[str] = None,
    progress_callback=None,
) -> List[Dict]:
    """
    抓取多个关键词的标准，并合并去重

    Args:
        keywords: 关键词列表
        page_size: 每页数量
        max_pages: 每个关键词的最大页数
        std_types: 标准类型过滤
        std_states: 标准状态过滤
        std_stages: 标准阶段过滤
        progress_callback: 进度回调函数

    Returns:
        去重后的标准信息列表
    """
    all_results = []
    seen_ids = set()  # 用于去重

    for kw_idx, keyword in enumerate(keywords):
        keyword = keyword.strip()
        if not keyword:
            continue

        if progress_callback:
            progress_callback(
                0, 0,
                f"开始搜索关键词 ({kw_idx + 1}/{len(keywords)}): {keyword}"
            )

        # 抓取单个关键词
        def keyword_progress(current, total, msg):
            if progress_callback:
                progress_callback(
                    current, total,
                    f"[{kw_idx + 1}/{len(keywords)}] {msg}"
                )

        results = fetch_single_keyword(
            keyword, page_size=page_size, max_pages=max_pages,
            std_types=std_types, std_states=std_states, std_stages=std_stages,
            progress_callback=keyword_progress,
        )

        # 去重：按标准号去重
        for item in results:
            std_code = item.get("standard_code", "")
            if std_code and std_code not in seen_ids:
                seen_ids.add(std_code)
                all_results.append(item)
            elif not std_code:
                # 没有标准号的直接添加
                all_results.append(item)

        if progress_callback:
            progress_callback(
                0, 0,
                f"关键词 '{keyword}' 完成，获取 {len(results)} 条，累计 {len(all_results)} 条"
            )

    return all_results


# ── CSV/Excel 输出 ──────────────────────────────────────
def write_csv(filename: str, rows: List[Dict[str, str]]) -> None:
    """写入 CSV 文件"""
    if not rows:
        print("没有可保存的数据。", file=sys.stderr)
        return

    with open(filename, mode="w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"已将 {len(rows)} 条结果保存到 {filename}")


def write_excel(filename: str, rows: List[Dict[str, str]]) -> None:
    """写入 Excel 文件，按标准类别分 Sheet"""
    try:
        import pandas as pd
    except ImportError:
        print("需要安装 pandas 和 openpyxl: pip install pandas openpyxl", file=sys.stderr)
        return

    if not rows:
        print("没有可保存的数据。", file=sys.stderr)
        return

    # 按标准类别分组
    grouped = {}
    for row in rows:
        category = row.get("standard_category", "其他")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(row)

    # 写入多 Sheet Excel
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for category, items in grouped.items():
            # Excel sheet name 不能超 31 字符
            safe_name = category[:31]
            df = pd.DataFrame(items)
            # 重命名列为中文
            df = df.rename(columns=FIELD_LABELS)
            df.to_excel(writer, sheet_name=safe_name, index=False)

    print(f"已将 {len(rows)} 条结果保存到 {filename}（共 {len(grouped)} 个 Sheet）")


# ── CLI ──────────────────────────────────────────────
def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="标准通爬虫 - 从 www.bzton.com 抓取标准信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 单个关键词搜索
  python scraper.py --keyword 人工智能 --output results.xlsx

  # 多个关键词搜索（合并去重）
  python scraper.py --keyword 人工智能 --keyword 机器学习 --output results.xlsx

  # 使用关键词文件
  python scraper.py --keywords-file keywords.txt --output results.xlsx

  # 限制抓取页数
  python scraper.py --keyword 人工智能 --max-pages 5 --output results.xlsx
        """
    )

    parser.add_argument("--keyword", action="append", help="搜索关键词，可重复指定多个")
    parser.add_argument("--keywords-file", help="包含多个关键词的文本文件，每行一个")
    parser.add_argument("--output", required=True, help="输出文件路径（.csv 或 .xlsx）")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--max-pages", type=int, default=0, help="每个关键词最大页数，0 表示不限制")

    args = parser.parse_args()

    # 收集关键词
    keywords = []
    if args.keyword:
        keywords.extend(args.keyword)
    if args.keywords_file:
        with open(args.keywords_file, encoding="utf-8") as f:
            keywords.extend([line.strip() for line in f if line.strip()])

    if not keywords:
        parser.error("请提供至少一个关键词（--keyword 或 --keywords-file）")

    # 进度回调
    def progress(current, total, msg):
        if total > 0:
            print(f"\r{msg} ({current}/{total})", end="", flush=True)
        else:
            print(f"\r{msg}", end="", flush=True)

    print(f"开始抓取，关键词: {keywords}")
    print(f"每页数量: {args.page_size}, 最大页数: {args.max_pages or '不限制'}")
    print("-" * 50)

    # 抓取数据
    results = fetch_multiple_keywords(
        keywords,
        page_size=args.page_size,
        max_pages=args.max_pages,
        progress_callback=progress,
    )

    print()  # 换行
    print("-" * 50)
    print(f"抓取完成，共 {len(results)} 条结果")

    # 输出文件
    if args.output.endswith(".xlsx"):
        write_excel(args.output, results)
    else:
        write_csv(args.output, results)


if __name__ == "__main__":
    main()
