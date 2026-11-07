# paper_night.py — longer PAPER session
# Runs multiple cycles, writes activity + balance, optional Telegram pings

import time
import json
from pathlib import Path
from datetime import datetime, timezone
from config import Config
from agents.analyst import Analyst
from agents.executor import Executor
from agents.risk import Risk
from fees import round_trip_fees

DATA_PATH = "mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc"
STATE_PATH = Path(f"/workspace/artifacts/d/{DATA_PATH}/state.json")
ACTIVITY_PATH = Path(f"/workspace/artifacts/d/{DATA_PATH}/activity.json")

def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"balance": 200.0, "today_pct": 0.0, "multiplier": 1.0, "mode": "PAPER", "positions": []}

def save_state(s):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    s["ts"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(s, indent=2))

def add_activity(row):
    act = {"rows": []}
    if ACTIVITY_PATH.exists():
        try:
            act = json.loads(ACTIVITY_PATH.read_text())
        except Exception:
            pass
    act["rows"].insert(0, row)
    act["rows"] = act["rows"][:50]
    ACTIVITY_PATH.write_text(json.dumps(act, indent=2))

def one_cycle(cfg, analyst, executor, risk, state, cycle_n):
    stack = state["balance"]
    # vary the fake numbers a bit each cycle
    vol = 22000 + (cycle_n * 1500)
    buys = 140 + cycle_n * 10
    h1 = 15 + (cycle_n % 5) * 8
    dex = {
        "volume": {"h1": vol},
        "txns": {"h1": {"buys": buys}, "m5": {"buys": 12, "sells": 10}},
        "priceChange": {"m5": -4, "h1": h1},
        "liquidity": {"usd": 42000 + cycle_n * 1000},
        "priceUsd": "0.001",
    }
    aud = {"bundled": cycle_n % 4}
    verdict = analyst.score(dex, aud)
    print(f"cycle {cycle_n}: score {verdict['score']} passed {verdict['passed']}")

    if not verdict["passed"]:
        add_activity({
            "kind": "rejected",
            "title": f"Rejected Sim{cycle_n}",
            "subtitle": f"Analyst · {verdict['failed'][0] if verdict['failed'] else 'score'}",
            "value": "Skipped",
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        return state

    sz = executor.size(stack, dex["liquidity"]["usd"], stack)
    if sz["sizeUsd"] <= 0:
        return state

    entry = 0.001
    pos = {
        "mint": f"SIM{cycle_n}",
        "name": f"Sim{cycle_n}",
        "entry_price": entry,
        "size_usd": sz["sizeUsd"],
        "peak_price": entry,
        "opened_at": time.time(),
        "stop_pct": cfg.get("risk.stop_pct", 6),
        "trail_active": False,
    }
    state.setdefault("positions", []).append(pos)
    state["balance"] -= sz["sizeUsd"]
    add_activity({
        "kind": "bought",
        "title": f"Bought {pos['name']}",
        "subtitle": "Executor",
        "value": f"${sz['sizeUsd']} · {sz['stackPct']}%",
        "ts": datetime.now(timezone.utc).isoformat(),
    })

    # immediate exit for the demo (stop)
    price = entry * 0.94
    chk = risk.check(pos, price, time.time())
    if chk.get("exit"):
        fees = round_trip_fees(pos["size_usd"])
        pnl = (price - entry) / entry * pos["size_usd"] - fees
        state["balance"] += pos["size_usd"] + pnl
        state["positions"].remove(pos)
        add_activity({
            "kind": "stopped",
            "title": f"Stopped {pos['name']}",
            "subtitle": f"Risk · -{pos['stop_pct']}% stop",
            "value": f"${pnl:.2f}",
            "ts": datetime.now(timezone.utc).isoformat(),
        })

    start = cfg.get("desk.paper_start_stack", 200)
    state["today_pct"] = (state["balance"] - start) / start * 100
    state["multiplier"] = state["balance"] / start
    return state

def run_night(cycles=8, delay=3):
    cfg = Config()
    analyst = Analyst(cfg)
    executor = Executor(cfg)
    risk = Risk(cfg)
    state = load_state()
    print(f"starting PAPER night, {cycles} cycles, balance {state['balance']}")
    for i in range(1, cycles + 1):
        state = one_cycle(cfg, analyst, executor, risk, state, i)
        save_state(state)
        print(f"  balance now {state['balance']:.2f}")
        time.sleep(delay)
    print("PAPER night done")
    return state

if __name__ == "__main__":
    run_night(cycles=6, delay=2)
