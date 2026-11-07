# agents/analyst.py
# Analyst — rules mode (Jev skipped). Same 4 names, same gate.

from datetime import datetime, timezone

class Analyst:
    def __init__(self, config):
        self.config = config

    def score(self, dex: dict, auditor: dict) -> dict:
        # dex keys from fields.py / DexScreener
        vol_h1 = float(dex.get("volume", {}).get("h1", 0) or 0)
        buys_h1 = int(dex.get("txns", {}).get("h1", {}).get("buys", 0) or 0)
        price_m5 = float(dex.get("priceChange", {}).get("m5", 0) or 0)
        price_h1 = float(dex.get("priceChange", {}).get("h1", 0) or 0)
        buys_m5 = int(dex.get("txns", {}).get("m5", {}).get("buys", 0) or 0)
        sells_m5 = int(dex.get("txns", {}).get("m5", {}).get("sells", 0) or 0)

        # settings
        alive_vol = self.config.get("analyst.alive_volume_h1", 25000)
        organic_buys = self.config.get("analyst.organic_buys_h1", 150)
        bundled_pen = self.config.get("analyst.bundled_penalty", 0.5)
        flush_drop = self.config.get("analyst.flush_drop_m5_pct", 5)
        chase_h1 = self.config.get("analyst.chase_h1_pct", 80)

        alive_6h = max(0.0, min(1.0, vol_h1 / alive_vol))
        organic = max(0.0, min(1.0, buys_h1 / organic_buys))
        # bundled penalty if auditor found 3+ (simplified)
        if auditor.get("bundled", 0) >= 3:
            organic *= bundled_pen

        if price_m5 <= -flush_drop and buys_m5 >= sells_m5:
            flush = 1.0
        elif price_m5 < 0:
            flush = 0.5
        else:
            flush = 0.0

        chase = max(0.0, min(1.0, price_h1 / chase_h1))

        score = round(100 * (alive_6h + organic + flush + (1 - chase)) / 4)

        min_alive = self.config.get("analyst.min_alive_6h", 0.70)
        min_org = self.config.get("analyst.min_organic", 0.65)
        max_chase = self.config.get("analyst.max_chase", 0.30)
        min_score = self.config.get("analyst.min_score", 70)

        failed = []
        if alive_6h < min_alive:
            failed.append(f"alive_6h {alive_6h:.2f}")
        if organic < min_org:
            failed.append(f"organic {organic:.2f}")
        if chase > max_chase:
            failed.append(f"chase {chase:.2f}")
        if score < min_score:
            failed.append(f"score {score}")

        return {
            "agent": "analyst",
            "model": "rules",
            "inputTokens": 0,
            "answers": {
                "alive_6h": round(alive_6h, 3),
                "organic": round(organic, 3),
                "flush": round(flush, 3),
                "chase": round(chase, 3),
            },
            "score": score,
            "passed": len(failed) == 0,
            "failed": failed,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
