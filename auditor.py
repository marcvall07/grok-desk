# agents/auditor.py
# Auditor — agent 2. 8 layers, first red kills. 7/8 is a no.

class Auditor:
    def __init__(self, config, db, bus):
        self.config = config
        self.db = db
        self.bus = bus

    async def run(self):
        while True:
            # pull from bus.auditor
            await asyncio.sleep(1)

    def audit(self, mint, scanner_json):
        layers = []
        # 1-8 in order, stop at first red
        # emit audit_layer as each finishes
        return {
            "agent": "auditor",
            "mint": mint,
            "passed": False,
            "layersChecked": 0,
            "layers": layers,
            "holders": None,
            "reason": None,
        }
