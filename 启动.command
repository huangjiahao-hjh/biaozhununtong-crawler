#!/bin/bash
cd "$(dirname "$0")"
echo "正在启动标准通爬虫..."
echo ""

# 检查 Python 版本
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "错误：未找到 Python3，请先安装 Python 3.8+"
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip3 install -q -r requirements.txt 2>/dev/null

# 启动应用
echo "启动 Web 界面..."
echo "浏览器将自动打开，如果没有请手动访问 http://localhost:8501"
echo ""
streamlit run app.py --server.headless true
