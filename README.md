# Boss直聘岗位爬虫分析系统

一个基于FastAPI的Boss直聘岗位数据爬取、分析和可视化系统。

## 功能特点

- 🔍 **岗位爬取**: 输入岗位关键词，自动爬取Boss直聘相关岗位数据
- 📊 **数据分析**: 统计岗位数量、薪资分布、地区分布、经验要求等
- 📈 **详细分析**: 关键词提取、技能需求分析、薪资范围分析
- ☁️ **词云生成**: 自动生成岗位关键词词云图
- 💼 **岗位列表**: 查看所有爬取的岗位详细信息

## 技术栈

- **后端**: FastAPI
- **数据库**: SQLite
- **爬虫**: requests + BeautifulSoup
- **数据分析**: pandas + numpy
- **分词**: jieba
- **词云**: wordcloud + matplotlib
- **前端**: HTML + CSS + JavaScript

## 安装步骤

### 1. 克隆或下载项目

```bash
cd /mnt/d/work/boss
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 安装中文字体（用于词云）

如果系统没有中文字体，需要下载并配置：

**Linux/WSL:**
```bash
# 下载字体文件（可选）
wget https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf
sudo mkdir -p /usr/share/fonts/truetype/simhei
sudo mv SimHei.ttf /usr/share/fonts/truetype/simhei/
sudo fc-cache -fv
```

或者在 `analyzer.py` 中修改字体路径为系统已有字体。

### 4. 启动后端服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 5. 打开前端页面

在浏览器中打开 `frontend/index.html`，或者使用HTTP服务器：

```bash
# 使用Python内置服务器
cd frontend
python -m http.server 8080
```

然后在浏览器访问 `http://localhost:8080`

## 使用方法

1. **输入岗位关键词**: 在搜索框中输入要爬取的岗位关键词，如 "Python开发"、"数据分析"、"AI算法" 等
2. **设置爬取页数**: 设置要爬取的页数（默认5页）
3. **开始爬取**: 点击"开始爬取"按钮，系统将自动爬取数据
4. **查看结果**: 
   - **数据统计**: 查看岗位总数、公司数量、薪资分布等基础统计
   - **详细分析**: 查看关键词、技能需求、薪资分析等详细信息
   - **词云分析**: 查看自动生成的词云图
   - **岗位列表**: 浏览所有爬取的岗位详情

## API接口

### 爬取岗位
```
POST /api/crawl
Body: {
    "keyword": "Python开发",
    "max_pages": 5
}
```

### 获取统计信息
```
GET /api/stats/{keyword}
```

### 获取详细分析
```
GET /api/analysis/{keyword}
```

### 生成词云
```
GET /api/wordcloud/{keyword}
```

### 获取岗位列表
```
GET /api/jobs/{keyword}?limit=100
```

## 数据存储

所有爬取的岗位数据存储在 `backend/boss_jobs.db` SQLite数据库中。

## 注意事项

1. **反爬虫**: Boss直聘有反爬虫机制，建议：
   - 控制爬取频率，避免过于频繁
   - 使用合理的User-Agent
   - 可能需要登录或使用代理（根据实际情况调整）

2. **页面结构**: Boss直聘的页面结构可能随时变化，如果爬取失败，需要更新 `crawler.py` 中的选择器。

3. **字体问题**: 如果词云中文显示为方块，需要确保系统安装了中文字体，并在 `analyzer.py` 中正确配置字体路径。

4. **API限制**: 如果Boss直聘有API接口，建议直接调用API而不是爬取HTML页面。

## 项目结构

```
boss/
├── backend/
│   ├── main.py          # FastAPI主程序
│   ├── crawler.py       # 爬虫模块
│   ├── database.py      # 数据库操作
│   └── analyzer.py      # 数据分析模块
├── frontend/
│   ├── index.html       # 前端页面
│   ├── style.css        # 样式文件
│   └── app.js           # 前端逻辑
├── requirements.txt      # Python依赖
└── README.md            # 项目说明
```

## 开发建议

1. 根据实际需求调整爬取策略和频率
2. 完善错误处理和重试机制
3. 添加数据导出功能（Excel/CSV）
4. 增加更多数据分析维度
5. 优化前端界面和交互体验

## 许可证

本项目仅供学习和研究使用，请遵守Boss直聘的使用条款和robots.txt规定。

