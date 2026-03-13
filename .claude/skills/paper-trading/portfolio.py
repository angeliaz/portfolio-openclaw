#!/usr/bin/env python3
"""
模拟仓 CLI 工具 — portfolio.py
数据库: data/portfolio.db (相对于项目根目录)

用法:
  portfolio.py init [--capital 1000000]
  portfolio.py buy <code> <qty> <price> --market <A|HK|US> [--fee <n>] [--note <text>]
  portfolio.py sell <code> <qty> <price> --market <A|HK|US> [--fee <n>] [--note <text>]
  portfolio.py positions [--live]
  portfolio.py pnl [--code <code>]
  portfolio.py history [--code <code>] [--n 20]
  portfolio.py snapshot
  portfolio.py cash
"""

import argparse
import sqlite3
import sys
import os
from datetime import date
from pathlib import Path


# ─── 数据库路径（项目根/data/portfolio.db）────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # skills/paper-trading → skills → .claude → project root
DB_PATH = PROJECT_ROOT / "data" / "portfolio.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))


def init_db(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS config (
        key   TEXT PRIMARY KEY,
        value TEXT
    );
    CREATE TABLE IF NOT EXISTS trades (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_date TEXT,
        code       TEXT,
        market     TEXT,
        name       TEXT,
        direction  TEXT,
        price      REAL,
        quantity   INTEGER,
        amount     REAL,
        fee        REAL DEFAULT 0,
        note       TEXT
    );
    CREATE TABLE IF NOT EXISTS positions (
        code       TEXT PRIMARY KEY,
        market     TEXT,
        name       TEXT,
        quantity   INTEGER,
        avg_cost   REAL,
        total_cost REAL,
        buy_thesis TEXT
    );
    CREATE TABLE IF NOT EXISTS snapshots (
        snap_date      TEXT PRIMARY KEY,
        total_value    REAL,
        cash_balance   REAL,
        unrealized_pnl REAL,
        realized_pnl   REAL
    );
    """)
    conn.commit()


# ─── 手续费估算 ───────────────────────────────────────────────────────────────
def calc_fee(market: str, direction: str, amount: float) -> float:
    if market == "A":
        base = amount * 0.0003
        fee = max(base, 5.0)
        if direction == "SELL":
            fee += amount * 0.001  # 印花税
        return round(fee, 2)
    elif market == "HK":
        return round(amount * 0.001 + 30, 2)  # 0.1% + HKD30规费
    else:  # US
        return 0.0


# ─── 获取现金余额 ─────────────────────────────────────────────────────────────
def get_cash(conn) -> float:
    row = conn.execute("SELECT value FROM config WHERE key='cash_balance'").fetchone()
    if row:
        return float(row[0])
    return 0.0


def set_cash(conn, cash: float):
    conn.execute("INSERT OR REPLACE INTO config (key,value) VALUES ('cash_balance', ?)", (str(cash),))


# ─── 命令实现 ─────────────────────────────────────────────────────────────────
def cmd_init(args):
    capital = args.capital
    conn = get_conn()
    init_db(conn)
    conn.execute("INSERT OR REPLACE INTO config VALUES ('initial_capital', ?)", (str(capital),))
    conn.execute("INSERT OR REPLACE INTO config VALUES ('cash_balance', ?)", (str(capital),))
    conn.execute("INSERT OR REPLACE INTO config VALUES ('start_date', ?)", (str(date.today()),))
    conn.execute("INSERT OR REPLACE INTO config VALUES ('currency', 'CNY')")
    conn.commit()
    print(f"✅ 模拟仓已初始化")
    print(f"   初始资金: ¥{capital:,.2f}")
    print(f"   起始日期: {date.today()}")
    print(f"   数据库: {DB_PATH}")


def cmd_buy(args):
    conn = get_conn()
    init_db(conn)
    cash = get_cash(conn)

    amount = args.price * args.qty
    fee = args.fee if args.fee is not None else calc_fee(args.market, "BUY", amount)
    total_cost = amount + fee

    if total_cost > cash:
        print(f"❌ 资金不足！需要 ¥{total_cost:,.2f}，当前现金 ¥{cash:,.2f}")
        sys.exit(1)

    today = str(date.today())
    name = args.name or args.code

    # 记录交易
    conn.execute(
        "INSERT INTO trades (trade_date,code,market,name,direction,price,quantity,amount,fee,note) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (today, args.code, args.market, name, "BUY", args.price, args.qty, amount, fee, args.note or "")
    )

    # 更新持仓
    row = conn.execute("SELECT quantity, total_cost FROM positions WHERE code=?", (args.code,)).fetchone()
    if row:
        new_qty = row[0] + args.qty
        new_total = row[1] + total_cost
        new_avg = new_total / new_qty
        conn.execute(
            "UPDATE positions SET quantity=?, avg_cost=?, total_cost=? WHERE code=?",
            (new_qty, new_avg, new_total, args.code)
        )
    else:
        avg = total_cost / args.qty
        conn.execute(
            "INSERT INTO positions (code,market,name,quantity,avg_cost,total_cost,buy_thesis) VALUES (?,?,?,?,?,?,?)",
            (args.code, args.market, name, args.qty, avg, total_cost, args.note or "")
        )

    # 扣减现金
    set_cash(conn, cash - total_cost)
    conn.commit()

    print(f"✅ 买入成功")
    print(f"   {args.market} {args.code} ({name})")
    print(f"   数量: {args.qty} 股  价格: {args.price}  金额: {amount:,.2f}")
    print(f"   手续费: {fee:,.2f}  合计: {total_cost:,.2f}")
    print(f"   剩余现金: {cash - total_cost:,.2f}")


def cmd_sell(args):
    conn = get_conn()
    init_db(conn)
    cash = get_cash(conn)

    row = conn.execute("SELECT quantity, avg_cost, total_cost, name FROM positions WHERE code=?", (args.code,)).fetchone()
    if not row or row[0] < args.qty:
        held = row[0] if row else 0
        print(f"❌ 持仓不足！当前持有 {held} 股，尝试卖出 {args.qty} 股")
        sys.exit(1)

    amount = args.price * args.qty
    fee = args.fee if args.fee is not None else calc_fee(args.market, "SELL", amount)
    proceeds = amount - fee
    name = args.name or row[3] or args.code

    today = str(date.today())
    conn.execute(
        "INSERT INTO trades (trade_date,code,market,name,direction,price,quantity,amount,fee,note) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (today, args.code, args.market, name, "SELL", args.price, args.qty, amount, fee, args.note or "")
    )

    # 更新持仓
    new_qty = row[0] - args.qty
    if new_qty == 0:
        conn.execute("DELETE FROM positions WHERE code=?", (args.code,))
    else:
        # 按比例减少成本
        proportion = new_qty / row[0]
        new_total = row[2] * proportion
        conn.execute(
            "UPDATE positions SET quantity=?, total_cost=? WHERE code=?",
            (new_qty, new_total, args.code)
        )

    set_cash(conn, cash + proceeds)
    conn.commit()

    realized_pnl = proceeds - (row[1] * args.qty)
    pnl_str = f"+{realized_pnl:,.2f}" if realized_pnl >= 0 else f"{realized_pnl:,.2f}"
    print(f"✅ 卖出成功")
    print(f"   {args.market} {args.code} ({name})")
    print(f"   数量: {args.qty} 股  价格: {args.price}  金额: {amount:,.2f}")
    print(f"   手续费: {fee:,.2f}  实收: {proceeds:,.2f}")
    print(f"   本次实现盈亏: {pnl_str}")
    print(f"   剩余现金: {cash + proceeds:,.2f}")


def cmd_positions(args):
    conn = get_conn()
    init_db(conn)
    rows = conn.execute(
        "SELECT code, market, name, quantity, avg_cost, total_cost FROM positions ORDER BY market, code"
    ).fetchall()

    cash = get_cash(conn)

    if not rows:
        print("📭 当前无持仓")
        print(f"   现金余额: {cash:,.2f}")
        return

    print(f"\n{'代码':<12} {'市场':<6} {'名称':<12} {'持仓':>8} {'均价':>10} {'成本':>14}")
    print("─" * 70)
    total_cost = 0
    for code, market, name, qty, avg, cost in rows:
        print(f"{code:<12} {market:<6} {name:<12} {qty:>8,} {avg:>10.2f} {cost:>14,.2f}")
        total_cost += cost

    print("─" * 70)
    print(f"{'合计':>44} {total_cost:>14,.2f}")
    print(f"现金余额: {cash:,.2f}")
    print(f"总资产(持仓成本): {total_cost + cash:,.2f}")

    if args.live:
        print("\n⚠️  --live 模式：请通过 Claude 调用 stock-sdk MCP 获取实时价格计算浮盈")
        print("   A股: mcp__stock-sdk__get_a_share_quotes  codes=[...]")
        print("   港股: mcp__stock-sdk__get_hk_quotes       codes=[...]")
        print("   美股: mcp__stock-sdk__get_us_quotes       codes=[...]")


def cmd_pnl(args):
    conn = get_conn()
    init_db(conn)

    query = "SELECT trade_date,code,market,direction,price,quantity,amount,fee,note FROM trades"
    params = []
    if args.code:
        query += " WHERE code=?"
        params.append(args.code)
    query += " ORDER BY trade_date, id"

    trades = conn.execute(query, params).fetchall()

    if not trades:
        print("📭 无交易记录")
        return

    # 计算已实现盈亏
    cost_basis = {}  # code -> (total_qty, total_cost)
    realized = {}    # code -> realized_pnl

    for trade_date, code, market, direction, price, qty, amount, fee, note in trades:
        if code not in cost_basis:
            cost_basis[code] = [0, 0.0]
            realized[code] = 0.0

        if direction == "BUY":
            cost_basis[code][0] += qty
            cost_basis[code][1] += amount + fee
        else:  # SELL
            if cost_basis[code][0] > 0:
                avg = cost_basis[code][1] / cost_basis[code][0]
                pnl = (price - avg) * qty - fee
                realized[code] += pnl
                cost_basis[code][0] -= qty
                cost_basis[code][1] -= avg * qty

    initial = conn.execute("SELECT value FROM config WHERE key='initial_capital'").fetchone()
    initial_capital = float(initial[0]) if initial else 0

    print(f"\n{'代码':<12} {'市场':<6} {'已实现盈亏':>14}")
    print("─" * 36)
    total_realized = 0
    for code in (([args.code] if args.code else sorted(realized.keys()))):
        if code in realized:
            pnl = realized[code]
            total_realized += pnl
            sign = "🟢" if pnl >= 0 else "🔴"
            print(f"{code:<12} {'—':<6} {sign} {pnl:>12,.2f}")

    print("─" * 36)
    print(f"{'已实现盈亏合计':>20} {total_realized:>14,.2f}")

    cash = get_cash(conn)
    print(f"\n现金余额: {cash:,.2f}")
    print(f"初始资金: {initial_capital:,.2f}")
    if initial_capital:
        total_return = (cash - initial_capital + total_realized) / initial_capital * 100
        print(f"总收益率(纯现金+已实现): {total_return:+.2f}%")


def cmd_history(args):
    conn = get_conn()
    init_db(conn)

    query = "SELECT trade_date,direction,code,market,quantity,price,amount,fee,note FROM trades"
    params = []
    if args.code:
        query += " WHERE code=?"
        params.append(args.code)
    query += f" ORDER BY trade_date DESC, id DESC LIMIT {args.n}"

    rows = conn.execute(query, params).fetchall()

    if not rows:
        print("📭 无交易记录")
        return

    print(f"\n{'日期':<12} {'方向':<5} {'代码':<10} {'市场':<5} {'数量':>8} {'价格':>10} {'金额':>12} {'手续费':>8}")
    print("─" * 80)
    for trade_date, direction, code, market, qty, price, amount, fee, note in rows:
        dir_str = "🟢买" if direction == "BUY" else "🔴卖"
        print(f"{trade_date:<12} {dir_str:<5} {code:<10} {market:<5} {qty:>8,} {price:>10.2f} {amount:>12,.2f} {fee:>8.2f}")
        if note:
            print(f"    备注: {note}")


def cmd_snapshot(args):
    conn = get_conn()
    init_db(conn)
    today = str(date.today())

    cash = get_cash(conn)
    positions = conn.execute("SELECT total_cost FROM positions").fetchall()
    total_cost = sum(r[0] for r in positions)

    initial = conn.execute("SELECT value FROM config WHERE key='initial_capital'").fetchone()
    initial_capital = float(initial[0]) if initial else 0

    # 简化快照：total_value用持仓成本+现金估算（无实时价格）
    total_value = total_cost + cash

    conn.execute(
        "INSERT OR REPLACE INTO snapshots (snap_date,total_value,cash_balance,unrealized_pnl,realized_pnl) "
        "VALUES (?,?,?,?,?)",
        (today, total_value, cash, 0, total_value - initial_capital)
    )
    conn.commit()
    print(f"✅ 快照已保存: {today}")
    print(f"   现金: {cash:,.2f}  持仓成本: {total_cost:,.2f}  估算总值: {total_value:,.2f}")


def cmd_cash(args):
    conn = get_conn()
    init_db(conn)
    cash = get_cash(conn)
    initial = conn.execute("SELECT value FROM config WHERE key='initial_capital'").fetchone()
    print(f"现金余额: {cash:,.2f}")
    if initial:
        print(f"初始资金: {float(initial[0]):,.2f}")


# ─── 入口 ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="模拟仓 CLI")
    sub = parser.add_subparsers(dest="cmd")

    # init
    p = sub.add_parser("init")
    p.add_argument("--capital", type=float, default=1_000_000)

    # buy
    p = sub.add_parser("buy")
    p.add_argument("code")
    p.add_argument("qty", type=int)
    p.add_argument("price", type=float)
    p.add_argument("--market", required=True, choices=["A", "HK", "US"])
    p.add_argument("--fee", type=float, default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--note", default=None)

    # sell
    p = sub.add_parser("sell")
    p.add_argument("code")
    p.add_argument("qty", type=int)
    p.add_argument("price", type=float)
    p.add_argument("--market", required=True, choices=["A", "HK", "US"])
    p.add_argument("--fee", type=float, default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--note", default=None)

    # positions
    p = sub.add_parser("positions")
    p.add_argument("--live", action="store_true")

    # pnl
    p = sub.add_parser("pnl")
    p.add_argument("--code", default=None)

    # history
    p = sub.add_parser("history")
    p.add_argument("--code", default=None)
    p.add_argument("--n", type=int, default=20)

    # snapshot
    sub.add_parser("snapshot")

    # cash
    sub.add_parser("cash")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "init": cmd_init,
        "buy": cmd_buy,
        "sell": cmd_sell,
        "positions": cmd_positions,
        "pnl": cmd_pnl,
        "history": cmd_history,
        "snapshot": cmd_snapshot,
        "cash": cmd_cash,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
