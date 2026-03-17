# Portfolio SOP — 项目说明

这是一个个人金融资产投资组合研究系统，覆盖 A/H/US 三市场。包含投研SOP、市场监控、模拟仓管理三大模块。

# 核心原则

使用第一性原理思考。你不能总假设我非常清楚自己想要什么和该怎么得到。请保持审慎，从原始需求和问题出发，如果动机和目标不清晰，停下来和我讨论。如果目标清晰但是路径不是最短，告诉我，并且建议更好的方式。

**不涉及技术面分析**：本系统所有研究均基于基本面，不使用任何技术面指标（K线形态、均线、MACD、RSI、BOLL等）作为买卖依据。如SOP中出现技术面相关内容，执行时忽略该部分。

## 可用 Skills

| Skill | 触发方式 | 功能 |
|---|---|---|
| `macro` | `/macro` | 宏观环境分析 + 资产配置框架 |
| `industry` | `/industry [行业名]` | 行业深度分析 |
| `stock` | `/stock [代码]` | 个股深度研究 |
| `etf` | `/etf [代码]` | ETF深度研究（折溢价/估值分位/买入判断） |
| `portfolio` | `/portfolio` | 当前持仓回顾 + 再平衡建议 |
| `arbitrage` | `/arbitrage [类型]` | 无风险/低风险套利机会扫描（AH溢价/ETF折溢价/可转债/打新/并购） |
| `opportunity` | `/opportunity [方向]` | 投资机会主动挖掘（宏观轮动/困境反转/量化筛选/事件驱动/对标比较） |
| `macro-monitor` | `/macro-monitor` | 宏观深度监控 + 资产配置框架更新 |
| `industry-monitor` | `/industry-monitor [行业]` | 行业深度监控 + 风险扫描，支持批量或单行业 |
| `stocks-monitor` | `/stocks-monitor` | watchlist 所有标的深度研究 |
| `daily-market` | `/daily-market` | 每日市场轻量扫描（≈3min）|
| `daily-stocks` | `/daily-stocks` | 每日个股异动轻量扫描（≈5min）|
| `paper-trading` | `/paper-trading [命令]` | 模拟仓：买卖/持仓/盈亏/历史 |

## 数据路由规则

执行任何分析任务时，按以下规则选择数据来源：

| 数据类型 | 首选工具 | 目标来源 |
|---|---|---|
| 实时行情 A股 | `mcp__stock-sdk__get_a_share_quotes` | — |
| 实时行情 港股 | `mcp__stock-sdk__get_hk_quotes` | — |
| 实时行情 美股 | `mcp__stock-sdk__get_us_quotes` | — |
| 历史K线 + 技术指标 | `mcp__stock-sdk__get_kline_with_indicators` | A/H/US均支持 |
| A股资金流向 | `mcp__stock-sdk__get_fund_flow` | — |
| A股大单分布 | `mcp__stock-sdk__get_panel_large_order` | — |
| A股行业板块 | `mcp__stock-sdk__get_industry_list` / `get_industry_spot` | — |
| A股概念板块 | `mcp__stock-sdk__get_concept_list` / `get_concept_spot` | — |
| 分红数据 A股 | `mcp__stock-sdk__get_dividend_detail` | — |
| 基金行情 | `mcp__stock-sdk__get_fund_quotes` | — |
| 宏观数据 (CN) | `mcp__tavily__tavily-search` | 东方财富 / 国家统计局 / 中国人民银行 |
| 宏观数据 (US/全球) | `mcp__tavily__tavily-search` | Fed / BLS / IMF / World Bank |
| 财务报表（三表）A/HK/US | `mcp__finance-data__get_financial_report` | 首选；备用 tavily-search |
| 财务摘要 PE/PB/ROE/EPS | `mcp__finance-data__get_financial_summary` | A/HK/US/ETF均支持 |
| 汇率 | `mcp__finance-data__get_fx_rate` | USD/CNY/HKD等 |
| 港美股行业分析 | `mcp__tavily__tavily-search` | 行业媒体 / 研究机构报告 |
| 财经新闻 | `mcp__tavily__tavily-search` | 首选；备用 WebSearch |
| 模拟仓操作 | `Bash → python .claude/skills/paper-trading/portfolio.py` | SQLite (data/portfolio.db) |
| 自选股列表 | `Read data/watchlist.md` | — |

## 关键文件路径

```
portfolio-sop/
├── CLAUDE.md                            # 本文件：项目说明 + 数据路由
├── README.md                            # 用户使用指南
├── plan.md                              # 系统架构计划
├── data/
│   ├── watchlist.md                     # 自选股及研究管道
│   ├── portfolio.db                     # SQLite 模拟仓数据库
│   └── data-sources.md                  # 数据来源手册
└── .claude/
    └── skills/
        ├── investment-sop/
        │   ├── macro.md                 # /macro
        │   ├── industry.md              # /industry
        │   ├── stock.md                 # /stock
        │   ├── etf.md                   # /etf
        │   └── portfolio.md             # /portfolio
        ├── monitor/
        │   ├── macro-monitor.md         # /macro-monitor
        │   ├── industry-monitor.md      # /industry-monitor
        │   ├── stocks-monitor.md        # /stocks-monitor
        │   ├── daily-market.md          # /daily-market
        │   └── daily-stocks.md          # /daily-stocks
        └── paper-trading/
            ├── paper-trading.md         # /paper-trading
            └── portfolio.py             # CLI 工具
```

**详细数据来源规格（精确到工具参数、备用源）→ 查阅 [data/data-sources.md](data/data-sources.md)**

---

## 注意事项

- **港股/美股数据局限**: stock-sdk 对港美股只提供行情和K线，无资金流、行业板块数据，需用 WebSearch 补充
- **搜索首选 Tavily**: 宏观数据/新闻/财报均优先用 `mcp__tavily__tavily-search`，WebSearch 作备用
- **财务报表**: 优先用 `mcp__finance-data__get_financial_report`，覆盖A/HK/US三市场
- **模拟仓**: 所有持仓操作通过 `python .claude/skills/paper-trading/portfolio.py` 执行，数据在 `data/portfolio.db`
