# paper_sim.py — simple PAPER loop using the three agents
# Feeds fake DexScreener-like data, updates balance, writes state.json

import json
import time
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
        act = json.loads(ACTIVITY_PATH.read_text())
    act["rows"].insert(0, row)
    act["rows"] = act["rows"][:30]
    ACTIVITY_PATH.write_text(json.dumps(act, indent=2))

def run_once():
    cfg = Config()
    analyst = Analyst(cfg)
    executor = Executor(cfg)
    risk = Risk(cfg)
    state = load_state()
    stack = state["balance"]

    # fake coin that should pass or fail depending on numbers
    dex = {
        "volume": {"h1": 28000},
        "txns": {"h1": {"buys": 160}, "m5": {"buys": 15, "sells": 12}},
        "priceChange": {"m5": -3, "h1": 18},
        "liquidity": {"usd": 45000},
        "priceUsd": "0.0012",
    }
    aud = {"bundled": 1}
    verdict = analyst.score(dex, aud)
    print("analyst", verdict["score"], verdict["passed"], verdict["failed"])

    if verdict["passed"]:
        sz = executor.size(stack, dex["liquidity"]["usd"], stack)
        if sz["sizeUsd"] > 0:
            # open PAPER position
            entry = float(dex["priceUsd"])
            pos = {
                "mint": "SIM111",
                "name": "SimCoin",
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
            print("opened", sz)

    # check open positions
    for pos in list(state.get("positions", [])):
        # simulate a price move
        price = pos["entry_price"] * 0.94   # hit stop
        chk = risk.check(pos, price, time.time())
        if chk.get("exit"):
            fees = round_trip_fees(pos["size_usd"])
            pnl = (price - pos["entry_price"]) / pos["entry_price"] * pos["size_usd"] - fees
            state["balance"] += pos["size_usd"] + pnl
            state["positions"].remove(pos)
            add_activity({
                "kind": "stopped",
                "title": f"Stopped {pos['name']}",
                "subtitle": f"Risk · -{pos['stop_pct']}% stop",
                "value": f"${pnl:.2f}",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            print("exited", chk["reason"], pnl)

    # today % and multiplier vs start
    start = cfg.get("desk.paper_start_stack", 200)
    state["today_pct"] = (state["balance"] - start) / start * 100
    state["multiplier"] = state["balance"] / start
    save_state(state)
    print("balance", state["balance"])

if __name__ == "__main__":
    run_once()
