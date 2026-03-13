# 数据来源手册

精确定义每类数据的获取工具、接口、备用来源。各 skill 执行时优先查阅本文档。

## 已安装 MCP 概览

| MCP | 前缀 | 核心能力 |
|---|---|---|
| `stock-sdk` | `mcp__stock-sdk__` | A/H/US实时行情、K线、技术指标、A股行业/概念/资金流 |
| `finance-data` | `mcp__finance-data__` | A/H/US财务报表、财务摘要(PE/PB/ROE)、汇率 |
| `tavily` | `mcp__tavily__tavily-search` | AI优化搜索，替代 WebSearch，全局已安装 ✅ |

---

## 一、A股数据 (沪深北交所)

| 数据类型 | 主要工具/接口 | 关键参数 | 备用来源 |
|---|---|---|---|
| 实时行情（含PE/PB/市值） | `mcp__stock-sdk__get_a_share_quotes` | codes=["sh600519"] | — |
| 批量全市场行情 | `mcp__stock-sdk__get_all_a_share_quotes` | market=all/sh/sz/kc/cy | — |
| 历史日/周/月K线 | `mcp__stock-sdk__get_history_kline` | symbol, startDate, endDate, period, adjust | — |
| 历史K线+技术指标 | `mcp__stock-sdk__get_kline_with_indicators` | symbol, period, startDate, indicators | 首选（9种指标一次获取） |
| 分钟K线（日内） | `mcp__stock-sdk__get_minute_kline` | symbol, period=1/5/15/30/60 | 仅当日 |
| 今日逐分钟时间线 | `mcp__stock-sdk__get_today_timeline` | code | — |
| 资金流向（主力/散户） | `mcp__stock-sdk__get_fund_flow` | codes=[...] | — |
| 大单分布（买卖盘） | `mcp__stock-sdk__get_panel_large_order` | codes=[...] | — |
| 行业板块列表 | `mcp__stock-sdk__get_industry_list` | — | 55+行业 |
| 行业板块实时数据 | `mcp__stock-sdk__get_industry_spot` | symbol=BK1027 | — |
| 行业板块成分股 | `mcp__stock-sdk__get_industry_constituents` | symbol | — |
| 行业板块K线 | `mcp__stock-sdk__get_industry_kline` | symbol, period, startDate | — |
| 概念板块列表 | `mcp__stock-sdk__get_concept_list` | — | 26000+概念 |
| 概念板块实时数据 | `mcp__stock-sdk__get_concept_spot` | symbol=概念名/代码 | — |
| 概念板块成分股 | `mcp__stock-sdk__get_concept_constituents` | symbol | — |
| 概念板块K线 | `mcp__stock-sdk__get_concept_kline` | symbol, period, startDate | — |
| 分红/送股历史 | `mcp__stock-sdk__get_dividend_detail` | symbol | — |
| 财务报表（利润/资产/现金流） | `mcp__finance-data__get_financial_report` | symbol, market=A, report_type | 巨潮/同花顺(备用) |
| 财务摘要（PE/PB/ROE/EPS/股息率） | `mcp__finance-data__get_financial_summary` | symbol, market=A | — |
| 分析师预期/目标价 | WebSearch | — | 东方财富 / 万得资讯 |
| 股票代码列表 | `mcp__stock-sdk__get_a_share_code_list` | market, simple | — |
| 交易日历 | `mcp__stock-sdk__get_trading_calendar` | — | — |

---

## 二、港股数据 (香港交易所)

| 数据类型 | 主要工具/接口 | 关键参数 | 备用来源 |
|---|---|---|---|
| 实时行情 | `mcp__stock-sdk__get_hk_quotes` | codes=["00700"] | — |
| 批量全市场行情 | `mcp__stock-sdk__get_all_hk_quotes` | batchSize, concurrency | — |
| 历史K线+技术指标 | `mcp__stock-sdk__get_kline_with_indicators` | symbol=00700, period | — |
| 历史K线（原始） | `mcp__stock-sdk__get_hk_history_kline` | symbol, startDate, endDate | — |
| 财务报表（利润/资产/现金流） | `mcp__finance-data__get_financial_report` | symbol=00700, market=HK | 港交所披露易(备用) |
| 财务摘要（PE/PB/ROE/EPS/股息率） | `mcp__finance-data__get_financial_summary` | symbol, market=HK | — |
| 行业/板块数据 | WebSearch | — | Bloomberg / 彭博 / 行业媒体 |
| 资金流/大单 | ❌ 无直接接口 | WebSearch | 东方财富港股频道 |
| 股票代码列表 | `mcp__stock-sdk__get_hk_code_list` | simple | — |

---

## 三、美股数据 (NYSE / NASDAQ)

| 数据类型 | 主要工具/接口 | 关键参数 | 备用来源 |
|---|---|---|---|
| 实时行情 | `mcp__stock-sdk__get_us_quotes` | codes=["AAPL"] | — |
| 批量全市场行情 | `mcp__stock-sdk__get_all_us_quotes` | market=all/NASDAQ/NYSE | — |
| 历史K线+技术指标 | `mcp__stock-sdk__get_kline_with_indicators` | symbol=AAPL, period | — |
| 历史K线（原始） | `mcp__stock-sdk__get_us_history_kline` | symbol, startDate, endDate | — |
| 财务报表（10-K/10-Q） | `mcp__finance-data__get_financial_report` | symbol=AAPL, market=US | SEC Edgar(备用) |
| 财务摘要（PE/PB/ROE/EPS/股息率） | `mcp__finance-data__get_financial_summary` | symbol, market=US | — |
| 分析师预期/EPS预测 | WebSearch | — | Seeking Alpha / Yahoo Finance |
| 行业/板块数据 | WebSearch | — | GICS分类 / Finviz |
| 资金流/机构持仓 | WebSearch | — | SEC 13F / WhaleWisdom |
| 股票代码列表 | `mcp__stock-sdk__get_us_code_list` | market=NASDAQ/NYSE | — |

---

## 四、基金数据 (公募基金)

| 数据类型 | 主要工具/接口 | 关键参数 |
|---|---|---|
| 基金实时行情/净值 | `mcp__stock-sdk__get_fund_quotes` | codes=["000001"] |
| 基金代码列表 | `mcp__stock-sdk__get_fund_code_list` | — |

---

## 五、宏观经济数据

### 中国宏观
| 指标 | 获取方式 | 目标来源 |
|---|---|---|
| GDP（季度/年度） | WebSearch | 国家统计局 stats.gov.cn |
| CPI / PPI（月度） | WebSearch | 国家统计局 / 东方财富 |
| PMI（制造业/非制造业） | WebSearch | 统计局 / 财新 |
| 利率（LPR/MLF/逆回购） | WebSearch | 中国人民银行 pbc.gov.cn |
| M1 / M2 / 社融 | WebSearch | 央行 / 东方财富数据中心 |
| 外汇储备 / 人民币汇率 | WebSearch | 央行 / 外汇管理局 |
| 进出口数据 | WebSearch | 海关总署 customs.gov.cn |
| 房地产数据 | WebSearch | 国家统计局 / 中指院 |

### 美国宏观
| 指标 | 获取方式 | 目标来源 |
|---|---|---|
| GDP（季度） | WebSearch | BEA(bea.gov) / FRED |
| CPI / PCE（月度） | WebSearch | BLS(bls.gov) / FRED |
| 非农就业 / 失业率 | WebSearch | BLS |
| 联邦基金利率 / 美联储声明 | WebSearch | Fed(federalreserve.gov) |
| 国债收益率曲线 | WebSearch | FRED / 美联储 |
| 贸易差额 | WebSearch | BEA / Census Bureau |

### 全球/其他
| 指标 | 获取方式 | 目标来源 |
|---|---|---|
| 全球经济预测 | WebSearch | IMF / World Bank |
| 欧元区利率 / ECB政策 | WebSearch | ECB(ecb.europa.eu) |
| 大宗商品（原油/黄金/铜） | WebSearch | CME / 东方财富 |
| VIX 恐慌指数 | WebSearch | CBOE / 东方财富 |

---

## 六、汇率数据

| 数据类型 | 主要工具 | 参数 | 备用 |
|---|---|---|---|
| 实时汇率 | `mcp__finance-data__get_fx_rate` | from_currency=USD, to_currency=CNY | WebSearch |

常用汇率对: USD/CNY, HKD/CNY, USD/HKD, EUR/USD, JPY/USD

---

## 七、通用搜索工具使用规则

| 场景 | 工具 | 说明 |
|---|---|---|
| 获取最新动态/新闻 | `mcp__tavily__tavily-search` | **首选**，AI优化结果，质量优于 WebSearch |
| 获取特定页面完整内容 | `WebFetch` | 适合抓取 SEC Edgar/港交所文件等结构化页面 |
| 搜索+精读 | `mcp__tavily__tavily-search` → WebFetch | 先搜索找到URL，再 Fetch 读取完整内容 |
| Tavily 不可用时备用 | `WebSearch` | 备用搜索 |

---

## 八、数据局限性汇总

| 局限 | 说明 | 应对方案 |
|---|---|---|
| 港股无行业板块数据 | stock-sdk 不提供港股板块分类 | WebSearch 彭博/行业媒体 |
| 港美股无资金流数据 | 仅A股有资金流和大单数据 | 以成交量/换手率替代判断 |
| 无财务报表直接接口 | 三市场财务数据均需 WebSearch | 标注数据来源时间，注意时效 |
| 美股无分钟K线 | stock-sdk 仅A股支持分钟数据 | 使用日线+技术指标替代 |
| 无分析师一致预期 | stock-sdk 不提供 | WebSearch 东财/Seeking Alpha |
