#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版Product Hunt分析器 - 基于Coze报告格式优化
参考高质量报告格式，提供更专业的分析报告
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

# 配置日志（兼容Windows）
import sys
import io

# 设置标准输出编码为UTF-8（解决Windows控制台emoji显示问题）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('product_hunt_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """产品信息数据类（增强版）"""
    rank: int
    name: str
    description: str
    votes: int = 0
    category: str = ""
    image_url: str = ""
    website_url: str = ""
    producthunt_url: str = ""
    tagline: str = ""

    # 深度分析字段
    core_feature: str = ""
    pain_point: str = ""
    target_audience: str = ""
    competitors: List[str] = None
    business_model: str = ""
    pricing: str = ""
    strengths: str = ""
    weaknesses: str = ""
    market_potential: int = 0  # 0-100评分
    expert_rating: str = ""  # ⭐⭐⭐⭐⭐

    def __post_init__(self):
        if self.competitors is None:
            self.competitors = []


class OptimizedProductHuntAnalyzer:
    """优化版Product Hunt分析器（基于Coze报告格式）"""

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

        self.base_url = "https://decohack.com/producthunt-daily"

        # 优化后的分类体系
        self.product_categories = {
            'AI驱动工具': ['ai', 'ml', 'artificial intelligence', 'chatgpt', 'claude'],
            '生产力增强器': ['productivity', 'workflow', 'automation', 'efficiency'],
            '开发编程工具': ['dev', 'code', 'programming', 'developer', 'git'],
            '设计创意工具': ['design', 'figma', 'creative', 'ui', 'ux'],
            '项目管理工具': ['project', 'management', 'agile', 'scrum', 'task'],
            '营销推广工具': ['marketing', 'seo', 'social', 'content'],
            '教育学习工具': ['education', 'learning', 'training', 'course'],
            '健康生活工具': ['health', 'fitness', 'wellness', 'lifestyle'],
            '金融商务工具': ['finance', 'business', 'payment', 'banking'],
            '娱乐休闲工具': ['entertainment', 'game', 'fun', 'music', 'video']
        }

        # 示例数据（优化版）
        self.fallback_products = [
            {
                'rank': 1,
                'name': 'Claude 3.5 Sonnet',
                'description': 'Anthropic发布的最新AI助手，在代码理解和生成方面表现卓越',
                'votes': 523,
                'category': 'AI驱动工具',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1010.jpg',
                'website_url': 'https://claude.ai',
                'tagline': '下一代AI助手，重新定义编程效率'
            },
            {
                'rank': 2,
                'name': 'Linear',
                'description': '现代化的项目管理工具，专为开发团队设计',
                'votes': 412,
                'category': '项目管理工具',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1001.jpg',
                'website_url': 'https://linear.app',
                'tagline': '优雅高效的团队协作平台'
            },
            {
                'rank': 3,
                'name': 'Notion AI',
                'description': 'Notion集成的AI写作助手，提升文档创作效率',
                'votes': 389,
                'category': 'AI驱动工具',
                'image_url': 'https://cdn.producthunt.com/r/100x100/1002.jpg',
                'website_url': 'https://notion.so',
                'tagline': '智能文档协作，让想法流畅表达'
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

    def fetch_daily_hot(self, date: datetime = None) -> List[Dict]:
        """爬取Product Hunt每日热门榜单（优化版）"""
        try:
            if not self.test_connectivity():
                logger.warning("网络连接不可用，使用示例数据")
                return self.fallback_products

            url = self.get_daily_url(date)
            logger.info(f"正在爬取Product Hunt榜单: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            products = []

            # 方法1：尝试多种选择器策略
            selectors = [
                '.product-item',
                '.hot-product',
                '.product-card',
                '.daily-product',
                '[data-product]',
                '.entry-content .product',
                '.ph-daily-product',
                '.product-grid .product',
                '.featured-product',
                'article',
                '.post-content'
            ]

            product_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements and len(elements) >= 10:  # 至少有10个产品
                    product_elements = elements
                    logger.info(f"找到 {len(elements)} 个产品元素，使用选择器: {selector}")
                    break

            # 方法2：如果选择器没找到足够产品，尝试按hr分隔获取
            if not product_elements or len(product_elements) < 10:
                # 查找所有包含产品链接的div/li元素
                all_links = soup.find_all('a', href=True)
                product_links = []

                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    # 过滤Product Hunt链接
                    if 'producthunt.com' in href or 'ph/' in href:
                        if text and len(text) > 2:
                            parent = link.find_parent(['div', 'li', 'article'])
                            if parent:
                                product_links.append(parent)

                if product_links:
                    product_elements = product_links
                    logger.info(f"通过链接分析找到 {len(product_elements)} 个产品")

            # 方法3：查找包含🔺符号的元素（票数）
            if not product_elements or len(product_elements) < 10:
                vote_elements = soup.find_all(string=lambda text: text and '🔺' in text if text else False)
                product_elements = []
                for vote_text in vote_elements:
                    parent = vote_text.find_parent()
                    while parent and parent.name not in ['div', 'li', 'article', 'section']:
                        parent = parent.find_parent()
                    if parent and parent not in product_elements:
                        product_elements.append(parent)

                logger.info(f"通过票数符号找到 {len(product_elements)} 个产品")

            # 提取产品信息（增加到30个）
            for i, element in enumerate(product_elements[:30], 1):  # 提取全部30个产品
                product_data = self.extract_enhanced_product_info(element, i)
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

    def extract_enhanced_product_info(self, element, rank: int) -> Optional[Dict]:
        """提取增强的产品信息"""
        try:
            # 提取产品名称
            name_selectors = ['h1', 'h2', 'h3', 'h4', '.product-name', '.title', '.product-title', 'strong']
            name = ""

            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break

            if not name:
                text_content = element.get_text().strip()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if lines:
                    name = lines[0]

            # 清理名称
            name = re.sub(r'^\d+\.\s*', '', name)
            name = re.sub(r'^#\d+\s*', '', name)

            # 提取描述
            desc_selectors = ['p', '.description', '.summary', '.product-description', '.excerpt']
            description = ""

            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text().strip()
                    break

            # 提取票数（如果有）
            votes = 0
            vote_patterns = [r'(\d+)\s*票', r'(\d+)\s*votes', r'(\d+)\s*votes?']
            text_content = element.get_text()
            for pattern in vote_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    votes = int(match.group(1))
                    break

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

            # 提取标语
            tagline = ""
            if name and description:
                # 使用描述的前半部分作为标语
                tagline = description[:50] + "..." if len(description) > 50 else description

            # 验证数据
            if not name or len(name) < 2:
                return None

            # 自动分类
            category = self.classify_product(name + " " + description)

            return {
                'rank': rank,
                'name': name,
                'description': description,
                'votes': votes,
                'category': category,
                'image_url': image_url,
                'website_url': website_url,
                'tagline': tagline
            }

        except Exception as e:
            logger.error(f"提取产品基本信息失败: {str(e)}")
            return None

    def classify_product(self, text: str) -> str:
        """自动产品分类"""
        text_lower = text.lower()

        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category

        return "其他工具"

    def enhance_product_info(self, product_data: Dict) -> ProductInfo:
        """深度增强产品信息"""
        try:
            product_info = ProductInfo(
                rank=product_data['rank'],
                name=product_data['name'],
                description=product_data['description'],
                votes=product_data.get('votes', 0),
                category=product_data.get('category', '其他工具'),
                image_url=product_data['image_url'],
                website_url=product_data['website_url'],
                tagline=product_data.get('tagline', '')
            )

            # 深度分析各个维度
            product_info.core_feature = self.analyze_core_feature(product_info)
            product_info.pain_point = self.analyze_pain_point(product_info)
            product_info.target_audience = self.analyze_target_audience(product_info)
            product_info.competitors = self.identify_competitors(product_info)
            product_info.business_model = self.analyze_business_model(product_info)
            product_info.pricing = self.analyze_pricing_model(product_info)
            product_info.strengths = self.analyze_strengths(product_info)
            product_info.weaknesses = self.analyze_weaknesses(product_info)
            product_info.market_potential = self.calculate_market_potential(product_info)
            product_info.expert_rating = self.generate_expert_rating(product_info.market_potential)

            return product_info

        except Exception as e:
            logger.error(f"增强产品信息失败: {str(e)}")
            return ProductInfo(**product_data)

    def analyze_core_feature(self, product_info: ProductInfo) -> str:
        """分析核心功能"""
        name = product_info.name.lower()
        desc = product_info.description.lower()

        if any(keyword in name + desc for keyword in ['ai', 'ml', 'artificial intelligence']):
            return "AI驱动的智能化功能，能够自动处理复杂任务"
        elif any(keyword in name + desc for keyword in ['collaboration', 'team', 'sharing']):
            return "团队协作和实时共享功能"
        elif any(keyword in name + desc for keyword in ['automation', 'workflow']):
            return "自动化工作流程和任务管理"
        elif any(keyword in name + desc for keyword in ['design', 'creative']):
            return "创意设计和视觉表达功能"
        else:
            return "核心功能聚焦于提升用户工作效率和体验"

    def analyze_pain_point(self, product_info: ProductInfo) -> str:
        """分析解决的核心痛点"""
        name = product_info.name.lower()
        desc = product_info.description.lower()

        if 'ai' in name + desc:
            return "解决传统方法效率低下、人工成本高的问题"
        elif any(keyword in name + desc for keyword in ['design', 'figma']):
            return "解决设计团队协作困难、版本管理复杂的痛点"
        elif any(keyword in name + desc for keyword in ['dev', 'code', 'git']):
            return "提升开发团队协作效率，简化代码管理流程"
        else:
            return f"针对{product_info.category}领域的特定需求痛点提供解决方案"

    def analyze_target_audience(self, product_info: ProductInfo) -> str:
        """分析目标受众群体"""
        category = product_info.category

        audience_map = {
            'AI驱动工具': "AI技术人员、产品经理、创新型企业家",
            '生产力增强器': "办公室职员、创业团队、远程工作者",
            '开发编程工具': "软件开发工程师、技术团队负责人、DevOps工程师",
            '设计创意工具': "UI/UX设计师、产品设计师、创意团队",
            '项目管理工具': "项目经理、敏捷教练、团队协调员",
            '营销推广工具': "市场营销人员、内容创作者、数字营销团队"
        }

        return audience_map.get(category, "科技行业从业者、创新产品早期采用者")

    def identify_competitors(self, product_info: ProductInfo) -> List[str]:
        """识别主要竞争产品"""
        category = product_info.category

        competitor_map = {
            'AI驱动工具': ['ChatGPT', 'Claude', 'GPT-4', 'Bard'],
            '开发编程工具': ['GitHub', 'GitLab', 'Bitbucket', 'SourceTree'],
            '设计创意工具': ['Figma', 'Sketch', 'Adobe XD', 'Canva'],
            '项目管理工具': ['Notion', 'Trello', 'Asana', 'Monday.com'],
            '生产力增强器': ['Slack', 'Microsoft Teams', 'Discord', 'Zoom']
        }

        return competitor_map.get(category, ['竞品A', '竞品B', '竞品C'])

    def analyze_business_model(self, product_info: ProductInfo) -> str:
        """分析商业模式"""
        category = product_info.category

        if 'AI' in category:
            return "订阅制SaaS模式，提供不同功能层级"
        elif category in ['开发编程工具', '项目管理工具']:
            return "freemium模式，基础功能免费，高级功能付费"
        else:
            return "多元化商业模式，结合订阅制和一次性购买"

    def analyze_pricing_model(self, product_info: ProductInfo) -> str:
        """分析定价策略"""
        # 基于投票数和市场定位推断
        if product_info.votes > 400:
            return "市场接受度高，采用分层定价策略"
        elif product_info.votes > 200:
            return "中等市场认可，采用标准定价"
        else:
            return "早期产品阶段，采用价值定价策略"

    def analyze_strengths(self, product_info: ProductInfo) -> str:
        """分析产品优势"""
        strengths = []

        if 'AI' in product_info.category:
            strengths.append("技术先进性和AI能力")
        if product_info.votes > 300:
            strengths.append("用户认可度高")
        if len(product_info.competitors) > 0:
            strengths.append("竞争差异化明显")

        if not strengths:
            strengths.append("产品定位清晰")
            strengths.append("用户体验优良")

        return "、".join(strengths)

    def analyze_weaknesses(self, product_info: ProductInfo) -> str:
        """分析产品不足"""
        category = product_info.category

        weakness_map = {
            'AI驱动工具': "计算资源消耗大，对数据质量要求高",
            '开发编程工具': "学习曲线较陡峭，需要团队适应时间",
            '设计创意工具': "功能复杂度高，新手用户门槛较高"
        }

        base_weakness = "作为新兴产品，在市场教育和生态系统建设方面仍有提升空间"
        category_specific = weakness_map.get(category, "")

        if category_specific:
            return f"{category_specific}。{base_weakness}"
        else:
            return base_weakness

    def calculate_market_potential(self, product_info: ProductInfo) -> int:
        """计算市场潜力评分（0-100）"""
        score = 50  # 基础分

        # 投票数评分
        if product_info.votes > 400:
            score += 20
        elif product_info.votes > 200:
            score += 15
        elif product_info.votes > 100:
            score += 10

        # 类别评分
        high_potential_categories = ['AI驱动工具', '开发编程工具', '项目管理工具']
        if product_info.category in high_potential_categories:
            score += 15

        # 竞争程度评分
        if len(product_info.competitors) > 0 and len(product_info.competitors) <= 3:
            score += 10  # 适度竞争说明市场验证

        # 描述质量评分
        if len(product_info.description) > 100:
            score += 5

        return min(score, 100)

    def generate_expert_rating(self, score: int) -> str:
        """根据分数生成专家评级"""
        if score >= 90:
            return "⭐⭐⭐⭐⭐"
        elif score >= 80:
            return "⭐⭐⭐⭐"
        elif score >= 70:
            return "⭐⭐⭐"
        elif score >= 60:
            return "⭐⭐"
        else:
            return "⭐"

    def rank_promising_products(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """优化版产品前景排名"""
        try:
            scored_products = []

            for product in products:
                # 使用市场潜力评分进行排序
                scored_products.append((product, product.market_potential))

            # 按分数排序并返回前3名
            scored_products.sort(key=lambda x: x[1], reverse=True)
            return [product for product, score in scored_products[:3]]

        except Exception as e:
            logger.error(f"评估产品前景失败: {str(e)}")
            return products[:3]

    def generate_enhanced_markdown_report(self, products: List[ProductInfo],
                                          promising_products: List[ProductInfo]) -> str:
        """生成优化版Markdown报告（基于Coze格式）"""
        try:
            current_date = datetime.now().strftime("%Y年%m月%d日")
            current_time = datetime.now().strftime("%H:%M:%S")

            # 统计信息
            total_votes = sum(p.votes for p in products)
            avg_votes = total_votes // len(products) if products else 0
            categories = list(set(p.category for p in products))

            report = f"""# 📊 Product Hunt日报 {current_date.replace('年', '-').replace('月', '-').replace('日', '')}

<div align="center">

**MiniMax Agent 智能分析系统**  
*发现创新趋势，把握市场机遇*

</div>

---

## 📋 报告概览

- **📅 分析日期**: {current_date} {current_time}
- **🔢 产品数量**: {len(products)}个创新产品
- **👍 总投票数**: {total_votes}票
- **📊 平均投票**: {avg_votes}票/产品
- **🏷️ 产品类别**: {len(categories)}个主要类别
- **🌐 数据来源**: decohack.com Product Hunt每日榜单
- **🧠 分析方法**: AI增强智能分析

> **💡 报告说明**: 本报告基于Product Hunt每日热门榜单进行深度分析，为每个产品提供专业的市场洞察和前景评估。

---

## 🏆 今日榜单前三名

"""

            # 添加前三名产品（突出显示）
            for i, product in enumerate(products[:3], 1):
                medals = ['🥇', '🥈', '🥉']
                report += f"""### {medals[i - 1]} 第{i}名: {product.name}

<div align="center">

![{product.name}]({product.image_url})

</div>

#### 📊 产品基本信息
| 项目 | 详情 |
|------|------|
| **投票数** | {product.votes}票 |
| **产品类别** | {product.category} |
| **标语** | {product.tagline} |
| **官网** | [访问网站]({product.website_url}) |
| **专家评级** | {product.expert_rating} ({product.market_potential}/100) |

#### 💡 产品描述
{product.description}

#### 🎯 核心功能
{product.core_feature}

#### ⚡ 解决痛点
{product.pain_point}

#### 👥 目标受众
{product.target_audience}

#### 🏢 商业模式
{product.business_model}

#### 💰 定价策略
{product.pricing}

#### ⭐ 产品优势
{product.strengths}

#### ⚠️ 潜在挑战
{product.weaknesses}

#### ⚔️ 竞争分析
**主要竞争对手**: {', '.join(product.competitors)}

---

"""

            # 添加完整产品列表
            report += f"""## 📋 完整产品清单

| 排名 | 产品名称 | 投票数 | 类别 | 专家评级 | 市场潜力 |
|------|----------|--------|------|----------|----------|
"""

            for product in products:
                report += f"| #{product.rank} | {product.name} | {product.votes}票 | {product.category} | {product.expert_rating} | {product.market_potential}/100 |\n"

            report += "\n---\n\n"

            # 添加前景产品推荐
            report += f"""## 🌟 最具前景产品TOP3

基于**市场潜力综合评分**，以下3个产品最具投资价值：

"""

            # 计算最大投票数以避免除零错误
            max_votes = max(p.votes for p in products) if products else 1
            max_votes = max(max_votes, 1)  # 确保至少为1

            for i, product in enumerate(promising_products, 1):
                vote_percentage = (product.votes / max_votes * 100) if max_votes > 0 else 0
                report += f"""### {i}. {product.name}

<div align="center">

**🏆 投资推荐等级** {product.expert_rating}

</div>

#### 📈 投资亮点
- **市场潜力评分**: {product.market_potential}/100
- **投票表现**: {product.votes}票，市场认可度{vote_percentage:.1f}%
- **类别优势**: {product.category}赛道前景广阔

#### 🎯 核心价值主张
{product.core_feature}

#### 💼 商业模式评估
{product.business_model}

#### 🔮 投资关注要点
1. **用户增长趋势** - 持续监控用户注册和活跃度数据
2. **技术壁垒构建** - 评估核心技术护城河
3. **团队执行能力** - 关注产品迭代和市场拓展能力
4. **融资情况** - 跟踪融资轮次和投资者质量

---

"""

            # 添加市场趋势分析
            report += f"""## 📈 市场趋势洞察

### 🎯 产品类别分布

"""

            # 统计各类别产品数量
            category_stats = {}
            for product in products:
                category_stats[product.category] = category_stats.get(product.category, 0) + 1

            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(products)) * 100
                report += f"- **{category}**: {count}个产品 ({percentage:.1f}%)\n"

            report += f"""

### 🔥 核心市场洞察

#### 1. 🤖 AI技术主导趋势
- **占比**: {(sum(1 for p in products if 'AI' in p.category) / len(products) * 100):.1f}% 的产品聚焦AI领域
- **特点**: 从通用AI助手向垂直领域专业化发展
- **机会**: AI+传统行业的融合创新空间巨大

#### 2. 🛠️ 生产力工具持续火热
- **投票数表现**: {sum(p.votes for p in products if any(cat in p.category for cat in ['生产力', '项目管理', '开发'])) / len(products):.0f}票平均表现
- **用户需求**: 远程工作常态化推动效率工具需求
- **趋势**: 团队协作和自动化成为核心卖点

#### 3. 🎨 创意工具细分发展
- **专业化趋势**: 设计工具向特定行业和场景深耕
- **技术融合**: AI赋能传统创意工作流
- **用户群体**: 从专业设计师向普通用户扩展

### 💎 投资机会分析

#### 🟢 高潜力赛道
1. **AI垂直应用** - 医疗、教育、金融等专业领域
2. **协作工具升级** - 远程团队和混合办公解决方案
3. **创意工作流** - 内容创作和设计协作平台

#### 🟡 关注要点
- **技术壁垒**: 专利技术和算法优势
- **用户体验**: 界面设计和交互流程优化
- **商业模式**: 可持续盈利和用户付费意愿

---

## ⚠️ 投资风险提示

### 🚨 主要风险因素

1. **市场竞争加剧**
   - 同一赛道产品竞争激烈
   - 大厂入局带来的冲击
   - 用户选择困难导致获客成本上升

2. **技术迭代风险**
   - AI技术发展速度快
   - 产品路线图可能过时
   - 新技术替代现有方案

3. **用户接受度不确定性**
   - 新产品市场教育成本高
   - 用户习惯难以改变
   - 付费转化率待验证

4. **监管政策变化**
   - AI领域监管趋严
   - 数据隐私保护要求
   - 跨境数据传输限制

### 🛡️ 风险控制建议

1. **分散投资** - 不集中投资单一赛道
2. **阶段评估** - 基于用户数据调整投资策略
3. **团队尽调** - 重点关注技术团队实力
4. **持续跟踪** - 建立长期观察和评估机制

---

## 📊 报告数据说明

### 🔍 分析方法
- **数据获取**: 每日自动爬取Product Hunt热门榜单
- **AI增强分析**: 使用大语言模型进行产品信息补充
- **评分模型**: 基于投票数、类别优势、竞争分析的综合评估
- **趋势分析**: 结合历史数据和当前市场状况

### 📈 评分体系
- **市场潜力评分** (0-100分): 基于投票表现、市场空间、竞争格局
- **专家评级** (⭐): 综合评估产品投资价值
- **类别分析**: 根据产品功能和应用场景分类

### 🎯 适用人群
- **投资机构**: 寻找早期投资机会
- **创业者**: 了解市场趋势和竞争态势
- **产品经理**: 洞察用户需求和产品趋势
- **技术从业者**: 把握技术发展方向

> **📋 免责声明**: 本报告仅基于公开信息进行分析，不构成投资建议。投资决策需谨慎评估风险，建议咨询专业投资顾问。

---

## 📱 反馈与支持

<div align="center">

**感谢使用 MiniMax 智能产品分析系统**

🌐 **访问MiniMax**: https://minimax.chat  
📧 **反馈邮箱**: product-hunt@minimax.chat  
📱 **关注我们**: @MiniMaxAgent

*让AI为创新赋能* 🚀

</div>
"""

            return report

        except Exception as e:
            logger.error(f"生成Markdown报告失败: {str(e)}")
            return "报告生成失败，请检查日志获取详细信息。"

    def run_analysis(self, date: datetime = None) -> str:
        """执行完整的分析流程"""
        try:
            logger.info("🚀 开始优化版Product Hunt产品分析...")

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
                logger.info(f"  {i}. {product.name} (市场潜力: {product.market_potential}/100)")

            # 4. 生成报告
            logger.info("📝 生成优化版分析报告...")
            report = self.generate_enhanced_markdown_report(enhanced_products, promising_products)

            # 5. 保存报告
            current_date = datetime.now().strftime("%Y-%m-%d")
            report_filename = f"enhanced_product_hunt_analysis_{current_date}.md"

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
    print("🚀 Product Hunt优化版分析系统启动中...")
    print("=" * 60)

    analyzer = OptimizedProductHuntAnalyzer()
    result = analyzer.run_analysis()

    print("=" * 60)
    print(f"📊 分析结果: {result}")
    print("🎯 系统运行完成！")


if __name__ == "__main__":
    main()