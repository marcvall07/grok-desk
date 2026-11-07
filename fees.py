# fees.py — FOMO fee model for PAPER PnL
# $5 to $47.50 -> 2% of the ticket
# $47.50 to $190 -> flat 0.95
# above $190 -> 0.50%
# each side; then minus fees_ref_discount (10% off)

def fomo_fee(ticket_usd: float, ref_discount: float = 0.10) -> float:
    if ticket_usd < 5:
        return 0.0
    if ticket_usd <= 47.50:
        fee = ticket_usd * 0.02
    elif ticket_usd <= 190:
        fee = 0.95
    else:
        fee = ticket_usd * 0.005
    return fee * (1 - ref_discount)

def round_trip_fees(ticket_usd: float, ref_discount: float = 0.10) -> float:
    return fomo_fee(ticket_usd, ref_discount) * 2
