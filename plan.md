# Portfolio SOP — 投研系统架构计划 (v2)

## Context
用户需要一套可在 Claude Code ("openclaw") 中使用的个人金融投资组合研究系统，覆盖A/H/US三市场。
系统设计为**3个独立可组合的 skill**，模拟仓采用工程化实现（Python + SQLite）。

## 数据能力评估 (stock-sdk MCP)

| 能力 | A股 | 港股 | 美股 |
|---|---|---|---|
| 实时行情(含PE/PB) | ✅ | ✅ | ✅ |
| 历史K线 + 9种技术指标 | ✅ | ✅ | ✅ |
| 资金流向/大单分布 | ✅ | ❌ | ❌ |
| 行业/概念板块 | ✅ | ❌ | ❌ |

**缺口通过 WebSearch/WebFetch 补充**: 宏观数据 / 财务报表 / 港美股行业 / 分析师预期

---

## 系统架构 (3 Skills)

### 目录结构
```
portfolio-sop/
├── CLAUDE.md                        # 数据路由规则 + 项目说明
├── README.md                        # 使用指南
├── plan.md                          # 本文件：系统架构计划
├── data/
│   ├── watchlist.md                 # 自选股及研究管道
│   ├── portfolio.db                 # SQLite 模拟仓数据库
│   └── data-sources.md              # 数据来源手册（精确到工具/接口/备用源）
└── .claude/
    └── skills/
        ├── investment-sop/          # 投研 SOP skill 目录
        │   ├── macro.md             # 宏观分析 + 资产配置框架
        │   ├── industry.md          # 行业深度分析
        │   ├── stock.md             # 个股/ETF深度研究
        │   └── portfolio.md         # 投资组合回顾 + 再平衡建议
        ├── monitor/                 # 监控体系 skill 目录 (5项监控需求 → 5个文件)
        │   ├── macro-monitor.md     # 1. 定时/手动 宏观环境分析 + 资产配置框架更新
        │   ├── industry-monitor.md  # 2. 定时/手动 行业深度分析 + 风险扫描
        │   ├── stocks-monitor.md    # 3. 定时/手动 watchlist 所有标的深度研究
        │   ├── daily-market.md      # 4. 每日市场异动轻量扫描
        │   └── daily-stocks.md      # 5. 每日个股异动轻量扫描
        └── paper-trading/           # 模拟仓 skill 目录
            ├── paper-trading.md     # Skill 定义 + 使用说明
            └── portfolio.py         # CLI 工具 (随 skill 打包)
```

**共11个文件**（investment-sop 拆为4个独立md；portfolio.py 随 skill 打包）

---

## Skill 设计规格

### Skill 1: `investment-sop/` — 投研 SOP (4个独立 skill)

每个 skill 独立触发，方法论内嵌其中。

| 文件 | 触发方式 | 功能 |
|---|---|---|
| `macro.md` | `/macro` 或 "宏观分析/市场温度/资产配置" | 宏观环境分析 + 资产配置框架 |
| `industry.md` | `/industry [行业名]` 或 "行业研究 X" | 行业深度分析 |
| `stock.md` | `/stock [代码]` 或 "研究 X / 深度分析 X" | 个股/ETF深度研究 |
| `portfolio.md` | `/portfolio` 或 "组合回顾/再平衡" | 当前持仓回顾 + 再平衡建议 |

**文件依赖:**
| Skill | 文件 | 操作 |
|---|---|---|
| macro.md | — | 仅用外部数据 |
| industry.md | — | 仅用外部数据 |
| stock.md | `data/research-notes/stock-[code]-[date].md` | Write 可选 |
| portfolio.md | `data/watchlist.md` | Read |

**MCP 工具 (各 skill 按需使用):**
| 工具 | 用途 | 适用 |
|---|---|---|
| get_a_share_quotes / get_hk_quotes / get_us_quotes | 实时行情+估值(PE/PB) | stock / portfolio |
| get_kline_with_indicators | 历史走势 + MA/MACD/RSI | stock |
| get_industry_list / get_industry_spot / get_industry_constituents | 行业板块表现 | industry / macro |
| get_concept_list / get_concept_spot / get_concept_constituents | 概念主题分析 | industry / macro |
| get_fund_flow | A股资金流 | stock / macro |
| get_dividend_detail | 分红历史 A股 | stock |
| WebSearch / WebFetch | 宏观数据 / 财报 / 新闻 | 全部 |

---

### Skill 2: `monitor/` — 监控体系 (5个文件，1:1 对应5项需求)

| # | 文件 | 触发方式 | 深度 | 说明 |
|---|---|---|---|---|
| 1 | `macro-monitor.md` | `/macro-monitor` | 深度 | 调用 investment-sop/macro.md + 输出资产配置框架变化 |
| 2 | `industry-monitor.md` | `/industry-monitor [行业]` | 深度 | 调用 investment-sop/industry.md，支持批量或单行业 |
| 3 | `stocks-monitor.md` | `/stocks-monitor` | 深度 | 对 watchlist 所有标的逐一调用 investment-sop/stock.md |
| 4 | `daily-market.md` | `/daily-market` | 轻量 ≈3min | A/H/US指数、板块轮动、关键新闻 |
| 5 | `daily-stocks.md` | `/daily-stocks` | 轻量 ≈5min | watchlist 每只标的异动快扫 |

**文件依赖:**
| Skill | 文件 | 操作 |
|---|---|---|
| stocks-monitor.md | `data/watchlist.md` | Read |
| industry-monitor.md | `data/watchlist.md` | Read (获取关注行业) |
| daily-stocks.md | `data/watchlist.md` | Read |

**MCP 工具:**
| 工具 | 用途 | 适用 |
|---|---|---|
| get_a_share_quotes / get_hk_quotes / get_us_quotes | 实时行情 | daily-stocks / stocks-monitor |
| get_industry_list / get_concept_list / get_industry_spot | 板块轮动 | daily-market / industry-monitor |
| get_fund_flow / get_panel_large_order | A股资金流 | daily-stocks |
| WebSearch | 财经新闻 / 宏观数据 | 全部 |

---

### Skill 3: `paper-trading/` — 模拟仓
- **触发**: "模拟仓", "paper trading", "买入/卖出/持仓/收益"
- **实现**: Python CLI + SQLite (主)，Markdown 报告 (次)

**文件依赖:**

| 文件 | 操作 | 说明 |
|---|---|---|
| `.claude/skills/paper-trading/portfolio.py` | Bash 执行 | CLI 工具，随 skill 打包，可移植 |
| `data/portfolio.db` | portfolio.py 读写 | 用户数据，留在项目 data/ 目录 |

**MCP 工具:**
| 工具 | 用途 |
|---|---|
| get_a_share_quotes / get_hk_quotes / get_us_quotes | `positions --live` 时拉实时价格计算浮盈 |

---

## Paper Trading 工程化设计

### `.claude/skills/paper-trading/portfolio.py` — CLI 工具

命令格式: **代码与市场类型分开传参**，手续费自动估算（可覆盖）

```
用法:
  portfolio.py init [--capital 1000000]                    # 初始化账本
  portfolio.py buy <code> <qty> <price> --market <A|HK|US> [--fee <n>] [--note <text>]
  portfolio.py sell <code> <qty> <price> --market <A|HK|US> [--fee <n>] [--note <text>]
  portfolio.py positions [--live]                          # --live 拉实时价格
  portfolio.py pnl [--code <code>]                        # 盈亏分析
  portfolio.py history [--code <code>] [--n 20]           # 交易历史
  portfolio.py snapshot                                    # 保存每日快照

示例:
  portfolio.py buy 600519 100 1500 --market A --note "茅台调整到位，估值合理"
  portfolio.py buy 00700 200 380 --market HK
  portfolio.py buy AAPL 10 210 --market US
```

手续费自动估算规则:
- **A股**: 买入 0.03%（最低5元），卖出 0.03% + 印花税 0.1%
- **港股**: 买卖各 0.1% + 固定规费（约HKD30/笔）
- **美股**: 默认0（主流券商免佣）
- 用户可通过 `--fee` 手动覆盖

### SQLite 数据库结构 (`data/portfolio.db`)

```sql
-- 组合配置
CREATE TABLE config (
  key TEXT PRIMARY KEY,
  value TEXT           -- initial_capital, start_date, currency
);

-- 交易记录
CREATE TABLE trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trade_date TEXT,      -- YYYY-MM-DD
  code TEXT,
  market TEXT,          -- A / HK / US
  name TEXT,
  direction TEXT,       -- BUY / SELL
  price REAL,
  quantity INTEGER,
  amount REAL,          -- price * quantity
  fee REAL DEFAULT 0,
  note TEXT
);

-- 当前持仓 (由 trades 计算维护)
CREATE TABLE positions (
  code TEXT PRIMARY KEY,
  market TEXT,
  name TEXT,
  quantity INTEGER,
  avg_cost REAL,
  total_cost REAL,
  buy_thesis TEXT       -- 买入逻辑
);

-- 每日快照 (可选，用于绘制净值曲线)
CREATE TABLE snapshots (
  snap_date TEXT PRIMARY KEY,
  total_value REAL,
  cash_balance REAL,
  unrealized_pnl REAL,
  realized_pnl REAL
);
```

### Skill 调用流程

```
用户: "查看持仓"
  → skill 调用 Bash: python portfolio.py positions
  → 获取持仓代码列表
  → 调用 stock-sdk 实时行情
  → 计算浮盈/浮亏/仓位权重
  → 输出 Markdown 持仓表
```

---

## 数据路由规则 (同 CLAUDE.md)

| 数据类型 | 工具 | 目标来源 |
|---|---|---|
| 实时行情 (A/H/US) | mcp__stock-sdk | — |
| 历史K线+技术指标 | mcp__stock-sdk | — |
| A股资金流/大单 | mcp__stock-sdk | — |
| A股行业/概念板块 | mcp__stock-sdk | — |
| 宏观数据 (CN) | WebSearch | 东方财富/国家统计局/央行 |
| 宏观数据 (US/全球) | WebSearch | Fed/BLS/IMF |
| 财务报表 | WebSearch | 雪球/同花顺/SEC Edgar |
| 港美股行业分析 | WebSearch | 彭博/行业媒体 |
| 财经新闻 | WebSearch | — |
| 模拟仓操作 | Bash → scripts/portfolio.py | SQLite |
| 自选股列表 | Read data/watchlist.md | — |

---

## 确认配置
- 模拟仓初始资金: **1,000,000 CNY (100万)**
- Skills 位置: **项目内 `.claude/skills/`**
- 模拟仓实现: **Python + SQLite (主)，Markdown 报告 (次)**

---

## 实施顺序

### Phase 1: 基础骨架
1. 创建 `CLAUDE.md` (数据路由规则) ✅
2. 创建 `README.md` (系统使用指南)
3. 创建 `data/watchlist.md` (模板，含示例标的)

### Phase 2: Paper Trading 工程化
4. 编写 `.claude/skills/paper-trading/portfolio.py` (SQLite CLI工具)
5. 初始化 `data/portfolio.db` (运行 `portfolio.py init --capital 1000000`)
6. 编写 `.claude/skills/paper-trading/paper-trading.md`

### Phase 3: Investment SOP Skills
7. 编写 `.claude/skills/investment-sop/macro.md`
8. 编写 `.claude/skills/investment-sop/industry.md`
9. 编写 `.claude/skills/investment-sop/stock.md`
10. 编写 `.claude/skills/investment-sop/portfolio.md`

### Phase 4: Monitor Skills
11. 编写 `.claude/skills/monitor/daily-market.md` (每日市场轻量扫描)
12. 编写 `.claude/skills/monitor/daily-stocks.md` (每日个股轻量扫描)
13. 编写 `.claude/skills/monitor/macro-monitor.md` (宏观深度监控)
14. 编写 `.claude/skills/monitor/industry-monitor.md` (行业深度监控)
15. 编写 `.claude/skills/monitor/stocks-monitor.md` (标的深度监控)

### Phase 5: 验证
14. 测试 `python portfolio.py buy 600519 100 1500 --market A`
15. 测试 `/paper-trading 查看持仓` (含实时价格)
16. 测试 `/stock 600519`
17. 测试 `/daily-market`
18. 测试 `/daily-stocks`
19. 测试 `/monitor stocks`

---

## 关键文件清单 (16个)

| 文件 | 类型 | 描述 | 状态 |
|---|---|---|---|
| `CLAUDE.md` | 配置 | 数据路由规则 + 项目说明 | ✅ |
| `plan.md` | 文档 | 本架构计划 | ✅ |
| `README.md` | 文档 | 系统使用指南 | 待完成 |
| `data/watchlist.md` | 动态数据 | 自选股列表 | 待完成 |
| `data/portfolio.db` | 数据库 | 模拟仓SQLite数据库 | 待完成 |
| `.claude/skills/paper-trading/portfolio.py` | Python | 模拟仓CLI工具 | 待完成 |
| `.claude/skills/paper-trading/paper-trading.md` | Skill | 模拟仓管理 | 待完成 |
| `.claude/skills/investment-sop/macro.md` | Skill | 宏观分析SOP | 待完成 |
| `.claude/skills/investment-sop/industry.md` | Skill | 行业分析SOP | 待完成 |
| `.claude/skills/investment-sop/stock.md` | Skill | 个股研究SOP | 待完成 |
| `.claude/skills/investment-sop/portfolio.md` | Skill | 组合管理SOP | 待完成 |
| `.claude/skills/monitor/macro-monitor.md` | Skill | 定时/手动宏观深度分析 | 待完成 |
| `.claude/skills/monitor/industry-monitor.md` | Skill | 定时/手动行业深度分析 | 待完成 |
| `.claude/skills/monitor/stocks-monitor.md` | Skill | 定时/手动标的深度研究 | 待完成 |
| `.claude/skills/monitor/daily-market.md` | Skill | 每日市场异动轻量扫描 | 待完成 |
| `.claude/skills/monitor/daily-stocks.md` | Skill | 每日个股异动轻量扫描 | 待完成 |
