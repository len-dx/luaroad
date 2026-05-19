-- Example Plugin: Game Logger
-- Logs all game additions and removals

function on_load()
    luaroad:log("Game Logger Plugin loaded!")
end

function on_game_added(appid, depot_key)
    games = luaroad:get_games()
    luaroad:log("[Logger] Games count: " .. #games)
    return true
end

function on_game_removed(appid)
    luaroad:log("[Logger] Game " .. appid .. " removed from config")
    return true
end
