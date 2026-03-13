---
name: industry
description: 行业深度分析。触发词：行业研究、行业分析、industry [行业名]，如"研究AI产业链"、"分析互联网行业"
---

# 行业分析 SOP

对单一行业进行系统性深度分析，覆盖产业逻辑、竞争格局、龙头估值、催化剂与风险。

用法: `/industry [行业名]`，例如 `/industry AI产业链`、`/industry 互联网`

---

## 分析框架（6个维度）

### 1. 产业概览
- 行业定义与边界（A/H/US覆盖范围）
- 产业链结构（上游/中游/下游）
- 行业规模与增速（TAM、历史CAGR、预期增速）
- 所处发展阶段（导入期/成长期/成熟期/衰退期）

### 2. 宏观与政策驱动
- 政策催化剂（中国产业政策、补贴、监管变化）
- 宏观驱动因素（利率敏感性、经济周期相关性）
- 技术变革（颠覆性技术对行业的影响）

### 3. 竞争格局
- CR3/CR5 集中度
- 核心壁垒（技术/规模/品牌/网络效应/资质）
- 龙头公司及市场份额
- 新进入者威胁与替代品风险

### 4. 行业数据获取

**A股行业数据:**
```
# 获取行业列表
mcp__stock-sdk__get_industry_list

# 目标行业实时数据（涨跌/成交/PE/PB）
mcp__stock-sdk__get_industry_spot  symbol=<BK代码或行业名>

# 行业成分股
mcp__stock-sdk__get_industry_constituents  symbol=<BK代码>

# 行业K线（近1年走势）
mcp__stock-sdk__get_industry_kline  symbol=<BK代码>  period=day  startDate=<1年前>

# 相关概念（如AI产业链）
mcp__stock-sdk__get_concept_list  → 搜索相关概念名
mcp__stock-sdk__get_concept_spot  symbol=<概念名>
mcp__stock-sdk__get_concept_constituents  symbol=<概念名>
```

**港股/美股行业数据（WebSearch）:**
```
WebSearch: "[行业名] 行业分析 港股/美股 [年份]"
WebSearch: "[行业名] 龙头股 估值比较 [年份]"
WebSearch: "[行业名] 产业链 [相关关键词]"
```

### 5. 龙头标的评估

对行业内3-5个核心标的进行快速评估：

| 标的 | 市场 | 市值 | PE/PB | ROE | 增速 | 护城河 | 相对吸引力 |
|---|---|---|---|---|---|---|---|

**数据获取:**
```
# A股龙头
mcp__stock-sdk__get_a_share_quotes  codes=["sh600xxx","sz000xxx"]
mcp__finance-data__get_financial_summary  symbol=600xxx  market=A

# 港股龙头
mcp__stock-sdk__get_hk_quotes  codes=["00700","09988"]
mcp__finance-data__get_financial_summary  symbol=00700  market=HK

# 美股龙头
mcp__stock-sdk__get_us_quotes  codes=["NVDA","MSFT"]
mcp__finance-data__get_financial_summary  symbol=NVDA  market=US
```

### 6. 催化剂 & 风险矩阵

**催化剂（按时间维度）:**
- 近期（1-3月）：业绩期、政策落地、产品发布
- 中期（3-12月）：行业拐点、并购重组、指数纳入
- 长期（1年+）：技术变革、市场扩张、竞争格局重塑

**风险矩阵:**

| 风险类型 | 具体风险 | 概率 | 影响 | 应对 |
|---|---|---|---|---|
| 政策风险 | 监管收紧 | 中 | 高 | 关注政策动向 |
| 竞争风险 | 新进入者 | 低 | 中 | — |
| 估值风险 | 估值过高 | — | — | 设置止盈价 |
| 宏观风险 | 经济下行 | — | — | — |

---

## 输出格式

```markdown
## [行业名] 深度分析 — YYYY-MM-DD

### 一句话判断
[行业评级：超配/标配/低配] + [核心逻辑一句话]

### 产业概览
[简述行业结构、规模、增速]

### 竞争格局
[龙头格局、核心壁垒]

### 行业走势
[近1年板块走势简评，相对大盘表现]

### 龙头标的

| 标的 | 市场 | PE | PB | ROE | 我的评价 |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### 催化剂
- 近期: ...
- 中期: ...

### 风险
- 主要风险1: ...
- 主要风险2: ...

### 投资结论
[是否有配置价值，首选标的，配置时机]
```

---

## 重点行业参考（快速查找）

| 行业 | A股板块代码参考 | 核心标的 |
|---|---|---|
| AI产业链-算力 | 半导体/服务器 | 寒武纪、海光信息 |
| AI产业链-应用 | 计算机/传媒 | 科大讯飞、万兴科技 |
| 互联网 | 港股/US | 腾讯、阿里、美团 |
| 新能源/锂电 | 电力设备 | 宁德时代、比亚迪 |
| 半导体 | 半导体 | 中芯国际、北方华创 |
| 消费（白酒） | 食品饮料 | 茅台、五粮液 |
| 医药 | 医药生物 | 创新药、CXO |
| 银行/金融 | 银行 | 招行、平安 |
