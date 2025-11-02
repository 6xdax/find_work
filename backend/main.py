from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import asyncio
from crawler import BossCrawler
from analyzer import DataAnalyzer
from database import Database
import os

app = FastAPI(title="Boss直聘爬虫系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
db = Database()
crawler = BossCrawler()
analyzer = DataAnalyzer(db)

# 创建静态文件目录
os.makedirs('static/wordclouds', exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

class CrawlRequest(BaseModel):
    keyword: str  # 岗位关键词
    max_pages: Optional[int] = 5  # 最大爬取页数

class CrawlResponse(BaseModel):
    success: bool
    message: str
    total_count: Optional[int] = None
    job_ids: Optional[List[int]] = None

@app.get("/")
async def root():
    return {"message": "Boss直聘爬虫系统API", "status": "running"}

@app.post("/api/crawl", response_model=CrawlResponse)
async def crawl_jobs(request: CrawlRequest):
    """爬取岗位数据"""
    try:
        # 开始爬取
        jobs = await crawler.crawl(keyword=request.keyword, max_pages=request.max_pages)
        
        if not jobs:
            return CrawlResponse(
                success=False,
                message=f"未找到关键词 '{request.keyword}' 相关的岗位"
            )
        
        # 保存到数据库
        job_ids = []
        for job in jobs:
            job_id = db.save_job(job)
            if job_id:
                job_ids.append(job_id)
        
        return CrawlResponse(
            success=True,
            message=f"成功爬取 {len(job_ids)} 个岗位",
            total_count=len(job_ids),
            job_ids=job_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")

@app.get("/api/stats/{keyword}")
async def get_statistics(keyword: str):
    """获取岗位统计数据"""
    try:
        stats = analyzer.get_statistics(keyword)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")

@app.get("/api/analysis/{keyword}")
async def get_analysis(keyword: str):
    """获取岗位详细分析"""
    try:
        analysis = analyzer.get_detailed_analysis(keyword)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/api/wordcloud/{keyword}")
async def generate_wordcloud(keyword: str):
    """生成词云图"""
    try:
        image_path = analyzer.generate_wordcloud(keyword)
        if os.path.exists(image_path):
            # 返回静态文件路径
            return FileResponse(
                image_path,
                media_type="image/png",
                filename=f"{keyword}_wordcloud.png"
            )
        else:
            raise HTTPException(status_code=404, detail="词云生成失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"词云生成失败: {str(e)}")

@app.get("/api/jobs/{keyword}")
async def get_jobs(keyword: str, limit: int = 100):
    """获取岗位列表"""
    try:
        jobs = db.get_jobs_by_keyword(keyword, limit)
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

