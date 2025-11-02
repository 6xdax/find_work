const API_BASE_URL = 'http://localhost:8000/api';

let currentKeyword = '';

// 显示标签页
function showTab(tabName) {
    // 隐藏所有标签内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // 移除所有按钮的active类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的标签内容
    document.getElementById(tabName + 'Tab').style.display = 'block';
    
    // 添加active类到对应按钮
    event.target.classList.add('active');
}

// 开始爬取
async function startCrawl() {
    const keyword = document.getElementById('keywordInput').value.trim();
    const maxPages = parseInt(document.getElementById('maxPages').value) || 5;
    
    if (!keyword) {
        alert('请输入岗位关键词');
        return;
    }
    
    currentKeyword = keyword;
    
    // 禁用按钮
    const crawlBtn = document.getElementById('crawlBtn');
    crawlBtn.disabled = true;
    crawlBtn.textContent = '爬取中...';
    
    // 显示状态
    const statusSection = document.getElementById('statusSection');
    const statusMessage = document.getElementById('statusMessage');
    const progressBar = document.getElementById('progressBar');
    
    statusSection.style.display = 'block';
    statusMessage.textContent = `正在爬取 "${keyword}" 相关岗位...`;
    progressBar.style.width = '30%';
    
    try {
        const response = await fetch(`${API_BASE_URL}/crawl`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                keyword: keyword,
                max_pages: maxPages
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressBar.style.width = '100%';
            statusMessage.textContent = data.message;
            statusSection.style.background = '#d4edda';
            statusSection.style.borderLeftColor = '#28a745';
            
            // 自动加载统计数据
            setTimeout(() => {
                loadStatistics();
                showTab('statistics');
                document.querySelector('.tab-btn').click();
            }, 1000);
        } else {
            throw new Error(data.message || '爬取失败');
        }
    } catch (error) {
        statusMessage.textContent = `错误: ${error.message}`;
        statusSection.style.background = '#f8d7da';
        statusSection.style.borderLeftColor = '#dc3545';
        console.error('爬取错误:', error);
    } finally {
        crawlBtn.disabled = false;
        crawlBtn.textContent = '开始爬取';
        setTimeout(() => {
            progressBar.style.width = '0%';
        }, 2000);
    }
}

// 加载统计数据
async function loadStatistics() {
    if (!currentKeyword) return;
    
    const content = document.getElementById('statisticsContent');
    content.innerHTML = '<div class="loading">加载中</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/stats/${encodeURIComponent(currentKeyword)}`);
        const data = await response.json();
        
        if (data.total_jobs === 0) {
            content.innerHTML = '<div class="error">暂无数据，请先爬取</div>';
            return;
        }
        
        let html = `
            <div class="stat-card">
                <div class="stat-label">总岗位数</div>
                <div class="stat-value">${data.total_jobs}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">公司数量</div>
                <div class="stat-value">${data.company_count}</div>
            </div>
        `;
        
        if (data.salary_statistics && data.salary_statistics.avg > 0) {
            html += `
                <div class="stat-card">
                    <div class="stat-label">平均薪资</div>
                    <div class="stat-value">${data.salary_statistics.avg}K</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">薪资中位数</div>
                    <div class="stat-value">${data.salary_statistics.median}K</div>
                </div>
            `;
        }
        
        content.innerHTML = html;
        
        // 显示薪资分布
        if (data.salary_statistics && data.salary_statistics.distribution) {
            const distributionHtml = `
                <div class="chart-container">
                    <h3>薪资分布</h3>
                    ${data.salary_statistics.distribution.map(item => `
                        <div style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>${item.range}</span>
                                <span>${item.count}个岗位 (${item.percentage}%)</span>
                            </div>
                            <div style="width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                <div style="width: ${item.percentage}%; height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            content.innerHTML += distributionHtml;
        }
        
        // 显示地区分布
        if (data.area_distribution && data.area_distribution.length > 0) {
            const areaHtml = `
                <div class="chart-container">
                    <h3>地区分布 Top 10</h3>
                    ${data.area_distribution.map(item => `
                        <div style="display: flex; justify-content: space-between; padding: 8px; background: white; margin: 5px 0; border-radius: 5px;">
                            <span>${item.area || '未知'}</span>
                            <span style="font-weight: bold; color: #667eea;">${item.count}</span>
                        </div>
                    `).join('')}
                </div>
            `;
            content.innerHTML += areaHtml;
        }
        
    } catch (error) {
        content.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        console.error('加载统计数据错误:', error);
    }
}

// 加载详细分析
async function loadAnalysis() {
    if (!currentKeyword) return;
    
    const content = document.getElementById('analysisContent');
    content.innerHTML = '<div class="loading">分析中</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/${encodeURIComponent(currentKeyword)}`);
        const data = await response.json();
        
        if (!data.total_jobs || data.total_jobs === 0) {
            content.innerHTML = '<div class="error">暂无数据，请先爬取</div>';
            return;
        }
        
        let html = `
            <div class="analysis-section">
                <div class="analysis-item">
                    <h3>📊 基础信息</h3>
                    <p><strong>关键词:</strong> ${data.keyword}</p>
                    <p><strong>总岗位数:</strong> ${data.total_jobs}</p>
                    <p><strong>分析时间:</strong> ${data.analysis_time || '未知'}</p>
                </div>
        `;
        
        // 关键词
        if (data.top_keywords && data.top_keywords.length > 0) {
            html += `
                <div class="analysis-item">
                    <h3>🔑 热门关键词</h3>
                    ${data.top_keywords.map(item => `
                        <span class="keyword-item">${item.word} (${item.weight.toFixed(2)})</span>
                    `).join('')}
                </div>
            `;
        }
        
        // 技能需求
        if (data.required_skills && data.required_skills.length > 0) {
            html += `
                <div class="analysis-item">
                    <h3>💼 技能需求</h3>
                    ${data.required_skills.map(item => `
                        <span class="skill-item">${item.skill} (${item.count}次)</span>
                    `).join('')}
                </div>
            `;
        }
        
        // 薪资分析
        if (data.salary_range_analysis) {
            const salary = data.salary_range_analysis;
            html += `
                <div class="analysis-item">
                    <h3>💰 薪资分析</h3>
                    <p>平均薪资: <strong>${salary.avg}K</strong></p>
                    <p>薪资范围: <strong>${salary.min}K - ${salary.max}K</strong></p>
                    <p>中位数: <strong>${salary.median}K</strong></p>
                </div>
            `;
        }
        
        html += '</div>';
        content.innerHTML = html;
        
    } catch (error) {
        content.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        console.error('加载分析数据错误:', error);
    }
}

// 加载词云
async function loadWordcloud() {
    if (!currentKeyword) return;
    
    const content = document.getElementById('wordcloudContent');
    content.innerHTML = '<div class="loading">生成词云中</div>';
    
    try {
        const imgUrl = `${API_BASE_URL}/wordcloud/${encodeURIComponent(currentKeyword)}?t=${Date.now()}`;
        content.innerHTML = `
            <div style="text-align: center;">
                <img src="${imgUrl}" alt="词云图" class="wordcloud-img" onerror="this.parentElement.innerHTML='<div class=\\'error\\'>词云生成失败，请确保有数据</div>'">
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        console.error('加载词云错误:', error);
    }
}

// 加载岗位列表
async function loadJobs() {
    if (!currentKeyword) return;
    
    const content = document.getElementById('jobsContent');
    content.innerHTML = '<div class="loading">加载中</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${encodeURIComponent(currentKeyword)}?limit=100`);
        const data = await response.json();
        
        if (!data.jobs || data.jobs.length === 0) {
            content.innerHTML = '<div class="error">暂无数据，请先爬取</div>';
            return;
        }
        
        let html = `
            <div style="margin-bottom: 20px;">
                <h3>共找到 ${data.count} 个岗位</h3>
            </div>
            <div class="job-list">
        `;
        
        data.jobs.forEach(job => {
            html += `
                <div class="job-card">
                    <div class="job-title">${job.title || '未知岗位'}</div>
                    <div class="job-company">${job.company || '未知公司'}</div>
                    <div class="job-info">
                        ${job.salary ? `<span style="color: #e74c3c; font-weight: bold;">💰 ${job.salary}</span>` : ''}
                        ${job.area ? `<span>📍 ${job.area}</span>` : ''}
                        ${job.experience ? `<span>⏰ ${job.experience}</span>` : ''}
                        ${job.education ? `<span>🎓 ${job.education}</span>` : ''}
                    </div>
                    ${job.description ? `<div style="margin-top: 10px; color: #666; font-size: 14px;">${job.description.substring(0, 200)}${job.description.length > 200 ? '...' : ''}</div>` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        content.innerHTML = html;
        
    } catch (error) {
        content.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        console.error('加载岗位列表错误:', error);
    }
}

// 标签页切换时加载对应数据
function showTab(tabName) {
    // 隐藏所有标签内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // 移除所有按钮的active类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的标签内容
    document.getElementById(tabName + 'Tab').style.display = 'block';
    
    // 添加active类到对应按钮
    event.target.classList.add('active');
    
    // 加载对应数据
    if (currentKeyword) {
        switch(tabName) {
            case 'statistics':
                loadStatistics();
                break;
            case 'analysis':
                loadAnalysis();
                break;
            case 'wordcloud':
                loadWordcloud();
                break;
            case 'jobs':
                loadJobs();
                break;
        }
    }
}

// 回车键触发爬取
document.getElementById('keywordInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        startCrawl();
    }
});

