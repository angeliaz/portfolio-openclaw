---
name: daily-market
description: 每日市场异动轻量扫描。触发词：每日市场、今日市场、daily market、市场扫描。约3分钟完成。
---

# 每日市场扫描 (Daily Market)

轻量级每日市场快扫，目标 ≈3分钟完成。覆盖 A/H/US 三市场指数、板块轮动、资金热点、关键新闻。

---

## 执行步骤（严格按顺序，并行调用提速）

### Step 1: 三市场主要指数行情（并行调用）

```
mcp__stock-sdk__get_a_share_quotes
  codes=["sh000001","sh000300","sz399001","sz399006","sh000688"]

mcp__stock-sdk__get_hk_quotes
  codes=["HSI","HSTECH","HSCEI"]

mcp__stock-sdk__get_us_quotes
  codes=["SPY","QQQ","DIA","IWM"]
```

### Step 2: A股行业板块涨跌（取今日涨跌幅最大的3涨3跌）

```
mcp__stock-sdk__get_industry_list
→ 选取主要行业
mcp__stock-sdk__get_industry_spot  symbol=<各行业>
```

### Step 3: A股资金流向

```
mcp__stock-sdk__get_fund_flow  codes=["sh000001"]
```

### Step 4: 关键新闻（1条 WebSearch，快速扫描）

```
WebSearch: "A股 港股 美股 今日市场 重要新闻"
```

---

## 输出格式（紧凑型）

```markdown
## 每日市场扫描 — YYYY-MM-DD

### 三市场指数

| 指数 | 现价 | 涨跌幅 | 成交额 |
|---|---|---|---|
| 上证指数 | — | —% | — |
| 沪深300 | — | —% | — |
| 创业板 | — | —% | — |
| 恒生指数 | — | —% | — |
| 恒生科技 | — | —% | — |
| 标普500(SPY) | — | —% | — |
| 纳斯达克(QQQ) | — | —% | — |

### 板块轮动

🟢 领涨: [板块1 +x%] [板块2 +x%] [板块3 +x%]
🔴 领跌: [板块1 -x%] [板块2 -x%] [板块3 -x%]

### 资金动向
- A股主力净流入: ±xxxx 亿（流入/流出）
- 北向资金: （WebSearch补充）

### 今日关键信息
- 📌 [重要新闻/政策1]
- 📌 [重要新闻/政策2]

### 异动提示
⚠️ [如有异常板块/事件]

---
_扫描时间约3min，详细分析请用 /macro 或 /industry_
```

---

## 注意
- 美股盘前/盘后：注意时区，A/H收盘后美股可能还未收盘
- 若无重大异动，输出保持简洁，不超过30行
- 有重大异动（单日±2%以上）需加 ⚠️ 标注并简述原因
