---
name: stocks-monitor
description: watchlist所有标的深度研究，定时或手动触发。触发词：标的监控、深度研究所有标的、stocks monitor、全量研究。
---

# 标的深度监控 (Stocks Monitor)

对 `data/watchlist.md` 中所有标的逐一执行深度研究，更新研究结论。建议每月一次。

---

## 执行协议

### Step 1: 读取标的列表

```
Read: data/watchlist.md
→ 提取所有标的（持仓 + 重点关注）
→ 按市场分组
```

### Step 2: 批量行情预加载（并行）

```
mcp__stock-sdk__get_a_share_quotes  codes=[全部A股代码]
mcp__stock-sdk__get_hk_quotes       codes=[全部港股代码]
mcp__stock-sdk__get_us_quotes       codes=[全部美股代码]
```

### Step 3: 逐标的深度研究

对每个标的执行 `investment-sop/stock.md` 完整框架：

```
# 财务摘要
mcp__finance-data__get_financial_summary  symbol=<code>  market=<A|HK|US>

# 历史K线+技术指标（月线看大趋势）
mcp__stock-sdk__get_kline_with_indicators
  symbol=<code>  period=month  startDate=<3年前>
  indicators=["MA","MACD","RSI","BOLL"]

# A股：资金流向
mcp__stock-sdk__get_fund_flow  codes=[<A股code>]

# A股：分红历史（每年更新一次即可）
mcp__stock-sdk__get_dividend_detail  symbol=<A股code>

# 最新动态
WebSearch: "[公司名] 最新动态 业绩 [季度]"
```

### Step 4: 更新研究结论

每个标的输出：
1. 简版研究摘要（5-8行）
2. 操作建议更新（买入/持有/减仓/卖出/观察）
3. 目标价 & 止损价更新

保存至：`data/research-notes/stock-[code]-YYYY-MM.md`

### Step 5: 汇总报告

---

## 单标的深度研究（参考 stock.md 完整框架）

执行顺序：
1. 基本行情（PE/PB/市值/52周高低）
2. 财务质量（ROE/增速/现金流/资产负债）
3. 估值分析（当前PE历史分位/目标价）
4. 技术面（趋势/MA/MACD/RSI）
5. 资金面（A股：主力流向/大单）
6. 最新动态（催化剂/风险）
7. 综合评分 & 操作建议

---

## 汇总输出格式

```markdown
## Watchlist 月度深度研究 — YYYY-MM

### 研究结论速览

| 代码 | 名称 | 市场 | PE | ROE | 技术面 | 操作建议 | 目标价 | 止损价 |
|---|---|---|---|---|---|---|---|---|
| 600519 | 贵州茅台 | A | 28x | 35% | 🟢多头 | 持有 | 1800 | 1300 |
| 00700 | 腾讯 | HK | 18x | 20% | 🟡震荡 | 观察 | 450 | 330 |
| NVDA | 英伟达 | US | 45x | 65% | 🔴超买 | 减仓30% | — | 750 |

### 操作建议汇总

**立即操作:**
- [标的] [操作] — [原因]

**条件操作（设置价位提醒）:**
- [标的] 若跌至 xxx 则买入 — [逻辑]
- [标的] 若涨至 xxx 则减仓 — [逻辑]

**维持持有:**
- [标的列表] — 逻辑不变

**移出 watchlist 建议:**
- [标的] — [原因：逻辑破坏/机会成本高/更好替代]

### 新增关注建议
- [标的] — 纳入理由

### 各标的研究摘要

**600519 贵州茅台 (A)**
- 财务: ROE 35%，净利率 50%，现金流质量高
- 估值: PE 28x，历史40%分位，合理偏低
- 技术: 季线多头排列，RSI=52 中性
- 动态: Q4业绩符合预期，批价稳定
- **结论**: 持有，目标价1800，止损1300

[... 其他标的同格式]
```

---

## 建议执行频率
- **常规**: 每月一次（建议季报发布后2周内执行）
- **加急**: 单标的异常（跌幅>10%/月、重大公告）
- **简化版**: 仓位>15%的核心持仓每两周执行一次
