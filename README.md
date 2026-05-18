# Product Hunt Analyzer

自动化抓取和分析 Product Hunt 每日热门产品的 Python 工具。

## 功能特性

- 🤖 **自动抓取**: 从 decohack.com 抓取 Product Hunt 每日热门榜单
- 🔍 **智能去重**: 自动检测并去除重复产品，显示去重统计
- 📊 **深度分析**: AI 增强产品信息分析
- 📝 **Markdown 报告**: 生成格式优美的分析报告

## 使用方法

```bash
python optimized_product_hunt_analyzer.py
```

## 报告示例

生成的报告保存在 `reports/` 目录，文件名格式：`2026-05-18_product_analysis.md`

报告头部包含：
- 上榜产品数量
- 去重处理信息（源页标题数、去重后数量、重复项）

## 项目结构

```
product-hunt-analyzer/
├── optimized_product_hunt_analyzer.py  # 主程序
├── reports/                             # 分析报告目录
└── README.md                           # 项目说明
```

## 依赖

- requests
- beautifulsoup4

## License

MIT
