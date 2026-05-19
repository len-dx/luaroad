-- Example Plugin: Custom Manifest Fetcher
-- Demonstrates how to overide manifest code fetching
-- Save to plugins/ folder and load from Plugins tab

function on_load()
    luaroad:log("Custom Manifest Plugin loaded!")
end

function fetch_manifest_code_ex(app_id, depot_id, gid)
    luaroad:log("Fetching manifest for app=" .. app_id .. " depot=" .. depot_id .. " gid=" .. gid)
    body, status = http_get("https://manifest.steam.run/api/manifest/" .. gid)
    if status == 200 and body then
        code = body:match('"content":"(%d+)"')
        if code then
            luaroad:log("Got manifest code: " .. code)
            return code
        end
    end
    return nil
end

function on_game_added(appid, depot_key)
    luaroad:log("Game " .. appid .. " was added to config")
end
