# GAG2 relay server — deploy this on Railway
# pip install fastapi uvicorn

from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import uvicorn
import os

app = FastAPI()

# In-memory store (resets on redeploy — fine for live stock data)
store = {
    "items":      [],
    "pets":       [],
    "weather":    "",
    "updated_at": None,
}

API_KEY = os.getenv("API_KEY", "")  # optional: set in Railway env vars to secure it

# ── Receive data from Roblox executor ─────────────────────────────────────────

@app.post("/update")
async def update(request: Request):
    # Optional API key check
    if API_KEY:
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    store["items"]      = data.get("items", [])
    store["pets"]       = data.get("pets", [])
    store["weather"]    = data.get("weather", "")
    store["updated_at"] = datetime.utcnow().isoformat()
    return {"status": "ok"}

# ── Serve data to notifier script ─────────────────────────────────────────────

@app.get("/v2/growagarden/stock")
async def stock():
    return {"items": [i for i in store["items"] if i.get("type") == "seed"]}

@app.get("/v2/growagarden/gearstock")
async def gearstock():
    return {"items": [i for i in store["items"] if i.get("type") == "gear"]}

@app.get("/v2/growagarden/petstock")
async def petstock():
    return {"pets": store["pets"]}

@app.get("/v2/growagarden/weather")
async def weather():
    return {"active": store["weather"]}

@app.get("/health")
async def health():
    return {"status": "online", "updated_at": store["updated_at"]}

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
