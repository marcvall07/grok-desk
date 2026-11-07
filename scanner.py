# agents/scanner.py
# Scanner — agent 1. Counts and cuts. Never judges quality.
# Numbers in [brackets] are settings. Never changes them.

import asyncio
from datetime import datetime, timezone

class Scanner:
    def __init__(self, config, db, bus):
        self.config = config
        self.db = db
        self.bus = bus
        self.waiting_room = {}  # mint -> {migrated_at, ...}

    async def run(self):
        # PumpPortal websocket subscribeMigration
        # DexScreener batch every [60]s
        # Kill rules in order, pass after [10] min
        while True:
            await asyncio.sleep(self.config.get("scanner.poll_s", 60))
            # heartbeat
            self._heartbeat()

    def _heartbeat(self):
        pass  # write to db.heartbeats

    def decide(self, mint, data):
        # returns the JSON output shape from the prompt
        return {
            "agent": "scanner",
            "mint": mint,
            "verdict": "pass",  # or "kill"
            "reason": None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
