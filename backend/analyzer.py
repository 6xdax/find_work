import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import numpy as np
from typing import Dict, List
from database import Database
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class DataAnalyzer:
    """数据分析类"""
    
    def __init__(self, db: Database):
        self.db = db
        # 初始化jieba
        jieba.initialize()
        # 添加IT行业常用词
        self._add_tech_keywords()
    
    def _add_tech_keywords(self):
        """添加技术关键词以提高分词准确性"""
        tech_words = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
            'Spring', 'Django', 'Flask', 'FastAPI', 'MySQL', 'Redis',
            'Docker', 'K8s', 'Kubernetes', 'AWS', '阿里云', '腾讯云',
            '机器学习', '深度学习', '神经网络', 'AI', '人工智能',
            '数据分析', '数据挖掘', '大数据', 'Hadoop', 'Spark',
            '前端开发', '后端开发', '全栈开发', '算法工程师', '数据工程师'
        ]
        for word in tech_words:
            jieba.add_word(word)
    
    def get_statistics(self, keyword: str) -> Dict:
        """获取基础统计信息"""
        jobs = self.db.get_all_jobs(keyword)
        
        if not jobs:
            return {
                "total_jobs": 0,
                "message": "暂无数据"
            }
        
        # 基础统计
        total_jobs = len(jobs)
        companies = set([job.get('company', '') for job in jobs if job.get('company')])
        
        # 薪资分析
        salary_stats = self._analyze_salary(jobs)
        
        # 地区分布
        area_dist = self._analyze_area(jobs)
        
        # 经验要求分布
        exp_dist = self._analyze_experience(jobs)
        
        # 学历要求分布
        edu_dist = self._analyze_education(jobs)
        
        return {
            "total_jobs": total_jobs,
            "company_count": len(companies),
            "salary_statistics": salary_stats,
            "area_distribution": area_dist,
            "experience_distribution": exp_dist,
            "education_distribution": edu_dist
        }
    
    def get_detailed_analysis(self, keyword: str) -> Dict:
        """获取详细分析"""
        jobs = self.db.get_all_jobs(keyword)
        
        if not jobs:
            return {"message": "暂无数据"}
        
        # 合并所有描述文本
        all_text = " ".join([
            f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}"
            for job in jobs
        ])
        
        # 关键词提取
        keywords = self._extract_keywords(all_text)
        
        # 技能需求分析
        skills = self._analyze_skills(all_text)
        
        # 薪资范围分析
        salary_range = self._analyze_salary_range(jobs)
        
        # 岗位趋势分析
        trends = self._analyze_trends(jobs)
        
        return {
            "keyword": keyword,
            "total_jobs": len(jobs),
            "top_keywords": keywords,
            "required_skills": skills,
            "salary_range_analysis": salary_range,
            "trends": trends,
            "analysis_time": str(jobs[0].get('crawl_time', '')) if jobs else ""
        }
    
    def generate_wordcloud(self, keyword: str) -> str:
        """生成词云图"""
        jobs = self.db.get_all_jobs(keyword)
        
        if not jobs:
            raise ValueError("没有数据可以生成词云")
        
        # 合并文本
        text = " ".join([
            f"{job.get('title', '')} {job.get('description', '')}"
            for job in jobs
        ])
        
        # 使用jieba分词
        words = jieba.cut(text)
        words_text = " ".join(words)
        
        # 过滤停用词和短词
        stopwords = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '或', '等', '在', '有', '为', '可', '能', '要', '会', '可以', '这个', '那个', '一个'}
        filtered_words = [w for w in words if len(w) > 1 and w not in stopwords and not w.isdigit()]
        words_text = " ".join(filtered_words)
        
        # 尝试使用不同的字体路径
        font_paths = [
            '/usr/share/fonts/truetype/simhei/SimHei.ttf',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
            'simhei.ttf'
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        # 生成词云
        wordcloud_config = {
            'width': 800,
            'height': 400,
            'background_color': 'white',
            'max_words': 200,
            'relative_scaling': 0.5,
            'colormap': 'viridis'
        }
        
        if font_path:
            wordcloud_config['font_path'] = font_path
        
        wordcloud = WordCloud(**wordcloud_config).generate(words_text)
        
        # 保存图片
        os.makedirs('static/wordclouds', exist_ok=True)
        image_path = f'static/wordclouds/{keyword}_wordcloud.png'
        
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'{keyword} 岗位词云分析', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(image_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return image_path
    
    def _analyze_salary(self, jobs: List[Dict]) -> Dict:
        """分析薪资分布"""
        salaries = []
        for job in jobs:
            salary = job.get('salary', '')
            if salary and salary != '面议':
                # 提取薪资数字
                numbers = re.findall(r'\d+', salary)
                if numbers:
                    try:
                        if 'K' in salary.upper() or 'k' in salary:
                            # 处理如 15K-30K 的格式
                            if len(numbers) >= 2:
                                min_sal = int(numbers[0])
                                max_sal = int(numbers[1])
                                salaries.append((min_sal + max_sal) / 2)
                            elif len(numbers) == 1:
                                salaries.append(int(numbers[0]))
                        elif '万' in salary:
                            # 处理万元格式
                            if len(numbers) >= 2:
                                min_sal = int(numbers[0]) * 10
                                max_sal = int(numbers[1]) * 10
                                salaries.append((min_sal + max_sal) / 2)
                            elif len(numbers) == 1:
                                salaries.append(int(numbers[0]) * 10)
                    except:
                        pass
        
        if not salaries:
            return {"avg": 0, "min": 0, "max": 0, "distribution": []}
        
        return {
            "avg": round(np.mean(salaries), 2),
            "min": int(min(salaries)),
            "max": int(max(salaries)),
            "median": int(np.median(salaries)),
            "distribution": self._salary_range_distribution(salaries)
        }
    
    def _salary_range_distribution(self, salaries: List[float]) -> List[Dict]:
        """薪资区间分布"""
        ranges = [
            (0, 10, "0-10K"),
            (10, 15, "10-15K"),
            (15, 20, "15-20K"),
            (20, 25, "20-25K"),
            (25, 30, "25-30K"),
            (30, 40, "30-40K"),
            (40, 50, "40-50K"),
            (50, float('inf'), "50K+")
        ]
        
        distribution = []
        for min_sal, max_sal, label in ranges:
            count = sum(1 for s in salaries if min_sal <= s < max_sal)
            if count > 0:
                distribution.append({"range": label, "count": count, "percentage": round(count/len(salaries)*100, 2)})
        
        return distribution
    
    def _analyze_area(self, jobs: List[Dict]) -> List[Dict]:
        """分析地区分布"""
        areas = [job.get('area', '') for job in jobs if job.get('area')]
        area_counter = Counter(areas)
        
        return [
            {"area": area, "count": count}
            for area, count in area_counter.most_common(10)
        ]
    
    def _analyze_experience(self, jobs: List[Dict]) -> List[Dict]:
        """分析经验要求分布"""
        experiences = [job.get('experience', '不限') for job in jobs]
        exp_counter = Counter(experiences)
        
        return [
            {"experience": exp, "count": count}
            for exp, count in exp_counter.most_common()
        ]
    
    def _analyze_education(self, jobs: List[Dict]) -> List[Dict]:
        """分析学历要求分布"""
        educations = [job.get('education', '不限') for job in jobs]
        edu_counter = Counter(educations)
        
        return [
            {"education": edu, "count": count}
            for edu, count in edu_counter.most_common()
        ]
    
    def _extract_keywords(self, text: str, top_k: int = 20) -> List[Dict]:
        """提取关键词"""
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        
        return [
            {"word": word, "weight": round(weight, 4)}
            for word, weight in keywords
        ]
    
    def _analyze_skills(self, text: str) -> List[Dict]:
        """分析技能需求"""
        # 常见技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'C++', 'C#',
            'React', 'Vue', 'Angular', 'Node.js', 'Spring', 'Django', 'Flask',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux',
            'TensorFlow', 'PyTorch', '机器学习', '深度学习', '数据分析'
        ]
        
        skill_count = {}
        text_lower = text.lower()
        
        for skill in skill_keywords:
            count = text_lower.count(skill.lower())
            if count > 0:
                skill_count[skill] = count
        
        sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"skill": skill, "count": count, "demand_rate": round(count/len(text)*100, 2)}
            for skill, count in sorted_skills[:15]
        ]
    
    def _analyze_salary_range(self, jobs: List[Dict]) -> Dict:
        """分析薪资范围"""
        return self._analyze_salary(jobs)
    
    def _analyze_trends(self, jobs: List[Dict]) -> Dict:
        """分析趋势（基于爬取时间）"""
        # 简单的趋势分析，可以基于时间分布
        return {
            "latest_crawl": jobs[0].get('crawl_time', '') if jobs else '',
            "job_count_by_date": "需要时间序列数据"
        }

