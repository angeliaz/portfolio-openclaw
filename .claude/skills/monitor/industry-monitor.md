---
name: industry-monitor
description: 行业深度监控，支持单行业或批量扫描。触发词：行业监控、industry monitor、扫描行业、更新行业分析。
---

# 行业深度监控 (Industry Monitor)

定时（建议每月）或手动触发。支持单行业深度分析或批量扫描所有关注行业。

用法：
- `/industry-monitor AI产业链` — 单行业深度分析
- `/industry-monitor` — 批量扫描 watchlist 中所有关注行业

---

## 执行协议

### Step 1: 确定分析范围

**单行业模式:** 直接使用用户指定行业

**批量模式:** 读取 `data/watchlist.md` 第四节"关注行业"列表：
```
Read: data/watchlist.md → 提取"关注行业"部分
```

### Step 2: 对每个行业执行完整分析

调用 `investment-sop/industry.md` 的6维度框架：

**数据采集（并行）:**
```
# A股行业数据
mcp__stock-sdk__get_industry_list
mcp__stock-sdk__get_industry_spot      symbol=<目标行业BK代码>
mcp__stock-sdk__get_industry_constituents  symbol=<BK代码>
mcp__stock-sdk__get_industry_kline     symbol=<BK代码>  period=week  startDate=<1年前>

# 相关概念
mcp__stock-sdk__get_concept_spot       symbol=<相关概念名>

# 行业龙头行情
mcp__stock-sdk__get_a_share_quotes    codes=[龙头代码]
mcp__finance-data__get_financial_summary  symbol=<龙头>  market=A

# 港股/美股行业龙头（如有）
mcp__stock-sdk__get_hk_quotes  codes=[...]
mcp__stock-sdk__get_us_quotes  codes=[...]

# 行业最新动态
WebSearch: "[行业名] 行业动态 最新 [月份]"
WebSearch: "[行业名] 政策 [最近3个月]"
```

### Step 3: 行业评级更新

基于分析结果给出评级变化：

| 评级 | 含义 |
|---|---|
| ⭐⭐⭐ 超配 | 估值低+景气度上行+催化剂明确 |
| ⭐⭐ 标配 | 基本面稳定，估值合理 |
| ⭐ 低配 | 估值偏高/景气度下行/风险大 |
| ❌ 回避 | 基本面恶化/政策风险/黑天鹅 |

### Step 4: 批量模式汇总输出

---

## 单行业输出格式

参考 `investment-sop/industry.md` 输出格式，保存至：
`data/research-notes/industry-[行业名]-YYYY-MM.md`

---

## 批量模式汇总输出

```markdown
## 关注行业月度扫描 — YYYY-MM

### 行业评级速览

| 行业 | 评级 | 本期变化 | 核心逻辑 | 首选标的 |
|---|---|---|---|---|
| AI产业链 | ⭐⭐⭐ 超配 | ↑上调 | AI应用落地加速，算力需求持续 | NVDA, 寒武纪 |
| 互联网 | ⭐⭐ 标配 | → 持平 | 估值合理，增速平稳 | 腾讯, 阿里 |
| 新能源 | ⭐ 低配 | ↓下调 | 产能过剩，价格战持续 | — |
| 消费白酒 | ⭐⭐ 标配 | → 持平 | 估值合理，复苏节奏偏慢 | 茅台 |

### 重点行业详情

[每个行业3-5句话核心判断]

**AI产业链:**
[核心观点 + 催化剂 + 风险]

**互联网:**
[核心观点 + 催化剂 + 风险]

### 本期变化汇总
- ↑ 上调: [行业] — 原因
- ↓ 下调: [行业] — 原因
- → 维持: [行业列表]

### 行动建议
- [具体操作建议]
```

---

## 建议执行频率
- **常规**: 每月一次（建议与宏观监控同步）
- **加急**: 行业重大政策出台、龙头财报季、板块剧烈波动（±10%/月）
