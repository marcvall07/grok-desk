# telegram.py — long polling, owner only, commands
# First /start becomes owner. Commands match STEP 9.

import asyncio
import httpx
import json
from pathlib import Path

DATA_PATH = "mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc"
STATE_PATH = Path(f"/workspace/artifacts/d/{DATA_PATH}/state.json")

class Telegram:
    def __init__(self, token: str):
        self.token = token
        self.base = f"https://api.telegram.org/bot{token}"
        self.owner = None
        self.offset = 0

    async def _post(self, method, payload):
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f"{self.base}/{method}", json=payload)
            return r.json()

    async def send(self, text: str, reply_markup=None):
        if not self.owner:
            return
        payload = {"chat_id": self.owner, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        await self._post("sendMessage", payload)

    def _load_state(self):
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text())
        return {"balance": 200.0, "today_pct": 0.0, "multiplier": 1.0, "mode": "PAPER"}

    def _save_state(self, state):
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2))

    async def handle(self, text: str):
        t = text.strip().lower()
        state = self._load_state()
        settings = state.setdefault("settings", {})
        agents = state.setdefault("agents_status", {
            "scanner": "running", "auditor": "running", "analyst": "running",
            "executor": "running", "risk": "running"
        })

        if t in ("/start", "start"):
            await self.send("Owner locked. PAPER desk ready.")
            return

        if t == "status":
            open_pos = len(state.get("positions", []))
            await self.send(
                f"mode {state['mode']}\n"
                f"balance ${state['balance']:.2f}\n"
                f"today {state['today_pct']:+.2f}%\n"
                f"multiplier {state['multiplier']:.2f}×\n"
                f"open positions: {open_pos}\n"
                f"graduations: {state.get('graduations', 0)}"
            )
            return

        if t.startswith("stack "):
            try:
                n = float(t.split()[1])
                state["balance"] = n
                self._save_state(state)
                await self.send(f"stack set to ${n:.2f}")
            except Exception:
                await self.send("usage: stack 1240")
            return

        if t == "paper":
            state["mode"] = "PAPER"
            self._save_state(state)
            await self.send("mode → PAPER")
            return

        if t == "live":
            await self.send("LIVE needs a full PAPER night + you typing LIVE to confirm")
            return

        if t.startswith("set stop to "):
            try:
                pct = t.replace("set stop to ", "").replace("%", "").strip()
                pct = float(pct.lstrip("-"))
                old = settings.get("stop_pct", 6)
                settings["stop_pct"] = pct
                state["settings"] = settings
                self._save_state(state)
                await self.send(f"stop -{old}% -> -{pct}%")
            except Exception:
                await self.send("usage: set stop to -8%")
            return

        if t.startswith("pause "):
            name = t.replace("pause ", "").strip().lower()
            if name in agents:
                if name == "risk" and state.get("positions"):
                    await self.send("Risk cannot be paused while a position is open")
                    return
                agents[name] = "paused"
                state["agents_status"] = agents
                self._save_state(state)
                await self.send(f"{name.capitalize()} paused")
            else:
                await self.send("unknown agent")
            return

        if t.startswith("resume "):
            name = t.replace("resume ", "").strip().lower()
            if name in agents:
                agents[name] = "running"
                state["agents_status"] = agents
                self._save_state(state)
                await self.send(f"{name.capitalize()} resumed")
            else:
                await self.send("unknown agent")
            return

        if t.startswith("buy "):
            coin = text.split(maxsplit=1)[1] if len(text.split()) > 1 else "X"
            await self.send(f"Buy {coin} — not sized, not on the desk\n[Buy on FOMO] would go here")
            return

        if t.startswith("sell "):
            coin = text.split(maxsplit=1)[1] if len(text.split()) > 1 else "X"
            await self.send(f"[Sell on FOMO] for {coin}")
            return

        if t.startswith("why "):
            coin = text.split(maxsplit=1)[1] if len(text.split()) > 1 else "X"
            await self.send(f"why {coin}: no decision recorded yet")
            return

        if t in ("sim", "trade", "papertrade"):
            # trigger one PAPER cycle
            import subprocess, sys
            subprocess.Popen([sys.executable, "paper_sim.py"], cwd="/workspace/artifacts/desk")
            await self.send("PAPER trade triggered — check the app in ~15s")
            return

        if t == "report":
            await self.send("Morning Page not yet generated (STEP 12)")
            return

        # unknown
        await self.send(
            "Commands:\n"
            "status\n"
            "stack 1240\n"
            "paper | live\n"
            "set stop to -8%\n"
            "pause Scanner / resume Scanner\n"
            "buy X / sell X / why X\n"
            "invite\n"
            "report"
        )

    async def poll(self):
        while True:
            try:
                data = await self._post("getUpdates", {"offset": self.offset, "timeout": 20})
                for u in data.get("result", []):
                    self.offset = u["update_id"] + 1
                    msg = u.get("message") or {}
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text") or ""
                    if self.owner is None and text.startswith("/start"):
                        self.owner = chat_id
                    if chat_id == self.owner and text:
                        await self.handle(text)
            except Exception as e:
                print("telegram poll error", e)
            await asyncio.sleep(1)
