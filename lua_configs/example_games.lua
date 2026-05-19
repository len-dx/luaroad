-- Luaroad Example Game Configuration
-- Place this file in your Steam/config/lua/ folder (for OpenSteamTool)
-- or Steam/config/stplug-in/ folder (for LumaCore)

-- Unlock a game by AppID
addappid(1361510)

-- Unlock a game with depot decryption key
addappid(1361511, 0, "5954562e7f5260400040a818bc29b60b335bb690066ff767e20d145a3b6b4af0")

-- Add access token for protected games
addtoken(1361510, "2764735786934684318")

-- Pin a specific manifest version (prevent updates)
setManifestid(1361511, "5656605350306673283")

-- Pin with explicit size
setManifestid(1361511, "5656605350306673283", 12345678)

-- Write AppTicket for Denuvo/SteamStub games
setAppTicket(1361510, "01000000000000000100000000000000")

-- Write ETicket for Denuvo/SteamStub games
setETicket(1361510, "01000000000000000100000000000000")

-- Set SteamID for stats/achievements
setStat(1361510, "76561197960287930")
