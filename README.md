# 标准通爬虫

从 [标准通](https://www.bzton.com) 批量抓取标准信息的工具，支持多关键词搜索、合并去重、多维度筛选和多格式导出。

## 功能特点

- 🔍 **多关键词搜索**：支持同时输入多个关键词，分别搜索后合并去重
- 📊 **完整信息抓取**：抓取标准的详细信息，包括归口单位、起草单位、目的意义、范围主要技术内容等
- 🎯 **多维度筛选**：支持按标准类型、标准阶段、实施状态筛选
- 📥 **多格式导出**：支持 Excel（按类别分 Sheet）和 CSV 格式
- 🖥️ **Web 界面**：基于 Streamlit 的可视化操作界面

## 抓取字段

| 字段 | 说明 |
|------|------|
| 超链接 | 标准详情页链接 |
| 标准号 | 标准编号或计划号 |
| 标准名称 | 标准中文名称 |
| 标准类别 | 国家标准/行业标准/地方标准/团体标准/企业标准 |
| 归口单位 | 技术归口单位 |
| 起草单位 | 主要起草和参与起草单位 |
| 实施状态 | 现行/正在起草/正在批准等 |
| ICS分类号 | 国际标准分类号 |
| 目的和意义 | 标准制定的目的和意义 |
| 范围和主要技术内容 | 标准范围和主要技术内容 |

## 快速启动

### 方法一：Web 界面（推荐）

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动应用：
```bash
streamlit run app.py
```

3. 浏览器会自动打开，输入关键词开始搜索

### 方法二：命令行

```bash
# 单个关键词搜索
python scraper.py --keyword 人工智能 --output results.xlsx

# 多个关键词搜索（合并去重）
python scraper.py --keyword 人工智能 --keyword 机器学习 --output results.xlsx

# 使用关键词文件
python scraper.py --keywords-file keywords.txt --output results.xlsx

# 限制抓取页数
python scraper.py --keyword 人工智能 --max-pages 5 --output results.xlsx
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keyword` | 搜索关键词，可重复指定多个 | - |
| `--keywords-file` | 包含多个关键词的文本文件，每行一个 | - |
| `--output` | 输出文件路径（.csv 或 .xlsx） | 必填 |
| `--page-size` | 每页数量 | 20 |
| `--max-pages` | 每个关键词最大页数，0 表示不限制 | 0 |

## 输出格式

### Excel 输出

- 按标准类别自动分 Sheet（国家标准、行业标准、地方标准等）
- 列名为中文

### CSV 输出

- 合并所有类别为一个文件
- 使用 UTF-8 BOM 编码，Excel 可直接打开

## 多关键词去重

当输入多个关键词时，系统会：
1. 分别搜索每个关键词
2. 合并所有结果
3. 按标准号去重（保留最完整的那条）

这样可以避免：
- 标准通网站对多关键词同时搜索的限制
- 重复的结果

## 注意事项

- 抓取速度受网络和服务器限制，大量数据需要较长时间
- 建议先用少量页数测试，确认无误后再全量抓取
- 请合理使用，避免对服务器造成过大压力
- 默认请求间隔为 0.5 秒，可自行调整

## 项目结构

```
标准通爬虫/
├── app.py              # Streamlit Web 界面
├── scraper.py          # 核心爬虫逻辑
├── requirements.txt    # 依赖包
├── README.md           # 项目说明
└── 启动.command        # macOS 启动脚本
└── 启动.bat            # Windows 启动脚本
```

## 技术栈

- Python 3.8+
- requests - HTTP 请求
- pandas - 数据处理
- openpyxl - Excel 读写
- streamlit - Web 界面

## 桌面版使用说明

### macOS 用户

首次运行可能会提示"已损坏，无法打开"或"来自未知开发者"，请按以下步骤操作：

1. 解压下载的 ZIP 文件
2. 打开终端，进入解压后的文件夹
3. 执行以下命令移除隔离属性：
   ```bash
   xattr -cr .
   ```
4. 双击 `bzton-crawler` 运行

或者：
- 打开 **系统偏好设置 > 安全性与隐私 > 通用**
- 点击 **"仍要打开"**

### Windows 用户

1. 解压下载的 ZIP 文件
2. 双击 `bzton-crawler.exe` 运行
3. 如果 Windows Defender 提示警告，点击 **"更多信息" > "仍要运行"**

## License

MIT
