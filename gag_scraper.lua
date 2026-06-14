-- GAG2 Stock Scraper — paste into your Roblox executor
-- Replace YOUR_RAILWAY_URL with your actual Railway server URL

local SERVER_URL = "https://YOUR_RAILWAY_URL.railway.app/update"
local INTERVAL   = 30  -- seconds between updates

local HttpService  = game:GetService("HttpService")
local RunService   = game:GetService("RunService")

-- ── Helpers ───────────────────────────────────────────────────────────────────

local function post(data)
    local ok, err = pcall(function()
        local body = HttpService:JSONEncode(data)
        local res  = syn.request({  -- use http.request if on other executors
            Url     = SERVER_URL,
            Method  = "POST",
            Headers = { ["Content-Type"] = "application/json" },
            Body    = body,
        })
        if res.StatusCode ~= 200 then
            warn("[GAG] Server error: " .. tostring(res.StatusCode))
        end
    end)
    if not ok then warn("[GAG] POST failed: " .. tostring(err)) end
end

-- ── Data readers ──────────────────────────────────────────────────────────────

local function getStock()
    local items = {}
    local ok, err = pcall(function()
        -- Seeds
        local seedShop = workspace:FindFirstChild("SeedShop") or workspace:FindFirstChild("Shop")
        if seedShop then
            for _, slot in ipairs(seedShop:GetDescendants()) do
                if slot:IsA("Model") and slot:FindFirstChild("SeedName") then
                    table.insert(items, {
                        name     = slot.SeedName.Value,
                        quantity = slot:FindFirstChild("Quantity") and slot.Quantity.Value or 1,
                        rarity   = slot:FindFirstChild("Rarity")   and slot.Rarity.Value   or "common",
                        type     = "seed",
                    })
                end
            end
        end
        -- Gear
        local gearShop = workspace:FindFirstChild("GearShop") or workspace:FindFirstChild("Gear")
        if gearShop then
            for _, slot in ipairs(gearShop:GetDescendants()) do
                if slot:IsA("Model") and slot:FindFirstChild("GearName") then
                    table.insert(items, {
                        name     = slot.GearName.Value,
                        quantity = slot:FindFirstChild("Quantity") and slot.Quantity.Value or 1,
                        rarity   = slot:FindFirstChild("Rarity")   and slot.Rarity.Value   or "common",
                        type     = "gear",
                    })
                end
            end
        end
    end)
    if not ok then warn("[GAG] Stock read error: " .. tostring(err)) end
    return items
end

local function getPets()
    local pets = {}
    local ok, err = pcall(function()
        local petArea = workspace:FindFirstChild("Pets") or workspace:FindFirstChild("PetSpawns")
        if petArea then
            for _, pet in ipairs(petArea:GetDescendants()) do
                if pet:IsA("Model") and pet:FindFirstChild("PetName") then
                    table.insert(pets, {
                        name   = pet.PetName.Value,
                        rarity = pet:FindFirstChild("Rarity") and pet.Rarity.Value or "common",
                        price  = pet:FindFirstChild("Price")  and tostring(pet.Price.Value) or "?",
                    })
                end
            end
        end
    end)
    if not ok then warn("[GAG] Pet read error: " .. tostring(err)) end
    return pets
end

local function getWeather()
    local weather = ""
    local ok, err = pcall(function()
        local wx = workspace:FindFirstChild("Weather") or workspace:FindFirstChild("WeatherSystem")
        if wx and wx:FindFirstChild("CurrentWeather") then
            weather = wx.CurrentWeather.Value
        elseif wx and wx:FindFirstChild("Active") then
            weather = wx.Active.Value
        end
    end)
    if not ok then warn("[GAG] Weather read error: " .. tostring(err)) end
    return weather
end

-- ── Main loop ─────────────────────────────────────────────────────────────────

print("[GAG] Scraper started — sending to " .. SERVER_URL)

while true do
    local payload = {
        items   = getStock(),
        pets    = getPets(),
        weather = getWeather(),
    }
    post(payload)
    print("[GAG] Data sent: " .. #payload.items .. " items, " .. #payload.pets .. " pets, weather: " .. tostring(payload.weather))
    task.wait(INTERVAL)
end
