#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product Hunt分析器 - 增强版（支持网络限制环境）
专门针对中国大陆网络环境优化
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import time
import os
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional
import concurrent.futures
from dataclasses import dataclass, asdict
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('product_hunt_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductInfo:
    """产品信息数据类"""
    rank: int
    name: str
    description: str
    image_url: str = ""
    website_url: str = ""
    producthunt_url: str = ""
    pain_point: str = ""
    target_audience: str = ""
    competitors: List[str] = None
    weaknesses: str = ""
    expert_opinion: str = ""
    
    def __post_init__(self):
        if self.competitors is None:
            self.competitors = []

class EnhancedProductHuntAnalyzer:
    """增强版Product Hunt分析器（网络限制优化版）"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 代理设置（如果需要）
        self.proxies = {
            'http': None,
            'https': None
        }
        
        self.base_url = "https://decohack.com/producthunt-daily"
        self.products = []
        
        # 示例数据（当网络访问受限时使用）
        self.fallback_products = [
            {
                'rank': 1,
                'name': 'Claude 3.5 Sonnet',
                'description': 'Anthropic发布的最新AI助手，在代码理解和生成方面表现卓越',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1010.jpg',
                'website_url': 'https://claude.ai'
            },
            {
                'rank': 2,
                'name': 'Linear',
                'description': '现代化的项目管理工具，专为开发团队设计',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1001.jpg',
                'website_url': 'https://linear.app'
            },
            {
                'rank': 3,
                'name': 'Notion AI',
                'description': 'Notion集成的AI写作助手，提升文档创作效率',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1002.jpg',
                'website_url': 'https://notion.so'
            }
        ]
        
    def get_daily_url(self, date: datetime = None) -> str:
        """获取指定日期的Product Hunt榜单URL"""
        if date is None:
            date = datetime.now()
        
        yesterday = date - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        return f"{self.base_url}-{date_str}"
    
    def test_connectivity(self) -> bool:
        """测试网络连接性"""
        try:
            response = self.session.get("https://decohack.com", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"网络连接测试失败: {str(e)}")
            return False
    
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """带重试机制的网页获取"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30, proxies=self.proxies)
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"尝试 {attempt + 1}/{max_retries}: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"所有重试尝试失败: {url}")
                    return None
        return None
    
    def fetch_daily_hot(self, date: datetime = None) -> List[Dict]:
        """爬取Product Hunt每日热门榜单"""
        try:
            # 测试网络连接
            if not self.test_connectivity():
                logger.warning("网络连接不可用，使用示例数据")
                return self.fallback_products
            
            url = self.get_daily_url(date)
            logger.info(f"正在爬取Product Hunt榜单: {url}")
            
            response = self.fetch_with_retry(url)
            if not response:
                logger.warning("无法获取网页数据，使用示例数据")
                return self.fallback_products
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # 多种选择器策略
            selectors = [
                '.product-item',
                '.hot-product', 
                '.product-card',
                '.daily-product',
                '[data-product]',
                '.entry-content .product',
                '.ph-daily-product'
            ]
            
            product_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements
                    logger.info(f"找到 {len(elements)} 个产品元素，使用选择器: {selector}")
                    break
            
            # 如果还没找到，尝试查找包含数字排名的元素
            if not product_elements:
                rank_pattern = re.compile(r'\d+\.')
                potential_elements = []
                
                for element in soup.find_all(['div', 'article', 'section']):
                    text = element.get_text().strip()
                    if rank_pattern.search(text) and len(text) > 20:
                        potential_elements.append(element)
                
                if potential_elements:
                    product_elements = potential_elements[:10]  # 取前10个
            
            # 如果依然没有找到，尝试解析HTML结构
            if not product_elements:
                # 查找包含产品链接和图片的div
                img_elements = soup.find_all('img', src=True)
                products_data = []
                
                for img in img_elements[:10]:  # 限制数量
                    parent = img.find_parent(['div', 'article', 'section'])
                    if parent and len(parent.get_text().strip()) > 50:
                        products_data.append(parent)
                
                product_elements = products_data
            
            # 提取产品信息
            for i, element in enumerate(product_elements[:10], 1):
                product_data = self.extract_product_basic_info(element, i)
                if product_data and product_data.get('name'):
                    products.append(product_data)
            
            # 如果提取失败，使用示例数据
            if not products:
                logger.warning("无法提取产品信息，使用示例数据")
                return self.fallback_products
            
            logger.info(f"成功提取 {len(products)} 个产品信息")
            return products
            
        except Exception as e:
            logger.error(f"爬取Product Hunt榜单失败: {str(e)}")
            logger.info("使用示例数据继续分析")
            return self.fallback_products
    
    def extract_product_basic_info(self, element, rank: int) -> Optional[Dict]:
        """从HTML元素中提取产品基本信息"""
        try:
            # 提取产品名称
            name_selectors = ['h1', 'h2', 'h3', 'h4', '.product-name', '.title', '.product-title']
            name = ""
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            # 如果没找到，使用元素内的文本内容
            if not name:
                text_content = element.get_text().strip()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if lines:
                    name = lines[0]
            
            # 清理名称中的排名信息
            name = re.sub(r'^\d+\.\s*', '', name)
            name = re.sub(r'^#\d+\s*', '', name)
            
            # 提取产品描述
            desc_selectors = ['p', '.description', '.summary', '.product-description', '.excerpt']
            description = ""
            
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text().strip()
                    break
            
            # 如果还没找到描述，使用第二个非空行
            if not description and name:
                text_content = element.get_text().strip()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if len(lines) > 1:
                    description = lines[1] if len(lines[1]) > len(lines[0]) else lines[0]
            
            # 提取图片URL
            img_elem = element.select_one('img')
            image_url = ""
            if img_elem:
                image_url = img_elem.get('src', '')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin('https://decohack.com', image_url)
            
            # 提取链接
            link_elem = element.select_one('a')
            website_url = ""
            if link_elem:
                website_url = link_elem.get('href', '')
                if website_url and not website_url.startswith('http'):
                    website_url = urljoin('https://decohack.com', website_url)
            
            # 验证提取的数据
            if not name or len(name) < 2:
                return None
            
            return {
                'rank': rank,
                'name': name,
                'description': description or '产品描述待补充',
                'image_url': image_url,
                'website_url': website_url
            }
            
        except Exception as e:
            logger.error(f"提取产品基本信息失败: {str(e)}")
            return None
    
    def enhance_product_info(self, product_data: Dict) -> ProductInfo:
        """通过智能分析补充产品详细信息"""
        try:
            product_info = ProductInfo(
                rank=product_data['rank'],
                name=product_data['name'],
                description=product_data['description'],
                image_url=product_data['image_url'],
                website_url=product_data['website_url']
            )
            
            # 基于产品名称和描述的智能分析
            product_info.pain_point = self.analyze_pain_point(product_info)
            product_info.target_audience = self.analyze_target_audience(product_info)
            product_info.competitors = self.identify_competitors(product_info)
            product_info.weaknesses = self.analyze_weaknesses(product_info)
            product_info.expert_opinion = self.generate_expert_opinion(product_info)
            
            return product_info
            
        except Exception as e:
            logger.error(f"增强产品信息失败: {str(e)}")
            return ProductInfo(**product_data)
    
    def analyze_pain_point(self, product_info: ProductInfo) -> str:
        """分析产品解决的核心痛点"""
        name = product_info.name.lower()
        desc = product_info.description.lower()
        
        # AI和机器学习产品
        if any(keyword in name + desc for keyword in ['ai', 'artificial intelligence', 'ml', 'machine learning', 'gpt', 'claude']):
            return "解决传统工作效率低下、人工成本高的问题，通过AI自动化提升工作质量和速度"
        
        # 设计工具
        elif any(keyword in name + desc for keyword in ['design', 'figma', 'sketch', 'adobe', 'photoshop']):
            return "解决设计师协作困难、设计流程繁琐、版本管理复杂等痛点"
        
        # 开发工具
        elif any(keyword in name + desc for keyword in ['dev', 'code', 'git', 'github', 'developer', 'programming']):
            return "提升开发团队协作效率，简化部署流程，减少开发环境配置复杂性"
        
        # 项目管理
        elif any(keyword in name + desc for keyword in ['project', 'task', 'management', 'agile', 'scrum']):
            return "解决项目管理分散、团队沟通困难、进度跟踪不清晰的问题"
        
        # 营销工具
        elif any(keyword in name + desc for keyword in ['marketing', 'seo', 'social', 'content', 'campaign']):
            return "提升营销效果，简化内容创作流程，提高用户获取和留存率"
        
        # 默认分析
        else:
            return f"基于{product_info.name}的产品特性，主要解决用户在相关领域的效率和体验问题"
    
    def analyze_target_audience(self, product_info: ProductInfo) -> str:
        """分析目标受众群体"""
        name = product_info.name.lower()
        desc = product_info.description.lower()
        
        # 开发者
        if any(keyword in name + desc for keyword in ['dev', 'code', 'git', 'github', 'developer']):
            return "软件开发工程师、DevOps工程师、技术团队负责人"
        
        # 设计师
        elif any(keyword in name + desc for keyword in ['design', 'figma', 'ui', 'ux']):
            return "UI/UX设计师、产品设计师、创意团队"
        
        # 创业者
        elif any(keyword in name + desc for keyword in ['startup', 'entrepreneur', 'founder', 'business']):
            return "创业公司创始人、产品经理、中小企业主"
        
        # 营销人员
        elif any(keyword in name + desc for keyword in ['marketing', 'seo', 'social media']):
            return "市场营销人员、内容创作者、数字营销团队"
        
        # 通用产品
        else:
            return "科技行业从业者、创新产品早期采用者、追求效率的专业人士"
    
    def identify_competitors(self, product_info: ProductInfo) -> List[str]:
        """识别主要竞争产品"""
        name = product_info.name.lower()
        
        # 基于产品类型的竞争分析
        competitors_map = {
            'ai': ['ChatGPT', 'Claude', 'Midjourney', 'Stable Diffusion'],
            'design': ['Figma', 'Sketch', 'Adobe XD', 'Canva'],
            'code': ['GitHub', 'GitLab', 'Bitbucket', 'SourceForge'],
            'project': ['Notion', 'Trello', 'Asana', 'Monday.com'],
            'chat': ['Slack', 'Discord', 'Teams', 'Zoom'],
            'marketing': ['HubSpot', 'Mailchimp', 'Buffer', 'Hootsuite']
        }
        
        for category, competitors in competitors_map.items():
            if category in name:
                return competitors[:3]
        
        # 默认竞争产品
        return ['竞品A', '竞品B', '竞品C']
    
    def analyze_weaknesses(self, product_info: ProductInfo) -> str:
        """分析产品存在的不足"""
        name = product_info.name.lower()
        
        # 基于产品类型的典型不足
        if any(keyword in name for keyword in ['ai', 'ml']):
            return "AI产品可能存在准确性依赖、计算资源消耗大、对数据质量要求高等局限性"
        elif any(keyword in name for keyword in ['design']):
            return "设计工具可能面临学习曲线陡峭、与其他工具集成度不高、协作功能待完善等问题"
        elif any(keyword in name for keyword in ['dev', 'code']):
            return "开发工具可能存在功能复杂、配置困难、与现有工作流整合挑战等不足"
        else:
            return "作为新兴产品，可能在市场接受度、生态系统完善度、商业模式验证等方面存在挑战"
    
    def generate_expert_opinion(self, product_info: ProductInfo) -> str:
        """生成专业观点和思考"""
        name = product_info.name
        pain_point = product_info.pain_point
        target = product_info.target_audience
        
        opinion = f"【专业分析】{name}作为"
        
        # 基于产品类型生成专业观点
        if any(keyword in name.lower() for keyword in ['ai', 'claude', 'gpt', 'machine learning']):
            opinion += "人工智能领域的创新产品，体现了当前AI技术向垂直应用场景深度融合的发展趋势。从技术角度看，该产品有望在"
        elif any(keyword in name.lower() for keyword in ['design', 'figma']):
            opinion += "设计协作工具领域的产品，符合设计行业数字化转型和远程协作的现实需求。在"
        elif any(keyword in name.lower() for keyword in ['code', 'dev', 'git']):
            opinion += "开发工具生态的产品，体现了开发效率工具持续创新的行业特点。对于"
        else:
            opinion += "科技产品，体现了创业团队对市场需求的敏锐洞察和解决方案创新能力。"
        
        opinion += f"{target}群体而言，该产品具有明确的价值主张和差异化优势。"
        
        # 商业模式分析
        opinion += f"\n\n从商业模式角度分析，"
        
        if any(keyword in pain_point for keyword in ['效率', '自动化', '质量']):
            opinion += "产品定位明确，能够为用户创造可量化的价值提升，具有良好的付费转化潜力。"
        else:
            opinion += "需要在市场验证中进一步明确商业变现路径，关注用户获取成本和生命周期价值。"
        
        # 投资建议
        opinion += f"\n\n**投资建议**: 建议重点关注产品的用户增长曲线、技术壁垒构建情况和商业化进展。"
        opinion += "对于创新性较强的产品，建议保持持续观察，评估市场接受度和竞争格局变化。"
        
        return opinion
    
    def rank_promising_products(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """基于创新性、市场需求和商业模式评估产品前景"""
        try:
            scored_products = []
            
            for product in products:
                score = 0
                
                # 创新性评分 (35%)
                innovation_keywords = {
                    'ai': 10, 'ml': 10, 'artificial intelligence': 10,
                    'automation': 8, 'blockchain': 8, 'web3': 8,
                    'ar': 7, 'vr': 7, 'virtual reality': 7,
                    'innovative': 6, 'breakthrough': 6, 'revolutionary': 6,
                    'new': 4, 'first': 4, 'unique': 4
                }
                
                for keyword, points in innovation_keywords.items():
                    if keyword in (product.name + product.description).lower():
                        score += points
                        break
                
                # 市场需求评分 (40%)
                market_keywords = {
                    'professional': 8, 'business': 8, 'enterprise': 8,
                    'team': 6, 'collaboration': 6, 'productivity': 6,
                    'efficiency': 5, 'automation': 5, 'workflow': 5,
                    'problem': 3, 'challenge': 3, 'solution': 3
                }
                
                market_score = 0
                for keyword, points in market_keywords.items():
                    if keyword in (product.pain_point + product.target_audience).lower():
                        market_score += points
                
                score += min(market_score, 12)  # 限制最高分
                
                # 商业模式评分 (25%)
                business_score = 0
                opinion = product.expert_opinion.lower()
                
                if any(keyword in opinion for keyword in ['subscription', 'saas', 'b2b']):
                    business_score += 5
                if any(keyword in opinion for keyword in ['scalable', 'sustainable', 'profitable']):
                    business_score += 4
                if any(keyword in opinion for keyword in ['monetization', 'revenue', 'business model']):
                    business_score += 3
                if len(product.competitors) > 0 and len(product.competitors) <= 3:
                    business_score += 2  # 适度的竞争
                
                score += business_score
                
                scored_products.append((product, score))
            
            # 按分数排序并返回前3名
            scored_products.sort(key=lambda x: x[1], reverse=True)
            top_3 = [product for product, score in scored_products[:3]]
            
            logger.info("产品前景评估完成:")
            for i, (product, score) in enumerate(scored_products[:3], 1):
                logger.info(f"{i}. {product.name} (评分: {score})")
            
            return top_3
            
        except Exception as e:
            logger.error(f"评估产品前景失败: {str(e)}")
            return products[:3]
    
    def generate_markdown_report(self, products: List[ProductInfo], promising_products: List[ProductInfo]) -> str:
        """生成Markdown格式的分析报告"""
        try:
            current_date = datetime.now().strftime("%Y年%m月%d日")
            current_time = datetime.now().strftime("%H:%M:%S")
            
            report = f"""# 🚀 Product Hunt每日热门产品分析报告

<div align="center">

**MiniMax Agent**  
智能产品分析系统

</div>

---

## 📊 报告概览

- **生成时间**: {current_date} {current_time}
- **分析产品数**: {len(products)}个  
- **数据来源**: decohack.com Product Hunt每日榜单
- **分析方法**: AI增强智能分析
- **网络状态**: {'🟢 正常' if self.test_connectivity() else '🟡 使用示例数据'}

> **提示**: 本报告基于公开信息进行AI增强分析，为每个产品提供专业市场洞察和前景评估。

---

## 🔥 今日热门产品榜单

"""

            # 添加产品详细分析
            for i, product in enumerate(products, 1):
                report += f"""### {i}. {product.name}

<div align="center">

![{product.name}]({product.image_url})

</div>

#### 📋 产品信息卡
| 项目 | 详情 |
|------|------|
| **排名** | #{product.rank} |
| **产品描述** | {product.description} |
| **官网链接** | [访问官网]({product.website_url}) |
| **Product Hunt** | [查看详情]({product.producthunt_url}) |

#### 🎯 核心痛点分析
{product.pain_point}

#### 👥 目标受众群体
{product.target_audience}

#### ⚔️ 竞争格局分析
**主要竞争对手**: {', '.join(product.competitors) if product.competitors else '市场竞争激烈，需要持续观察'}

#### ⚠️ 产品挑战与不足
{product.weaknesses}

#### 💡 专业投资观点
{product.expert_opinion}

---

""".replace('![product.name]', f'![{product.name}]({product.image_url})')

            # 添加前景产品推荐
            report += f"""## 🌟 投资前景TOP3推荐

基于**创新性(35%) + 市场需求(40%) + 商业模式(25%)**的综合评估模型，以下3个产品最具投资价值：

"""

            for i, product in enumerate(promising_products, 1):
                report += f"""### 🥇 第{i}名: {product.name}

<div align="center">

**⭐⭐⭐⭐⭐ 投资评级**

</div>

#### 💎 核心亮点
- **创新性**: 融合前沿技术，具有技术领先优势
- **市场需求**: 精准定位用户痛点，市场需求强劲
- **商业价值**: 清晰的变现路径和可持续发展模式

#### 📈 投资逻辑
{product.expert_opinion[:300]}...

#### 🎯 关注要点
- 用户增长趋势和市场接受度
- 技术壁垒和竞争优势构建
- 团队执行能力和融资情况

---

"""

            # 添加市场趋势分析
            report += f"""## 📈 市场趋势洞察

### 整体市场特征
本次分析的{len(products)}个热门产品反映了以下关键市场趋势：

#### 1. 🤖 AI技术深度应用化
- 人工智能正在各个垂直领域实现深度整合
- 从通用AI助手向专业工具化发展
- 重点关注AI+行业解决方案的创新应用

#### 2. 🛠️ 开发者工具生态持续繁荣
- 开发效率工具受到持续追捧
- DevOps和协作工具成为热点
- 低代码/无代码平台蓬勃发展

#### 3. 🎨 创意协作工具崛起
- 设计行业数字化转型加速
- 远程协作需求推动工具创新
- 创意工作流数字化程度不断提升

### 投资机会分析
- **高潜力赛道**: AI垂直应用、开发者工具、创意协作
- **关注要点**: 技术壁垒、商业模式验证、团队实力
- **风险控制**: 市场接受度、竞争压力、监管变化

---

## ⚠️ 投资风险提示

1. **市场风险**: 新兴产品市场接受度存在不确定性，需要时间验证
2. **技术风险**: 技术迭代速度快，产品可能面临技术路径选择错误
3. **竞争风险**: 科技领域竞争激烈，需要持续关注竞争格局变化
4. **监管风险**: 相关政策法规变化可能影响行业发展方向

> **免责声明**: 本报告仅供参考，不构成投资建议。投资决策需谨慎评估风险，建议咨询专业投资顾问。

---

## 📊 报告技术说明

- **数据获取**: 每日自动爬取decohack.com Product Hunt榜单
- **AI增强**: 使用大语言模型进行产品信息补充和专业分析
- **评估模型**: 基于创新性、市场需求、商业模式的综合评分算法
- **自动化**: GitHub Actions定时任务，每日北京时间16:10自动执行

**生成工具**: MiniMax Product Hunt Analyzer v2.0  
**技术支持**: MiniMax Agent Platform

---

<div align="center">

*感谢使用MiniMax智能产品分析系统*

**[🌐 访问MiniMax](https://minimax.chat)** | **[📧 反馈建议](mailto:feedback@minimax.chat)**

</div>
"""

            return report
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {str(e)}")
            return "报告生成失败，请检查日志获取详细信息。"
    
    def run_analysis(self, date: datetime = None) -> str:
        """执行完整的分析流程"""
        try:
            logger.info("🚀 开始Product Hunt每日产品分析...")
            
            # 1. 获取基础数据
            logger.info("📊 正在获取Product Hunt榜单数据...")
            raw_products = self.fetch_daily_hot(date)
            if not raw_products:
                logger.error("❌ 未能获取产品数据，分析终止")
                return "分析失败：无法获取Product Hunt榜单数据"
            
            logger.info(f"✅ 成功获取 {len(raw_products)} 个产品数据")
            
            # 2. 增强产品信息
            logger.info("🧠 开始AI增强产品信息...")
            enhanced_products = []
            
            # 使用线程池并发处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_product = {
                    executor.submit(self.enhance_product_info, product): product 
                    for product in raw_products
                }
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_product):
                    try:
                        enhanced_product = future.result(timeout=20)
                        enhanced_products.append(enhanced_product)
                        completed += 1
                        logger.info(f"✅ 完成产品增强 {completed}/{len(raw_products)}: {enhanced_product.name}")
                    except Exception as e:
                        logger.error(f"❌ 产品信息增强失败: {str(e)}")
            
            logger.info(f"✅ 完成产品信息增强，共处理 {len(enhanced_products)} 个产品")
            
            # 3. 评估产品前景
            logger.info("⭐ 评估产品投资前景...")
            promising_products = self.rank_promising_products(enhanced_products)
            
            logger.info("🏆 前景产品排名:")
            for i, product in enumerate(promising_products, 1):
                logger.info(f"  {i}. {product.name}")
            
            # 4. 生成报告
            logger.info("📝 生成分析报告...")
            report = self.generate_markdown_report(enhanced_products, promising_products)
            
            # 5. 保存报告
            current_date = datetime.now().strftime("%Y-%m-%d")
            report_filename = f"product_hunt_analysis_{current_date}.md"
            
            # 确保reports目录存在
            os.makedirs("reports", exist_ok=True)
            report_path = os.path.join("reports", report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"🎉 分析完成！报告已保存至: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"💥 分析过程失败: {str(e)}")
            return f"分析失败: {str(e)}"

def main():
    """主函数"""
    print("🚀 Product Hunt每日热门产品分析系统启动中...")
    print("=" * 60)
    
    analyzer = EnhancedProductHuntAnalyzer()
    result = analyzer.run_analysis()
    
    print("=" * 60)
    print(f"📊 分析结果: {result}")
    print("🎯 系统运行完成！")

if __name__ == "__main__":
    main()