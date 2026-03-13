---
name: paper-trading
description: 模拟仓管理。买入、卖出、查持仓、盈亏分析、交易历史。触发词：模拟仓、paper trading、买入、卖出、持仓、收益、盈亏
---

# 模拟仓管理 (Paper Trading)

你是一位模拟仓管理助手。所有账本操作通过调用 `portfolio.py` CLI 完成，数据存储于 SQLite。

## CLI 工具路径

```
.claude/skills/paper-trading/portfolio.py
```

> 始终使用此相对路径（相对于项目根目录）调用，例如：
> `python .claude/skills/paper-trading/portfolio.py <命令>`

---

## 命令速查

| 功能 | 命令 |
|---|---|
| 初始化账本 | `python .claude/skills/paper-trading/portfolio.py init [--capital 1000000]` |
| 买入 | `python .claude/skills/paper-trading/portfolio.py buy <code> <qty> <price> --market <A\|HK\|US> [--note "..."]` |
| 卖出 | `python .claude/skills/paper-trading/portfolio.py sell <code> <qty> <price> --market <A\|HK\|US>` |
| 查持仓 | `python .claude/skills/paper-trading/portfolio.py positions` |
| 持仓+实时浮盈 | `python .claude/skills/paper-trading/portfolio.py positions --live` |
| 盈亏分析 | `python .claude/skills/paper-trading/portfolio.py pnl [--code <code>]` |
| 交易历史 | `python .claude/skills/paper-trading/portfolio.py history [--code <code>] [--n 20]` |
| 每日快照 | `python .claude/skills/paper-trading/portfolio.py snapshot` |
| 查现金余额 | `python .claude/skills/paper-trading/portfolio.py cash` |

---

## 手续费规则（自动计算）

| 市场 | 买入 | 卖出 |
|---|---|---|
| A股 | 0.03%（最低¥5） | 0.03%（最低¥5）+ 印花税0.1% |
| 港股 | 0.1% + HKD30规费 | 0.1% + HKD30规费 |
| 美股 | 0（免佣） | 0（免佣） |

用 `--fee <金额>` 可手动覆盖。

---

## 代码格式规范

| 市场 | 格式 | 示例 |
|---|---|---|
| A股 | 纯数字 | `600519` |
| 港股 | 5位数字 | `00700` |
| 美股 | 字母代码 | `AAPL` |

---

## 工作流程

### 查看持仓（含实时浮盈）

```
1. 运行: python .claude/skills/paper-trading/portfolio.py positions
2. 获取持仓代码列表（按市场分组）
3. 调用 MCP 获取实时价格：
   - A股: mcp__stock-sdk__get_a_share_quotes  codes=["sh600519"]
   - 港股: mcp__stock-sdk__get_hk_quotes       codes=["00700"]
   - 美股: mcp__stock-sdk__get_us_quotes       codes=["AAPL"]
4. 计算每个持仓的浮盈/浮亏/仓位权重
5. 输出 Markdown 持仓表（含总资产、总浮盈、各仓位占比）
```

### 买入操作

```
用户: "买入茅台100股，价格1500元"
→ 确认: 代码=600519, 数量=100, 价格=1500, 市场=A
→ 执行: python .claude/skills/paper-trading/portfolio.py buy 600519 100 1500 --market A
→ 输出: 买入确认 + 手续费 + 剩余现金
```

### 卖出操作

```
用户: "卖出腾讯200股，价格380港元"
→ 确认: 代码=00700, 数量=200, 价格=380, 市场=HK
→ 执行: python .claude/skills/paper-trading/portfolio.py sell 00700 200 380 --market HK
→ 输出: 卖出确认 + 本次实现盈亏 + 剩余现金
```

---

## 持仓报告格式

执行 `positions --live` 流程后，输出以下格式：

```markdown
## 模拟仓持仓报告 — YYYY-MM-DD

### 持仓明细

| 代码 | 市场 | 名称 | 持仓 | 均价 | 现价 | 市值 | 浮盈 | 涨幅 | 占比 |
|---|---|---|---|---|---|---|---|---|---|
| 600519 | A | 贵州茅台 | 100 | 1500 | 1520 | 152,000 | +2,000 | +1.33% | 15.2% |

### 资产概览

| 项目 | 金额 |
|---|---|
| 持仓市值 | xxx,xxx |
| 现金余额 | xxx,xxx |
| 总资产 | xxx,xxx |
| 总浮盈 | +/-xxx |
| 总收益率 | +/-x.xx% |
```

---

## 注意事项

- 数据库路径: `data/portfolio.db`（相对于项目根）
- 所有金额单位默认 CNY；港股以 HKD 记录，美股以 USD 记录
- `--live` 实时价格需通过 Claude 调用 MCP 获取，不在 CLI 内直接调用网络
- 若需重置账本，运行 `init` 命令并手动删除旧数据库
