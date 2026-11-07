# fields.py — raw key mapping from STEP 2 samples
# Agents read only through this mapping. Never guess a key.

# PumpPortal migration message (keys filled when first live sample arrives)
PUMPPORTAL = {
    "mint": None,          # to be confirmed from live message
    "pool": None,
    "signature": None,
    "creator": None,
}

# DexScreener pair
DEXSCREENER = {
    "pairAddress": "pairAddress",
    "priceUsd": "priceUsd",
    "liquidity_usd": "liquidity.usd",
    "marketCap": "marketCap",
    "volume_m5": "volume.m5",
    "volume_h1": "volume.h1",
    "txns_m5_buys": "txns.m5.buys",
    "txns_m5_sells": "txns.m5.sells",
    "txns_h1_buys": "txns.h1.buys",
    "txns_h1_sells": "txns.h1.sells",
    "priceChange_m5": "priceChange.m5",
    "priceChange_h1": "priceChange.h1",
    "pairCreatedAt": "pairCreatedAt",
}

# RugCheck report
RUGCHECK_REPORT = {
    "creator": "creator",
    "creatorBalance": "creatorBalance",
    "mintAuthority": "token.mintAuthority",
    "freezeAuthority": "token.freezeAuthority",
    "supply": "token.supply",
    "topHolders": "topHolders",
    "markets": "markets",          # LP info lives under markets[].lp
}

# RugCheck insiders graph
RUGCHECK_GRAPH = {
    "nodes": None,   # empty in sample; structure TBD
    "edges": None,
}

# RPC
RPC = {
    "mintAuthority": "result.value.data.parsed.info.mintAuthority",
    "freezeAuthority": "result.value.data.parsed.info.freezeAuthority",
    "supply": "result.value.data.parsed.info.supply",
}
