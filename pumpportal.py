# pumpportal.py — real websocket hook for graduations
# ONE connection, subscribeMigration only. Free.

import asyncio
import json
import websockets
from pathlib import Path
from datetime import datetime, timezone

WS_URL = "wss://pumpportal.fun/api/data"
RAW_DIR = Path("/workspace/artifacts/desk/logs/raw")

class PumpPortal:
    def __init__(self, on_migration):
        self.on_migration = on_migration
        self.reconnect_delay = 1

    async def run(self):
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    await ws.send(json.dumps({"method": "subscribeMigration"}))
                    print("PumpPortal subscribed to migrations")
                    self.reconnect_delay = 1
                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                            # save raw sample
                            RAW_DIR.mkdir(parents=True, exist_ok=True)
                            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                            (RAW_DIR / f"pumpportal_{ts}.json").write_text(raw)
                            await self.on_migration(msg)
                        except Exception as e:
                            print("msg error", e)
            except Exception as e:
                print(f"PumpPortal disconnected: {e}, reconnect in {self.reconnect_delay}s")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)
