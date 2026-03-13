#!/usr/bin/env python3
"""
MCP 数据获取验证脚本
用途：验证 stock-sdk MCP 在不同市场/场景下的数据获取能力
运行方式：在 Claude Code 中直接阅读本脚本，或让 Claude 逐块调用 MCP 工具
注意：本脚本为"调用说明 + 结果模板"，需在 Claude Code 环境下执行 MCP 工具

当前可用 MCP: stock-sdk, finance-data
finance-data 工具: get_stock_price / get_financial_report / get_financial_summary / get_fx_rate
finance-data 路径: /Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/finance_data_server.py

验证日期: 2026-03-11
"""

# ─────────────────────────────────────────────
# 场景一：A股实时行情
# ─────────────────────────────────────────────
SCENARIO_A = {
    "name": "A股实时行情",
    "tool": "mcp__stock-sdk__get_a_share_quotes",
    "params": {
        "codes": ["sh600519", "sz000858", "sh000001"]
        # 格式: sh=上交所, sz=深交所; 指数同样支持
    },
    "key_fields": [
        "name",          # 股票名称
        "code",          # 代码
        "price",         # 最新价（CNY）
        "change",        # 涨跌额
        "changePercent", # 涨跌幅 %
        "pe",            # 市盈率（动态）
        "peStatic",      # 市盈率（静态/TTM）
        "pb",            # 市净率
        "totalMarketCap",      # 总市值（亿元）
        "circulatingMarketCap",# 流通市值
        "turnoverRate",  # 换手率 %
        "high52w",       # 52周最高
        "low52w",        # 52周最低
        "volume",        # 成交量（手）
        "amount",        # 成交额（万元）
        "time",          # 行情时间戳 YYYYMMDDHHMMSS
    ],
    "validation": [
        "price > 0",
        "time 非空",
        "pe > 0（指数可能为 None）",
        "市值单位为亿元 CNY",
    ],
    "known_issues": [],
}

# ─────────────────────────────────────────────
# 场景二：港股实时行情
# ─────────────────────────────────────────────
SCENARIO_HK = {
    "name": "港股实时行情",
    "tool": "mcp__stock-sdk__get_hk_quotes",
    "params": {
        "codes": ["00700", "09988", "03690"]
        # 格式: 5位数字补零，不需要前缀
    },
    "key_fields": [
        "name",          # 股票名称（中文）
        "code",          # 代码
        "price",         # 最新价（HKD）
        "currency",      # 币种：HKD
        "change",        # 涨跌额
        "changePercent", # 涨跌幅 %
        "totalMarketCap",      # 总市值（亿港元）
        "circulatingMarketCap",# 流通市值
        "high52w",       # 52周最高（在 raw 中）
        "low52w",        # 52周最低（在 raw 中）
        "volume",        # 成交量（股）
        "amount",        # 成交额（港元）
        "time",          # 行情时间 YYYY/MM/DD HH:MM:SS
    ],
    "validation": [
        "price > 0",
        "currency == 'HKD'",
        "time 格式 YYYY/MM/DD HH:MM:SS（与A股不同）",
        "注意：港股没有 pe/pb 顶层字段，需从 raw 提取",
    ],
    "known_issues": [
        "pe/pb 字段在 raw[] 中，顶层结构比 A股 字段少",
        "bid/ask 档位数据不返回（港股）",
    ],
}

# ─────────────────────────────────────────────
# 场景三：美股实时行情
# ─────────────────────────────────────────────
SCENARIO_US = {
    "name": "美股实时行情",
    "tool": "mcp__stock-sdk__get_us_quotes",
    "params": {
        "codes": ["AAPL", "BABA", "NVDA"]
        # 格式: ticker 大写，不需要交易所后缀（返回时自动带 .OQ/.N）
    },
    "key_fields": [
        "name",          # 公司英文全称
        "code",          # 代码（含后缀，如 AAPL.OQ）
        "price",         # 最新价（USD）
        "change",        # 涨跌额
        "changePercent", # 涨跌幅 %
        "pe",            # 市盈率
        "pb",            # 市净率
        "totalMarketCap",      # 总市值（亿美元）
        "high52w",       # 52周最高（USD）
        "low52w",        # 52周最低（USD）
        "volume",        # 成交量（股）
        "amount",        # 成交额（USD）
        "time",          # 行情时间 YYYY-MM-DD HH:MM:SS（美东时间）
        "turnoverRate",  # 换手率
    ],
    "validation": [
        "price > 0",
        "time 格式 YYYY-MM-DD HH:MM:SS（与 A/H 不同）",
        "市值单位为亿美元",
        "注意：美股盘前/盘后价格可能与 price 不同",
    ],
    "known_issues": [
        "返回的 code 带交易所后缀（AAPL.OQ）与输入不同",
        "bid/ask 不返回",
    ],
}

# ─────────────────────────────────────────────
# 场景四：历史 K 线（日线）
# ─────────────────────────────────────────────
SCENARIO_KLINE_A = {
    "name": "A股历史K线",
    "tool": "mcp__stock-sdk__get_history_kline",
    "params": {
        "symbol": "600519",         # 纯数字代码
        "period": "daily",
        "adjust": "qfq",            # 前复权
        "startDate": "20250101",
        "endDate": "20260311",
    },
    "key_fields": ["date", "open", "high", "low", "close", "volume", "amount", "amplitude", "changePercent", "change", "turnoverRate"],
    "validation": [
        "返回列表，每条为一个交易日",
        "close 为前复权价格",
    ],
    "known_issues": [],
}

SCENARIO_KLINE_HK = {
    "name": "港股历史K线",
    "tool": "mcp__stock-sdk__get_hk_history_kline",
    "params": {
        "symbol": "00700",
        "period": "daily",
        "adjust": "qfq",
        "startDate": "20250101",
        "endDate": "20260311",
    },
    "key_fields": ["date", "open", "high", "low", "close", "volume"],
    "validation": ["港股专用接口，代码格式同实时行情"],
    "known_issues": [],
}

SCENARIO_KLINE_US = {
    "name": "美股历史K线",
    "tool": "mcp__stock-sdk__get_us_history_kline",
    "params": {
        "symbol": "105.AAPL",       # 美股代码格式：{market_id}.{ticker}
        "period": "daily",
        "adjust": "qfq",
        "startDate": "20250101",
        "endDate": "20260311",
    },
    "key_fields": ["date", "open", "high", "low", "close", "volume"],
    "validation": [
        "注意：美股代码格式为 105.AAPL（纳斯达克）或 106.XX（NYSE）",
        "也可直接用 get_kline_with_indicators 并指定 market='US'",
    ],
    "known_issues": [
        "美股代码需要带市场前缀 105./106.，与实时行情不同",
    ],
}

# ─────────────────────────────────────────────
# 场景五：带技术指标的 K 线（统一接口，支持三市场）
# ─────────────────────────────────────────────
SCENARIO_KLINE_WITH_INDICATORS = {
    "name": "带技术指标K线（统一接口）",
    "tool": "mcp__stock-sdk__get_kline_with_indicators",
    "params_a": {
        "symbol": "600519",
        "market": "A",
        "period": "daily",
        "adjust": "qfq",
        "startDate": "20250601",
        "endDate": "20260311",
        "indicators": {
            "ma": {"periods": [20, 60, 120]},
            "macd": True,
            "rsi": {"periods": [6, 14]},
        }
    },
    "params_hk": {
        "symbol": "00700",
        "market": "HK",
        "period": "daily",
        "adjust": "qfq",
        "startDate": "20250601",
        "endDate": "20260311",
        "indicators": {"ma": True, "macd": True}
    },
    "params_us": {
        "symbol": "AAPL",           # 此接口支持直接用 ticker，无需 105. 前缀
        "market": "US",
        "period": "daily",
        "adjust": "qfq",
        "startDate": "20250601",
        "endDate": "20260311",
        "indicators": {"ma": True, "rsi": True}
    },
    "key_fields": ["date", "close", "indicators.ma", "indicators.macd", "indicators.rsi"],
    "validation": [
        "此接口自动处理指标计算所需的历史数据，推荐优先使用",
        "market 参数可自动识别，显式指定更安全",
    ],
    "known_issues": [],
}

# ─────────────────────────────────────────────
# 场景六：财务数据（分红历史）
# ─────────────────────────────────────────────
SCENARIO_DIVIDEND = {
    "name": "分红派息历史",
    "tool": "mcp__stock-sdk__get_dividend_detail",
    "params": {
        "symbol": "600519"          # 纯数字代码，仅支持 A 股
    },
    "key_fields": [
        "reportDate",         # 报告期
        "dividendPretax",     # 每10股派息（含税，元）
        "dividendYield",      # 股息率
        "eps",                # 每股收益
        "bps",                # 每股净资产
        "netProfitYoy",       # 净利同比增速 %
        "totalShares",        # 总股本
        "exDividendDate",     # 除权日
        "assignProgress",     # 进度（实施分配/预案等）
    ],
    "validation": [
        "返回结构: {total: N, data: [...]}",
        "数据从上市以来全量，按时间倒序",
        "dividendPretax 为每10股派息金额",
        "股息率 = dividendYield（已计算好）",
    ],
    "known_issues": [
        "仅支持 A 股，港股/美股暂无分红接口",
        "payDate（实际派息日）字段通常为 null",
    ],
    "investment_use": [
        "计算股息率趋势",
        "验证派息连续性（稳定增长型公司护城河指标）",
        "EPS 历史序列可辅助计算增速 CAGR",
    ],
}

# ─────────────────────────────────────────────
# 场景七：资金流向
# ─────────────────────────────────────────────
SCENARIO_FUND_FLOW = {
    "name": "资金流向",
    "tool": "mcp__stock-sdk__get_fund_flow",
    "params": {
        "codes": ["600519", "000858"]
        # ⚠️ 注意: 经测试，带 sh/sz 前缀会导致解析异常，请用纯数字代码
    },
    "key_fields": [
        "mainInflow",     # 主力流入（元）
        "mainOutflow",    # 主力流出
        "mainNet",        # 主力净流入
        "mainNetRatio",   # 主力净流入占总成交额比例 %
        "retailInflow",   # 散户流入
        "retailOutflow",  # 散户流出
        "retailNet",      # 散户净流入
        "totalFlow",      # 总资金流动
        "date",           # 日期
    ],
    "validation": [
        "仅支持 A 股",
        "代码格式：纯数字（不含 sh/sz 前缀）",
    ],
    "known_issues": [
        "⚠️ BUG：传入 sh600519 格式时，仅解析到市场ID '1'，数据全为0",
        "⚠️ 修复方案：改用纯数字代码 ['600519', '000858']",
        "数据为当日截面，不含历史时序",
    ],
}

# ─────────────────────────────────────────────
# 场景八：股票搜索（代码确认）
# ─────────────────────────────────────────────
SCENARIO_SEARCH = {
    "name": "股票搜索",
    "tool": "mcp__stock-sdk__search_stock",
    "params_examples": [
        {"keyword": "茅台"},
        {"keyword": "00700"},
        {"keyword": "AAPL"},
    ],
    "key_fields": ["code", "name", "market", "type"],
    "validation": ["返回 A/H/US 混合结果，需按市场筛选"],
    "known_issues": [],
}

# ─────────────────────────────────────────────
# 缺失数据清单（finance-data MCP 未接入）
# ─────────────────────────────────────────────
FINANCE_DATA_MCP = {
    "mcp": "finance-data（已配置，重启 Claude Code 后生效）",
    "server": "/Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/finance_data_server.py",
    "venv": "/Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/.venv/bin/python3",
    "tools": {
        "get_stock_price": {
            "用途": "A/H/US 实时价格（含 change/change_pct/volume 等）",
            "路由": "A股→Tushare→AKShare→yfinance；US→AlphaVantage→yfinance；HK→AKShare→yfinance",
        },
        "get_financial_report": {
            "用途": "财务报表（income_statement/balance_sheet/cash_flow）",
            "参数": "symbol, market, report_type, period(annual/quarterly)",
        },
        "get_financial_summary": {
            "用途": "关键指标（PE/PB/ROE/市值/EPS/股息率）",
            "参数": "symbol, market",
        },
        "get_fx_rate": {
            "用途": "汇率（USD/CNY, HKD/CNY 等）",
            "路由": "exchangerate-api → AKShare → AlphaVantage → yfinance",
        },
    },
    "still_missing": [
        "宏观数据（CPI/PMI/国债收益率/VIX）→ 手工提供",
        "卖方一致预期 → 手工提供研报摘录",
        "行业 PE/PB 历史分位 → 理杏仁/Choice 手工查询",
    ],
}

# ─────────────────────────────────────────────
# 代码格式速查表
# ─────────────────────────────────────────────
CODE_FORMAT_TABLE = """
┌──────────┬────────────────────────────────┬──────────────────────┬─────────────────────────────┐
│ 市场     │ 实时行情                       │ 历史K线              │ 带指标K线 / 资金流向        │
├──────────┼────────────────────────────────┼──────────────────────┼─────────────────────────────┤
│ A 股     │ sh600519 / sz000858            │ 600519（纯数字）     │ 600519 + market='A'         │
│          │ （get_a_share_quotes）         │ （get_history_kline）│ 资金流向同纯数字            │
├──────────┼────────────────────────────────┼──────────────────────┼─────────────────────────────┤
│ 港股     │ 00700（5位补零，无前缀）       │ 00700                │ 00700 + market='HK'         │
│          │ （get_hk_quotes）              │（get_hk_history_kline│                             │
├──────────┼────────────────────────────────┼──────────────────────┼─────────────────────────────┤
│ 美股     │ AAPL（大写 ticker）            │ 105.AAPL             │ AAPL + market='US'          │
│          │ （get_us_quotes）              │（get_us_history_kline│ （指标接口自动识别）        │
└──────────┴────────────────────────────────┴──────────────────────┴─────────────────────────────┘

注意事项：
- 资金流向 get_fund_flow：只用纯数字 A 股代码，带前缀会导致数据全零 BUG
- 美股历史K线 get_us_history_kline：需要 105.（纳斯达克）或 106.（NYSE）前缀
- get_kline_with_indicators：统一接口，推荐优先使用，美股直接传 AAPL 即可
"""

if __name__ == "__main__":
    print("=== MCP 数据验证脚本 ===")
    print("本脚本为配置文档，请在 Claude Code 中调用对应 MCP 工具进行验证")
    print(CODE_FORMAT_TABLE)
    print(f"\n⚠️  缺失 MCP: {MISSING_DATA['mcp']}")
    print("缺失数据场景：")
    for item in MISSING_DATA["missing_scenarios"]:
        print(f"  - {item['数据']}: {item['用途']}")
        print(f"    临时替代: {item['临时替代']}")
