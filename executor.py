# agents/executor.py
# Executor — sizing + ticket rules. Never places orders.

class Executor:
    def __init__(self, config):
        self.config = config

    def size(self, stack: float, liquidity_usd: float, free: float) -> dict:
        stack_pct = self.config.get("executor.stack_pct", 8) / 100
        max_pool_pct = self.config.get("executor.max_pool_pct", 2) / 100
        min_ticket = self.config.get("executor.min_ticket_usd", 47.50)
        below_min = self.config.get("executor.below_min", "bump")

        raw = stack * stack_pct
        capped = min(raw, liquidity_usd * max_pool_pct)
        size = round(capped, 2)

        reason = None
        if size < min_ticket:
            if below_min == "bump" and free >= min_ticket:
                size = min_ticket
                reason = "bumped"
            else:
                return {"sizeUsd": 0, "reason": "under $47.50", "stackPct": stack_pct * 100}

        if size > free:
            return {"sizeUsd": 0, "reason": "no free stack", "stackPct": stack_pct * 100}

        return {
            "sizeUsd": size,
            "stackPct": round(size / stack * 100, 2) if stack else 0,
            "reason": reason,
        }
