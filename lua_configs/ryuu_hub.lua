-- Ryuu Manifest Hub Plugin for Luaroad
-- Place this in plugins/ folder, then load it from Plugins tab.
-- Requires an API key set in Settings or Manifests tab.

function fetch_manifest_code(gid)
    local api_key = luaroad:get_setting("ryuu_api_key", "")
    if api_key == "" then
        luaroad:log("[Ryuu] No API key configured", "warning")
        return nil
    end
    local headers = {}
    headers["Authorization"] = "Bearer " .. api_key
    local body, status = http_get("https://api.ryuu.gg/manifest/" .. gid, headers)
    if status == 200 and body then
        return body
    end
    luaroad:log("[Ryuu] HTTP " .. tostring(status) .. " for GID " .. gid, "warning")
    return nil
end

function fetch_manifest_code_ex(app_id, depot_id, gid)
    local api_key = luaroad:get_setting("ryuu_api_key", "")
    if api_key == "" then
        return nil
    end
    local headers = {}
    headers["Authorization"] = "Bearer " .. api_key
    local body, status = http_get("https://api.ryuu.gg/manifest/" .. app_id .. "/" .. gid, headers)
    if status == 200 and body then
        local code = body:match('"code":"(%d+)"')
        if code then
            return code
        end
        return body
    end
    return nil
end
