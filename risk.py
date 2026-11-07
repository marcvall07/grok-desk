# agents/risk.py
# Risk — stop, trail, timeout. Never moves stop down.

class Risk:
    def __init__(self, config):
        self.config = config

    def check(self, position: dict, price: float, now_ts: float) -> dict:
        entry = position["entry_price"]
        peak = max(position.get("peak_price", entry), price)
        stop_pct = position.get("stop_pct", self.config.get("risk.stop_pct", 6)) / 100
        trail_start = self.config.get("risk.trail_start_pct", 20) / 100
        trail_pct = self.config.get("risk.trail_pct", 12) / 100
        timeout_h = self.config.get("risk.timeout_h", 3)
        timeout_min_gain = self.config.get("risk.timeout_min_gain_pct", 5) / 100

        # update peak
        position["peak_price"] = peak

        # trail on
        if price >= entry * (1 + trail_start):
            position["trail_active"] = True

        # rules in order
        if price <= entry * (1 - stop_pct):
            return {"exit": True, "reason": "stop", "exit_price": price}

        if position.get("trail_active") and price <= peak * (1 - trail_pct):
            return {"exit": True, "reason": "trail", "exit_price": price}

        open_hours = (now_ts - position["opened_at"]) / 3600
        if open_hours >= timeout_h and price < entry * (1 + timeout_min_gain):
            return {"exit": True, "reason": "timeout", "exit_price": price}

        return {"exit": False, "peak": peak}
