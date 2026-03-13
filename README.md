# Portfolio SOP — 个人投研系统

覆盖 A/H/US 三市场的个人金融投资组合研究系统，运行于 Claude Code (openclaw)。

---

## 系统结构

```
portfolio-sop/
├── CLAUDE.md                          # 数据路由规则（自动加载）
├── data/
│   ├── watchlist.md                   # 自选股 & 研究管道
│   ├── portfolio.db                   # 模拟仓 SQLite 数据库
│   ├── data-sources.md                # 数据来源手册
│   └── research-notes/                # 研究报告存档
└── .claude/skills/
    ├── investment-sop/
    │   ├── macro.md                   # /macro — 宏观分析
    │   ├── industry.md                # /industry — 行业分析
    │   ├── stock.md                   # /stock — 个股研究
    │   └── portfolio.md               # /portfolio — 组合管理
    ├── monitor/
    │   ├── daily-market.md            # /daily-market — 每日市场扫描
    │   ├── daily-stocks.md            # /daily-stocks — 每日个股扫描
    │   ├── macro-monitor.md           # /macro-monitor — 宏观深度监控
    │   ├── industry-monitor.md        # /industry-monitor — 行业深度监控
    │   └── stocks-monitor.md          # /stocks-monitor — 标的深度研究
    └── paper-trading/
        ├── paper-trading.md           # /paper-trading — 模拟仓管理
        └── portfolio.py               # CLI 工具
```

---

## 快速入门

### 投研分析

| 命令 | 功能 |
|---|---|
| `/macro` | 宏观经济环境分析 + 资产配置框架 |
| `/industry [行业名]` | 行业深度分析（如 `/industry AI产业链`）|
| `/stock [代码]` | 个股/ETF深度研究（如 `/stock 600519`）|
| `/portfolio` | 投资组合回顾 + 再平衡建议 |

### 监控体系

| 命令 | 频率 | 功能 |
|---|---|---|
| `/daily-market` | 每日 | A/H/US指数 + 板块轮动 + 关键新闻（≈3min）|
| `/daily-stocks` | 每日 | watchlist 个股异动快扫（≈5min）|
| `/macro-monitor` | 每周/手动 | 宏观深度分析 + 资产配置框架更新 |
| `/industry-monitor [行业]` | 每月/手动 | 行业深度分析 + 风险扫描 |
| `/stocks-monitor` | 每月/手动 | watchlist 所有标的深度研究 |

### 模拟仓

| 命令示例 | 功能 |
|---|---|
| `模拟仓 买入 600519 100股 1500元` | 买入记录 |
| `模拟仓 卖出 AAPL 10股 210美元` | 卖出记录 |
| `模拟仓 查看持仓` | 持仓 + 实时浮盈 |
| `模拟仓 盈亏分析` | 已实现/未实现盈亏 |

---

## 数据能力

| 数据类型 | 工具 | 覆盖市场 |
|---|---|---|
| 实时行情 + PE/PB | stock-sdk MCP | A / HK / US |
| 历史K线 + 9种技术指标 | stock-sdk MCP | A / HK / US |
| 行业/概念板块 | stock-sdk MCP | A股 |
| 资金流向/大单 | stock-sdk MCP | A股 |
| 财务报表/摘要 | finance-data MCP | A / HK / US |
| 汇率 | finance-data MCP | 主流货币对 |
| 宏观数据/新闻/财报 | WebSearch + WebFetch | 全球 |

详见 [data/data-sources.md](data/data-sources.md)

---

## 配置说明

- **自选股**: 编辑 `data/watchlist.md`，/portfolio、/daily-stocks、/stocks-monitor 均依赖此文件
- **模拟仓初始资金**: 1,000,000 CNY（100万），运行 `python .claude/skills/paper-trading/portfolio.py init` 可重置
- **研究报告**: 自动保存至 `data/research-notes/`
