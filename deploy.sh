#!/bin/bash
# Product Hunt分析系统部署脚本

echo "🚀 Product Hunt每日热门产品分析系统部署脚本"
echo "================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，请先安装pip3"
    exit 1
fi

echo "✅ pip3 已安装"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境？(y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已创建并激活"
fi

# 安装依赖
echo "📦 安装Python依赖包..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖包安装成功"
else
    echo "❌ 依赖包安装失败"
    exit 1
fi

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p reports
mkdir -p logs
mkdir -p data

# 设置权限
chmod +x enhanced_product_hunt_analyzer.py
chmod +x test_system.py

# 运行测试
echo "🧪 运行系统测试..."
python3 test_system.py

if [ $? -eq 0 ]; then
    echo "✅ 系统测试通过"
else
    echo "❌ 系统测试失败"
    exit 1
fi

# 手动运行一次分析
echo "📊 执行首次分析..."
python3 enhanced_product_hunt_analyzer.py

if [ $? -eq 0 ]; then
    echo "✅ 首次分析执行成功"
    
    # 显示生成的报告
    latest_report=$(ls -t reports/product_hunt_analysis_*.md | head -1)
    if [ -n "$latest_report" ]; then
        echo "📄 最新报告已生成: $latest_report"
        echo "📖 报告预览:"
        head -20 "$latest_report"
        echo "..."
    fi
else
    echo "❌ 首次分析执行失败"
    exit 1
fi

# 检查Git配置（如果存在）
if [ -d ".git" ]; then
    echo "🔧 Git仓库检测到"
    echo "GitHub Actions配置: .github/workflows/product-hunt-analysis.yml"
    echo "设置说明:"
    echo "1. 确保仓库有GitHub Actions权限"
    echo "2. 推送代码后，Actions将自动执行"
    echo "3. 可在Actions页面查看执行历史"
else
    echo "⚠️ 未检测到Git仓库"
    echo "如需使用GitHub Actions自动化，请:"
    echo "1. git init"
    echo "2. git remote add origin <your-repo-url>"
    echo "3. git push"
fi

echo ""
echo "🎉 部署完成！"
echo "================================================"
echo "📋 使用说明:"
echo "• 手动执行: python3 enhanced_product_hunt_analyzer.py"
echo "• 运行测试: python3 test_system.py"
echo "• 查看报告: ls -la reports/"
echo "• 查看日志: tail -f product_hunt_analysis.log"
echo ""
echo "📚 文档:"
echo "• README.md - 详细使用说明"
echo "• .github/workflows/ - GitHub Actions配置"
echo ""
echo "🆘 获取帮助:"
echo "• 查看日志: cat product_hunt_analysis.log"
echo "• 重新测试: python3 test_system.py"
echo "• 查看帮助: python3 enhanced_product_hunt_analyzer.py --help"