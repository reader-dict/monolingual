local export = {}

local m_table = require("Module:table")
local string_utilities_module = "Module:string utilities"
local en_utilities_module = "Module:en-utilities"

local insert = table.insert
local concat = table.concat
local dump = mw.dumpObject
local unpack = unpack or table.unpack -- Lua 5.2 compatibility

local function list_or_element_contains(list_or_element, item)
	if type(list_or_element) == "table" then
		return m_table.contains(list_or_element, item) and true or false
	end
	return list_or_element == item
end

function export.key_to_placename(group, key)
	if group.key_to_placename == false then
		return key, key
	end
	if group.key_to_placename then
		local full_placename, elliptical_placename = group.key_to_placename(key)
		return full_placename, elliptical_placename
	end
	key = key:gsub(",.*", "")
	return key, key
end

function export.placename_to_key(group, placename)
	if group.placename_to_key == false then
		return placename
	elseif group.placename_to_key then
		local key = group.placename_to_key(placename)
		return key
	elseif group.default_placetype == "city" then
		return placename
	else
		local defcon = group.default_container
		if not defcon then
			return placename
		elseif type(defcon) == "string" then
			return placename .. ", " .. defcon
		elseif type(defcon) == "table" and (defcon.placetype == "country" or
				defcon.placetype == "constituent country") then
			return placename .. ", " .. defcon.key
		else
			return placename
		end
	end
end

function export.initialize_spec(group, key, spec)
	if spec.initialized then
		return
	end
	local container = spec.container
	local containers
	local container_from_default
	if not container then
		container = group.default_container
		container_from_default = true
	end
	if container then
		if type(container) == "string" or container.key then
			container = {container}
		end
		containers = {}
		for _, cont in ipairs(container) do
			if type(cont) == "string" then
				if group.canonicalize_key_container and not container_from_default then
					cont = group.canonicalize_key_container(cont)
				else
					cont = {key = cont, placetype = "country"}
				end
			end
			insert(containers, cont)
		end
	end
	spec.containers = containers
	spec.container = nil
	local function value_with_default(val, default_val)
		if val == nil then
			return default_val
		else
			return val
		end
	end
	local function set_or_default(prop)
		spec[prop] = value_with_default(spec[prop], group["default_" .. prop])
	end
	set_or_default("placetype")
	set_or_default("divs")
	spec.addl_divs = group.addl_divs
	for _, prop in ipairs {
		"keydesc",
		"fulldesc",
		"addl_parents",
		"overriding_bare_label_parents",
		"bare_category_parent_type",
		"wp",
		"wpcat",
		"commonscat",
		"british_spelling",
		"the",
		"no_container_cat",
		"no_container_parent",
		"no_generic_place_cat",
		"no_check_holonym_mismatch",
		"no_auto_augment_container",
		"no_include_container_in_desc",
		"is_city",
		"is_former_place",
	} do
		set_or_default(prop)
	end
	-- `default_placetype == "city"` is correct; if `default_placetype` has something else like `prefecture-level city`
	-- as the canonical placetype but also lists `city` (as Chinese prefecture-level cities do), don't mark as
	-- is_city.
	spec.is_city = value_with_default(spec.is_city, group.default_placetype == "city")
	spec.initialized = true
end

local function find_matching_key_in_group(group, placetypes, key, alias_resolution)
	local spec = group.data[key]
	if not spec then
		return nil
	end

	local function check_correct_placetype(placetype)
		if type(placetype) == "table" then
			for _, pt in ipairs(placetype) do
				if list_or_element_contains(placetypes, pt) then
					return true
				end
			end
			return false
		else
			return list_or_element_contains(placetypes, placetype)
		end
	end

	if spec.alias_of then
		local resolved_key = spec.alias_of
		local resolved_spec = group.data[resolved_key]
		if alias_resolution == "none" or alias_resolution == "display" then
			-- We could be working with non-initialized/defaulted spec, since we're pulling it directly from the group.
			local placetype = spec.placetype or resolved_spec.placetype or group.default_placetype
			if not check_correct_placetype(placetype) then
				return nil
			end
			if alias_resolution == "display" then
				if spec.display == true then
					key = resolved_key
				elseif spec.display then
					key = spec.display
				end
			end
			return key, spec
		end
		key = resolved_key
		spec = resolved_spec
	end

	-- We could be working with non-initialized/defaulted spec, since we're pulling it directly from the group.
	local placetype = spec.placetype or group.default_placetype
	if not check_correct_placetype(placetype) then
		return nil
	end
	export.initialize_spec(group, key, spec)
	return key, spec
end

local function find_matching_placename_in_group(group, placetypes, placename, alias_resolution)
	local key = export.placename_to_key(group, placename)
	return find_matching_key_in_group(group, placetypes, key, alias_resolution)
end

function export.find_canonical_key(key)
	local found_locations = {}
	for _, group in ipairs(export.locations) do
		local spec = group.data[key]
		if not spec then
			-- do nothing
		elseif spec.alias_of then
			mw.log(("Skipping alias '%s' of canonical '%s'"):format(key, spec.alias_of))
		else
			insert(found_locations, {group, spec})
		end
	end
	if not found_locations[1] then
		return nil
	else
		local group, spec = unpack(found_locations[1])
		export.initialize_spec(group, key, spec)
		return group, spec
	end
end

function export.iterate_matching_location(data)
	local i = 0
	local n = #export.locations
	return function()
		while true do
			i = i + 1
			if i > n then
				break
			end
			local group = export.locations[i]
			local key, spec
			if data.placename then
				key, spec = find_matching_placename_in_group(group, data.placetypes, data.placename,
					data.alias_resolution)
			else
				key, spec = find_matching_key_in_group(group, data.placetypes, data.key, data.alias_resolution)
			end
			if key then
				return group, key, spec
			end
		end
	end
end

function export.get_matching_location(data)
	local all_found = {}
	for group, key, spec in export.iterate_matching_location(data) do
		insert(all_found, {group, key, spec})
	end
	return unpack(all_found[1])
end

function export.iterate_containers(group, key, spec)
	local keys_seen = {}
	keys_seen[key] = true
	local iterations = 0
	local last_iteration_containers = {{group = group, key = key, spec = spec}}
	return function()
		iterations = iterations + 1
		local next_iteration_containers = {}
		for _, location in ipairs(last_iteration_containers) do
			local containers = location.spec.containers
			if containers then
				for _, container in ipairs(containers) do
					local container_group, container_key, container_spec = export.get_matching_location {
						placetypes = container.placetype,
						key = container.key,
					}
					if not keys_seen[container_key] then
						insert(next_iteration_containers, {
							group = container_group, key = container_key, spec = container_spec
						})
						keys_seen[container_key] = true
					end
				end
			end
		end
		if not next_iteration_containers[1] then
			return nil
		end
		last_iteration_containers = next_iteration_containers
		return next_iteration_containers
	end
end

function export.construct_linked_placename(spec, placename, display_form)
	local linked_placename = display_form and placename ~= display_form and ("[[%s|%s]]"):format(placename,
		display_form) or ("[[%s]]"):format(placename)
	if spec.the then
		linked_placename = "the " .. linked_placename
	end
	return linked_placename
end

return export