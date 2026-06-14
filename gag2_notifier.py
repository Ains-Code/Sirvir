# GAG2 full notifier — stock, pets & weather
# pip install requests python-dotenv
# → python gag2_notifier.py

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

WEBHOOK   = os.getenv("WEBHOOK_URL", "https://discord.com/api/webhooks/1515704094419980338/XlFD0Y1xCfvEVagK8kznLxcEX4LDNHjyMZws41WU1DjAcm-ZIAh_0WjN0qhBpM5eQWAX")
INTERVAL  = 30
MIN_RARITY = "legendary"

RARITY_ORDER = ["common", "uncommon", "rare", "legendary", "mythic", "super"]

# ── API endpoints ─────────────────────────────────────────────────────────────

_BASE       = os.getenv("API_BASE", "https://sirvir-production.up.railway.app")
SEED_API    = f"{_BASE}/v2/growagarden/stock"
GEAR_API    = f"{_BASE}/v2/growagarden/gearstock"
PET_API     = f"{_BASE}/v2/growagarden/petstock"
WEATHER_API = f"{_BASE}/v2/growagarden/weather"

# ── Watch lists ───────────────────────────────────────────────────────────────

WATCH_SG = [
    "Banana", "Coconut", "Grape", "Green Bean", "Acorn", "Cherry",
    "Dragon Fruit", "Pomegranate", "Ghost Pepper", "Lotus", "Dragon's Breath",
    "Beanstalk", "Advanced Watering Can", "Super Sprinkler", "Magnifying Glass",
    "Wheelbarrow", "Master Sprinkler", "Teleporter",
]

WATCH_PETS = [
    {"name": "Robin",           "rarity": "legendary", "price": "75K",  "ability": "Eats ripe fruits, drops seeds"},
    {"name": "Bee",             "rarity": "legendary", "price": "1M",   "ability": "Patrols garden, swarms intruders"},
    {"name": "Monkey",          "rarity": "mythic",    "price": "1M",   "ability": "Brings ripe fruits to you"},
    {"name": "Golden Dragonfly","rarity": "mythic",    "price": "3M",   "ability": "Increases gold chance 2x"},
    {"name": "Unicorn",         "rarity": "mythic",    "price": "4M",   "ability": "Doubles rainbow fruit chance"},
    {"name": "Ice Serpent",     "rarity": "super",     "price": "8M",   "ability": "Freezes intruders in garden"},
    {"name": "Black Dragon",    "rarity": "super",     "price": "10M",  "ability": "Breathes fire on thieves"},
    {"name": "Magma Golem",     "rarity": "super",     "price": "15M",  "ability": "Burns enemy crops when stealing"},
]
WATCH_PET_MAP = {p["name"]: p for p in WATCH_PETS}

WATCH_WX = [
    {"name": "Lightning",  "emoji": "⚡",  "rarity": "rare",      "mult": "70x",  "effect": "Electric mutation (70x) on struck crops."},
    {"name": "Starfall",   "emoji": "🌟",  "rarity": "rare",      "mult": "25x",  "effect": "Starstruck mutation (25x) on crops."},
    {"name": "Rainbow",    "emoji": "🌈",  "rarity": "rare",      "mult": "30x",  "effect": "Rainbow seeds spawn on map. Carpet gear given."},
    {"name": "Midas",      "emoji": "✨",  "rarity": "rare",      "mult": "10x",  "effect": "Gold seeds spawn. Crops can get Gold mutation (10x)."},
    {"name": "Bloodmoon",  "emoji": "🩸",  "rarity": "super",     "mult": "80x",  "effect": "Bloodlit mutation (80x). Beams hit random plots."},
    {"name": "Disco Moon", "emoji": "🪩",  "rarity": "legendary", "mult": "30x",  "effect": "Night event. Stealing makes crops Rainbow mutated."},
]
WATCH_WX_MAP = {w["name"]: w for w in WATCH_WX}

RARE_WX  = {"Bloodmoon", "Starfall"}
HIGH_PET = {"mythic", "super"}
HIGH_SG  = {"mythic", "super"}

# ── State ─────────────────────────────────────────────────────────────────────

seen: set[str] = set()

# ── Helpers ───────────────────────────────────────────────────────────────────

def rarity_ok(rarity: str) -> bool:
    try:
        return RARITY_ORDER.index(rarity.lower()) >= RARITY_ORDER.index(MIN_RARITY)
    except ValueError:
        return False

def color_for(rarity: str) -> int:
    return {
        "super":     0xE74C3C,
        "mythic":    0x9B59B6,
        "legendary": 0xF0A500,
        "rare":      0x5865F2,
        "uncommon":  0x57F287,
    }.get(rarity.lower(), 0x888780)

def post(payload: dict) -> None:
    requests.post(WEBHOOK, json=payload, timeout=8)

# ── Alert functions ───────────────────────────────────────────────────────────

def alert_stock(name: str, qty: int, kind: str, rarity: str) -> None:
    ping = "@here " if rarity.lower() in HIGH_SG else ""
    icon = "🌱" if kind == "seed" else "⚙️"
    post({
        "content": ping + f"{icon} **{name}** in stock!",
        "embeds": [{
            "title":       f"{icon} {name}",
            "description": f"**Type:** {kind.title()} | **Rarity:** {rarity.title()} | **Qty:** {qty}",
            "color":       color_for(rarity),
        }],
    })
    print(f"[STOCK] {name} [{rarity}] x{qty}")

def alert_pet(name: str, rarity: str, price: str) -> None:
    info = WATCH_PET_MAP.get(name, {})
    ping = "@here " if rarity.lower() in HIGH_PET else ""
    post({
        "content": ping + f"🐾 **{name}** spawned!",
        "embeds": [{
            "title": f"🐾 {name} on the map!",
            "description": (
                f"**Rarity:** {rarity.title()}\n"
                f"**Price:** {price} Sheckles\n"
                f"**Ability:** {info.get('ability', '—')}\n\n"
                "⚡ Buy fast — first come, first served!"
            ),
            "color":  color_for(rarity),
            "footer": {"text": "Pet spawns are timed!"},
        }],
    })
    print(f"[PET] {name} [{rarity}]")

def alert_weather(name: str, rarity: str) -> None:
    info = WATCH_WX_MAP.get(name, {})
    ping = "@here " if name in RARE_WX else ""
    icon = info.get("emoji", "🌦️")
    mult = info.get("mult", "—")
    post({
        "content": ping + f"{icon} **{name}** weather started!",
        "embeds": [{
            "title": f"{icon} {name}",
            "description": (
                f"**Effect:** {info.get('effect', '—')}\n"
                f"**Mutation multiplier:** {mult}\n"
                f"**Duration:** {info.get('duration', '~2-5 min')}"
            ),
            "color":  color_for(rarity),
            "footer": {"text": "Harvest before it ends!"},
        }],
    })
    print(f"[WEATHER] {name} [{rarity}]")

# ── Main loop ─────────────────────────────────────────────────────────────────

while True:
    try:
        # Stock & gear
        for kind, url in [("seed", SEED_API), ("gear", GEAR_API)]:
            items = requests.get(url, timeout=10).json().get("items", [])
            for item in items:
                name    = item["name"]
                qty     = item.get("quantity", 0)
                rarity  = item.get("rarity", "common")
                if qty <= 0 or name not in WATCH_SG or not rarity_ok(rarity):
                    continue
                key = f"sg:{name}:{qty}"
                if key in seen:
                    continue
                seen.add(key)
                alert_stock(name, qty, kind, rarity)

        # Pet spawns
        pets = requests.get(PET_API, timeout=10).json().get("pets", [])
        for pet in pets:
            name   = pet["name"]
            rarity = pet.get("rarity", "common")
            price  = pet.get("price", "?")
            if name not in WATCH_PET_MAP:
                continue
            key = f"pet:{name}"
            if key in seen:
                continue
            seen.add(key)
            alert_pet(name, rarity, price)

        # Weather events
        wx     = requests.get(WEATHER_API, timeout=10).json()
        active = wx.get("active", wx.get("current", ""))
        if active and active in WATCH_WX_MAP:
            rarity = WATCH_WX_MAP[active].get("rarity", "rare")
            key    = f"wx:{active}"
            if key not in seen:
                seen.add(key)
                alert_weather(active, rarity)

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(INTERVAL)
