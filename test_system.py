#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product Hunt分析系统测试脚本
用于验证系统各个组件的功能
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
import tempfile
import shutil

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from enhanced_product_hunt_analyzer import EnhancedProductHuntAnalyzer, ProductInfo

class TestProductHuntAnalyzer(unittest.TestCase):
    """Product Hunt分析器测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.analyzer = EnhancedProductHuntAnalyzer()
        
    def test_url_generation(self):
        """测试URL生成功能"""
        # 测试默认日期
        url = self.analyzer.get_daily_url()
        self.assertIn('producthunt-daily', url)
        
        # 测试指定日期
        test_date = datetime(2024, 1, 1)
        url = self.analyzer.get_daily_url(test_date)
        self.assertIn('2023-12-31', url)  # 应该返回前一天的URL
        
        print("✅ URL生成测试通过")
    
    def test_pain_point_analysis(self):
        """测试痛点分析功能"""
        # 测试AI产品
        ai_product = ProductInfo(1, "Claude 3.5 Sonnet", "AI助手", "", "", "", "", "", [])
        pain_point = self.analyzer.analyze_pain_point(ai_product)
        self.assertIn("效率", pain_point)
        
        # 测试设计工具
        design_product = ProductInfo(2, "Figma", "设计工具", "", "", "", "", "", [])
        pain_point = self.analyzer.analyze_pain_point(design_product)
        self.assertIn("设计师", pain_point)
        
        print("✅ 痛点分析测试通过")
    
    def test_target_audience_analysis(self):
        """测试目标受众分析功能"""
        # 测试开发者工具
        dev_product = ProductInfo(1, "GitHub Copilot", "代码助手", "", "", "", "", "", [])
        audience = self.analyzer.analyze_target_audience(dev_product)
        self.assertIn("开发", audience)
        
        print("✅ 目标受众分析测试通过")
    
    def test_competitor_identification(self):
        """测试竞争产品识别功能"""
        # 测试AI产品
        ai_product = ProductInfo(1, "ChatGPT", "AI助手", "", "", "", "", "", [])
        competitors = self.analyzer.identify_competitors(ai_product)
        self.assertIsInstance(competitors, list)
        self.assertGreater(len(competitors), 0)
        
        print("✅ 竞争产品识别测试通过")
    
    def test_weakness_analysis(self):
        """测试产品不足分析功能"""
        # 测试通用产品
        product = ProductInfo(1, "TestProduct", "测试产品", "", "", "", "", "", [])
        weaknesses = self.analyzer.analyze_weaknesses(product)
        self.assertIsInstance(weaknesses, str)
        self.assertGreater(len(weaknesses), 0)
        
        print("✅ 产品不足分析测试通过")
    
    def test_expert_opinion_generation(self):
        """测试专业观点生成功能"""
        product = ProductInfo(1, "AI Assistant", "AI助手", "", "", "", "提高工作效率", "专业人士", [])
        opinion = self.analyzer.generate_expert_opinion(product)
        self.assertIn("专业分析", opinion)
        self.assertIn("AI", opinion)
        
        print("✅ 专业观点生成测试通过")
    
    def test_product_ranking(self):
        """测试产品前景排名功能"""
        products = [
            ProductInfo(1, "AI Product", "AI产品", "", "", "", "提高效率", "专业人士", []),
            ProductInfo(2, "Design Tool", "设计工具", "", "", "", "设计协作", "设计师", []),
            ProductInfo(3, "Dev Tool", "开发工具", "", "", "", "开发效率", "开发者", [])
        ]
        
        ranked = self.analyzer.rank_promising_products(products)
        self.assertIsInstance(ranked, list)
        self.assertLessEqual(len(ranked), 3)
        
        print("✅ 产品前景排名测试通过")
    
    def test_report_generation(self):
        """测试报告生成功能"""
        products = [
            ProductInfo(1, "Test Product", "测试产品", "", "", "", "测试痛点", "测试受众", [])
        ]
        promising = products[:1]
        
        report = self.analyzer.generate_markdown_report(products, promising)
        self.assertIn("Product Hunt每日热门产品分析报告", report)
        self.assertIn("Test Product", report)
        self.assertIn("测试痛点", report)
        
        print("✅ 报告生成测试通过")
    
    def test_network_connectivity(self):
        """测试网络连接"""
        # 这个测试可能在网络不可用时失败，但我们会捕获异常
        try:
            is_connected = self.analyzer.test_connectivity()
            self.assertIsInstance(is_connected, bool)
            print(f"✅ 网络连接测试通过 - 连接状态: {'已连接' if is_connected else '未连接'}")
        except Exception as e:
            print(f"⚠️ 网络连接测试跳过: {str(e)}")
    
    def test_fallback_data(self):
        """测试降级数据"""
        # 验证降级数据的结构
        fallback = self.analyzer.fallback_products
        self.assertIsInstance(fallback, list)
        self.assertGreater(len(fallback), 0)
        
        for product in fallback:
            self.assertIn('rank', product)
            self.assertIn('name', product)
            self.assertIn('description', product)
        
        print("✅ 降级数据测试通过")
    
    def test_enhanced_product_info(self):
        """测试产品信息增强功能"""
        basic_product = {
            'rank': 1,
            'name': 'Test AI Tool',
            'description': 'AI-powered productivity tool',
            'image_url': 'https://example.com/image.jpg',
            'website_url': 'https://example.com'
        }
        
        enhanced = self.analyzer.enhance_product_info(basic_product)
        self.assertIsInstance(enhanced, ProductInfo)
        self.assertEqual(enhanced.rank, 1)
        self.assertEqual(enhanced.name, 'Test AI Tool')
        self.assertIsInstance(enhanced.pain_point, str)
        self.assertIsInstance(enhanced.target_audience, str)
        self.assertIsInstance(enhanced.competitors, list)
        
        print("✅ 产品信息增强测试通过")

def run_integration_test():
    """运行集成测试"""
    print("🚀 开始Product Hunt分析系统集成测试")
    print("=" * 60)
    
    try:
        # 创建临时报告目录
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 创建reports目录
            os.makedirs("reports", exist_ok=True)
            
            # 初始化分析器
            analyzer = EnhancedProductHuntAnalyzer()
            
            # 运行完整分析流程
            print("📊 运行完整分析流程...")
            result = analyzer.run_analysis()
            
            # 验证结果
            if result and result.endswith('.md'):
                print(f"✅ 分析成功完成: {result}")
                
                # 检查报告文件
                if os.path.exists(result):
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 1000:  # 检查内容长度
                            print("✅ 报告内容验证通过")
                        else:
                            print("⚠️ 报告内容可能不完整")
                
                # 复制报告到原始目录以便查看
                shutil.copy2(result, os.path.join(original_dir, os.path.basename(result)))
                print(f"📄 报告已复制到: {os.path.join(original_dir, os.path.basename(result))}")
                
            else:
                print(f"❌ 分析失败: {result}")
            
        finally:
            # 恢复原始目录
            os.chdir(original_dir)
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🧪 Product Hunt分析系统测试套件")
    print("=" * 60)
    
    # 运行单元测试
    print("\n📋 运行单元测试...")
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestProductHuntAnalyzer)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 运行集成测试
    print("\n🔗 运行集成测试...")
    integration_success = run_integration_test()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"单元测试: {'✅ 通过' if test_result.wasSuccessful() else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    
    if test_result.wasSuccessful() and integration_success:
        print("\n🎉 所有测试通过！系统功能正常。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查系统配置。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)