---
name: stock
description: 个股或ETF深度研究。触发词：研究某只股票、深度分析、/stock [代码]，如"研究茅台"、"分析腾讯"、"研究NVDA"
---

# 个股/ETF 深度研究 SOP

对单一标的进行全面深度研究，覆盖商业模式、财务质量、估值、技术面、催化剂与风险。

用法: `/stock [代码]`，例如 `/stock 600519`、`/stock 00700`、`/stock NVDA`

---

## 研究框架（7个维度）

### 1. 基本信息 & 实时行情

```
# 根据市场选择对应接口：
A股: mcp__stock-sdk__get_a_share_quotes  codes=["sh600519"]
港股: mcp__stock-sdk__get_hk_quotes      codes=["00700"]
美股: mcp__stock-sdk__get_us_quotes      codes=["NVDA"]
```

获取：当前价格、PE(TTM)、PE(静)、PB、市值、52周高低、成交量、换手率

### 2. 商业模式 & 竞争优势

分析要点：
- **业务构成**: 主营业务、收入结构（产品线/地区/客户）
- **商业模式**: 盈利模式、变现路径、单位经济模型
- **护城河**: 技术壁垒/品牌/规模/网络效应/转换成本/资质许可
- **行业地位**: 市场份额、竞争对手比较
- **管理层**: 创始人/管理层背景、股权激励、治理结构

**数据来源:** WebSearch "[公司名] 商业模式分析"、最新年报摘要

### 3. 财务质量分析

```
# 财务摘要（PE/PB/ROE/EPS/股息率）
mcp__finance-data__get_financial_summary  symbol=<code>  market=<A|HK|US>

# 完整财务报表（近5期）
mcp__finance-data__get_financial_report  symbol=<code>  market=<A|HK|US>  report_type=income_statement
mcp__finance-data__get_financial_report  symbol=<code>  market=<A|HK|US>  report_type=balance_sheet
mcp__finance-data__get_financial_report  symbol=<code>  market=<A|HK|US>  report_type=cash_flow
```

**核心指标评估：**

| 维度 | 指标 | 优质标准 |
|---|---|---|
| 成长性 | 收入CAGR(3年) | > 15% |
| 盈利性 | ROE | > 15%，且稳定 |
| 盈利性 | 净利率 | 持续提升或稳定高位 |
| 现金质量 | 经营现金流/净利润 | > 80%（高质量利润） |
| 财务健康 | 资产负债率 | 制造业<60%，科技<50% |
| 股东回报 | 分红率 / 股息率 | 有稳定分红计划 |

**A股分红历史（额外检查）:**
```
mcp__stock-sdk__get_dividend_detail  symbol=600519
```

### 4. 估值分析

**绝对估值（DCF/DDM参考）:**
- 使用 WebSearch 获取分析师目标价共识

**相对估值（比较法）:**
- PE/PB 与历史均值比较（历史分位数）
- PE/PB 与同业龙头比较
- PEG = PE / 增速（< 1 通常低估）

**历史K线 + 技术指标（辅助判断买入时机）:**
```
mcp__stock-sdk__get_kline_with_indicators
  symbol=<代码>
  period=week          # 周线看趋势
  startDate=<2年前>
  indicators=["MA","MACD","RSI","BOLL","KDJ"]
```

解读重点：
- MA(20/60/120/250): 多头排列 vs 死叉
- MACD: 金叉/死叉，柱状图趋势
- RSI: > 70 超买，< 30 超卖
- BOLL: 价格与上下轨关系

### 5. 资金流向（A股专项）

```
# 主力资金流向
mcp__stock-sdk__get_fund_flow       codes=["sh600519"]

# 大单分布（买盘 vs 卖盘）
mcp__stock-sdk__get_panel_large_order  codes=["sh600519"]
```

解读：主力持续净流入 + 大单买盘占优 = 看多信号

### 6. 催化剂 & 风险

**近期催化剂（1-3月）:**
- 业绩披露日期（下次财报时间）
- 产品/技术发布节点
- 政策催化
- 回购/分红公告

**主要风险:**
- 业绩不及预期的概率
- 估值收缩风险（市场风格切换）
- 竞争加剧/行业黑天鹅
- 管理层风险

**数据来源:**
```
WebSearch: "[公司名] 最新动态 [季度]"
WebSearch: "[公司名] 业绩预告 [年份]"
WebSearch: "[公司名] 分析师评级 目标价"
```

### 7. 综合评估 & 投资结论

**评分卡（1-5分）:**
| 维度 | 评分 | 说明 |
|---|---|---|
| 商业质量 | /5 | 护城河深度 |
| 成长性 | /5 | 收入/利润增速 |
| 估值吸引力 | /5 | 当前估值水平 |
| 财务健康 | /5 | 资产负债质量 |
| 催化剂 | /5 | 近中期驱动力 |
| **综合** | **/25** | |

---

## 输出格式

```markdown
## [公司名]([代码]) 深度研究 — YYYY-MM-DD

### 一句话判断
[买入/观察/回避] — [核心逻辑一句话]

### 基本数据
- 当前价格: xxx  市值: xxxB
- PE(TTM): xx  PB: x.x  ROE: xx%
- 52周: 最低xxx / 最高xxx

### 商业模式
[2-3句话概述核心业务和护城河]

### 财务亮点
- 收入增速: xx% (近3年CAGR)
- 净利率: xx%（趋势：上升/稳定/下降）
- ROE: xx%
- 现金流质量: 高/中/低

### 估值
- 当前PE: xx，历史分位: xx%
- 目标价参考: xxx（分析师共识/DCF）
- 安全边际: xx%

### 技术面
[MA/MACD/RSI当前信号简评]

### 催化剂
- 短期: ...
- 中期: ...

### 主要风险
- 风险1: ...
- 风险2: ...

### 投资结论
评分: x/25
[具体操作建议：买入价位/仓位/止损/目标价]
```

研究报告可选保存至 `data/research-notes/stock-[code]-[YYYY-MM-DD].md`

---

## ETF 特殊处理

ETF研究简化版（不做商业模式分析）：
1. 获取实时行情（PE/折溢价率）
2. 查看历史K线（趋势 + 技术指标）
3. 分析跟踪指数构成（WebSearch "[ETF名] 前十大持仓"）
4. 评估当前估值（成分指数整体PE/PB历史分位）
5. 输出：当前估值水平 + 建议仓位
