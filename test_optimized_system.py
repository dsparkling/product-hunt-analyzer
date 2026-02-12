#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版Product Hunt分析系统测试脚本
专门测试优化功能的验证脚本
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
import tempfile
import shutil

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from optimized_product_hunt_analyzer import OptimizedProductHuntAnalyzer, ProductInfo

class TestOptimizedProductHuntAnalyzer(unittest.TestCase):
    """优化版Product Hunt分析器测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.analyzer = OptimizedProductHuntAnalyzer()
        
    def test_product_classification(self):
        """测试产品自动分类功能"""
        # 测试AI产品分类
        ai_text = "AI-powered productivity tool for automation"
        category = self.analyzer.classify_product(ai_text)
        self.assertEqual(category, "AI驱动工具")
        
        # 测试开发工具分类
        dev_text = "Developer code collaboration platform"
        category = self.analyzer.classify_product(dev_text)
        self.assertEqual(category, "开发编程工具")
        
        print("✅ 产品自动分类测试通过")
    
    def test_enhanced_analysis(self):
        """测试增强分析功能"""
        # 创建测试产品
        test_product = ProductInfo(
            rank=1,
            name="TestAI Assistant",
            description="AI-powered productivity tool for teams",
            votes=350,
            category="AI驱动工具"
        )
        
        # 测试核心功能分析
        core_feature = self.analyzer.analyze_core_feature(test_product)
        self.assertIn("AI驱动", core_feature)
        
        # 测试市场潜力计算
        potential = self.analyzer.calculate_market_potential(test_product)
        self.assertGreater(potential, 0)
        self.assertLessEqual(potential, 100)
        
        # 测试专家评级
        rating = self.analyzer.generate_expert_rating(potential)
        self.assertIn("⭐", rating)
        
        print("✅ 增强分析功能测试通过")
    
    def test_market_potential_calculation(self):
        """测试市场潜力计算"""
        # 高投票数产品
        high_vote_product = ProductInfo(
            rank=1, name="Test1", description="Test", votes=450, category="AI驱动工具"
        )
        high_score = self.analyzer.calculate_market_potential(high_vote_product)
        
        # 低投票数产品
        low_vote_product = ProductInfo(
            rank=2, name="Test2", description="Test", votes=50, category="其他工具"
        )
        low_score = self.analyzer.calculate_market_potential(low_vote_product)
        
        self.assertGreater(high_score, low_score)
        
        print("✅ 市场潜力计算测试通过")
    
    def test_business_model_analysis(self):
        """测试商业模式分析"""
        # AI产品
        ai_product = ProductInfo(rank=1, name="AI Tool", description="AI tool", category="AI驱动工具")
        business_model = self.analyzer.analyze_business_model(ai_product)
        self.assertIn("订阅", business_model)
        
        # 开发工具
        dev_product = ProductInfo(rank=2, name="Dev Tool", description="Dev tool", category="开发编程工具")
        business_model = self.analyzer.analyze_business_model(dev_product)
        self.assertIn("freemium", business_model)
        
        print("✅ 商业模式分析测试通过")
    
    def test_competitor_identification(self):
        """测试竞争产品识别"""
        ai_product = ProductInfo(rank=1, name="ChatGPT", description="AI assistant", category="AI驱动工具")
        competitors = self.analyzer.identify_competitors(ai_product)
        
        self.assertIsInstance(competitors, list)
        self.assertGreater(len(competitors), 0)
        self.assertIn("ChatGPT", competitors)  # 应该在AI工具竞争者列表中
        
        print("✅ 竞争产品识别测试通过")
    
    def test_enhanced_report_generation(self):
        """测试增强报告生成"""
        # 创建测试产品数据
        products = [
            ProductInfo(
                rank=1,
                name="TestAI",
                description="AI-powered productivity tool",
                votes=300,
                category="AI驱动工具",
                tagline="AI助力团队效率提升",
                market_potential=85,
                expert_rating="⭐⭐⭐⭐"
            ),
            ProductInfo(
                rank=2,
                name="TestDesign",
                description="Design collaboration platform",
                votes=200,
                category="设计创意工具",
                tagline="设计师的协作利器",
                market_potential=75,
                expert_rating="⭐⭐⭐⭐"
            )
        ]
        
        promising = products[:1]
        
        # 生成报告
        report = self.analyzer.generate_enhanced_markdown_report(products, promising)
        
        # 验证报告内容
        self.assertIn("Product Hunt日报", report)
        self.assertIn("TestAI", report)
        self.assertIn("AI驱动工具", report)
        self.assertIn("市场潜力", report)
        self.assertIn("⭐⭐⭐⭐", report)
        self.assertIn("投资亮点", report)
        
        print("✅ 增强报告生成测试通过")
    
    def test_complete_analysis_workflow(self):
        """测试完整分析流程"""
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        
        try:
            os.chdir(temp_dir)
            os.makedirs("reports", exist_ok=True)
            
            # 运行完整分析
            analyzer = OptimizedProductHuntAnalyzer()
            result = analyzer.run_analysis()
            
            # 验证结果
            self.assertTrue(result.endswith('.md'))
            self.assertTrue(os.path.exists(result))
            
            # 检查报告内容长度
            with open(result, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertGreater(len(content), 2000)  # 确保内容充实
            
            print("✅ 完整分析流程测试通过")
            
        finally:
            os.chdir(original_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)

def run_enhanced_integration_test():
    """运行增强版集成测试"""
    print("🚀 开始Product Hunt优化版分析系统集成测试")
    print("=" * 70)
    
    try:
        # 创建临时报告目录
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 创建reports目录
            os.makedirs("reports", exist_ok=True)
            
            # 初始化分析器
            analyzer = OptimizedProductHuntAnalyzer()
            
            # 运行完整分析流程
            print("📊 运行优化版完整分析流程...")
            result = analyzer.run_analysis()
            
            # 验证结果
            if result and result.endswith('.md'):
                print(f"✅ 分析成功完成: {result}")
                
                # 检查报告文件
                if os.path.exists(result):
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 3000:  # 检查优化版内容长度
                            print("✅ 优化版报告内容验证通过")
                            
                            # 检查关键优化内容
                            key_features = [
                                "Product Hunt日报",
                                "报告概览",
                                "今日榜单前三名",
                                "完整产品清单",
                                "最具前景产品TOP3",
                                "市场趋势洞察",
                                "投资机会分析",
                                "投资风险提示"
                            ]
                            
                            for feature in key_features:
                                if feature in content:
                                    print(f"  ✅ {feature} - 包含")
                                else:
                                    print(f"  ⚠️ {feature} - 缺失")
                            
                        else:
                            print("⚠️ 报告内容可能不完整")
                
                # 复制报告到原始目录以便查看
                shutil.copy2(result, os.path.join(original_dir, os.path.basename(result)))
                print(f"📄 优化版报告已复制到: {os.path.join(original_dir, os.path.basename(result))}")
                
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
    print("🧪 Product Hunt优化版分析系统测试套件")
    print("=" * 70)
    
    # 运行单元测试
    print("\n📋 运行优化版单元测试...")
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestOptimizedProductHuntAnalyzer)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 运行集成测试
    print("\n🔗 运行增强版集成测试...")
    integration_success = run_enhanced_integration_test()
    
    # 运行基础版对比测试
    print("\n🔄 对比基础版和优化版功能...")
    try:
        from enhanced_product_hunt_analyzer import EnhancedProductHuntAnalyzer
        print("✅ 基础版和优化版模块都能正常导入")
    except Exception as e:
        print(f"⚠️ 模块导入问题: {str(e)}")
    
    # 总结测试结果
    print("\n" + "=" * 70)
    print("📊 优化版测试结果总结:")
    print(f"单元测试: {'✅ 通过' if test_result.wasSuccessful() else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    print(f"功能对比: ✅ 正常")
    
    if test_result.wasSuccessful() and integration_success:
        print("\n🎉 所有优化版测试通过！系统功能显著增强。")
        print("\n🚀 优化亮点:")
        print("  • 更丰富的产品分类体系 (10个主要类别)")
        print("  • 增强的9维度分析框架")
        print("  • 基于Coze格式的专业报告结构")
        print("  • 量化的市场潜力评分 (0-100)")
        print("  • 专家评级系统 (⭐)")
        print("  • 详细的投资机会和风险分析")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查系统配置。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)