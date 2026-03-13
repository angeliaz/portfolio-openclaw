# tools/ 使用说明

本目录包含两套 MCP 数据工具的参考手册与独立验证脚本。

---

## 文件一览

| 文件 | 对应 MCP | 类型 | 需要运行？ |
|------|----------|------|-----------|
| `verify_mcp_data.py` | stock-sdk | 参考手册 | 否 |
| `run_data_verify.py` | stock-sdk | 独立验证脚本 | 是 |
| `verify_finance_data.py` | finance-data | 参考手册 | 否 |
| `run_finance_data_verify.py` | finance-data | 独立验证脚本 | 是 |

---

## stock-sdk MCP（行情 / K线 / 资金流向）

### `verify_mcp_data.py` — 参考手册（Claude 调用时查这里）

不需要运行。是给 Claude 看的数据契约文档，定义了：
- 每个工具的正确调用参数（A/H/US 三市场）
- 各市场代码格式规范（最核心的速查表）
- 已知 bug（如 `get_fund_flow` 不能带 `sh/sz` 前缀）

**使用方式**：告诉 Claude「帮我查 XX 的行情/K线/分红」，Claude 会参照此文档用正确格式调用 MCP 工具。

### `run_data_verify.py` — 独立验证脚本

直接请求新浪/腾讯/东方财富公开接口，验证数据源是否可用。无需额外安装依赖。

```bash
cd /Users/sophia/Documents/Angelia/code/cursor/investment-sop/tools
python3 run_data_verify.py
```

**使用场景**：怀疑数据拉不到、或想确认某个接口还在工作时运行。

**验证内容**：A股实时行情、港股实时行情、美股实时行情、A/H/US 历史K线、分红数据、汇率（新浪临时方案）。

---

## finance-data MCP（财务报表 / 估值指标 / 汇率）

### `verify_finance_data.py` — 参考手册（Claude 调用时查这里）

不需要运行。是给 Claude 看的数据契约文档，定义了：
- 四个工具的调用参数与返回字段（`get_stock_price` / `get_financial_report` / `get_financial_summary` / `get_fx_rate`）
- 数据源路由优先级（exchangerate-api → AKShare → Alpha Vantage → yfinance）
- 字段注意事项（如 `dividend_yield` 是小数、`market_cap` 未换算需 `/1e8`）
- 投资 SOP 步骤到工具的映射（3a财报体检、3b估值、跨市值折算）

**使用方式**：告诉 Claude「帮我查 AAPL 的财务报表/PE/汇率」，Claude 会参照此文档调用 finance-data MCP。

### `run_finance_data_verify.py` — 独立验证脚本

需要在虚拟环境中安装依赖：

```bash
cd /Users/sophia/Documents/Angelia/code/cursor/investment-sop/tools
python3 -m venv .venv
source .venv/bin/activate
pip install yfinance akshare
```

运行：

```bash
python3 run_finance_data_verify.py
```

运行结束后可退出虚拟环境：

```bash
deactivate
```

**使用场景**：怀疑 finance-data MCP 某个数据源挂了时，用此脚本定位是哪一层出问题。

**验证内容**：exchangerate-api 汇率、yfinance 可用性（美股/港股/汇率）、AKShare 可用性（A股/港股）、Alpha Vantage 配额与连通性、财务报表（income_stmt）、关键指标（PE/PB/ROE）。

---

## 两套 MCP 分工速查

| 需求 | 用哪个 MCP |
|------|-----------|
| 实时行情（价格/涨跌/市值）| stock-sdk（更快） |
| 历史K线 + 技术指标 | stock-sdk |
| 资金流向（主力/散户）| stock-sdk |
| A股分红历史 | stock-sdk `get_dividend_detail` |
| 三张财务报表（收入/资产/现金流）| finance-data `get_financial_report` |
| PE/PB/ROE/股息率 估值指标 | finance-data `get_financial_summary` |
| 汇率（USD/CNY, HKD/CNY）| finance-data `get_fx_rate` |

---

## 代码格式速查

### stock-sdk

| 市场 | 实时行情 | 历史K线 | 资金流向 |
|------|---------|---------|---------|
| A股 | `sh600519` / `sz000858` | `600519`（纯数字）| `600519`（纯数字）|
| 港股 | `00700`（5位补零）| `00700` | — |
| 美股 | `AAPL`（大写）| `105.AAPL`（纳斯达克）| — |

注意：`get_fund_flow` 带 `sh/sz` 前缀会导致数据全零 bug，只用纯数字。

### finance-data

| 市场 | symbol 格式 | market 参数 |
|------|------------|------------|
| A股 | `600519` | `"A"` |
| 港股 | `00700` | `"HK"` |
| 美股 | `AAPL` | `"US"` |
| ETF | `SPY` / `510300` | `"ETF"` |
| 汇率 | `from_currency="USD"` | `to_currency="CNY"` |
