# links.py — THE ONLY place FOMO URLs are built
# Never write a FOMO URL anywhere else. Never drop r=savipww.

CHAIN_ID = {
    "solana": 1399811149,
    "robinhood": 4663,
    "base": 8453,
    "bnb": 56,
}

SIGNUP_URL = "https://fomo.family/r/savipww"

def coin_url(address: str, chain: str = "solana") -> str:
    if chain not in CHAIN_ID:
        # log it in real code
        return SIGNUP_URL
    return (
        f"https://fomo.family/coin?address={address}"
        f"&chainId={CHAIN_ID[chain]}&r=savipww&source=share_link"
    )

def profile_url(handle: str) -> str:
    h = handle.lstrip("@")
    return f"https://fomo.family/profile/{h}?source=share_link&r=savipww"
