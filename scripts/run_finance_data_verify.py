#!/usr/bin/env python3
"""
finance-data MCP 数据源独立验证运行器
依赖: yfinance, akshare（pip install yfinance akshare）；exchangerate-api 无需安装
运行: python3 run_finance_data_verify.py

说明：finance-data MCP 底层使用 exchangerate-api / AKShare / Alpha Vantage / yfinance
     本脚本直接调用相同数据源，验证各通道可用性
适用于：无 Claude Code 环境时独立验证，或排查数据源故障
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime

# ─── 工具函数 ──────────────────────────────────

def fetch(url: str, timeout: int = 15, headers: dict = None) -> str:
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, */*",
    }
    if headers:
        default_headers.update(headers)
    req = urllib.request.Request(url, headers=default_headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def ok(label: str, value=None) -> None:
    suffix = f" → {value}" if value is not None else ""
    print(f"  ✓ {label}{suffix}")

def fail(label: str, reason: str = "") -> None:
    suffix = f"（{reason}）" if reason else ""
    print(f"  ✗ {label}{suffix}")

def warn(label: str, reason: str = "") -> None:
    suffix = f"：{reason}" if reason else ""
    print(f"  ⚠  {label}{suffix}")

def section(title: str) -> None:
    print(f"\n{'─'*58}")
    print(f"  {title}")
    print(f"{'─'*58}")

# ─── 场景一：汇率（exchangerate-api，无需 key）────────────

def verify_fx_exchangerate_api():
    section("场景 1 / 汇率 - exchangerate-api.com（finance-data 首选）")
    pairs = [("USD", "CNY"), ("HKD", "CNY"), ("USD", "HKD")]
    for from_c, to_c in pairs:
        url = f"https://open.er-api.com/v6/latest/{from_c}"
        try:
            raw = json.loads(fetch(url))
            if raw.get("result") == "success":
                rate = raw.get("rates", {}).get(to_c)
                if rate:
                    ok(f"{from_c}/{to_c}", f"汇率={rate:.4f}")
                else:
                    fail(f"{from_c}/{to_c}", f"{to_c} 不在返回的 rates 中")
            else:
                fail(f"{from_c}/{to_c}", raw.get("error-type", "未知错误"))
        except Exception as e:
            fail(f"{from_c}/{to_c}", str(e))

# ─── 场景二：yfinance 可用性（fallback 兜底）──────────────

def verify_yfinance():
    section("场景 2 / yfinance 可用性（finance-data 最终 fallback）")
    try:
        import yfinance as yf
        ok("yfinance 已安装")
        # 测试美股
        try:
            t = yf.Ticker("AAPL")
            info = t.info
            price = info.get("regularMarketPrice") or info.get("currentPrice")
            if price:
                ok("AAPL 价格可获取", f"${price}")
            else:
                warn("AAPL 返回空价格", "Yahoo 可能限速，稍后再试")
        except Exception as e:
            fail("AAPL yfinance 请求", str(e))

        # 测试港股（格式：0700.HK）
        try:
            t = yf.Ticker("0700.HK")
            info = t.info
            price = info.get("regularMarketPrice") or info.get("currentPrice")
            if price:
                ok("腾讯 0700.HK 价格可获取", f"HKD {price}")
            else:
                warn("0700.HK 返回空价格", "Yahoo 可能限速")
        except Exception as e:
            fail("0700.HK yfinance 请求", str(e))

        # 测试汇率
        try:
            t = yf.Ticker("USDCNY=X")
            info = t.info
            rate = info.get("regularMarketPrice") or info.get("previousClose")
            if rate:
                ok("USD/CNY yfinance", f"汇率≈{rate:.4f}")
            else:
                warn("USD/CNY yfinance 返回空", "Yahoo 可能限速")
        except Exception as e:
            fail("USD/CNY yfinance", str(e))

    except ImportError:
        fail("yfinance 未安装", "请运行: pip install yfinance")

# ─── 场景三：AKShare 可用性（A股/港股 primary）───────────

def verify_akshare():
    section("场景 3 / AKShare 可用性（A股/港股 primary 数据源）")
    try:
        import akshare as ak
        ok("akshare 已安装")

        # 测试 A 股实时行情
        try:
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                row = df[df["代码"] == "600519"]
                if not row.empty:
                    price = row.iloc[0].get("最新价")
                    ok("贵州茅台 600519 可获取", f"¥{price}")
                else:
                    ok(f"A股行情接口正常（返回 {len(df)} 条记录）")
            else:
                fail("A股行情接口返回空")
        except Exception as e:
            fail("A股实时行情 stock_zh_a_spot_em", str(e))

        # 测试港股实时行情
        try:
            df = ak.stock_hk_spot_em()
            if df is not None and not df.empty:
                ok(f"港股行情接口正常（返回 {len(df)} 条记录）")
            else:
                fail("港股行情接口返回空")
        except Exception as e:
            fail("港股实时行情 stock_hk_spot_em", str(e))

        # 测试 A 股财务指标（估值用）
        try:
            df = ak.stock_a_lg_indicator(symbol="600519")
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                pe = latest.get("pe") or latest.get("市盈率") or "N/A"
                ok("600519 财务指标可获取", f"PE≈{pe}")
            else:
                fail("600519 财务指标返回空")
        except Exception as e:
            fail("A股财务指标 stock_a_lg_indicator", str(e))

    except ImportError:
        fail("akshare 未安装", "请运行: pip install akshare")

# ─── 场景四：Alpha Vantage 配额检查 ──────────────────────

def verify_alpha_vantage():
    section("场景 4 / Alpha Vantage 配额与连通性")
    try:
        import os
        # 尝试读取 .env 中的 API key
        env_path = "/Users/sophia/Documents/Angelia/code/cursor/finance-tools/finance-data-mcp/.env"
        api_key = None
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ALPHA_VANTAGE_API_KEY") and "=" in line:
                        api_key = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass

        if not api_key or api_key.startswith("#"):
            warn("ALPHA_VANTAGE_API_KEY 未配置", "跳过 Alpha Vantage 验证")
            print("  ℹ  配置路径:", env_path)
            return

        ok(f"API Key 已配置（末尾: ...{api_key[-6:]}）")

        # 测试接口连通性（AAPL 报价，使用 GLOBAL_QUOTE）
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
        )
        try:
            raw = json.loads(fetch(url, timeout=15))
            if "Global Quote" in raw:
                q = raw["Global Quote"]
                price = q.get("05. price")
                if price:
                    ok("AAPL Alpha Vantage", f"${price}")
                else:
                    warn("AAPL 返回空价格", "可能为配额耗尽或 key 无效")
            elif "Note" in raw:
                warn("Alpha Vantage 请求限速", raw.get("Note", "")[:80])
            elif "Information" in raw:
                warn("Alpha Vantage 提示", raw.get("Information", "")[:80])
            else:
                fail("Alpha Vantage 响应格式异常", str(raw)[:100])
        except Exception as e:
            fail("Alpha Vantage 请求", str(e))

    except Exception as e:
        fail("Alpha Vantage 检查", str(e))

# ─── 场景五：finance-data 财务报表底层（yfinance）验证 ────

def verify_financial_report():
    section("场景 5 / 财务报表底层数据（yfinance income_stmt）")
    try:
        import yfinance as yf
        t = yf.Ticker("AAPL")
        df = t.income_stmt
        if df is not None and not df.empty:
            cols = list(df.columns[:3])
            ok(f"AAPL 利润表返回 {len(cols)} 个报告期")
            for col in cols:
                try:
                    import pandas as pd
                    label = pd.Timestamp(col).strftime("%Y") if hasattr(col, "year") else str(col)[:10]
                except Exception:
                    label = str(col)[:10]
                revenue_keys = ["Total Revenue", "Revenue", "TotalRevenue"]
                rev = None
                for k in revenue_keys:
                    if k in df.index:
                        v = df.loc[k, col]
                        try:
                            rev = float(v)
                        except Exception:
                            pass
                        break
                if rev:
                    ok(f"  {label} 营收", f"${rev/1e9:.1f}B")
                else:
                    warn(f"  {label} 营收字段为 None")
        else:
            fail("AAPL income_stmt 返回空")
    except ImportError:
        fail("yfinance 未安装，跳过财务报表验证")
    except Exception as e:
        fail("财务报表获取", str(e))

# ─── 场景六：财务摘要（financial_summary）验证 ────────────

def verify_financial_summary():
    section("场景 6 / 关键指标摘要（get_financial_summary 底层）")
    try:
        import yfinance as yf
        import math

        def sf(v):
            try:
                f = float(v)
                return None if (math.isnan(f) or math.isinf(f)) else f
            except Exception:
                return None

        t = yf.Ticker("AAPL")
        info = t.info
        if not info:
            fail("AAPL info 返回空")
            return
        pe = sf(info.get("trailingPE") or info.get("forwardPE"))
        pb = sf(info.get("priceToBook"))
        dy = sf(info.get("dividendYield"))
        roe = sf(info.get("returnOnEquity"))
        mktcap = sf(info.get("marketCap"))
        ok("AAPL 关键指标可获取")
        ok("  PE（trailing）", pe)
        ok("  PB", pb)
        ok("  股息率", f"{dy*100:.2f}%" if dy else "N/A")
        ok("  ROE", f"{roe*100:.1f}%" if roe else "N/A")
        ok("  市值", f"${mktcap/1e12:.2f}T" if mktcap else "N/A")
    except ImportError:
        fail("yfinance 未安装，跳过摘要验证")
    except Exception as e:
        fail("关键指标摘要", str(e))

# ─── 汇总 ─────────────────────────────────────────────────

def main():
    print("=" * 58)
    print("  finance-data MCP 数据源验证报告")
    print(f"  验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 58)

    verify_fx_exchangerate_api()
    verify_yfinance()
    verify_akshare()
    verify_alpha_vantage()
    verify_financial_report()
    verify_financial_summary()

    print(f"\n{'='*58}")
    print("  验证完成")
    print(f"{'='*58}")
    print("""
已验证场景：
  1. 汇率           → exchangerate-api（免费首选）USD/CNY, HKD/CNY
  2. yfinance       → fallback 兜底（美股/港股/A股/FX）
  3. AKShare        → A股/港股 primary 数据源
  4. Alpha Vantage  → 美股/ETF primary 数据源（配额25次/天/key）
  5. 财务报表       → yfinance income_stmt（三表核心）
  6. 关键指标       → yfinance PE/PB/ROE/股息率/市值

已知问题：
  ⚠  yfinance 请求间隔 ≥10秒（Yahoo 限速），多次连续调用较慢
  ⚠  Alpha Vantage 免费额度 25次/天，多 key 轮换可扩大配额
  ⚠  finance-data 不含 K线/技术指标/分红历史 → 用 stock-sdk 补充
  ⚠  财务数字为原始值（元/美元），展示需除以 1e8 转换为亿

代码格式速查：
  A股    → symbol='600519'，market='A'
  港股   → symbol='00700'，market='HK'
  美股   → symbol='AAPL'，market='US'
  ETF    → symbol='SPY'，market='ETF'
  汇率   → from_currency='USD'，to_currency='CNY'
""")

if __name__ == "__main__":
    main()
