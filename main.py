# main.py — Railway-ready with static server
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from aiohttp import web
from telegram import Telegram
from pumpportal import PumpPortal

DATA_PATH = os.environ.get("DATA_PATH", "mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc")
TG_TOKEN = os.environ.get("TG_TOKEN", "")
PORT = int(os.environ.get("PORT", 8080))
OUT_DIR = Path(f"/tmp/d/{DATA_PATH}")
WEB_DIR = Path(__file__).parent / "web"

def write_json(name, obj):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(json.dumps(obj, indent=2))

async def json_writer():
    while True:
        state_path = OUT_DIR / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text())
        else:
            state = {
                "balance": 200.0, "today_pct": 0.0, "multiplier": 1.0,
                "mode": "PAPER", "graduations": 0, "positions": [],
                "settings": {}, "agents_status": {},
            }
        state["ts"] = datetime.now(timezone.utc).isoformat()
        write_json("state.json", state)
        await asyncio.sleep(15)

async def on_migration(msg):
    print("MIGRATION", str(msg)[:200])
    state_path = OUT_DIR / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"graduations": 0}
    state["graduations"] = state.get("graduations", 0) + 1
    state["last_mint"] = msg.get("mint") or msg.get("token") or "unknown"
    write_json("state.json", state)

async def handle_index(request):
    return web.FileResponse(WEB_DIR / "index.html")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_static("/d/", OUT_DIR.parent, show_index=False)
    app.router.add_static("/", WEB_DIR, show_index=False)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"web listening on {PORT}")

async def main():
    if not TG_TOKEN:
        print("WARNING: TG_TOKEN not set")
    print("desk started")
    await start_web()
    tg = Telegram(TG_TOKEN)
    pp = PumpPortal(on_migration)
    await asyncio.gather(
        json_writer(),
        tg.poll(),
        pp.run(),
    )

if __name__ == "__main__":
    asyncio.run(main())
