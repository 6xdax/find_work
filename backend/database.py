import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: str = "boss_jobs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建岗位表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT,
                salary TEXT,
                area TEXT,
                experience TEXT,
                education TEXT,
                description TEXT,
                keyword TEXT,
                crawl_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON jobs(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON jobs(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_time ON jobs(crawl_time)')
        
        conn.commit()
        conn.close()
    
    def save_job(self, job: Dict) -> Optional[int]:
        """保存岗位数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs (title, company, salary, area, experience, education, description, keyword, crawl_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get('title', ''),
                job.get('company', ''),
                job.get('salary', ''),
                job.get('area', ''),
                job.get('experience', ''),
                job.get('education', ''),
                job.get('description', ''),
                job.get('keyword', ''),
                job.get('crawl_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            return job_id
        except Exception as e:
            print(f"保存岗位数据出错: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def get_jobs_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict]:
        """根据关键词查询岗位"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM jobs 
                WHERE keyword LIKE ? 
                ORDER BY crawl_time DESC 
                LIMIT ?
            ''', (f'%{keyword}%', limit))
            
            rows = cursor.fetchall()
            jobs = [dict(row) for row in rows]
            return jobs
        except Exception as e:
            print(f"查询岗位数据出错: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_all_jobs(self, keyword: Optional[str] = None) -> List[Dict]:
        """获取所有岗位或指定关键词的岗位"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if keyword:
                cursor.execute('SELECT * FROM jobs WHERE keyword LIKE ? ORDER BY crawl_time DESC', (f'%{keyword}%',))
            else:
                cursor.execute('SELECT * FROM jobs ORDER BY crawl_time DESC')
            
            rows = cursor.fetchall()
            jobs = [dict(row) for row in rows]
            return jobs
        except Exception as e:
            print(f"查询岗位数据出错: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_statistics(self, keyword: str) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 总岗位数
            cursor.execute('SELECT COUNT(*) FROM jobs WHERE keyword LIKE ?', (f'%{keyword}%',))
            total_count = cursor.fetchone()[0]
            
            # 公司数量
            cursor.execute('SELECT COUNT(DISTINCT company) FROM jobs WHERE keyword LIKE ?', (f'%{keyword}%',))
            company_count = cursor.fetchone()[0]
            
            # 薪资分布
            cursor.execute('''
                SELECT salary, COUNT(*) as count 
                FROM jobs 
                WHERE keyword LIKE ? AND salary != '' AND salary != '面议'
                GROUP BY salary 
                ORDER BY count DESC 
                LIMIT 10
            ''', (f'%{keyword}%',))
            salary_dist = [{'salary': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_count': total_count,
                'company_count': company_count,
                'salary_distribution': salary_dist
            }
        except Exception as e:
            print(f"获取统计信息出错: {str(e)}")
            return {}
        finally:
            conn.close()

