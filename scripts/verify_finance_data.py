#!/usr/bin/env python3
"""
finance-data MCP 数据获取验证脚本
用途：定义 finance-data MCP 四个工具的调用规范、返回字段、路由优先级、已知问题
运行方式：在 Claude Code 中直接阅读本脚本，或让 Claude 逐块调用 MCP 工具

当前可用 MCP: finance-data
工具清单: get_stock_price / get_financial_report / get_financial_summary / get_fx_rate
MCP 路径: /Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/finance_data_server.py
venv: /Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/.venv/bin/python3

验证日期: 2026-03-11
"""

# ─────────────────────────────────────────────
# 数据源路由优先级
# ─────────────────────────────────────────────
ROUTING_PRIORITY = {
    "US / ETF": ["alpha_vantage", "yfinance"],
    "A 股":     ["tushare", "akshare", "alpha_vantage", "yfinance"],
    "HK 港股":  ["akshare", "alpha_vantage", "yfinance"],
    "FX 汇率":  ["exchangerate-api（免费，无需key）", "akshare", "alpha_vantage", "yfinance"],
}

# Alpha Vantage 免费额度: 25次/天/key，5次/分钟
# 支持多 key 轮换，总配额 = 25 × key数量
# yfinance 请求间隔 ≥10秒（Yahoo 限速严格）
# Tushare 免费约 200次/分钟

# ─────────────────────────────────────────────
# 场景一：实时股价 get_stock_price
# ─────────────────────────────────────────────
SCENARIO_PRICE_US = {
    "name": "美股实时价格",
    "tool": "mcp__finance-data__get_stock_price",
    "params": {
        "symbol": "AAPL",
        "market": "US",    # enum: US / HK / A / ETF
    },
    "return_fields": {
        "symbol":         "代码",
        "market":         "市场",
        "name":           "公司名称",
        "price":          "最新价（USD）",
        "change":         "涨跌额",
        "change_pct":     "涨跌幅 %",
        "volume":         "成交量（股）",
        "high":           "日内最高",
        "low":            "日内最低",
        "open":           "开盘价",
        "previous_close": "昨收",
        "currency":       "币种（USD）",
        "source":         "实际使用数据源",
        "timestamp":      "时间戳 ISO8601",
        "sources_tried":  "降级链路记录（数组）",
    },
    "known_issues": [
        "yfinance 请求间隔 ≥10秒，多次连续调用会 sleep（慢）",
        "Alpha Vantage 每日 25 次限额，超额后自动降级到 yfinance",
        "盘前/盘后价格不返回（只有 regularMarketPrice）",
    ],
}

SCENARIO_PRICE_HK = {
    "name": "港股实时价格",
    "tool": "mcp__finance-data__get_stock_price",
    "params": {
        "symbol": "00700",   # 5位补零格式
        "market": "HK",
    },
    "notes": [
        "AKShare 内部转换为 0700.HK 格式",
        "yfinance fallback 同样支持（格式同 0700.HK）",
        "currency 返回 HKD",
    ],
}

SCENARIO_PRICE_A = {
    "name": "A股实时价格",
    "tool": "mcp__finance-data__get_stock_price",
    "params": {
        "symbol": "600519",  # 纯数字，不含 sh/sz 前缀
        "market": "A",
    },
    "notes": [
        "Tushare 内部转为 600519.SH / 000001.SZ 格式",
        "AKShare fallback 同样支持",
        "currency 返回 CNY",
    ],
}

SCENARIO_PRICE_ETF = {
    "name": "ETF 实时价格（如 SPY）",
    "tool": "mcp__finance-data__get_stock_price",
    "params": {
        "symbol": "SPY",
        "market": "ETF",   # ETF 走 Alpha Vantage → yfinance，同美股路由
    },
}

# ─────────────────────────────────────────────
# 场景二：财务报表 get_financial_report
# ─────────────────────────────────────────────
SCENARIO_REPORT = {
    "name": "财务报表（三表）",
    "tool": "mcp__finance-data__get_financial_report",
    "params_income": {
        "symbol": "AAPL",
        "market": "US",
        "report_type": "income_statement",  # income_statement / balance_sheet / cash_flow
        "periods": 5,                        # 返回最近 N 个报告期，默认 5
    },
    "return_structure": {
        "symbol": "代码",
        "market": "市场",
        "report_type": "报表类型",
        "period": "期间粒度（annual/quarterly）",
        "count": "实际返回期数",
        "data": "报告期数组（倒序，最新在前）",
        "source": "数据源",
        "timestamp": "时间戳",
    },
    "income_statement_fields": [
        "period",            # 报告期（如 '2024' 或 '2024-09-28'）
        "revenue",           # 总收入
        "cost_of_revenue",   # 营业成本
        "gross_profit",      # 毛利润
        "operating_income",  # 营业利润（EBIT）
        "ebitda",            # EBITDA
        "net_income",        # 净利润
        "eps_basic",         # 基本每股收益
        "eps_diluted",       # 稀释每股收益
        "interest_expense",  # 利息支出
        "tax_provision",     # 所得税
    ],
    "balance_sheet_fields": [
        "period",
        "total_assets",            # 总资产
        "current_assets",          # 流动资产
        "cash_and_equivalents",    # 现金及等价物
        "short_term_investments",  # 短期投资
        "net_receivables",         # 净应收款
        "inventory",               # 存货
        "total_liabilities",       # 总负债
        "current_liabilities",     # 流动负债
        "long_term_debt",          # 长期债务
        "total_debt",              # 总债务
        "total_equity",            # 股东权益
        "retained_earnings",       # 留存收益
    ],
    "cash_flow_fields": [
        "period",
        "operating_cash_flow",       # 经营活动现金流（OCF）
        "depreciation_amortization", # 折旧摊销
        "investing_cash_flow",       # 投资活动现金流
        "capital_expenditure",       # 资本支出（capex，通常为负）
        "financing_cash_flow",       # 筹资活动现金流
        "dividends_paid",            # 分红支付
        "net_change_in_cash",        # 净现金变动
        "free_cash_flow",            # 自由现金流（OCF + capex，已计算）
    ],
    "known_issues": [
        "数字单位：yfinance 返回原始值（美元/元），未做亿元换算，需自行除以 1e8",
        "A股/港股财报覆盖不如美股完整，部分字段可能为 None",
        "期间粒度固定为 annual（yfinance 不支持季度选项）",
        "部分非标准科目名称（如 Normalized EBITDA）可能导致字段为 None",
    ],
    "investment_use": [
        "3a财报体检：增长卡（revenue/net_income yoy）、盈利卡（gross_profit/operating_income margins）",
        "现金卡：free_cash_flow 连续性",
        "负债卡：total_debt / total_equity 计算 D/E ratio",
        "3b估值：EPS 历史序列 → 计算 EPS CAGR → DCF 增速假设参考",
    ],
}

# ─────────────────────────────────────────────
# 场景三：关键指标速查 get_financial_summary
# ─────────────────────────────────────────────
SCENARIO_SUMMARY = {
    "name": "关键指标速查（估值筛选用）",
    "tool": "mcp__finance-data__get_financial_summary",
    "params": {
        "symbol": "AAPL",
        "market": "US",
    },
    "return_fields": {
        "symbol":         "代码",
        "market":         "市场",
        "name":           "公司名称",
        "pe_ratio":       "市盈率（trailing PE 优先，fallback forward PE）",
        "pb_ratio":       "市净率",
        "dividend_yield": "股息率（小数，如 0.0058 表示 0.58%）",
        "eps":            "每股收益（trailing EPS）",
        "roe":            "净资产收益率（小数）",
        "market_cap":     "总市值（原始值，单位本币，未换算）",
        "52w_high":       "52周最高价",
        "52w_low":        "52周最低价",
        "beta":           "贝塔系数",
        "price":          "当前价格",
        "sector":         "行业板块（英文，主要对美股有效）",
        "industry":       "细分行业（英文）",
        "currency":       "币种",
        "source":         "数据源",
        "timestamp":      "时间戳",
    },
    "known_issues": [
        "dividend_yield 为小数（0.0058），展示时需 ×100 转为百分比",
        "market_cap 为原始数字（如 3000000000000），需 /1e8 换算为亿",
        "A股/港股 sector/industry 字段通常为空字符串",
        "pe_ratio 对亏损公司返回 None（无法计算）",
        "roe 为小数（0.156 表示 15.6%），展示时需 ×100",
    ],
    "investment_use": [
        "第3步估值分析：快速确认 PE/PB/股息率，对照 DCF 结论做合理性校验",
        "第2步林奇分类辅助：PE < 15 + 高股息率 → 稳定增长型信号",
        "否决门快速红线：PE > 50 且无增速支撑 → 预警",
    ],
}

# ─────────────────────────────────────────────
# 场景四：汇率 get_fx_rate
# ─────────────────────────────────────────────
SCENARIO_FX = {
    "name": "汇率获取",
    "tool": "mcp__finance-data__get_fx_rate",
    "params_examples": [
        {"from_currency": "USD", "to_currency": "CNY"},   # 美元兑人民币
        {"from_currency": "HKD", "to_currency": "CNY"},   # 港币兑人民币
        {"from_currency": "USD", "to_currency": "HKD"},   # 美元兑港币（跨市值折算）
    ],
    "return_fields": {
        "from":          "源货币代码（大写）",
        "to":            "目标货币代码（大写）",
        "rate":          "汇率（1单位 from = rate单位 to）",
        "source":        "实际使用数据源",
        "timestamp":     "时间戳",
        "sources_tried": "降级链路记录",
    },
    "routing_detail": [
        "1. exchangerate-api.com（free tier，无需key，最快）",
        "2. AKShare（新浪汇率接口）",
        "3. Alpha Vantage CURRENCY_EXCHANGE_RATE",
        "4. yfinance（{FROM}{TO}=X 格式，最慢）",
    ],
    "known_issues": [
        "exchangerate-api 免费版每日 1500 次，正常使用不会超限",
        "历史汇率不支持（只有实时快照），历史需手工提供",
        "加密货币对不支持（如 BTC/USD）",
    ],
    "investment_use": [
        "港股/中概市值换算为 CNY：price(HKD) × 总股本 / 1e8 × HKD/CNY",
        "美股市值换算为 CNY：market_cap(USD) × USD/CNY / 1e8",
        "跨市场估值对比时必须统一货币",
    ],
}

# ─────────────────────────────────────────────
# 代码格式速查表
# ─────────────────────────────────────────────
CODE_FORMAT_TABLE = """
┌──────────┬────────────────────────┬──────────────────────────────────────────────┐
│ 市场     │ symbol 格式            │ 备注                                         │
├──────────┼────────────────────────┼──────────────────────────────────────────────┤
│ A 股     │ 600519 / 000001        │ 纯6位数字，不含 sh/sz；Tushare内部加后缀     │
│ 港股     │ 00700 / 09988          │ 5位补零，不含 hk 前缀；AKShare内部处理       │
│ 美股     │ AAPL / NVDA / BABA     │ 大写 ticker，不含交易所后缀                  │
│ ETF      │ SPY / QQQ / 510300     │ 美国ETF同美股格式；A股ETF同A股格式           │
│ FX 汇率  │ USD / HKD / CNY / EUR  │ 3字母 ISO 4217，大写                         │
└──────────┴────────────────────────┴──────────────────────────────────────────────┘

各工具 market 参数枚举值：
  get_stock_price / get_financial_report / get_financial_summary:
    "US" | "HK" | "A" | "ETF"
  get_fx_rate:
    无 market 参数，只有 from_currency / to_currency
"""

# ─────────────────────────────────────────────
# finance-data vs stock-sdk 能力对比
# ─────────────────────────────────────────────
COMPARISON_WITH_STOCK_SDK = """
finance-data MCP 擅长：
  ✓ 三张财务报表（income/balance/cash_flow）→ 3a 财报体检核心数据源
  ✓ 关键估值指标（PE/PB/ROE/股息率/市值）→ 3b 估值快速校验
  ✓ 汇率实时快照（USD/CNY, HKD/CNY）→ 跨市值折算
  ✓ 美股覆盖质量好（Alpha Vantage + yfinance 双保险）

stock-sdk MCP 擅长：
  ✓ 日线/分钟K线 + 技术指标（MA/MACD/RSI）→ 趋势研判
  ✓ 资金流向（主力/散户净流入）→ 市场情绪辅助
  ✓ 行业/概念板块行情 → 比价参考
  ✓ A股分红历史（get_dividend_detail）→ 股息率趋势
  ✓ 实时行情响应快（腾讯/新浪接口）

互补使用建议：
  - 看价格/行情 → stock-sdk（更快）
  - 看财务报表/估值指标 → finance-data（更全）
  - 汇率 → finance-data get_fx_rate（exchangerate-api 更可靠）
  - A股分红 → stock-sdk get_dividend_detail（finance-data 无此接口）
"""

# ─────────────────────────────────────────────
# 投资SOP中的使用场景映射
# ─────────────────────────────────────────────
SOP_USE_CASES = {
    "第3步-3a财报体检": {
        "工具": "get_financial_report",
        "报表": ["income_statement", "balance_sheet", "cash_flow"],
        "重点字段": ["revenue", "net_income", "operating_cash_flow", "free_cash_flow",
                     "total_debt", "total_equity", "eps_diluted"],
        "注意": "数字为原始值，需手动换算（/1e8 = 亿）",
    },
    "第3步-3b估值分析": {
        "工具": "get_financial_summary",
        "重点字段": ["pe_ratio", "pb_ratio", "dividend_yield", "eps", "roe", "market_cap"],
        "注意": "pe_ratio 为 trailing PE，dividend_yield 为小数需×100",
    },
    "跨市值折算": {
        "工具": "get_fx_rate",
        "用法": "get_fx_rate(USD, CNY) + get_fx_rate(HKD, CNY)",
        "注意": "只有实时汇率，历史汇率需手工提供",
    },
    "第2步否决门-财务红线": {
        "工具": "get_financial_report（cash_flow）",
        "检查项": "free_cash_flow 连续3年为正 → 通过；持续为负 → 红线",
    },
}

if __name__ == "__main__":
    print("=== finance-data MCP 验证脚本 ===")
    print("本脚本为配置文档，请在 Claude Code 中调用对应 MCP 工具进行验证")
    print(CODE_FORMAT_TABLE)
    print(COMPARISON_WITH_STOCK_SDK)
