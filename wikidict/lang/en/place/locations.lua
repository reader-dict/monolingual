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

local function make_key_to_placename(container_patterns, divtype_patterns)
	if type(container_patterns) == "string" then
		container_patterns = {container_patterns}
	end
	if type(divtype_patterns) == "string" then
		divtype_patterns = {divtype_patterns}
	end
	return function(key)
		local full_placename = key
		if container_patterns then
			for _, container_pattern in ipairs(container_patterns) do
				local nsubs
				full_placename, nsubs = full_placename:gsub(container_pattern, "")
				if nsubs > 0 then
					break
				end
			end
		end
		local elliptical_placename = full_placename
		if divtype_patterns then
			for _, divtype_pattern in ipairs(divtype_patterns) do
				local nsubs
				elliptical_placename, nsubs = elliptical_placename:gsub(divtype_pattern, "")
				if nsubs > 0 then
					break
				end
			end
		end
		return full_placename, elliptical_placename
	end
end

local function make_placename_to_key(container_suffix, divtype_suffix)
	return function(placename)
		local key = placename
		if divtype_suffix then
			if not key:find(divtype_suffix .. "$") then
				key = key .. divtype_suffix
			end
		end
		if container_suffix then
			key = key .. container_suffix
		end
		return key
	end
end

local function make_canonicalize_key_container(suffix, placetype)
	return function(container)
		if type(container) == "string" then
			return {key = container .. (suffix or ""), placetype = placetype}
		else
			return container
		end
	end
end

export.continents = {
	["Earth"] = {the = true, placetype = "planet", addl_parents = {"nature"},
			fulldesc = "=the planet [[Earth]] and the features found on it"},
		["Africa"] = {placetype = "continent", container = {key = "Earth", placetype = "planet"}},
		["America"] = {placetype = {"supercontinent", "continent"}, container = {key = "Earth", placetype = "planet"},
				keydesc = "[[America]], in the sense of [[North America]] and [[South America]] combined",
				wp = "Americas"},
		["Americas"] = {alias_of = "America", the = true},
			["North America"] = {placetype = "continent", container = {key = "America", placetype = "supercontinent"}},
				["Caribbean"] = {the = true, placetype = {"continental region", "region"}, container = {key = "North America", placetype = "continent"}},
				["Central America"] = {placetype = {"continental region", "region"}, container = {key = "North America", placetype = "continent"}},
			["South America"] = {placetype = "continent", container = {key = "America", placetype = "supercontinent"}},
		["Antarctica"] = {placetype = "continent", container = {key = "Earth", placetype = "planet"},
				fulldesc = "=the territory of [[Antarctica]]"},
		["Eurasia"] = {placetype = {"supercontinent", "continent"}, container = {key = "Earth", placetype = "planet"},
				keydesc = "[[Eurasia]], i.e. [[Europe]] and [[Asia]] together"},
			["Asia"] = {placetype = "continent", container = {key = "Eurasia", placetype = "supercontinent"}},
			["Europe"] = {placetype = "continent", container = {key = "Eurasia", placetype = "supercontinent"}},
		["Oceania"] = {placetype = "continent", container = {key = "Earth", placetype = "planet"}},
			["Melanesia"] = {placetype = {"continental region", "region"}, container = {key = "Oceania", placetype = "continent"}},
			["Micronesia"] = {placetype = {"continental region", "region"}, container = {key = "Oceania", placetype = "continent"}},
			["Polynesia"] = {placetype = {"continental region", "region"}, container = {key = "Oceania", placetype = "continent"}},
}

export.continents_group = {
	default_overriding_bare_label_parents = {}, -- container parents should be used
	default_divs = {{type = "countries", prep = "in"}},
	-- It's enough to mention the first-level continent or continent group. It seems excessive to write e.g.
	-- "El Salvador, a country in Central America, a continental region in North America, a continent in America, ...".
	default_no_include_container_in_desc = true,
	default_no_container_cat = true,
	default_no_container_parent = true,
	default_no_auto_augment_container = true,
	default_no_generic_place_cat = true,
	-- French Guyana is in France but not in Europe, which should not be an issue, so don't check holonym mismatches at
	-- this level. We also run into problems with supercontinents, which have "continent" as the fallback and cause
	-- mismatches.
	default_no_check_holonym_mismatch = true,
	data = export.continents,
}

-- Countries: including those with partial recognition that are normally considered countries (e.g. Kosovo, Taiwan).
export.countries = {
	["Afghanistan"] = {container = "Asia", divs = {"provinces", "districts"}},
	["Albania"] = {container = "Europe", divs = {"counties", "municipalities", "communes",
		{type = "administrative units", cat_as = "communes"},
	}, british_spelling = true},
	["Algeria"] = {container = "Africa", divs = {"provinces", "communes", "districts", "municipalities"}},
	["Andorra"] = {container = "Europe", divs = {"parishes"}, british_spelling = true},
	["Angola"] = {container = "Africa", divs = {"provinces", "municipalities"}},
	["Antigua and Barbuda"] = {container = "Caribbean", divs = {"provinces"}, british_spelling = true},
	["Argentina"] = {container = "South America", divs = {"provinces", "departments", "municipalities"}},
	["Armenia"] = {container = {"Europe", "Asia"}, divs = {"provinces", "districts", "municipalities"},
		british_spelling = true},
	["Republic of Armenia"] = {alias_of = "Armenia", the = true}, -- differs in "the"
	-- Both a country and continent
	["Australia"] = {container = "Oceania", divs = {
		{type = "states", cat_as = "states and territories"},
		{type = "territories", cat_as = "states and territories"},
		{type = "ABBREVIATION_OF states", cat_as = "abbreviations of states and territories"},
		{type = "ABBREVIATION_OF territories", cat_as = "abbreviations of states and territories"},
		"local government areas", "dependent territories",
	}, british_spelling = true},
	["Austria"] = {container = "Europe", divs = {"states", "districts", "municipalities"}, british_spelling = true},
	["Azerbaijan"] = {container = {"Europe", "Asia"}, divs = {"districts", "municipalities"}, british_spelling = true},
	["Bahamas"] = {the = true, container = "Caribbean", divs = {"districts"}, british_spelling = true, wp = "The %l"},
	["Bahrain"] = {container = "Asia", divs = {"governorates"}},
	["Bangladesh"] = {container = "Asia", divs = {"divisions", "districts", "municipalities"}, british_spelling = true},
	["Barbados"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Belarus"] = {container = "Europe", divs = {"regions", "districts"}, british_spelling = true},
	["Belgium"] = {container = "Europe", divs = {"regions", "provinces", "municipalities"}, british_spelling = true},
	["Belize"] = {container = "Central America", divs = {"districts"}, british_spelling = true},
	["Benin"] = {container = "Africa", divs = {"departments", "communes"}},
	["Bhutan"] = {container = "Asia", divs = {"districts", "gewogs"}},
	["Bolivia"] = {container = "South America", divs = {"provinces", "departments", "municipalities"}},
	["Bosnia and Herzegovina"] = {container = "Europe", divs = {"entities", "cantons", "municipalities"}, british_spelling = true},
	["Bosnia and Hercegovina"] = {alias_of = "Bosnia and Herzegovina", display = true},
	["Bosnia"] = {alias_of = "Bosnia and Herzegovina", display = true},
	["Botswana"] = {container = "Africa", divs = {"districts", "subdistricts"}, british_spelling = true},
	["Brazil"] = {container = "South America", divs = {
		"states", "municipalities", "macroregions",
		{type = "ABBREVIATION_OF states", cat_as = "abbreviations of states"},
	}},
	["Brunei"] = {container = "Asia", divs = {"districts", "mukims"}, british_spelling = true},
	["Bulgaria"] = {container = "Europe", divs = {"provinces", "municipalities"}, british_spelling = true},
	["Burkina Faso"] = {container = "Africa", divs = {"regions", "departments", "provinces"}},
	["Burundi"] = {container = "Africa", divs = {"provinces", "communes"}},
	["Cambodia"] = {container = "Asia", divs = {"provinces", "districts"}},
	["Cameroon"] = {container = "Africa", divs = {"regions", "departments"}},
	["Canada"] = {container = "North America", divs = {
		{type = "provinces", cat_as = "provinces and territories"},
		{type = "territories", cat_as = "provinces and territories"},
		{type = "ABBREVIATION_OF provinces", cat_as = "abbreviations of provinces and territories"},
		{type = "ABBREVIATION_OF territories", cat_as = "abbreviations of provinces and territories"},
		"counties", "districts", "municipalities", "regional municipalities",
		"rural municipalities", "parishes",
		-- Don't change the following to something more politically correct (e.g. "First Nations reserves") until/unless
		-- the Canadian government makes a similar switch (and note that as of Apr 18 2025, the Wikipedia article is
		-- still at [[w:Indian reserves]]).
		"Indian reserves",
		"census divisions",
		{type = "townships", prep = "in"},
	},
		british_spelling = true},
	["Cape Verde"] = {container = "Africa", divs = {"municipalities", "parishes"}},
	["Central African Republic"] = {the = true, container = "Africa", divs = {"prefectures", "subprefectures"}},
	["Chad"] = {container = "Africa", divs = {"regions", "departments"}},
	["Chile"] = {container = "South America", divs = {"regions", "provinces", "communes"}},
	["China"] = {container = "Asia", divs = {
		{type = "provinces", cat_as = "provinces and autonomous regions"},
		{type = "autonomous regions", cat_as = "provinces and autonomous regions"},
		{type = "FORMER provinces", cat_as = "former provinces"},
		"special administrative regions",
		"prefectures",
		{type = "FORMER prefectures", cat_as = "former prefectures"},
		"prefecture-level cities",
		{type = "counties", cat_as = "counties and county-level cities"},
		{type = "county-level cities", cat_as = "counties and county-level cities"},
		{type = "FORMER counties", cat_as = "former counties and county-level cities"},
		{type = "FORMER county-level cities", cat_as = "former counties and county-level cities"},
		-- "towns" (but not "townships") are automatically added as they are specified as generic_before_non_cities.
		"districts",
		{type = "FORMER districts", cat_as = "former districts"},
		"subdistricts",
		"townships",
		"municipalities",
		{type = "direct-administered municipalities", cat_as = "municipalities"},
	}},
	["People's Republic of China"] = {alias_of = "China", the = true}, -- differs in "the"
	["Colombia"] = {container = "South America", divs = {"departments", "municipalities"}},
	["Comoros"] = {the = true, container = "Africa", divs = {"autonomous islands"}},
	["Costa Rica"] = {container = "Central America", divs = {"provinces", "cantons"}},
	["Croatia"] = {container = "Europe", divs = {"counties", "municipalities"}, british_spelling = true},
	["Cuba"] = {container = "Caribbean", divs = {"provinces", "municipalities"}},
	["Cyprus"] = {container = {"Europe", "Asia"}, divs = {"districts"}, british_spelling = true},
	["Czech Republic"] = {the = true, container = "Europe", divs = {"regions", "districts", "municipalities"}, british_spelling = true},
	["Czechia"] = {alias_of = "Czech Republic"}, -- differs in "the"
	["Democratic Republic of the Congo"] = {the = true, container = "Africa", divs = {"provinces", "territories"}},
	["Congo"] = {alias_of = "Democratic Republic of the Congo", display = true, the = true},
	["Denmark"] = {container = "Europe", divs = {"regions", "municipalities", "dependent territories"},
		british_spelling = true,
		-- Wikipedia separates [[w:Denmark]] (constituent country) from [[w:Danish Realm]] (country)
	},
	["Djibouti"] = {container = "Africa", divs = {"regions", "districts"}},
	["Dominica"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Dominican Republic"] = {the = true, container = "Caribbean", divs = {"provinces", "municipalities"},
		keydesc = "the [[Dominican Republic]], the country that shares the [[Caribbean]] island of [[Hispaniola]] with [[Haiti]]"},
	["East Timor"] = {container = "Asia", divs = {"municipalities"}, wp = "Timor-Leste"},
	["Timor-Leste"] = {alias_of = "East Timor", display = true},
	["Ecuador"] = {container = "South America", divs = {"provinces", "cantons"}},
	["Egypt"] = {container = "Africa", divs = {"governorates", "regions"}, british_spelling = true},
	["El Salvador"] = {container = "Central America", divs = {"departments", "municipalities"}},
	["Equatorial Guinea"] = {container = "Africa", divs = {"provinces"}},
	["Eritrea"] = {container = "Africa", divs = {"regions", "subregions"}},
	["Estonia"] = {container = "Europe", divs = {"counties", "municipalities"}, british_spelling = true},
	["Eswatini"] = {container = "Africa", british_spelling = true},
	["Swaziland"] = {alias_of = "Eswatini", display = true},
	["Ethiopia"] = {container = "Africa", divs = {"regions", "zones"}},
	["Federated States of Micronesia"] = {the = true, container = "Micronesia", divs = {"states"}},
	["Micronesia"] = {alias_of = "Federated States of Micronesia"},
	["Fiji"] = {container = "Melanesia", divs = {"divisions", "provinces"}, british_spelling = true},
	["Finland"] = {container = "Europe", divs = {"regions", "municipalities"}, british_spelling = true},
	["France"] = {container = "Europe", divs = {"regions", "cantons", "collectivities",
		"communes",
		{type = "municipalities", cat_as = "communes"},
		"departments",
		{type = "prefectures", cat_as = {"prefectures", "departmental capitals"}},
		{type = "French prefectures", cat_as = {"prefectures", "departmental capitals"}},
		"dependent territories", "territories", "provinces",
	}, british_spelling = true},
	["Gabon"] = {container = "Africa", divs = {"provinces", "departments"}},
	["Gambia"] = {the = true, container = "Africa", divs = {"divisions", "districts"}, british_spelling = true, wp = "The %l"},
	["Georgia"] = {container = {"Europe", "Asia"}, divs = {"regions", "districts"},
		keydesc = "the country of [[Georgia]], in [[Eurasia]]", british_spelling = true, wp = "%l (country)"},
	["Germany"] = {container = "Europe", divs = {
		"states",
		-- Bavaria, Baden-Württemberg, Hesse and North Rhine-Westphalia have administrative regions as divisions, but
		-- there aren't really enough of them to categorize per state.
		"regions",
		"municipalities", "districts"}, british_spelling = true},
	["Ghana"] = {container = "Africa", divs = {"regions", "districts"}, british_spelling = true},
	["Greece"] = {container = "Europe", divs = {"regions", "regional units", "municipalities",
		{type = "peripheries", cat_as = {"regions"}},
	}, british_spelling = true},
	["Grenada"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Guatemala"] = {container = "Central America", divs = {"departments", "municipalities"}},
	["Guinea"] = {container = "Africa", divs = {"regions", "prefectures"}},
	["Guinea-Bissau"] = {container = "Africa", divs = {"regions"}},
	["Guyana"] = {container = "South America", divs = {"regions"}, british_spelling = true},
	["Haiti"] = {container = "Caribbean", divs = {"departments", "arrondissements"}},
	["Honduras"] = {container = "Central America", divs = {"departments", "municipalities"}},
	["Hungary"] = {container = "Europe", divs = {"counties", "districts"}, british_spelling = true},
	["Iceland"] = {container = "Europe", divs = {"regions", "municipalities", "counties"}, british_spelling = true},
	["India"] = {container = "Asia", divs = {
		{type = "states", cat_as = "states and union territories"},
		{type = "union territories", cat_as = "states and union territories"},
		{type = "ABBREVIATION_OF states", cat_as = "abbreviations of states and union territories"},
		{type = "ABBREVIATION_OF union territories", cat_as = "abbreviations of states and union territories"},
		"divisions", "districts", "municipalities",
	}, british_spelling = true},
	["Indonesia"] = {container = "Asia", divs = {"regencies", "provinces",
		{type = "ABBREVIATION_OF provinces", cat_as = "abbreviations of provinces"},
	}},
	["Iran"] = {container = "Asia", divs = {"provinces", "counties"}},
	["Iraq"] = {container = "Asia", divs = {"governorates", "districts"}},
	["Ireland"] = {container = "Europe", addl_parents = {"British Isles"},
		divs = {"counties", "districts", "provinces"}, british_spelling = true, wp = "Republic of %l"},
	["Republic of Ireland"] = {alias_of = "Ireland", the = true}, -- differs in "the"
	["Israel"] = {container = "Asia", divs = {"districts"}},
	["Italy"] = {container = "Europe", divs = {
		"regions", "provinces", "metropolitan cities", "municipalities",
		{type = "autonomous regions", cat_as = "regions"},
	}, british_spelling = true},
	["Ivory Coast"] = {container = "Africa", divs = {"districts", "regions"}},
	-- We should really be using Ivory Coast (common name) but there are political ramifications to the use of
	-- Côte d'Ivoire so don't make it a display alias.
	["Côte d'Ivoire"] = {alias_of = "Ivory Coast"},
	["Jamaica"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Japan"] = {container = "Asia", divs = {"prefectures", "subprefectures", "municipalities"}},
	["Jordan"] = {container = "Asia", divs = {"governorates"}},
	["Kazakhstan"] = {container = {"Asia", "Europe"}, divs = {"regions", "districts"}},
	["Kenya"] = {container = "Africa", divs = {"counties"}, british_spelling = true},
	["Kiribati"] = {container = "Micronesia", british_spelling = true},
	["Kosovo"] = {container = "Europe", divs = {"districts", "municipalities"}, british_spelling = true},
	["Kuwait"] = {container = "Asia", divs = {"governorates", "areas"}},
	["Kyrgyzstan"] = {container = "Asia", divs = {"regions", "districts"}},
	["Laos"] = {container = "Asia", divs = {"provinces", "districts"}},
	["Latvia"] = {container = "Europe", divs = {"municipalities"}, british_spelling = true},
	["Lebanon"] = {container = "Asia", divs = {"governorates", "districts"}},
	["Lesotho"] = {container = "Africa", divs = {"districts"}, british_spelling = true},
	["Liberia"] = {container = "Africa", divs = {"counties", "districts"}},
	["Libya"] = {container = "Africa", divs = {"districts", "municipalities"}},
	["Liechtenstein"] = {container = "Europe", divs = {"municipalities"}, british_spelling = true},
	["Lithuania"] = {container = "Europe", divs = {"counties", "municipalities"}, british_spelling = true},
	["Luxembourg"] = {container = "Europe", divs = {"cantons", "districts"}, british_spelling = true},
	["Madagascar"] = {container = "Africa", divs = {"regions", "districts"}},
	["Malawi"] = {container = "Africa", divs = {"regions", "districts"}, british_spelling = true},
	["Malaysia"] = {container = "Asia", divs = {"states", "federal territories", "districts"}, british_spelling = true},
	["Maldives"] = {the = true, container = "Asia", divs = {"provinces", "administrative atolls"}, british_spelling = true},
	["Mali"] = {container = "Africa", divs = {"regions", "cercles"}},
	["Malta"] = {container = "Europe", divs = {"regions", "local councils"}, british_spelling = true},
	["Marshall Islands"] = {the = true, container = "Micronesia", divs = {"municipalities"}},
	["Mauritania"] = {container = "Africa", divs = {"regions", "departments"}},
	["Mauritius"] = {container = "Africa", divs = {"districts"}, british_spelling = true},
	["Mexico"] = {container = "North America", addl_parents = {"Central America"}, divs = {
		"states", "municipalities",
		{type = "ABBREVIATION_OF states", cat_as = "abbreviations of states"},
	}},
	["Moldova"] = {container = "Europe", divs = {
		{type = "districts", cat_as = "districts and autonomous territorial units"},
		{type = "autonomous territorial units", cat_as = "districts and autonomous territorial units"},
		"communes", "municipalities",
	}, british_spelling = true},
	["Monaco"] = {placetype = {"city-state", "country"}, container = "Europe",
		-- We want the first placetype to be 'city-state' so the description of Monaco says it's a city-state, but we
		-- want its parent to be "countries in Europe".
		bare_category_parent_type = {type = "countries", prep = "in"},
		is_city = true, british_spelling = true},
	["Mongolia"] = {container = "Asia", divs = {"provinces", "districts"}},
	["Montenegro"] = {container = "Europe", divs = {"municipalities"}},
	["Morocco"] = {container = "Africa", divs = {"regions", "prefectures", "provinces"}},
	["Mozambique"] = {container = "Africa", divs = {"provinces", "districts"}},
	["Myanmar"] = {container = "Asia",
		divs = {"regions", "states", "union territories",
		{type = "self-administered zones", cat_as = "self-administered areas"},
		{type = "self-administered divisions", cat_as = "self-administered areas"},
		"districts"}},
	["Burma"] = {alias_of = "Myanmar"}, -- not display-canonicalizing; has political connotations
	["Namibia"] = {container = "Africa", divs = {"regions", "constituencies"}, british_spelling = true},
	["Nauru"] = {container = "Micronesia", divs = {"districts"}, british_spelling = true},
	["Nepal"] = {container = "Asia", divs = {"provinces", "districts"}},
	["Netherlands"] = {the = true, placetype = {"country", "constituent country"}, container = "Europe",
		divs = {"provinces", "municipalities",
			{type = "FORMER municipalities", cat_as = "former municipalities"},
			"dependent territories", "constituent countries"}, british_spelling = true,
		-- Wikipedia separates [[w:Netherlands]] (constituent country) from [[w:Kingdom of the Netherlands]]
		-- (country)
	},
	["New Zealand"] = {container = "Polynesia", divs = {
		"regions", "dependent territories", "territorial authorities",
		{type = "districts", cat_as = "territorial authorities"},
	},
		british_spelling = true},
	["Nicaragua"] = {container = "Central America", divs = {"departments", "municipalities"}},
	["Niger"] = {container = "Africa", divs = {"regions", "departments"}},
	["Nigeria"] = {container = "Africa", divs = {
		"states",
		-- Categorize the Federal Capital Territory as a state because there's only one of it; we could categorize
		-- everything under 'states and territories' but that seems a bit pointless.
		{type = "federal territories", cat_as = "states"},
		"local government areas",
	}, british_spelling = true},
	["North Korea"] = {container = "Asia", addl_parents = {"Korea"}, divs = {"provinces", "counties"}},
	["North Macedonia"] = {container = "Europe", divs = {"regions", "municipalities"}, british_spelling = true},
	["Macedonia"] = {alias_of = "North Macedonia", display = true},
	["Republic of North Macedonia"] = {alias_of = "North Macedonia", the = true}, -- differs in "the"
	["Republic of Macedonia"] = {alias_of = "North Macedonia", the = true}, -- differs in "the"
	["Norway"] = {container = "Europe",
		divs = {"counties", "municipalities", "dependent territories", "districts", "unincorporated areas"},
		british_spelling = true},
	["Oman"] = {container = "Asia", divs = {"governorates", "provinces"}},
	["Pakistan"] = {container = "Asia", divs = {
		{type = "provinces", cat_as = "provinces and territories"},
		{type = "administrative territories", cat_as = "provinces and territories"},
		{type = "federal territories", cat_as = "provinces and territories"},
		{type = "territories", cat_as = "provinces and territories"},
		"divisions", "districts",
	}, british_spelling = true},
	["Palau"] = {container = "Micronesia", divs = {"states"}},
	["Palestine"] = {container = "Asia", divs = {"governorates"}},
	["State of Palestine"] = {alias_of = "Palestine", the = true}, -- differs in "the"
	["Panama"] = {container = "Central America", divs = {"provinces", "districts"}},
	["Papua New Guinea"] = {container = "Melanesia", divs = {"provinces", "districts"}, british_spelling = true},
	["Paraguay"] = {container = "South America", divs = {"departments", "districts"}},
	["Peru"] = {container = "South America", divs = {"regions", "provinces", "districts"}},
	["Philippines"] = {the = true, container = "Asia", divs = {"regions", "provinces", "districts", "municipalities", "barangays"}},
	["Poland"] = {divs = {"voivodeships", "counties",
		{type = "Polish colonies", cat_as = {{type = "villages", prep = "in"}}},
	}, container = "Europe", british_spelling = true},
	["Portugal"] = {container = "Europe", divs = {
		{type = "autonomous regions", cat_as = "districts and autonomous regions"},
		{type = "districts", cat_as = "districts and autonomous regions"},
		"provinces", "municipalities"}, british_spelling = true},
	["Qatar"] = {container = "Asia", divs = {"municipalities", "zones"}},
	["Republic of the Congo"] = {the = true, container = "Africa", divs = {"departments", "districts"}},
	["Congo Republic"] = {alias_of = "Republic of the Congo", display = true, the = true},
	["Romania"] = {container = "Europe", divs = {
		"regions", "counties", "communes",
		{type = "ABBREVIATION_OF counties", cat_as = "abbreviations of counties"},
	}, british_spelling = true},
	["Russia"] = {container = {"Europe", "Asia"}, divs = {
		"federal subjects", "republics", "autonomous oblasts", "autonomous okrugs", "oblasts", "krais", "federal cities",
		"districts", "federal districts"},
		british_spelling = true},
	["Rwanda"] = {container = "Africa", divs = {"provinces", "districts"}},
	["Saint Kitts and Nevis"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Saint Lucia"] = {container = "Caribbean", divs = {"districts"}, british_spelling = true},
	["Saint Vincent and the Grenadines"] = {container = "Caribbean", divs = {"parishes"}, british_spelling = true},
	["Samoa"] = {container = "Polynesia", divs = {"districts"}, british_spelling = true},
	["San Marino"] = {container = "Europe", divs = {"municipalities"}, british_spelling = true},
	["São Tomé and Príncipe"] = {container = "Africa", divs = {"districts"}},
	["Saudi Arabia"] = {container = "Asia", divs = {"provinces", "governorates"}},
	["Senegal"] = {container = "Africa", divs = {"regions", "departments"}},
	["Serbia"] = {container = "Europe", divs = {"districts", "municipalities", "autonomous provinces"}},
	["Seychelles"] = {container = "Africa", divs = {"districts"}, british_spelling = true},
	["Sierra Leone"] = {container = "Africa", divs = {"provinces", "districts"}, british_spelling = true},
	["Singapore"] = {container = "Asia", divs = {"districts"}, british_spelling = true},
	["Slovakia"] = {container = "Europe", divs = {"regions", "districts"}, british_spelling = true},
	["Slovenia"] = {container = "Europe", divs = {"statistical regions", "municipalities"}, british_spelling = true},
	-- Note: the official name does not include "the" at the beginning, but it sounds strange in
	-- English to leave it out and it's commonly included, so we include it.
	["Solomon Islands"] = {the = true, container = "Melanesia", divs = {"provinces"}, british_spelling = true},
	["Somalia"] = {container = "Africa", divs = {"regions", "districts"}},
	["South Africa"] = {container = "Africa", divs = {
		"provinces",
		"districts",
		{type = "district municipalities", cat_as = "districts"},
		{type = "metropolitan municipalities", cat_as = "districts"},
		"municipalities",
	}, british_spelling = true},
	["South Korea"] = {container = "Asia", addl_parents = {"Korea"}, divs = {"provinces", "counties", "districts"}},
	["South Sudan"] = {container = "Africa", divs = {"regions", "states", "counties"}, british_spelling = true},
	["Spain"] = {container = "Europe", divs = {"autonomous communities", "provinces", "municipalities",
		"comarcas", "autonomous cities"},
		british_spelling = true},
	["Sri Lanka"] = {container = "Asia", divs = {"provinces", "districts"}, british_spelling = true},
	["Sudan"] = {container = "Africa", divs = {"states", "districts"}, british_spelling = true},
	["Suriname"] = {container = "South America", divs = {"districts"}},
	["Sweden"] = {container = "Europe", divs = {"provinces", "counties", "municipalities"}, british_spelling = true},
	["Switzerland"] = {container = "Europe", divs = {"cantons", "municipalities", "districts"}, british_spelling = true},
	["Syria"] = {container = "Asia", divs = {"governorates", "districts"}},
	["Taiwan"] = {container = "Asia", divs = {"counties", "districts", "townships", "special municipalities"}},
	["Republic of China"] = {alias_of = "Taiwan", the = true}, -- differs in "the", different political connotations
	["Tajikistan"] = {container = "Asia", divs = {"regions", "districts"}},
	["Tanzania"] = {container = "Africa", divs = {"regions", "districts"}, british_spelling = true},
	["Thailand"] = {container = "Asia", divs = {"provinces", "districts", "subdistricts"}},
	["Togo"] = {container = "Africa", divs = {"provinces", "prefectures"}},
	["Tonga"] = {container = "Polynesia", divs = {"divisions"}, british_spelling = true},
	["Trinidad and Tobago"] = {container = "Caribbean", divs = {"regions", "municipalities"}, british_spelling = true},
	["Tunisia"] = {container = "Africa", divs = {"governorates", "delegations"}},
	["Turkey"] = {container = {"Europe", "Asia"}, divs = {"provinces", "districts"}},
	-- Foreign names generally get display-canonicalized.
	["Türkiye"] = {alias_of = "Turkey", display = true},
	["Turkmenistan"] = {container = "Asia", divs = {
		-- The 5 regions are often also called provinces
		"regions", {type = "provinces", cat_as = "regions"}, "districts"},
	},
	["Tuvalu"] = {container = "Polynesia", divs = {"atolls"}, british_spelling = true},
	["Uganda"] = {container = "Africa", divs = {"districts", "counties"}, british_spelling = true},
	["Ukraine"] = {container = "Europe", divs = {
		{type = "oblasts", cat_as = "oblasts and autonomous republics"},
		{type = "autonomous republics", cat_as = "oblasts and autonomous republics"},
		"raions", "hromadas",
	}, british_spelling = true},
	["United Arab Emirates"] = {the = true, container = "Asia", divs = {"emirates"}},
	-- Abbreviations get display-canonicalized.
	["UAE"] = {alias_of = "United Arab Emirates", display = true, the = true},
	["U.A.E."] = {alias_of = "United Arab Emirates", display = true, the = true},
	["United Kingdom"] = {the = true, container = "Europe", addl_parents = {"British Isles"},
		divs = {"constituent countries", "counties", "districts", "boroughs", "territories", "dependent territories",
			"traditional counties"},
		keydesc = "the [[United Kingdom]] of Great Britain and Northern Ireland", british_spelling = true},
	-- Abbreviations get display-canonicalized.
	["UK"] = {alias_of = "United Kingdom", display = true, the = true},
	["U.K."] = {alias_of = "United Kingdom", display = true, the = true},
	["United States"] = {the = true, container = "North America",
		divs = {"counties", "county seats", "states", "territories", "dependent territories",
			{type = "ABBREVIATION_OF states", cat_as = "abbreviations of states"},
			{type = "DEROGATORY_NAME_FOR states", cat_as = "derogatory names for states"},
			{type = "NICKNAME_FOR states", cat_as = "nicknames for states"},
			{type = "OFFICIAL_NICKNAME_FOR states", cat_as = "official nicknames for states"},
			{type = "boroughs", prep = "in"}, -- exist in Pennsylvania and New Jersey
			"municipalities", -- these exist politically at least in Colorado and Connecticut
			{type = "census-designated places", prep = "in"},
			{type = "unincorporated communities", prep = "in"},
			-- Don't change the following to something more politically correct until/unless the US government makes a
			-- similar switch (and note that as of Apr 18 2025, the Wikipedia article is still at
			-- [[w:Indian reservations]]).
			"Indian reservations",
		}},
	-- Abbreviations and long forms (when possible) get display-canonicalized.
	["US"] = {alias_of = "United States", display = true, the = true},
	["U.S."] = {alias_of = "United States", display = true, the = true},
	["USA"] = {alias_of = "United States", display = true, the = true},
	["U.S.A."] = {alias_of = "United States", display = true, the = true},
	["United States of America"] = {alias_of = "United States", display = true, the = true},
	["Uruguay"] = {container = "South America", divs = {"departments", "municipalities"}},
	["Uzbekistan"] = {container = "Asia", divs = {"regions", "districts"}},
	["Vanuatu"] = {container = "Melanesia", divs = {"provinces"}, british_spelling = true},
	["Vatican City"] = {placetype = {"city-state", "country"}, container = "Europe",
		-- We want the first placetype to be 'city-state' so the description of Vatican City says it's a city-state,
		-- but we want its parent to be "countries in Europe".
		bare_category_parent_type = {type = "countries", prep = "in"},
		addl_parents = {"Rome"}, is_city = true, british_spelling = true},
	["Vatican"] = {alias_of = "Vatican City", the = true}, -- differs in "the"
	["Venezuela"] = {container = "South America", divs = {"states", "municipalities"}},
	["Vietnam"] = {container = "Asia", divs = {"provinces", "districts", "municipalities"}},
	["Western Sahara"] = {placetype = {"territory", "country"}, container = "Africa",
		bare_category_parent_type = {type = "countries", prep = "in"},
	},
	-- Not display-canonicalizable both due to differences in 'the' and the sovereignty dispute over Western Sahara
	["Sahrawi Arab Democratic Republic"] = {alias_of = "Western Sahara", the = true},
	["Yemen"] = {container = "Asia", divs = {"governorates", "districts"}},
	["Zambia"] = {container = "Africa", divs = {"provinces", "districts"}, british_spelling = true},
	["Zimbabwe"] = {container = "Africa", divs = {"provinces", "districts"}, british_spelling = true},
}

local function canonicalize_continent_container(key)
	if type(key) ~= "string" then
		return key
	end
	if export.continents[key] then
		return {key = key, placetype = export.continents[key].placetype}
	end
end

export.countries_group = {
	canonicalize_key_container = canonicalize_continent_container,
	default_overriding_bare_label_parents = {"+++", "countries"},
	default_placetype = "country",
	default_no_container_cat = true,
	default_no_container_parent = true,
	-- No need to augment country holonyms with continents; not needed for disambiguation.
	default_no_auto_augment_container = true,
	data = export.countries,
}

-- Country-like entities: typically overseas territories or de-facto independent countries, which in both cases
-- are not internationally recognized as sovereign nations but which we treat similarly to countries.
export.country_like_entities = {
	-- British Overseas Territory
	["Akrotiri and Dhekelia"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Cyprus", "Europe", "Asia"},
		british_spelling = true,
	},
	-- Åland: Listed as a region of Finland. Wikipedia lists this under "dependent territories" in
	--   [[w:List of sovereign states and dependent territories by continent]].
	-- unincorporated territory of the United States
	["American Samoa"] = {
		placetype = {"unincorporated territory", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Polynesia"},
	},
	-- British Overseas Territory
	["Anguilla"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- de-facto independent state, internationally recognized as part of Georgia
	["Abkhazia"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Georgia", "Europe", "Asia"},
		divs = {"districts"},
		keydesc = "the de-facto independent state of [[Abkhazia]], internationally recognized as part of the country of [[Georgia]]",
		british_spelling = true,
	},
	-- Australian external territory
	["Ashmore and Cartier Islands"] = {
		the = true,
		placetype = {"external territory", "territory"},
		container = "Australia",
		addl_parents = {"Asia"},
	},
	-- constituent country of the Netherlands
	["Aruba"] = {
		placetype = {"constituent country", "country"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- British Overseas Territory
	["Bermuda"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"North America"},
		british_spelling = true,
	},
	-- special municipality of the Netherlands
	["Bonaire"] = {
		placetype = {"special municipality", "municipality", "overseas territory", "territory"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		is_city = true,
		british_spelling = true,
	},
	-- British Overseas Territory
	["British Indian Ocean Territory"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Asia"},
		british_spelling = true,
	},
	-- British Overseas Territory
	["British Virgin Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- Norwegian dependent territory
	["Bouvet Island"] = {
		placetype = {"dependent territory", "territory"},
		container = "Norway",
		addl_parents = {"Africa"},
		british_spelling = true,
	},
	-- British Overseas Territory
	["Cayman Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- Australian external territory
	["Christmas Island"] = {
		placetype = {"external territory", "territory"},
		container = "Australia",
		addl_parents = {"Asia"},
		british_spelling = true,
	},
	-- Sui generis French "state private property" per Wikipedia; classify as overseas territory like the
	-- French Southern and Antarctic Lands.
	["Clipperton Island"] = {
		placetype = {"overseas territory", "territory"},
		container = "France",
		addl_parents = {"North America"},
	},
	-- Australian external territory; also called the Keeling Islands or (officially) the Cocos (Keeling) Islands
	["Cocos Islands"] = {
		the = true,
		placetype = {"external territory", "territory"},
		container = "Australia",
		addl_parents = {"Asia"},
		wp = "Cocos (Keeling) Islands",
		british_spelling = true,
	},
	["Cocos (Keeling) Islands"] = {alias_of = "Cocos Islands", display = true, the = true},
	["Keeling Islands"] = {alias_of = "Cocos Islands", display = true, the = true},
	-- self-governing but in free association with New Zealand
	["Cook Islands"] = {
		the = true,
		placetype = {"country"},
		container = "New Zealand",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- constituent country of the Netherlands
	["Curaçao"] = {
		placetype = {"constituent country", "country"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- special territory of Chile
	["Easter Island"] = {
		placetype = {"special territory", "territory"},
		container = "Chile",
		addl_parents = {"Polynesia"},
	},
	-- British Overseas Territory
	["Falkland Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"South America"},
		british_spelling = true,
	},
	-- autonomous territory of Denmark
	["Faroe Islands"] = {
		the = true,
		placetype = {"autonomous territory", "territory"},
		container = "Denmark",
		addl_parents = {"Europe"},
		british_spelling = true,
	},
	-- overseas department and region of France
	["French Guiana"] = {
		placetype = {"overseas department", "department", "administrative region", "region"},
		container = "France",
		divs = {"communes"},
		addl_parents = {"South America"},
		british_spelling = true,
	},
	-- overseas collectivity of France
	["French Polynesia"] = {
		placetype = {"overseas collectivity", "collectivity"},
		container = "France",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- French overseas territory
	["French Southern and Antarctic Lands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "France",
		addl_parents = {"Africa"},
	},
	-- British Overseas Territory
	["Gibraltar"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Europe"},
		is_city = true,
		british_spelling = true,
	},
	-- autonomous territory of Denmark
	["Greenland"] = {
		placetype = {"autonomous territory", "territory"},
		container = "Denmark",
		addl_parents = {"North America"},
		divs = {"municipalities"},
		british_spelling = true,
	},
	-- overseas department and region of France
	["Guadeloupe"] = {
		placetype = {"overseas department", "department", "administrative region", "region"},
		container = "France",
		addl_parents = {"Caribbean"},
		divs = {"communes"},
		british_spelling = true,
	},
	-- unincorporated territory of the United States
	["Guam"] = {
		placetype = {"unincorporated territory", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Micronesia"},
	},
	-- self-governing British Crown dependency; technically called the Bailiwick of Guernsey
	["Guernsey"] = {
		placetype = {"crown dependency", "dependency", "dependent territory", "bailiwick", "territory"},
		container = "United Kingdom",
		addl_parents = {"British Isles", "Europe"},
		british_spelling = true,
		wp = "Bailiwick of %l",
	},
	["Bailiwick of Guernsey"] = {alias_of = "Guernsey", the = true},
	-- Australian external territory
	["Heard Island and McDonald Islands"] = {
		the = true,
		placetype = {"external territory", "territory"},
		container = "Australia",
		addl_parents = {"Africa"},
	},
	-- special administrative region of China
	["Hong Kong"] = {
		placetype = {"special administrative region", "city"},
		container = "China",
		is_city = true,
		british_spelling = true,
	},
	-- self-governing British Crown dependency
	["Isle of Man"] = {
		the = true,
		placetype = {"crown dependency", "dependency", "dependent territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"British Isles", "Europe"},
		british_spelling = true,
	},
	-- Norwegian unincorporated area
	["Jan Mayen"] = {
		placetype = {"unincorporated area", "dependent territory", "territory", "island"},
		container = "Norway",
		addl_parents = {"Europe"},
		british_spelling = true,
	},
	-- self-governing British Crown dependency; technically called the Bailiwick of Jersey
	["Jersey"] = {
		placetype = {"crown dependency", "dependency", "dependent territory", "bailiwick", "territory"},
		container = "United Kingdom",
		addl_parents = {"British Isles", "Europe"},
		british_spelling = true,
	},
	["Bailiwick of Jersey"] = {alias_of = "Jersey", the = true},
	-- special administrative region of China
	["Macau"] = {
		placetype = {"special administrative region", "city"},
		container = "China",
		is_city = true,
		british_spelling = true,
	},
	-- overseas department and region of France
	["Martinique"] = {
		placetype = {"overseas department", "department", "administrative region", "region"},
		container = "France",
		divs = {"communes"},
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- overseas department and region of France
	["Mayotte"] = {
		placetype = {"overseas department", "department", "administrative region", "region"},
		container = "France",
		divs = {"communes"},
		addl_parents = {"Africa"},
		british_spelling = true,
	},
	-- British Overseas Territory
	["Montserrat"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- special collectivity of France
	["New Caledonia"] = {
		placetype = {"special collectivity", "collectivity"},
		container = "France",
		addl_parents = {"Melanesia"},
		british_spelling = true,
	},
	-- dependent territory of New Zealand
	["New Zealand Subantarctic Islands"] = {
		the = true,
		placetype = {"dependent territory", "territory"},
		container = "New Zealand",
		addl_parents = {"Antarctica"},
		british_spelling = true,
	},
	-- self-governing but in free association with New Zealand
	["Niue"] = {
		placetype = {"country"},
		container = "New Zealand",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- Australian external territory
	["Norfolk Island"] = {
		placetype = {"external territory", "territory"},
		container = "Australia",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- de-facto independent state, internationally recognized as part of Cyprus
	["Northern Cyprus"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Cyprus", "Turkey", "Europe", "Asia"},
		divs = {"districts"},
		keydesc = "the de-facto independent state of [[Northern Cyprus]], internationally recognized as part of the country of [[Cyprus]]",
		british_spelling = true,
	},
	-- commonwealth, unincorporated territory of the United States
	["Northern Mariana Islands"] = {
		the = true,
		placetype = {"commonwealth", "unincorporated territory", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Micronesia"},
	},
	-- British Overseas Territory
	["Pitcairn Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- commonwealth of the United States
	["Puerto Rico"] = {
		placetype = {"commonwealth", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Caribbean"},
		divs = {"municipalities"},
	},
	-- overseas department and region of France
	["Réunion"] = {
		placetype = {"overseas department", "department", "administrative region", "region"},
		container = "France",
		divs = {"communes"},
		addl_parents = {"Africa"},
		british_spelling = true,
	},
	-- special municipality of the Netherlands
	["Saba"] = {
		placetype = {"special municipality", "municipality", "overseas territory", "territory"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		is_city = true,
		british_spelling = true,
	},
	-- overseas collectivity of France
	["Saint Barthélemy"] = {
		placetype = {"overseas collectivity", "collectivity"},
		container = "France",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- British Overseas Territory
	["Saint Helena, Ascension and Tristan da Cunha"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		divs = {{type = "constituent parts", container_parent_type = false}},
		addl_parents = {"Atlantic Ocean", "Africa"},
		british_spelling = true,
	},
		-- constituent parts of the combined oveseas territory
		["Ascension Island"] = {
			placetype = {"constituent part", "territory", "island"},
			container = {key = "Saint Helena, Ascension and Tristan da Cunha", placetype = "overseas territory"},
			addl_parents = {"Atlantic Ocean"},
			overriding_bare_label_parents = {},
			no_container_cat = false,
			no_container_parent = false,
			no_auto_augment_container = false,
		},
		["Saint Helena"] = {
			placetype = {"constituent part", "territory", "island"},
			container = {key = "Saint Helena, Ascension and Tristan da Cunha", placetype = "overseas territory"},
			addl_parents = {"Atlantic Ocean"},
			overriding_bare_label_parents = {},
			no_container_cat = false,
			no_container_parent = false,
			no_auto_augment_container = false,
		},
		["Tristan da Cunha"] = {
			placetype = {"constituent part", "territory", "archipelago"},
			container = {key = "Saint Helena, Ascension and Tristan da Cunha", placetype = "overseas territory"},
			addl_parents = {"Atlantic Ocean"},
			overriding_bare_label_parents = {},
			no_container_cat = false,
			no_container_parent = false,
			no_auto_augment_container = false,
		},
	-- overseas collectivity of France
	["Saint Martin"] = {
		placetype = {"overseas collectivity", "collectivity"},
		container = "France",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- overseas collectivity of France
	["Saint Pierre and Miquelon"] = {
		placetype = {"overseas collectivity", "collectivity"},
		container = "France",
		divs = {"communes"},
		addl_parents = {"North America"},
		british_spelling = true,
	},
	-- special municipality of the Netherlands
	["Sint Eustatius"] = {
		placetype = {"special municipality", "municipality", "overseas territory", "territory"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		is_city = true,
		british_spelling = true,
	},
	-- constituent country of the Netherlands
	["Sint Maarten"] = {
		placetype = {"constituent country", "country"},
		container = "Netherlands",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- de-facto independent state, internationally recognized as part of Somalia
	["Somaliland"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Somalia", "Africa"},
		keydesc = "the de-facto independent state of [[Somaliland]], internationally recognized as part of the country of [[Somalia]]",
		british_spelling = true,
	},
	-- British Overseas Territory
	-- FIXME: We should form the group "South Georgia and the South Sandwich Islands" like we did for
	-- "Saint Helena, Ascension and Tristan da Cunha".
	["South Georgia"] = {
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Atlantic Ocean"},
		british_spelling = true,
	},
	-- de-facto independent state, internationally recognized as part of Georgia
	["South Ossetia"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Georgia", "Europe", "Asia"},
		keydesc = "the de-facto independent state of [[South Ossetia]], internationally recognized as part of the country of [[Georgia]]",
		british_spelling = true,
	},
	-- British Overseas Territory
	["South Sandwich Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Atlantic Ocean"},
		wp = true,
		wpcat = "South Georgia and the South Sandwich Islands",
		british_spelling = true,
	},
	-- Norwegian unincorporated area
	["Svalbard"] = {
		placetype = {"unincorporated area", "dependent territory", "territory", "archipelago"},
		container = "Norway",
		addl_parents = {"Europe"},
		british_spelling = true,
	},
	-- dependent territory of New Zealand
	["Tokelau"] = {
		placetype = {"dependent territory", "territory"},
		container = "New Zealand",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
	-- de-facto independent state, internationally recognized as part of Moldova
	["Transnistria"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Moldova", "Europe"},
		keydesc = "the de-facto independent state of [[Transnistria]], internationally recognized as part of [[Moldova]]",
		british_spelling = true,
	},
	-- British Overseas Territory
	["Turks and Caicos Islands"] = {
		the = true,
		placetype = {"overseas territory", "territory"},
		container = "United Kingdom",
		addl_parents = {"Caribbean"},
		british_spelling = true,
	},
	-- unincorporated territory of the United States
	["United States Minor Outlying Islands"] = {
		the = true,
		placetype = {"unincorporated territory", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Islands", "Micronesia", "Polynesia", "Caribbean"},
	},
		-- FIXME: We should add entries for the other minor outlying islands.
		-- Baker Island (Oceania)
		-- Howland Island (Oceania)
		-- Jarvis Island (Oceania)
		-- Johnston Atoll (Oceania)
		-- Kingman Reef (Oceania)
		-- Midway Atoll (Oceania)
		-- Navassa Island (Caribbean)
		-- Palmyra Atoll (Oceania)
		-- Wake Island (Oceania)
		["Wake Island"] = {
			placetype = {"unincorporated territory", "overseas territory", "territory"},
			container = "United States",
			addl_parents = {"Micronesia"},
		},
	-- unincorporated territory of the United States
	["United States Virgin Islands"] = {
		the = true,
		placetype = {"unincorporated territory", "overseas territory", "territory"},
		container = "United States",
		addl_parents = {"Caribbean"},
	},
	["U.S. Virgin Islands"] = {alias_of = "United States Virgin Islands", display = true, the = true},
	["US Virgin Islands"] = {alias_of = "United States Virgin Islands", display = true, the = true},
	-- overseas collectivity of France
	["Wallis and Futuna"] = {
		placetype = {"overseas collectivity", "collectivity"},
		container = "France",
		addl_parents = {"Polynesia"},
		british_spelling = true,
	},
}

export.country_like_entities_group = {
	-- don't do any transformations between key and placename; in particular, don't chop off anything from
	-- "Saint Helena, Ascension and Tristan da Cunha".
	key_to_placename = false,
	placename_to_key = false,
	canonicalize_key_container = make_canonicalize_key_container(nil, "country"),
	default_overriding_bare_label_parents = {"country-like entities"},
	default_no_container_cat = true,
	default_no_container_parent = true,
	-- These entities often aren't really part of their container; a village in Wallis and Futuna (an overseas
	-- collectivity of France in Polynesia), for example, shouldn't be treated as a village in France, nor as a village
	-- in Europe.
	default_no_auto_augment_container = true,
	data = export.country_like_entities,
}

-- Former countries and such; we don't create "Cities in ..." categories because they don't exist anymore
export.former_countries = {
	-- de-facto independent state of Armenian ethnicity, internationally recognized as part of Azerbaijan
	-- (also known as Nagorno-Karabakh)
	-- NOTE: Formerly listed Armenia as a parent; this seems politically non-neutral so I've taken it out.
	["Artsakh"] = {
		placetype = {"unrecognized country", "country"},
		addl_parents = {"Azerbaijan", "Europe", "Asia"},
		keydesc = "the former de-facto independent state of [[Artsakh]], internationally recognized as part of [[Azerbaijan]]",
		british_spelling = true,
	},
	["Nagorno-Karabakh"] = {alias_of = "Artsakh"},
	["Czechoslovakia"] = {container = "Europe", british_spelling = true},
	["East Germany"] = {container = "Europe", addl_parents = {"Germany"}, british_spelling = true},
	["North Vietnam"] = {container = "Asia", addl_parents = {"Vietnam"}},
	["Persia"] = {placetype = {"empire", "country"}, container = "Asia", divs = {"provinces"}},
	["Byzantine Empire"] = {
		the = true, placetype = {"empire", "country"}, container = {"Europe", "Africa", "Asia"},
		addl_parents = {"Ancient Europe", "Ancient Near East"},
		divs = {
			"provinces", "themes",
		}},
	["Roman Empire"] = {
		the = true, placetype = {"empire", "country"}, container = {"Europe", "Africa", "Asia"}, addl_parents = {"Rome"},
		divs = {
			"provinces",
			{type = "FORMER provinces", cat_as = "provinces"},
		}},
	["South Vietnam"] = {container = "Asia", addl_parents = {"Vietnam"}},
	["Soviet Union"] = {
		the = true, container = {"Europe", "Asia"}, divs = {"republics", "autonomous republics"},
		british_spelling = true},
	["West Germany"] = {container = "Europe", addl_parents = {"Germany"}, british_spelling = true},
	["Yugoslavia"] = {container = "Europe", divs = {"districts"},
		keydesc = "the former [[Kingdom of Yugoslavia]] (1918–1943) or the former [[Socialist Federal Republic of Yugoslavia]] (1943–1992)", british_spelling = true},
}

export.former_countries_group = {
	canonicalize_key_container = canonicalize_continent_container,
	default_overriding_bare_label_parents = {"former countries and country-like entities"},
	default_is_former_place = true,
	default_placetype = "country",
	default_no_container_cat = true,
	default_no_container_parent = true,
	-- No need to augment country holonyms with continents; not needed for disambiguation.
	default_no_auto_augment_container = true,
	data = export.former_countries,
}

-----------------------------------------------------------------------------------
--                                  Subpolity tables                             --
-----------------------------------------------------------------------------------

export.australia_states_and_territories = {
	["Australian Capital Territory, Australia"] = {the = true, placetype = "territory"},
	["Jervis Bay Territory, Australia"] = {the = true, placetype = "territory"},
	["New South Wales, Australia"] = {},
	["Northern Territory, Australia"] = {the = true, placetype = "territory"},
	["Queensland, Australia"] = {},
	["South Australia, Australia"] = {},
	["Tasmania, Australia"] = {},
	["Victoria, Australia"] = {},
	["Western Australia, Australia"] = {},
}

-- states and territories of Australia
export.australia_group = {
	default_container = "Australia",
	default_placetype = "state",
	default_divs = "local government areas",
	data = export.australia_states_and_territories,
}

export.austria_states = {
	["Vienna, Austria"] = {},
	["Lower Austria, Austria"] = {},
	["Upper Austria, Austria"] = {},
	["Styria, Austria"] = {},
	["Tyrol, Austria"] = {wp = "Tyrol (state)"},
	["Carinthia, Austria"] = {},
	["Salzburg, Austria"] = {wp = "Salzburg (state)"},
	["Vorarlberg, Austria"] = {},
	["Burgenland, Austria"] = {},
}

-- states of Austria
export.austria_group = {
	default_container = "Austria",
	default_placetype = "state",
	default_divs = "municipalities",
	data = export.austria_states,
}

export.bangladesh_divisions = {
	["Barisal Division, Bangladesh"] = {},
	["Chittagong Division, Bangladesh"] = {},
	["Dhaka Division, Bangladesh"] = {},
	["Khulna Division, Bangladesh"] = {},
	["Mymensingh Division, Bangladesh"] = {},
	["Rajshahi Division, Bangladesh"] = {},
	["Rangpur Division, Bangladesh"] = {},
	["Sylhet Division, Bangladesh"] = {},
}

-- divisions of Bangladesh
export.bangladesh_group = {
	key_to_placename = make_key_to_placename(", Bangladesh$", " Division$"),
	placename_to_key = make_placename_to_key(", Bangladesh", " Division"),
	default_container = "Bangladesh",
	default_placetype = "division",
	default_divs = "districts",
	data = export.bangladesh_divisions,
}

export.brazil_states = {
	["Acre, Brazil"] = {wp = "%l (state)"},
	["Alagoas, Brazil"] = {},
	["Amapá, Brazil"] = {},
	["Amazonas, Brazil"] = {wp = "%l (Brazilian state)"},
	["Bahia, Brazil"] = {},
	["Ceará, Brazil"] = {},
	["Distrito Federal, Brazil"] = {wp = "Federal District (Brazil)"},
	["Espírito Santo, Brazil"] = {},
	["Goiás, Brazil"] = {},
	["Maranhão, Brazil"] = {},
	["Mato Grosso, Brazil"] = {},
	["Mato Grosso do Sul, Brazil"] = {},
	["Minas Gerais, Brazil"] = {},
	["Pará, Brazil"] = {},
	["Paraíba, Brazil"] = {},
	["Paraná, Brazil"] = {wp = "%l (state)"},
	["Pernambuco, Brazil"] = {},
	["Piauí, Brazil"] = {},
	["Rio de Janeiro, Brazil"] = {wp = "%l (state)"},
	["Rio Grande do Norte, Brazil"] = {},
	["Rio Grande do Sul, Brazil"] = {},
	["Rondônia, Brazil"] = {},
	["Roraima, Brazil"] = {},
	["Santa Catarina, Brazil"] = {wp = "%l (state)"},
	["São Paulo, Brazil"] = {wp = "%l (state)"},
	["Sergipe, Brazil"] = {},
	["Tocantins, Brazil"] = {},
}

-- states of Brazil
export.brazil_group = {
	default_container = "Brazil",
	default_placetype = "state",
	default_divs = "municipalities",
	data = export.brazil_states,
}

export.canada_provinces_and_territories = {
	["Alberta, Canada"] = {divs = {
		{type = "municipal districts", container_parent_type = "rural municipalities"},
	}},
	["British Columbia, Canada"] = {divs =
		{type = "regional districts", container_parent_type = false},
		"regional municipalities",
	},
	["Manitoba, Canada"] = {divs = {"rural municipalities"}},
	["New Brunswick, Canada"] = {divs = {"counties", "parishes", {type = "civil parishes", cat_as = "parishes"}}},
	["Newfoundland and Labrador, Canada"] = {},
	["Northwest Territories, Canada"] = {the = true, placetype = "territory"},
	["Nova Scotia, Canada"] = {divs = {"counties", "regional municipalities"}},
	["Nunavut, Canada"] = {placetype = "territory"},
	["Ontario, Canada"] = {divs = {"counties", "regional municipalities", {type = "townships", prep = "in"}}},
	["Prince Edward Island, Canada"] = {divs = {"counties", "parishes", "rural municipalities"}},
	["Saskatchewan, Canada"] = {divs = {"rural municipalities"}},
	["Quebec, Canada"] = {divs = {
		"counties",
		{type = "regional county municipalities", container_parent_type = "regional municipalities"},
		-- administrative regions have an official (but non-governmental) function but there don't appear to be any
		-- equivalent regions elsewhere in Canada, so disable the [[Category:Regions of Canada]] grouping
		{type = "regions", container_parent_type = false},
		{type = "townships", prep = "in"},
		{type = "parish municipalities", cat_as = {{type = "parishes", container_parent_type = "counties"}, "municipalities"}},
		{type = "township municipalities", cat_as = {{type = "townships", prep = "in"}, "municipalities"}},
		{type = "village municipalities", cat_as = {{type = "villages", prep = "in"}, "municipalities"}},
	}},
	["Yukon, Canada"] = {placetype = "territory"},
	["Yukon Territory, Canada"] = {alias_of = "Yukon, Canada", the = true},
}

-- provinces and territories of Canada
export.canada_group = {
	default_container = "Canada",
	default_placetype = "province",
	data = export.canada_provinces_and_territories,
}

export.china_provinces_and_autonomous_regions = {
	-- direct-administered municipalities are not here but below under prefecture-level cities
	["Anhui, China"] = {},
	["Fujian, China"] = {},
	["Fuchien, China"] = {alias_of = "Fujian, China", display = true},
	["Gansu, China"] = {},
	["Guangdong, China"] = {},
	["Guangxi, China"] = {placetype = "autonomous region"},
	["Guizhou, China"] = {},
	["Hainan, China"] = {},
	["Hebei, China"] = {},
	["Heilongjiang, China"] = {},
	["Henan, China"] = {},
	["Hubei, China"] = {},
	["Hunan, China"] = {},
	["Inner Mongolia, China"] = {placetype = "autonomous region"},
	["Jiangsu, China"] = {},
	["Jiangxi, China"] = {},
	["Jilin, China"] = {},
	["Liaoning, China"] = {},
	["Ningxia, China"] = {placetype = "autonomous region"},
	["Qinghai, China"] = {},
	["Shaanxi, China"] = {},
	["Shandong, China"] = {},
	["Shanxi, China"] = {},
	["Sichuan, China"] = {},
	["Tibet, China"] = {placetype = "autonomous region", wp = "Tibet Autonomous Region"},
	["Xinjiang, China"] = {placetype = "autonomous region"},
	["Yunnan, China"] = {},
	["Zhejiang, China"] = {},
}

-- provinces and autonomous regions of China
export.china_group = {
	default_container = "China",
	default_placetype = "province",
	default_divs = {
		"prefectures", "prefecture-level cities",
		"districts", "subdistricts", "townships",
		{type = "counties", cat_as = "counties and county-level cities"},
		{type = "county-level cities", cat_as = "counties and county-level cities"},
	},
	data = export.china_provinces_and_autonomous_regions,
}

export.china_prefecture_level_cities = {
	-- In China, a "prefecture-level city" is not a city in any real sense. It is rather a prefecture, which is an
	-- administrative unit smaller than a province but bigger than a county, which is administratively controlled by
	-- the chief city of the prefecture (which bears the same name as the prefecture), in a unified government. Prior
	-- to the mid-1980's, in fact, prefecture-level cities *were* prefectures, and a few of them (especially in the
	-- western portion of China) have not yet been converted. Generally a given province is entirely tiled by
	-- prefecture-level cities, another indication that they should be treated as prefectures and not cities per se.
	-- Yet another indication is that prefecture-level cities can contain counties and county-level cities (which, much
	-- like prefecture-level cities, are effectively counties surrounding a chief city of the county, again which bears
	-- the same name as the county-level city).
	--
	-- For this reason, we treat prefecture-level cities as non-city political divisions, and separately enumerate the
	-- most populous so we can separately categorize districts and counties under them instead of lumping them at the
	-- province level.
	--
	-- Note also that China separately distinguishes "urban area" from "metro area". Sometimes the two figures are
	-- identical but sometimes the metro area is larger (and very occasionally smaller, which I assume is an error). I'm
	-- guessing that the "urban area" is the contiguous urban area over a certain density while the metro area includes
	-- all urban areas above a certain density; when the latter is greater, it's because of satellite cities in the
	-- metro area separated by suburban/exurban or rural land.

	-- At first I chose all prefecture/province-level cities with a total prefecture/province-level population of at
	-- least 6,000,000 per the 2020 census with data taken from https://www.citypopulation.de/en/china/admin/ (a total
	-- of 67, including the four direct-administered municipalities), and also chose all prefecture/province-level
	-- cities whose "urban population" was at least 2,000,000 per the 2020 census with data taken from Wikipedia
	-- [[w:List of cities in China by population#Cities and towns by population]] (a total of 61 cities; if we cut off
	-- at 1.5 million we'd have 84 cities, and if we cut off at 1 million we'd have 105 cities). Merging them produces
	-- 87 cities. Note that this leaves off a few well-known cities (Guilin, Qiqihar, Kashgar, Lhasa, ...) but includes
	-- a lot of obscure cities.
	--
	-- At a later date I added all cities from citypopulation.de whose "urban" population per the 2020 China census was
	-- >= 1 million, and then finally added all urban agglomerations from citypopulation.de whose 2025-01-01 estimate
	-- was >= 1 million. These are sorted below by the urban agglomeration value (which is generally of the "adm-urb" =
	-- "administrative area (urban population)" type) and sometimes groups nearby cities into a single agglomeration
	-- (most notably in the case of the Pearl River Delta, grouped under Guangzhou with an agglomeration population of
	-- 72,700,000 but including a large number of nearby large cities in the agglomeration (although for some reason not
	-- Hong Kong, maybe due to the administrative issues involved). In addition, citypopulation.de includes divisions
	-- under a prefecture-level city if they are city-like and have an agglomeration population of at least 1 million;
	-- this includes several county-level cities, one county and one district (Wanzhou, a "district" of Chongqing
	-- despite being 142 miles away). None of the county-level cities or counties have districts under them, only
	-- subdistricts, towns and townships.

	["Guangzhou"] = {container = "Guangdong"}, -- 18.7 prefectural, 18.8 urban; sub-provincial city; 16.097 urban (72.700 adm-urb including Dongguan, Foshan, Huizhou, Jiangmen, Shenzhen, Zhongshan) per citypopulation.de
	["Dongguan"] = {container = "Guangdong"}, -- 10.5 prefectural, 10.5 urban; 9.645 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Foshan"] = {container = "Guangdong"}, -- 9.5 prefectural, 9.5 urban; 9.043 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Huizhou"] = {container = "Guangdong"}, -- 6.0 prefectural, 2.5 urban; 2.900 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Jiangmen"] = {container = "Guangdong"}, -- 4.798 prefectural, 2.7 urban; 1.795 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Shenzhen"] = {container = "Guangdong"}, -- 17.5 prefectural, 14.7 urban; sub-provincial city; 17.445 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Zhongshan"] = {container = "Guangdong"}, -- 4.418 prefectural, 4.4 urban; 3.842 per citypopulation.de; included by citypopulation.de in Guangzhou agglomeration
	["Shanghai"] = {placetype = {"direct-administered municipality", "municipality", "city"}}, -- 24.9 prefectural, 29.9 urban; 21.910 urban (41.600 adm-urb including Changshu, Changzhou, Suzhou, Wuxi) per citypopulation.de
	["Changshu"] = {container = "Jiangsu"}, -- 1.231 urban per citypopulation.de; included by citypopulation.de in Shanghai agglomeration
	-- NOTE: Not to be confused with Cangzhou in Hebei
	["Changzhou"] = {container = "Jiangsu"}, -- 5.278 prefectural, 3.6 urban; 3.187 urban per citypopulation.de; included by citypopulation.de in Shanghai agglomeration
	-- NOTE: There is also a prefecture-level city Suzhou in Anhui with 5.3 million prefectural inhabitants
	["Suzhou"] = {container = "Jiangsu"}, -- 12.8 prefectural, 4.3 urban; 5.893 urban per citypopulation.de; included by citypopulation.de in Shanghai agglomeration
	["Wuxi"] = {container = "Jiangsu"}, -- 7.5 prefectural, 3.3 urban; 3.957 per citypopulation.de; included by citypopulation.de in Shanghai agglomeration
	["Beijing"] = {placetype = {"direct-administered municipality", "municipality", "city"}}, -- 21.9 prefectural, 21.9 urban; 18.961 urban (21.500 adm-urb) per citypopulation.de
	["Chengdu"] = {container = "Sichuan"}, -- 20.9 prefectural, 16.9 urban; sub-provincial city; 13.568 urban (18.100 adm-urb) per citypopulation.de
	["Xiamen"] = {container = "Fujian"}, -- 5.163 prefectural, 5.2 urban; sub-provincial city; 4.617 urban (15.400 adm-urb including Jinjiang, Quanzhou, Putian) per citypopulation.de
	["Jinjiang"] = {container = "Fujian"}, -- 1.416 urban per citypopulation.de; included by citypopulation.de in Xiamen agglomeration
	["Quanzhou"] = {container = "Fujian"}, -- 8.8 prefectural, 1.7 urban (6.7 metro); 1.469 urban per citypopulation.de; included by citypopulation.de in Xiamen agglomeration
	["Putian"] = {container = "Fujian"}, -- 3.210 prefectural, 2.0 urban; 1.539 urban per citypopulation.de; included by citypopulation.de in Xiamen agglomeration
	["Hangzhou"] = {container = "Zhejiang"}, -- 11.9 prefectural, 10.7 urban; sub-provincial city; 9.236 urban (14.600 adm-urb including Shaoxing) per citypopulation.de
	["Shaoxing"] = {container = "Zhejiang"}, -- 5.270 prefectural, 2.5 urban; 2.333 urban per citypopulation.de; included by citypopulation.de in Hangzhou agglomeration
	["Xi'an"] = {container = "Shaanxi"}, -- 12.1 prefectural, 11.9 urban; sub-provincial city; 9.393 urban (13.400 adm-urb including Xianyang) per citypopulation.de
	["Xianyang"] = {container = "Shaanxi"}, -- 1.193 urban per citypopulation.de; included by citypopulation.de in Xi'an agglomeration
	["Chongqing"] = {placetype = {"direct-administered municipality", "municipality", "city"}}, -- 32.1 prefectural, 16.9 urban; 9.581 urban (12.900 adm-urb) per citypopulation.de
	["Wuhan"] = {container = "Hubei"}, -- 12.4 prefectural, 12.3 urban; sub-provincial city; 10.495 urban (12.600 adm-urb) per citypopulation.de
	["Tianjin"] = {placetype = {"direct-administered municipality", "municipality", "city"}}, -- 13.9 prefectural, 13.9 urban; 11.052 urban (11.700 adm-urb) per citypopulation.de
	["Changsha"] = {container = "Hunan"}, -- 10.0 prefectural, 6.0 urban; 5.630 urban (11.500 adm-urb including Xiangtan, Zhuzhou) per citypopulation.de
	-- Changsha County -- 1.024 urban per citypopulation.de
	["Zhuzhou"] = {container = "Hunan"}, -- 1.510 urban per citypopulation.de; included by citypopulation.de in Changsha agglomeration
	["Zhengzhou"] = {container = "Henan"}, -- 12.6 prefectural, 6.7 urban; 6.461 urban (10.300 adm-urb) per citypopulation.de
	["Nanjing"] = {container = "Jiangsu"}, -- 9.3 prefectural, 9.3 urban; sub-provincial city; 7.520 urban (9.500 adm-urb including Ma'anshan) per citypopulation.de
	["Shenyang"] = {container = "Liaoning"}, -- 9.1 prefectural, 7.9 urban; sub-provincial city; 7.026 urban (8.800 adm-urb including Fushun) per citypopulation.de
	["Fushun"] = {container = "Liaoning"}, -- 1.229 urban per citypopulation.de; included by citypopulation.de in Shenyang agglomeration
	["Hefei"] = {container = "Anhui"}, -- 9.4 prefectural, 4.2 urban; 5.056 urban (8.200 adm-urb) per citypopulation.de
	["Shantou"] = {container = "Guangdong"}, -- 5.502 prefectural, 4.3 urban; 3.839 urban (8.050 adm-urb including Chaozhou, Jieyang, Puning) per citypopulation.de
	["Chaozhou"] = {container = "Guangdong"}, -- 1.254 urban per citypopulation.de; included by citypopulation.de in Shantou agglomeration
	["Jieyang"] = {container = "Guangdong"}, -- 1.243 urban per citypopulation.de; included by citypopulation.de in Shantou agglomeration
	["Qingdao"] = {container = "Shandong"}, -- 10.1 prefectural, 7.1 urban; sub-provincial city; 6.165 urban (7.700 adm-urb) per citypopulation.de
	["Ningbo"] = {container = "Zhejiang"}, -- 9.4 prefectural, 5.1 urban; sub-provincial city; 3.731 urban (7.600 adm-urb including Cixi, Yuyao) per citypopulation.de
	["Cixi"] = {container = "Zhejiang"}, -- 1.458 urban per citypopulation.de; included by citypopulation.de in Ningbo agglomeration
	["Yuyao"] = {container = "Zhejiang"}, -- 1.014 urban per citypopulation.de; included by citypopulation.de in Ningbo agglomeration
	-- Hong Kong 7.500 agglomeration per citypopulation.de 2025-01-01 estimate including Kowloon, Victoria
	["Wenzhou"] = {container = "Zhejiang"}, -- 9.6 prefectural, 3.6 urban; 2.582 urban (7.000 adm-urb including Rui'an, Cangnan, Pingyang) per citypopulation.de
	-- Rui'an is a "county-level city" of the "prefecture-level city" of Wenzhou but in fact is 19 miles away from Wenzhou city proper (urban core to urban core).
	["Rui'an"] = {placetype = "county-level city", container = {key = "Wenzhou", placetype = "prefecture-level city"}, divs = {"subdistricts", "townships"}}, -- 1.013 urban per citypopulation.de; included by citypopulation.de in Wenzhou agglomeration
	["Kunming"] = {container = "Yunnan"}, -- 8.5 prefectural, 6.0 urban; 5.273 urban (6.800 adm-urb) per citypopulation.de
	-- includes Láiwú city
	["Jinan"] = {container = "Shandong", wp = "%l, %c"}, -- 9.2 prefectural, 8.4 urban; sub-provincial city; 5.648 urban (6.750 adm-urb) per citypopulation.de
	-- includes Xīnjí city
	["Shijiazhuang"] = {container = "Hebei"}, -- 11.2 prefectural, 4.1 urban; 5.090 urban (6.450 adm-urb) per citypopulation.de
	["Taiyuan"] = {container = "Shanxi"}, -- 5.304 prefectural, 4.5 urban; 4.304 urban (6.150 adm-urb) per citypopulation.de
	["Harbin"] = {container = "Heilongjiang"}, -- 10.0 prefectural, 7.0 urban; sub-provincial city; 5.243 urban (5.550 adm-urb) per citypopulation.de
	["Nanning"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}}, -- 8.7 prefectural, 3.8 urban; 4.583 urban (5.550 adm-urb) per citypopulation.de
	["Dalian"] = {container = "Liaoning"}, -- 7.5 prefectural, 5.7 urban; sub-provincial city; 4.914 urban (5.400 adm-urb) per citypopulation.de
	["Guiyang"] = {container = "Guizhou"}, -- 5.987 prefectural, 3.5 urban; 4.021 urban (5.300 adm-urb) per citypopulation.de
	["Changchun"] = {container = "Jilin"}, -- 9.1 prefectural, 5.7 urban; sub-provincial city; 4.557 urban (5.200 adm-urb) per citypopulation.de
	["Nanchang"] = {container = "Jiangxi"}, -- 6.3 prefectural, 3.6 (3.9?) urban, 5.3 metro; 3.519 urban (5.150 adm-urb) per citypopulation.de
	["Ürümqi"] = {container = {key = "Xinjiang, China", placetype = "autonomous region"}}, -- 4.054 prefectural, 4.3 urban; 3.843 urban (5.000 adm-urb) per citypopulation.de
	["Urumqi"] = {alias_of = "Ürümqi", display = true},
	["Fuzhou"] = {container = "Fujian"}, -- 8.3 prefectural, 4.1 urban; 3.723 urban (4.775 adm-urb) per citypopulation.de
	["Linyi"] = {container = "Shandong"}, -- 11.0 prefectural, 2.3 urban; 2.744 urban (4.650 adm-urb) per citypopulation.de
	["Zibo"] = {container = "Shandong"}, -- 4.704 prefectural, 2.6 urban; 2.750 urban (3.975 adm-urb) per citypopulation.de
	["Luoyang"] = {container = "Henan"}, -- 7.1 prefectural, 2.4 urban; 2.231 urban (3.750 adm-urb) per citypopulation.de
	["Lanzhou"] = {container = "Gansu"}, -- 4.359 prefectural, 3.1 urban; 3.013 urban (3.575 adm-urb) per citypopulation.de
	["Nantong"] = {container = "Jiangsu"}, -- 7.7 prefectural, 2.3 urban; 2.988 urban (3.475 adm-urb) citypopulation.de
	["Weifang"] = {container = "Shandong"}, -- 9.4 prefectural, 2.7 urban; 1.998 urban (3.325 adm-urb) per citypopulation.de
	["Jiangyin"] = {container = "Jiangsu"}, -- 1.331 urban (3.200 adm-urb including Zhangjiagang) per citypopulation.de
	["Zhangjiagang"] = {container = "Jiangsu"}, -- 1.056 urban per citypopulation.de; included in Jiangyin figures
	["Xuzhou"] = {container = "Jiangsu"}, -- 9.1 prefectural, 2.6 urban; 2.846 urban (3.150 adm-urb) per citypopulation.de
	["Handan"] = {container = "Hebei"}, -- 9.4 prefectural, 2.8 urban; 2.095 urban (2.925 adm-urb) per citypopulation.de
	["Hohhot"] = {container = {key = "Inner Mongolia, China", placetype = "autonomous region"}}, -- 3.446 prefectural, 2.7 urban; 2.373 urban (2.850 adm-urb) per citypopulation.de
	["Haikou"] = {container = "Hainan"}, -- 2.873 prefectural, 2.3 urban; 2.349 urban (2.800 adm-urb) per citypopulation.de
	["Tangshan"] = {container = "Hebei"}, -- 7.7 prefectural, 3.4 urban; 2.550 urban (2.750 adm-urb) per citypopulation.de
	["Xinxiang"] = {container = "Henan"}, -- 6.3 prefectural, 1.2 urban, 2.7 metro; 1.271 urban (2.700 adm-urb) per citypopulation.de
	["Yiwu"] = {container = "Zhejiang"}, -- 1.481 urban (2.700 adm-urb) per citypopulation.de
	["Zhuhai"] = {container = "Guangdong"}, -- 2.439 prefectural, 2.4 urban; 2.207 urban (2.675 adm-urb) per citypopulation.de
	["Taizhou, Zhejiang"] = {container = "Zhejiang"}, -- 6.6 prefectural, 1.6 urban; 1.486 urban (2.625 adm-urb) per citypopulation.de
	["Taizhou"] = {alias_of = "Taizhou, Zhejiang"},
	["Yantai"] = {container = "Shandong"}, -- 7.1 prefectural, 2.5 urban; 2.312 urban (2.550 adm-urb) per citypopulation.de
	["Yinchuan"] = {container = {key = "Ningxia, China", placetype = "autonomous region"}}, -- 1.663 urban (2.525 adm-urb) per citypopulation.de
	["Liuzhou"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}}, -- 4.157 prefectural, 2.2 urban; 2.205 urban (2.500 adm-urb) per citypopulation.de
	["Anshan"] = {container = "Liaoning"}, -- 1.480 urban (2.350 adm-urb including Liáoyáng) per citypopulation.de
	["Yangzhou"] = {container = "Jiangsu"}, -- 2.067 urban (2.300 adm-urb) per citypopulation.de
	["Jiaxing"] = {container = "Zhejiang"}, -- 1.188 urban (2.275 adm-urb) per citypopulation.de
	["Xining"] = {container = "Qinghai"}, -- 1.677 urban (2.250 adm-urb) per citypopulation.de
	-- includes Dìngzhōu city and Xióngān Xīnqū
	["Baoding"] = {container = "Hebei"}, -- 11.5 prefectural, 2.0 urban; 1.940 urban (2.225 adm-urb) per citypopulation.de
	["Baotou"] = {container = {key = "Inner Mongolia, China", placetype = "autonomous region"}}, -- 2.709 prefectural, 2.2 urban; 2.104 urban (2.200 adm-urb) per citypopulation.de
	["Ganzhou"] = {container = "Jiangxi"}, -- 9.0 prefectural, 1.6 urban; 1.778 urban (2.150 adm-urb) per citypopulation.de
	["Pingdingshan"] = {container = "Henan"}, -- 1.046 urban (2.100 adm-urb) per citypopulation.de
	["Zunyi"] = {container = "Guizhou"}, -- 6.6 prefectural, 2.4 urban/metro; 1.675 urban (2.025 adm-urb) per citypopulation.de
	["Bengbu"] = {container = "Anhui"}, -- 1.078 urban (2.000 adm-urb) per citypopulation.de
	["Datong"] = {container = "Shanxi"}, -- 3.105 prefectural, 2.0 urban; 1.810 urban (2.000 adm-urb) per citypopulation.de
	["Anyang"] = {container = "Henan"}, -- 1.188 urban (1.960 adm-urb) per citypopulation.de
	["Huai'an"] = {container = "Jiangsu"}, -- 4.556 prefectural, 2.6 urban; 1.805 urban (1.940 adm-urb) per citypopulation.de
	["Zaozhuang"] = {container = "Shandong"}, -- 1.350 urban (1.900 adm-urb) per citypopulation.de
	["Zhanjiang"] = {container = "Guangdong"}, -- 7.0 prefectural, 1.9 urban; 1.401 urban (1.890 adm-urb) per citypopulation.de
	["Huainan"] = {container = "Anhui"}, -- 1.256 urban (1.880 adm-urb) per citypopulation.de
	["Jining"] = {container = "Shandong"}, -- 8.4 prefectural, 1.5 urban; 1.700 urban (1.880 adm-urb) per citypopulation.de
	["Daqing"] = {container = "Heilongjiang"}, -- 1.604 urban (1.860 adm-urb) per citypopulation.de
	["Wuhu"] = {container = "Anhui"}, -- 1.598 urban (1.850 adm-urb) per citypopulation.de
	["Guilin"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}}, -- 1.361 urban (1.830 adm-urb) per citypopulation.de
	["Mianyang"] = {container = "Sichuan"}, -- 1.549 urban (1.800 adm-urb) per citypopulation.de
	["Xiangyang"] = {container = "Hubei"}, -- 1.686 urban (1.800 adm-urb) per citypopulation.de
	["Huzhou"] = {container = "Zhejiang"}, -- 1.084 urban (1.750 adm-urb) per citypopulation.de
	["Puyang"] = {container = "Henan"}, -- 0.824 urban (1.750 adm-urb) per citypopulation.de
	["Shangqiu"] = {container = "Henan"}, -- 7.8 prefectural, 1.9 urban (2.8 metro); 1.031 urban (1.750 adm-urb) per citypopulation.de
	["Qinhuangdao"] = {container = "Hebei"}, -- 1.520 urban (1.740 adm-urb) per citypopulation.de
	["Xingtai"] = {container = "Hebei"}, -- 7.1 prefectural, 971,000 urban; 1.5 urban (1.700 adm-urb) per citypopulation.de
	["Nanyang"] = {container = "Henan", wp = "%l, %c"}, -- 9.7 prefectural, 2.1 urban/metro; 1.481 urban (1.680 adm-urb) per citypopulation.de
	["Jiaozuo"] = {container = "Henan"}, -- 0.875 urban (1.640 adm-urb) per citypopulation.de
	["Jilin City"] = {container = "Jilin"}, -- 1.509 urban (1.610 adm-urb) per citypopulation.de
	["Jilin"] = {alias_of = "Jilin City"},
	["Jinhua"] = {container = "Zhejiang"}, -- 7.1 prefectural, 1.5 urban; 1.041 urban (1.590 adm-urb) per citypopulation.de
	["Shangrao"] = {container = "Jiangxi"}, -- 6.5 prefectural, 2.1 urban, 1.3 metro [sic]; 1.342 urban (1.580 adm-urb) per citypopulation.de
	["Heze"] = {container = "Shandong"}, -- 8.8 prefectural, 1.3 urban; 1.294 urban (1.570 adm-urb) per citypopulation.de
	["Yulin"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}, wp = "%l, %c"}, -- 0.878 urban (1.570 adm-urb) per citypopulation.de
	["Tai'an"] = {container = "Shandong"}, -- 1.417 urban (1.560 adm-urb) per citypopulation.de
	["Weihai"] = {container = "Shandong"}, -- 1.340 urban (1.510 adm-urb) per citypopulation.de
	-- Taizhou, Jiangsu would be here (1.490 adm-urb) but moved to china_prefecture_level_cities_2 to avoid clash
	["Yancheng"] = {container = "Jiangsu"}, -- 6.7 prefectural, 1.6 urban; 1.353 urban (1.460 adm-urb) per citypopulation.de
	["Zhangjiakou"] = {container = "Hebei"}, -- 1.339 urban (1.450 adm-urb) per citypopulation.de
	["Maoming"] = {container = "Guangdong"}, -- 6.2 prefectural, 2.5 urban; 1.308 urban (1.440 adm-urb) per citypopulation.de
	["Nanchong"] = {container = "Sichuan"}, -- 1.254 urban (1.440 adm-urb) per citypopulation.de
	["Fuyang"] = {container = "Anhui", wp = "%l, %c"}, -- 8.2 prefectural, 2.1 urban; 1.191 urban (1.410 adm-urb) per citypopulation.de
	["Xuchang"] = {container = "Henan"}, -- 0.850 urban (1.390 adm-urb) per citypopulation.de
	["Yichang"] = {container = "Hubei"}, -- 1.284 urban (1.390 adm-urb) per citypopulation.de
	["Dazhou"] = {container = "Sichuan"}, -- 1.136 urban (1.380 adm-urb) per citypopulation.de
	["Kaifeng"] = {container = "Henan"}, -- 1.194 urban (1.340 adm-urb) per citypopulation.de
	["Luzhou"] = {container = "Sichuan"}, -- 1.128 urban (1.340 adm-urb) per citypopulation.de
	["Qingyuan"] = {container = "Guangdong"}, -- 1.198 urban (1.340 adm-urb) per citypopulation.de
	["Huaibei"] = {container = "Anhui"}, -- 0.831 urban (1.330 adm-urb) per citypopulation.de
	["Yibin"] = {container = "Sichuan"}, -- 1.101 urban (1.310 adm-urb) per citypopulation.de
	["Lu'an"] = {container = "Anhui"}, -- 1.070 urban (1.300 adm-urb) per citypopulation.de
	["Dezhou"] = {container = "Shandong"}, -- 0.843 urban (1.290 adm-urb) per citypopulation.de
	["Rizhao"] = {container = "Shandong"}, -- 1.147 urban (1.270 adm-urb) per citypopulation.de
	["Changzhi"] = {container = "Shanxi"}, -- 1.047 urban (1.250 adm-urb) per citypopulation.de
	["Hengyang"] = {container = "Hunan"}, -- 6.6 prefectural, 1.5 urban; 1.185 urban (1.250 adm-urb) per citypopulation.de
	["Jinzhou"] = {container = "Liaoning"}, -- 1.021 urban (1.240 adm-urb) per citypopulation.de
	["Liaocheng"] = {container = "Shandong"}, -- 1.020 urban (1.240 adm-urb) per citypopulation.de
	["Changde"] = {container = "Hunan"}, -- 1.101 urban (1.230 adm-urb) per citypopulation.de
	["Suqian"] = {container = "Jiangsu"}, -- 1.082 urban (1.230 adm-urb) per citypopulation.de
	["Xinyang"] = {container = "Henan"}, -- 6.2 prefectural, 1.4 urban/metro; 1.015 urban (1.230 adm-urb) per citypopulation.de
	["Baoji"] = {container = "Shaanxi"}, -- 1.108 urban (1.220 adm-urb) per citypopulation.de
	["Yueyang"] = {container = "Hunan"}, -- 1.125 urban (1.220 adm-urb) per citypopulation.de
	["Zhenjiang"] = {container = "Jiangsu"}, -- 1.124 urban (1.210 adm-urb) per citypopulation.de
	-- Wanzhou is a "district" of the "direct-administered municipality" of Chongqing but in fact is 142 miles away from Chongqing city proper.
	["Wanzhou"] = {placetype = "district", container = {key = "Chongqing", placetype = "direct-administered municipality"}, divs = {"subdistricts", "townships"}, wp = "%l, %c"}, -- 1.078 urban (1.190 adm-urb) per citypopulation.de
	["Ulanhad"] = {container = {key = "Inner Mongolia, China", placetype = "autonomous region"}}, -- 1.093 urban (1.180 adm-urb) per citypopulation.de
	["Chifeng"] = {alias_of = "Ulanhad"},
	["Ulankhad"] = {alias_of = "Ulanhad", display = true},
	["Ezhou"] = {container = "Hubei"}, -- < 0.750 urban (1.180 adm-urb) per citypopulation.de
	["Zhaoqing"] = {container = "Guangdong"}, -- 1.036 urban (1.160 adm-urb) per citypopulation.de
	["Lianyungang"] = {container = "Jiangsu"}, -- 4.599 prefectural, 2.0 urban; 1.071 urban (1.150 adm-urb) per citypopulation.de
	["Qujing"] = {container = "Yunnan"}, -- 0.976 urban (1.150 adm-urb) per citypopulation.de
	-- Shuyang is a "county" of the "prefecture-level city" of Suqian but in fact is 38 miles away from Suqian city proper (urban core to urban core).
	-- The county itself is 37 miles by 34 miles.
	["Shuyang"] = {placetype = "county", container = {key = "Suqian", placetype = "prefecture-level city"}, divs = {"subdistricts", "townships"}, wp = "%l County"}, -- 0.986 urban (1.120 adm-urb) per citypopulation.de
	-- Yongkang is a "county-level city" of the "prefecture-level city" of Jinhua but in fact is 32 miles away from Jinhua city proper (urban core to urban core).
	["Yongkang"] = {placetype = "county-level city", container = {key = "Jinhua", placetype = "prefecture-level city"}, divs = {"subdistricts", "townships"}, wp = "%l, Zhejiang"}, -- < 0.750 urban (1.110 adm-urb) per citypopulation.de
	["Zhoukou"] = {container = "Henan"}, -- 9.0 prefectural, 721,000 urban (1.6 metro); < 0.750 urban (1.100 adm-urb) per citypopulation.de
	["Beihai"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}}, -- < 1 urban (1.090 adm-urb) per citypopulation.de
	["Jiujiang"] = {container = "Jiangxi"}, -- < 0.750 urban (1.080 adm-urb) per citypopulation.de
	["Shaoyang"] = {container = "Hunan"}, -- 6.6 prefectural, 802,000 urban, 1.4 metro; < 1 urban (1.080 adm-urb) per citypopulation.de
	["Chuzhou"] = {container = "Anhui"}, -- < 0.750 urban (1.070 adm-urb) per citypopulation.de
	["Hengshui"] = {container = "Hebei"}, -- 0.885 urban (1.070 adm-urb) per citypopulation.de
	["Shiyan"] = {container = "Hubei"}, -- 0.955 urban (1.070 adm-urb) per citypopulation.de
	["Huludao"] = {container = "Liaoning"}, -- 0.764 urban (1.060 adm-urb) per citypopulation.de
	["Dongying"] = {container = "Shandong"}, -- 0.961 urban (1.050 adm-urb) per citypopulation.de
	["Guigang"] = {container = {key = "Guangxi, China", placetype = "autonomous region"}}, -- 0.921 urban (1.050 adm-urb) per citypopulation.de
	-- Liuyang is a "county-level city" of the "prefecture-level city" of Changsha but in fact is 47 miles away from Changsha city proper (urban core to urban core).
	["Liuyang"] = {placetype = "county-level city", container = {key = "Changsha", placetype = "prefecture-level city"}, divs = {"subdistricts", "townships"}}, -- 0.886 urban (1.040 adm-urb) per citypopulation.de
	-- NOTE: Not to be confused with Changzhou in Jiangsu
	["Cangzhou"] = {container = "Hebei"}, -- 7.3 prefectural, 621,000 urban; 0.759 urban (1.030 adm-urb) per citypopulation.de
	["Liupanshui"] = {container = "Guizhou"}, -- < 0.750 urban (1.030 adm-urb) per citypopulation.de
	["Panjin"] = {container = "Liaoning"}, -- 0.980 urban (1.030 adm-urb) per citypopulation.de
	["Qiqihar"] = {container = "Heilongjiang"}, -- 1.030 urban (1.030 adm-urb) per citypopulation.de
	["Linfen"] = {container = "Shanxi"}, -- < 0.750 urban (1.010 adm-urb) per citypopulation.de
	-- Tengzhou is a "county-level city" of the "prefecture-level city" of Zaozhuang but in fact is 30 miles away from Zaozhuang city proper (urban core to urban core).
	["Tengzhou"] = {placetype = "county-level city", container = {key = "Zaozhuang", placetype = "prefecture-level city"}, divs = {"subdistricts", "townships"}}, -- 0.937 urban (1.010 adm-urb) per citypopulation.de

	-- 3 extra that got added in earlier incarnations and aren't found in the "major agglomerations of the world" page https://citypopulation.de/en/world/agglomerations/ reference date 2025-01-01
	["Kunshan"] = {container = "Jiangsu"}, -- 1.652 urban (2020 China census) per citypopulation.de
	["Zhumadian"] = {container = "Henan"}, -- 7.0 prefectural, 722,000 urban per Wikipedia; 0.754 urban per citypopulation.de
	["Bijie"] = {container = "Guizhou"}, -- 6.9 prefectural, ? urban, ? metro (not listed in Wikipedia); < 0.750 urban per citypopulation.de
}

export.china_prefecture_level_cities_group = {
	-- don't do any transformations between key and placename; in particular, don't chop off anything from
	-- "Taizhou, Zhejiang" or "Suzhou, Anhui".
	key_to_placename = false,
	placename_to_key = false, -- don't add ", China" to make the key
	default_container = "China",
	canonicalize_key_container = make_canonicalize_key_container(", China", "province"),
	-- Prefecture-level cities aren't really cities but allow them to be identified that way, as many people
	-- don't understand how Chinese administrative divisions work.
	default_placetype = {"prefecture-level city", "city"},
	default_divs = {
		-- "towns" (but not "townships") are automatically added as they are specified as generic_before_non_cities,
		-- and prefecture-level cities (as well as county-level cities) are considered non-cities.
		"districts", "subdistricts", "townships",
		{type = "counties", cat_as = "counties and county-level cities"},
		{type = "county-level cities", cat_as = "counties and county-level cities"},
	},
	data = export.china_prefecture_level_cities,
}

-- Needed to avoid problems with two cities called Taizhou and Suzhou.
export.china_prefecture_level_cities_2 = {
	-- NOTE: There is also a larger and better-known prefecture-level city Taizhou in Zhejiang.
	["Taizhou, Jiangsu"] = {container = "Jiangsu"}, -- 1.3 urban (1.490 adm-urb) per citypopulation.de 2020 census
	["Taizhou"] = {alias_of = "Taizhou, Jiangsu"},
	-- NOTE: There is also a larger and better-known prefecture-level city Suzhou in Jiangsu.
	["Suzhou, Anhui"] = {container = "Anhui"}, -- 5.3 prefectural, 1.766 metro and "urban"; < 1 urban (1.010 adm-urb) per citypopulation.de 2020 census
	-- hopefully this will work because we also have Suzhou as a key by itself for the larger, more-well-known Suzhou in Jiangsu
	["Suzhou"] = {alias_of = "Suzhou, Anhui"},
}

export.china_prefecture_level_cities_group_2 = {
	-- don't do any transformations between key and placename; in particular, don't chop off anything from
	-- "Taizhou, Jiangsu".
	placename_to_key = false, -- don't add ", China" to make the key
	default_container = "China",
	canonicalize_key_container = make_canonicalize_key_container(", China", "province"),
	-- Prefecture-level cities aren't really cities but allow them to be identified that way, as many people
	-- don't understand how Chinese administrative divisions work.
	default_placetype = {"prefecture-level city", "city"},
	default_divs = {
		-- "towns" (but not "townships") are automatically added as they are specified as generic_before_non_cities,
		-- and prefecture-level cities (as well as county-level cities) are considered non-cities.
		"districts", "subdistricts", "townships",
		{type = "counties", cat_as = "counties and county-level cities"},
		{type = "county-level cities", cat_as = "counties and county-level cities"},
	},
	data = export.china_prefecture_level_cities_2,
}

export.finland_regions = {
	["Lapland, Finland"] = {wp = "%l (%c)"},
	["North Ostrobothnia, Finland"] = {},
	["Northern Ostrobothnia, Finland"] = {alias_of = "North Ostrobothnia, Finland", display = true},
	["Kainuu, Finland"] = {},
	["North Karelia, Finland"] = {},
	["Northern Savonia, Finland"] = {},
	["North Savo, Finland"] = {alias_of = "Northern Savonia, Finland", display = true},
	["Southern Savonia, Finland"] = {},
	["South Savo, Finland"] = {alias_of = "Southern Savonia, Finland", display = true},
	["South Karelia, Finland"] = {},
	["Central Finland, Finland"] = {},
	["South Ostrobothnia, Finland"] = {},
	["Southern Ostrobothnia, Finland"] = {alias_of = "South Ostrobothnia, Finland", display = true},
	["Ostrobothnia, Finland"] = {wp = "%l (region)"},
	["Central Ostrobothnia, Finland"] = {},
	["Pirkanmaa, Finland"] = {},
	["Satakunta, Finland"] = {},
	["Päijänne Tavastia, Finland"] = {},
	["Päijät-Häme, Finland"] = {alias_of = "Päijänne Tavastia, Finland", display = true},
	["Tavastia Proper, Finland"] = {},
	["Kanta-Häme, Finland"] = {alias_of = "Tavastia Proper, Finland", display = true},
	["Kymenlaakso, Finland"] = {},
	["Uusimaa, Finland"] = {},
	["Southwest Finland, Finland"] = {},
	["Åland Islands, Finland"] = {the = true, wp = "Åland"},
	["Åland, Finland"] = {alias_of = "Åland Islands, Finland"}, -- differs in "the"
}

-- regions of Finland
export.finland_group = {
	default_container = "Finland",
	default_placetype = "region",
	default_divs = "municipalities",
	data = export.finland_regions,
}

export.france_administrative_regions = {
	["Auvergne-Rhône-Alpes, France"] = {},
	["Bourgogne-Franche-Comté, France"] = {},
	["Brittany, France"] = {wp = "%l (administrative region)"},
	["Centre-Val de Loire, France"] = {},
	["Corsica, France"] = {},
	-- overseas departments are handled in `export.country_like_entities`
	-- ["French Guiana"] = {},
	["Grand Est, France"] = {},
	-- ["Guadeloupe"] = {},
	["Hauts-de-France, France"] = {},
	["Île-de-France, France"] = {},
	-- ["Martinique"] = {},
	-- ["Mayotte"] = {},
	["Normandy, France"] = {wp = "%l (administrative region)"},
	["Nouvelle-Aquitaine, France"] = {},
	["Occitania, France"] = {wp = "%l (administrative region)"},
	["Occitanie, France"] = {alias_of = "Occitania, France", display = true},
	["Pays de la Loire, France"] = {},
	["Provence-Alpes-Côte d'Azur, France"] = {},
	-- ["Réunion"] = {},
}

-- administrative regions of France
export.france_group = {
	default_container = "France",
	-- Canonically these are 'administrative regions' but also treat as 'region' ('administrative region' falls back
	-- to 'region').
	default_placetype = "region",
	default_divs = {
		"communes",
		{type = "municipalities", cat_as = "communes"},
		"departments",
		{type = "prefectures", cat_as = {"prefectures", "departmental capitals"}},
		{type = "French prefectures", cat_as = {"prefectures", "departmental capitals"}},
	},
	data = export.france_administrative_regions,
}

export.france_departments = {
	["Ain, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 01
	["Aisne, France"] = {container = "Hauts-de-France"}, -- 02
	["Allier, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 03
	["Alpes-de-Haute-Provence, France"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 04
	["Hautes-Alpes, France"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 05
	["Alpes-Maritimes, France"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 06
	["Ardèche, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 07
	["Ardennes, France"] = {container = "Grand Est", wp = "%l (department)"}, -- 08
	["Ariège, France"] = {container = "Occitania", wp = "%l (department)"}, -- 09
	["Aube, France"] = {container = "Grand Est"}, -- 10
	["Aude, France"] = {container = "Occitania"}, -- 11
	["Aveyron, France"] = {container = "Occitania"}, -- 12
	["Bouches-du-Rhône, France"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 13
	["Calvados, France"] = {container = "Normandy", wp = "%l (department)"}, -- 14
	["Cantal, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 15
	["Charente, France"] = {container = "Nouvelle-Aquitaine"}, -- 16
	["Charente-Maritime, France"] = {container = "Nouvelle-Aquitaine"}, -- 17
	["Cher, France"] = {container = "Centre-Val de Loire", wp = "%l (department)"}, -- 18
	["Corrèze, France"] = {container = "Nouvelle-Aquitaine"}, -- 19
	["Corse-du-Sud, France"] = {container = "Corsica"}, -- 2A
	["Haute-Corse, France"] = {container = "Corsica"}, -- 2B
	["Côte-d'Or, France"] = {container = "Bourgogne-Franche-Comté"}, -- 21
	["Côte d'Or, France"] = {alias_of = "Côte-d'Or, France", display = true},
	["Côtes-d'Armor, France"] = {container = "Brittany"}, -- 22
	["Côtes d'Armor, France"] = {alias_of = "Côtes-d'Armor, France", display = true},
	["Creuse, France"] = {container = "Nouvelle-Aquitaine"}, -- 23
	["Dordogne, France"] = {container = "Nouvelle-Aquitaine"}, -- 24
	["Doubs, France"] = {container = "Bourgogne-Franche-Comté"}, -- 25
	["Drôme, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 26
	["Eure, France"] = {container = "Normandy"}, -- 27
	["Eure-et-Loir, France"] = {container = "Centre-Val de Loire"}, -- 28
	["Finistère, France"] = {container = "Brittany"}, -- 29
	["Gard, France"] = {container = "Occitania"}, -- 30
	["Haute-Garonne, France"] = {container = "Occitania"}, -- 31
	["Gers, France"] = {container = "Occitania"}, -- 32
	["Gironde, France"] = {container = "Nouvelle-Aquitaine"}, -- 33
	["Hérault, France"] = {container = "Occitania"}, -- 34
	["Ille-et-Vilaine, France"] = {container = "Brittany"}, -- 35
	["Indre, France"] = {container = "Centre-Val de Loire"}, -- 36
	["Indre-et-Loire, France"] = {container = "Centre-Val de Loire"}, -- 37
	["Isère, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 38
	["Jura, France"] = {container = "Bourgogne-Franche-Comté", wp = "%l (department)"}, -- 39
	["Landes, France"] = {container = "Nouvelle-Aquitaine", wp = "%l (department)"}, -- 40
	["Loir-et-Cher, France"] = {container = "Centre-Val de Loire"}, -- 41
	["Loire, France"] = {container = "Auvergne-Rhône-Alpes", wp = "%l (department)"}, -- 42
	["Haute-Loire, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 43
	["Loire-Atlantique, France"] = {container = "Pays de la Loire"}, -- 44
	["Loiret, France"] = {container = "Centre-Val de Loire"}, -- 45
	["Lot, France"] = {container = "Occitania", wp = "%l (department)"}, -- 46
	["Lot-et-Garonne, France"] = {container = "Nouvelle-Aquitaine"}, -- 47
	["Lozère, France"] = {container = "Occitania"}, -- 48
	["Maine-et-Loire, France"] = {container = "Pays de la Loire"}, -- 49
	["Manche, France"] = {container = "Normandy"}, -- 50
	["Marne, France"] = {container = "Grand Est", wp = "%l (department)"}, -- 51
	["Haute-Marne, France"] = {container = "Grand Est"}, -- 52
	["Mayenne, France"] = {container = "Pays de la Loire"}, -- 53
	["Meurthe-et-Moselle, France"] = {container = "Grand Est"}, -- 54
	["Meuse, France"] = {container = "Grand Est", wp = "%l (department)"}, -- 55
	["Morbihan, France"] = {container = "Brittany"}, -- 56
	["Moselle, France"] = {container = "Grand Est", wp = "%l (department)"}, -- 57
	["Nièvre, France"] = {container = "Bourgogne-Franche-Comté"}, -- 58
	["Nord, France"] = {container = "Hauts-de-France", wp = "%l (French department)"}, -- 59
	["Oise, France"] = {container = "Hauts-de-France"}, -- 60
	["Orne, France"] = {container = "Normandy"}, -- 61
	["Pas-de-Calais, France"] = {container = "Hauts-de-France"}, -- 62
	["Puy-de-Dôme, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 63
	["Pyrénées-Atlantiques, France"] = {container = "Nouvelle-Aquitaine"}, -- 64
	["Hautes-Pyrénées, France"] = {container = "Occitania"}, -- 65
	["Pyrénées-Orientales, France"] = {container = "Occitania"}, -- 66
	["Bas-Rhin, France"] = {container = "Grand Est"}, -- 67
	["Haut-Rhin, France"] = {container = "Grand Est"}, -- 68
	["Rhône, France"] = {container = "Auvergne-Rhône-Alpes", wp = "%l (department)"}, -- 69D
	["Metropolis of Lyon, France"] = {container = "Auvergne-Rhône-Alpes", the = true}, -- 69M
	["Lyon Metropolis, France"] = {alias_of = "Metropolis of Lyon, France"},
	["Lyon, France"] = {alias_of = "Metropolis of Lyon, France"},
	["Haute-Saône, France"] = {container = "Bourgogne-Franche-Comté"}, -- 70
	["Saône-et-Loire, France"] = {container = "Bourgogne-Franche-Comté"}, -- 71
	["Sarthe, France"] = {container = "Pays de la Loire"}, -- 72
	["Savoie, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 73
	["Haute-Savoie, France"] = {container = "Auvergne-Rhône-Alpes"}, -- 74
	["Paris, France"] = {container = "Île-de-France"}, -- 75
	["Seine-Maritime, France"] = {container = "Normandy"}, -- 76
	["Seine-et-Marne, France"] = {container = "Île-de-France"}, -- 77
	["Yvelines, France"] = {container = "Île-de-France"}, -- 78
	["Deux-Sèvres, France"] = {container = "Nouvelle-Aquitaine"}, -- 79
	["Somme, France"] = {container = "Hauts-de-France", wp = "%l (department)"}, -- 80
	["Tarn, France"] = {container = "Occitania", wp = "%l (department)"}, -- 81
	["Tarn-et-Garonne, France"] = {container = "Occitania"}, -- 82
	["Var, France"] = {container = "Provence-Alpes-Côte d'Azur", wp = "%l (department)"}, -- 83
	["Vaucluse, France"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 84
	["Vendée, France"] = {container = "Pays de la Loire"}, -- 85
	["Vienne, France"] = {container = "Nouvelle-Aquitaine", wp = "%l (department)"}, -- 86
	["Haute-Vienne, France"] = {container = "Nouvelle-Aquitaine"}, -- 87
	["Vosges, France"] = {container = "Grand Est", wp = "%l (department)"}, -- 88
	["Yonne, France"] = {container = "Bourgogne-Franche-Comté"}, -- 89
	["Territoire de Belfort, France"] = {container = "Bourgogne-Franche-Comté"}, -- 90
	["Essonne, France"] = {container = "Île-de-France"}, -- 91
	["Hauts-de-Seine, France"] = {container = "Île-de-France"}, -- 92
	["Seine-Saint-Denis, France"] = {container = "Île-de-France"}, -- 93
	["Val-de-Marne, France"] = {container = "Île-de-France"}, -- 94
	["Val-d'Oise, France"] = {container = "Île-de-France"}, -- 95
	--["Guadeloupe"] = {container = "Guadeloupe"}, -- 971
	--["Martinique"] = {container = "Martinique"}, -- 972
	--["Guyane"] = {container = "French Guiana", wp = "French Guiana"}, -- 973
	--["La Réunion"] = {container = "Réunion", wp = "Réunion"}, -- 974
	--["Mayotte"] = {container = "Mayotte"}, -- 976
}

export.france_departments_group = {
	placename_to_key = make_placename_to_key(", France"),
	canonicalize_key_container = make_canonicalize_key_container(", France", "region"),
	default_placetype = "department",
	default_divs = {
		"communes",
		{type = "municipalities", cat_as = "communes"},
	},
	data = export.france_departments,
}

export.germany_states = {
	["Baden-Württemberg, Germany"] = {},
	["Bavaria, Germany"] = {},
	-- Berlin, Bremen and Hamburg are effectively city-states and don't have districts ([[Kreise]]), so override
	-- the default_divs setting. Better not to include them at all since they're included as cities down below.
	-- ["Berlin"] = {divs = {}},
	["Brandenburg, Germany"] = {},
	-- ["Bremen"] = {divs = {}},
	-- ["Hamburg"] = {divs = {}},
	["Hesse, Germany"] = {},
	["Lower Saxony, Germany"] = {},
	["Mecklenburg-Vorpommern, Germany"] = {},
	["Mecklenburg-Western Pomerania, Germany"] = {alias_of = "Mecklenburg-Vorpommern, Germany", display = true},
	["North Rhine-Westphalia, Germany"] = {},
	["Rhineland-Palatinate, Germany"] = {},
	["Saarland, Germany"] = {},
	["Saxony, Germany"] = {},
	["Saxony-Anhalt, Germany"] = {},
	["Schleswig-Holstein, Germany"] = {},
	["Thuringia, Germany"] = {},
}

-- states of Germany
export.germany_group = {
	default_container = "Germany",
	default_placetype = "state",
	default_divs = {"districts", "municipalities"},
	data = export.germany_states,
}

export.greece_regions = {
	["Attica, Greece"] = {wp = "%l (region)"},
	["Central Greece, Greece"] = {wp = "%l (administrative region)"},
	["Central Macedonia, Greece"] = {},
	["Crete, Greece"] = {},
	["Eastern Macedonia and Thrace, Greece"] = {},
	["Epirus, Greece"] = {wp = "%l (region)"},
	["Ionian Islands, Greece"] = {the = true, wp = "%l (region)"},
	["North Aegean, Greece"] = {the = true},
	-- I would expect 'the Peloponnese' but Wikipedia mostly has categories like [[w:Category:Geography of Peloponnese (region)]]
	-- and [[w:Category:Buildings and structures in Peloponnese (region)]]; only [[w:Category:People from the Peloponnese (region)]]
	-- has "the" in it.
	["Peloponnese, Greece"] = {wp = "%l (region)"},
	["South Aegean, Greece"] = {the = true},
	["Thessaly, Greece"] = {},
	["Western Greece, Greece"] = {},
	["Western Macedonia, Greece"] = {},
	["Mount Athos, Greece"] = {placetype = {"autonomous region", "region"}, wp = "Monastic community of Mount Athos"},
}

-- regions of Greece
export.greece_group = {
	default_container = "Greece",
	default_placetype = "region",
	data = export.greece_regions,
}

local india_polity_with_divisions = {"divisions", "districts"}
local india_polity_without_divisions = {"districts"}

-- States and union territories of India. Only some of them are divided into divisions.
export.india_states_and_union_territories = {
	["Andaman and Nicobar Islands, India"] =
		{the = true, placetype = "union territory", divs = india_polity_without_divisions},
	["Andhra Pradesh, India"] = {divs = india_polity_without_divisions},
	["Arunachal Pradesh, India"] = {divs = india_polity_with_divisions},
	["Assam, India"] = {divs = india_polity_with_divisions},
	["Bihar, India"] = {divs = india_polity_with_divisions},
	["Chandigarh, India"] = {placetype = "union territory", divs = india_polity_without_divisions},
	["Chhattisgarh, India"] = {divs = india_polity_with_divisions},
	["Dadra and Nagar Haveli and Daman and Diu, India"] = {placetype = "union territory", divs = india_polity_without_divisions},
	["Delhi, India"] = {placetype = "union territory", divs = india_polity_with_divisions},
	["Goa, India"] = {divs = india_polity_without_divisions},
	["Gujarat, India"] = {divs = india_polity_without_divisions},
	["Haryana, India"] = {divs = india_polity_with_divisions},
	["Himachal Pradesh, India"] = {divs = india_polity_with_divisions},
	["Jammu and Kashmir, India"] = {placetype = "union territory", divs = india_polity_with_divisions,
		wp = "%l (union territory)"},
	["Jharkhand, India"] = {divs = india_polity_with_divisions},
	["Karnataka, India"] = {divs = india_polity_with_divisions},
	["Kerala, India"] = {divs = india_polity_without_divisions},
	["Ladakh, India"] = {placetype = "union territory", divs = india_polity_with_divisions},
	["Lakshadweep, India"] = {placetype = "union territory", divs = india_polity_without_divisions},
	["Madhya Pradesh, India"] = {divs = india_polity_with_divisions},
	["Maharashtra, India"] = {divs = india_polity_with_divisions},
	["Manipur, India"] = {divs = india_polity_without_divisions},
	["Meghalaya, India"] = {divs = india_polity_with_divisions},
	["Mizoram, India"] = {divs = india_polity_without_divisions},
	["Nagaland, India"] = {divs = india_polity_with_divisions},
	["Odisha, India"] = {divs = india_polity_with_divisions},
	["Puducherry, India"] = {placetype = "union territory", divs = india_polity_without_divisions,
		wp = "%l (union territory)"},
	["Pondicherry, India"] = {alias_of = "Puducherry, India", display = true},
	["Punjab, India"] = {divs = india_polity_with_divisions, wp = "%l, %c"},
	["Rajasthan, India"] = {divs = india_polity_with_divisions},
	["Sikkim, India"] = {divs = india_polity_without_divisions},
	["Tamil Nadu, India"] = {divs = india_polity_without_divisions},
	["Telangana, India"] = {divs = india_polity_without_divisions},
	["Tripura, India"] = {divs = india_polity_without_divisions},
	["Uttar Pradesh, India"] = {divs = india_polity_with_divisions},
	["Uttarakhand, India"] = {divs = india_polity_with_divisions},
	["West Bengal, India"] = {divs = india_polity_with_divisions},
}

-- states and union territories of India
export.india_group = {
	default_container = "India",
	default_placetype = "state",
	data = export.india_states_and_union_territories,
}

export.indonesia_provinces = {
	["Aceh, Indonesia"] = {},
	["Bali, Indonesia"] = {},
	["Bangka Belitung Islands, Indonesia"] = {the = true},
	["Banten, Indonesia"] = {},
	["Bengkulu, Indonesia"] = {},
	["Central Java, Indonesia"] = {},
	["Central Kalimantan, Indonesia"] = {},
	["Central Papua, Indonesia"] = {},
	["Central Sulawesi, Indonesia"] = {},
	["East Java, Indonesia"] = {},
	["East Kalimantan, Indonesia"] = {},
	["East Nusa Tenggara, Indonesia"] = {},
	["Gorontalo, Indonesia"] = {},
	["Highland Papua, Indonesia"] = {wp = "%l"},
	["Special Capital Region of Jakarta, Indonesia"] = {the = true, wp = "Jakarta"},
	["Jakarta, Indonesia"] = {alias_of = "Special Capital Region of Jakarta, Indonesia"},
	["Jambi, Indonesia"] = {},
	["Lampung, Indonesia"] = {},
	["Maluku, Indonesia"] = {},
	["North Kalimantan, Indonesia"] = {},
	["North Maluku, Indonesia"] = {},
	["North Sulawesi, Indonesia"] = {},
	["North Papua, Indonesia"] = {},
	["North Sumatra, Indonesia"] = {},
	["Papua, Indonesia"] = {wp = "%l (province)"},
	["Riau, Indonesia"] = {},
	["Riau Islands, Indonesia"] = {the = true},
	["Southeast Sulawesi, Indonesia"] = {},
	["South Kalimantan, Indonesia"] = {},
	["South Papua, Indonesia"] = {},
	["South Sulawesi, Indonesia"] = {},
	["South Sumatra, Indonesia"] = {},
	["Southwest Papua, Indonesia"] = {},
	["West Java, Indonesia"] = {},
	["West Kalimantan, Indonesia"] = {},
	["West Nusa Tenggara, Indonesia"] = {},
	["West Papua, Indonesia"] = {wp = "%l (province)"},
	["West Sulawesi, Indonesia"] = {},
	["West Sumatra, Indonesia"] = {},
	["Special Region of Yogyakarta, Indonesia"] = {the = true},
	["Yogyakarta, Indonesia"] = {alias_of = "Special Region of Yogyakarta, Indonesia"},
}

-- provinces of Indonesia
export.indonesia_group = {
	default_container = "Indonesia",
	default_placetype = "province",
	-- per https://www.quora.com/Does-Indonesia-use-British-or-American-English, Indonesia tends to use American
	-- spellings.
	data = export.indonesia_provinces,
}

export.iran_provinces = {
	["Alborz Province, Iran"] = {}, -- abbreviation AL, capital [[w:Karaj]]
	["Ardabil Province, Iran"] = {}, -- abbreviation AR, capital [[w:Ardabil]]
	["Bushehr Province, Iran"] = {}, -- abbreviation BU, capital [[w:Bushehr]]
	["Chaharmahal and Bakhtiari Province, Iran"] = {}, -- abbreviation CB, capital [[w:Shahr-e Kord]]
	["East Azerbaijan Province, Iran"] = {}, -- abbreviation EA, capital [[w:Tabriz]]
	["Fars Province, Iran"] = {}, -- abbreviation FA, capital [[w:Shiraz]]
	["Pars Province, Iran"] = {alias_of = "Fars Province, Iran", display = true},
	["Gilan Province, Iran"] = {}, -- abbreviation GN, capital [[w:Rasht]]
	["Golestan Province, Iran"] = {}, -- abbreviation GO, capital [[w:Gorgan]]
	["Hamadan Province, Iran"] = {}, -- abbreviation HA, capital [[w:Hamadan]]
	["Hormozgan Province, Iran"] = {}, -- abbreviation HO, capital [[w:Bandar Abbas]]
	["Ilam Province, Iran"] = {}, -- abbreviation IL, capital [[w:Ilam, Iran|Ilam]]
	["Isfahan Province, Iran"] = {}, -- abbreviation IS, capital [[w:Isfahan]]
	["Kerman Province, Iran"] = {}, -- abbreviation KN, capital [[w:Kerman]]
	["Kermanshah Province, Iran"] = {}, -- abbreviation KE, capital [[w:Kermanshah]]
	["Khuzestan Province, Iran"] = {}, -- abbreviation KH, capital [[w:Ahvaz]]
	["Kohgiluyeh and Boyer-Ahmad Province, Iran"] = {}, -- abbreviation KB, capital [[w:Yasuj]]
	["Kurdistan Province, Iran"] = {}, -- abbreviation KU, capital [[w:Sanandaj]]
	["Lorestan Province, Iran"] = {}, -- abbreviation LO, capital [[w:Khorramabad]]
	["Markazi Province, Iran"] = {}, -- abbreviation MA, capital [[w:Arak, Iran|Arak]]
	["Mazandaran Province, Iran"] = {}, -- abbreviation MN, capital [[w:Sari, Iran|Sari]]
	["North Khorasan Province, Iran"] = {}, -- abbreviation NK, capital [[w:Bojnord]]
	["Qazvin Province, Iran"] = {}, -- abbreviation QA, capital [[w:Qazvin]]
	["Qom Province, Iran"] = {}, -- abbreviation QM, capital [[w:Qom]]
	["Razavi Khorasan Province, Iran"] = {}, -- abbreviation RK, capital [[w:Mashhad]]
	["Semnan Province, Iran"] = {}, -- abbreviation SE, capital [[w:Semnan, Iran|Semnan]]
	["Sistan and Baluchestan Province, Iran"] = {}, -- abbreviation SB, capital [[w:Zahedan]]
	["South Khorasan Province, Iran"] = {}, -- abbreviation SK, capital [[w:Birjand]]
	["Tehran Province, Iran"] = {}, -- abbreviation TE, capital [[w:Tehran]]
	["West Azerbaijan Province, Iran"] = {}, -- abbreviation WA, capital [[w:Urmia]]
	["Yazd Province, Iran"] = {}, -- abbreviation YA, capital [[w:Yazd]]
	["Zanjan Province, Iran"] = {}, -- abbreviation ZA, capital [[w:Zanjan, Iran|Zanjan]]
}

-- provinces of Iran
export.iran_group = {
	key_to_placename = make_key_to_placename(", Iran", " Province$"),
	placename_to_key = make_placename_to_key(", Iran", " Province"),
	default_container = "Iran",
	default_placetype = "province",
	-- There aren't nearly enough counties of Iran currently entered in any language to allow for categorizing them
	-- per-province. (As of 2025-05-09, there are only 6 counties in each of [[Category:en:Counties of Iran]],
	-- [[Category:fa:Counties of Iran]] and [[Category:ar:Counties of Iran]].)
	-- default_divs = "counties",
	-- For obscure reasons, provinces of Iran, Laos, Thailand and Vietnam use lowercase 'province'
	default_wp = "%e province",
	data = export.iran_provinces,
}

export.ireland_counties = {
	["County Carlow, Ireland"] = {},
	["County Cavan, Ireland"] = {},
	["County Clare, Ireland"] = {},
	["County Cork, Ireland"] = {},
	["County Donegal, Ireland"] = {},
	["County Dublin, Ireland"] = {},
	["County Galway, Ireland"] = {},
	["County Kerry, Ireland"] = {},
	["County Kildare, Ireland"] = {},
	["County Kilkenny, Ireland"] = {},
	["County Laois, Ireland"] = {},
	["County Leitrim, Ireland"] = {},
	["County Limerick, Ireland"] = {},
	["County Longford, Ireland"] = {},
	["County Louth, Ireland"] = {},
	["County Mayo, Ireland"] = {},
	["County Meath, Ireland"] = {},
	["County Monaghan, Ireland"] = {},
	["County Offaly, Ireland"] = {},
	["County Roscommon, Ireland"] = {},
	["County Sligo, Ireland"] = {},
	["County Tipperary, Ireland"] = {},
	["County Waterford, Ireland"] = {},
	["County Westmeath, Ireland"] = {},
	["County Wexford, Ireland"] = {},
	["County Wicklow, Ireland"] = {},
}

local function make_irish_type_key_to_placename(container_pattern)
	return function(key)
		key = key:gsub(container_pattern, "")
		local elliptical_key = key:gsub("^County ", "")
		return key, elliptical_key
	end
end

local function make_irish_type_placename_to_key(container_suffix)
	return function(placename)
		if not placename:find("^County ") and not placename:find("^City ") then
			placename = "County " .. placename
		end
		return placename .. container_suffix
	end
end

-- counties of Ireland
export.ireland_group = {
	key_to_placename = make_irish_type_key_to_placename(", Ireland$"),
	placename_to_key = make_irish_type_placename_to_key(", Ireland"),
	default_container = "Ireland",
	default_placetype = "county",
	data = export.ireland_counties,
}

export.italy_administrative_regions = {
	["Abruzzo, Italy"] = {},
	["Aosta Valley, Italy"] = {placetype = {"autonomous region", "administrative region", "region"}},
	["Apulia, Italy"] = {},
	["Basilicata, Italy"] = {},
	["Calabria, Italy"] = {},
	["Campania, Italy"] = {},
	["Emilia-Romagna, Italy"] = {},
	["Friuli-Venezia Giulia, Italy"] = {placetype = {"autonomous region", "administrative region", "region"}},
	["Lazio, Italy"] = {},
	["Liguria, Italy"] = {},
	["Lombardy, Italy"] = {},
	["Marche, Italy"] = {},
	["Molise, Italy"] = {},
	["Piedmont, Italy"] = {},
	["Sardinia, Italy"] = {placetype = {"autonomous region", "administrative region", "region"}},
	["Sicily, Italy"] = {placetype = {"autonomous region", "administrative region", "region"}},
	["Trentino-Alto Adige, Italy"] = {placetype = {"autonomous region", "administrative region", "region"}},
	["Tuscany, Italy"] = {},
	["Umbria, Italy"] = {},
	["Veneto, Italy"] = {},
}

-- administrative regions of Italy
export.italy_group = {
	default_container = "Italy",
	default_placetype = "region",
	data = export.italy_administrative_regions,
}

-- table of Japanese prefectures; interpolated into the main 'places' table, but also needed separately
export.japan_prefectures = {
	["Aichi Prefecture, Japan"] = {},
	["Akita Prefecture, Japan"] = {},
	["Aomori Prefecture, Japan"] = {},
	["Chiba Prefecture, Japan"] = {},
	["Ehime Prefecture, Japan"] = {},
	["Fukui Prefecture, Japan"] = {},
	["Fukuoka Prefecture, Japan"] = {},
	["Fukushima Prefecture, Japan"] = {},
	["Gifu Prefecture, Japan"] = {},
	["Gunma Prefecture, Japan"] = {},
	["Hiroshima Prefecture, Japan"] = {},
	["Hokkaido Prefecture, Japan"] = {divs = "subprefectures", wp = "Hokkaido"},
	["Hyōgo Prefecture, Japan"] = {},
	["Hyogo Prefecture, Japan"] = {alias_of = "Hyōgo Prefecture, Japan", display = true},
	["Ibaraki Prefecture, Japan"] = {},
	["Ishikawa Prefecture, Japan"] = {},
	["Iwate Prefecture, Japan"] = {},
	["Kagawa Prefecture, Japan"] = {},
	["Kagoshima Prefecture, Japan"] = {},
	["Kanagawa Prefecture, Japan"] = {},
	["Kōchi Prefecture, Japan"] = {},
	["Kochi Prefecture, Japan"] = {alias_of = "Kōchi Prefecture, Japan", display = true},
	["Kumamoto Prefecture, Japan"] = {},
	["Kyoto Prefecture, Japan"] = {},
	["Mie Prefecture, Japan"] = {},
	["Miyagi Prefecture, Japan"] = {},
	["Miyazaki Prefecture, Japan"] = {},
	["Nagano Prefecture, Japan"] = {},
	["Nagasaki Prefecture, Japan"] = {},
	["Nara Prefecture, Japan"] = {},
	["Niigata Prefecture, Japan"] = {},
	["Ōita Prefecture, Japan"] = {},
	["Oita Prefecture, Japan"] = {alias_of = "Ōita Prefecture, Japan", display = true},
	["Okayama Prefecture, Japan"] = {},
	["Okinawa Prefecture, Japan"] = {},
	["Osaka Prefecture, Japan"] = {},
	["Saga Prefecture, Japan"] = {},
	["Saitama Prefecture, Japan"] = {},
	["Shiga Prefecture, Japan"] = {},
	["Shimane Prefecture, Japan"] = {},
	["Shizuoka Prefecture, Japan"] = {},
	["Tochigi Prefecture, Japan"] = {},
	["Tokushima Prefecture, Japan"] = {},
	["Tottori Prefecture, Japan"] = {},
	["Toyama Prefecture, Japan"] = {},
	["Wakayama Prefecture, Japan"] = {},
	["Yamagata Prefecture, Japan"] = {},
	["Yamaguchi Prefecture, Japan"] = {},
	["Yamanashi Prefecture, Japan"] = {},
}

-- prefectures of Japan
export.japan_group = {
	key_to_placename = make_key_to_placename(", Japan$", " Prefecture$"),
	placename_to_key = make_placename_to_key(", Japan", " Prefecture"),
	default_container = "Japan",
	default_placetype = "prefecture",
	data = export.japan_prefectures,
}

export.laos_provinces = {
	["Attapeu Province, Laos"] = {},
	["Bokeo Province, Laos"] = {},
	["Bolikhamxai Province, Laos"] = {},
	["Champasak Province, Laos"] = {},
	["Houaphanh Province, Laos"] = {},
	["Khammouane Province, Laos"] = {},
	["Luang Namtha Province, Laos"] = {},
	["Luang Prabang Province, Laos"] = {},
	["Oudomxay Province, Laos"] = {},
	["Phongsaly Province, Laos"] = {},
	["Salavan Province, Laos"] = {},
	["Savannakhet Province, Laos"] = {},
	["Vientiane Province, Laos"] = {},
	["Vientiane Prefecture, Laos"] = {placetype = "prefecture", wp = "%l"},
	["Sainyabuli Province, Laos"] = {},
	["Sekong Province, Laos"] = {},
	["Xaisomboun Province, Laos"] = {},
	["Xiangkhouang Province, Laos"] = {},
}

local function laos_placename_to_key(placename)
	if placename == "Vientiane Prefecture" then
		return placename .. ", Laos"
	end
	if placename:find(" Province$") then
		return placename .. ", Laos"
	end
	return placename .. " Province, Laos"
end

-- provinces of Laos
export.laos_group = {
	key_to_placename = make_key_to_placename(", Laos$", {" Province$", " Prefecture$"}),
	placename_to_key = laos_placename_to_key,
	default_container = "Laos",
	default_placetype = "province",
	-- For obscure reasons, provinces of Iran, Laos, Thailand and Vietnam use lowercase 'province'
	default_wp = "%e province",
	data = export.laos_provinces,
}

export.lebanon_governorates = {
	["Akkar Governorate, Lebanon"] = {},
	["Baalbek-Hermel Governorate, Lebanon"] = {},
	["Beirut Governorate, Lebanon"] = {},
	["Beqaa Governorate, Lebanon"] = {},
	["Keserwan-Jbeil Governorate, Lebanon"] = {},
	["Mount Lebanon Governorate, Lebanon"] = {},
	["Nabatieh Governorate, Lebanon"] = {},
	-- These two are generic enough that we don't want to automatically augment a use of `gov/North Governorate` or
	-- `gov/South Governorate` with `c/Lebanon`.
	["North Governorate, Lebanon"] = {no_auto_augment_container = true},
	["South Governorate, Lebanon"] = {no_auto_augment_container = true},
}

-- governorates of Lebanon
export.lebanon_group = {
	key_to_placename = make_key_to_placename(", Lebanon$", " Governorate$"),
	placename_to_key = make_placename_to_key(", Lebanon", " Governorate"),
	default_container = "Lebanon",
	default_placetype = "governorate",
	data = export.lebanon_governorates,
}

export.malaysia_states = {
	["Johor, Malaysia"] = {},
	["Kedah, Malaysia"] = {},
	["Kelantan, Malaysia"] = {},
	["Malacca, Malaysia"] = {},
	["Negeri Sembilan, Malaysia"] = {},
	["Pahang, Malaysia"] = {},
	["Penang, Malaysia"] = {},
	["Perak, Malaysia"] = {},
	["Perlis, Malaysia"] = {},
	["Sabah, Malaysia"] = {},
	["Sarawak, Malaysia"] = {},
	["Selangor, Malaysia"] = {},
	["Terengganu, Malaysia"] = {},
}

-- states of Malaysia
export.malaysia_group = {
	default_container = "Malaysia",
	default_placetype = "state",
	default_wp = "%l, %c",
	data = export.malaysia_states,
}

export.malta_regions = {
	-- Some of the regions are generic enough that we don't want to automatically augment a use of e.g.
	-- `r/Northern Region` with `c/Malta`. In particular;
	-- * "Eastern Region" also occurs at least in Ghana, Uganda, Iceland, Nigeria, Venezuela, North Macedonia and
	--   El Salvador;
	-- * "Northern Region" also occurs at least in Ghana, Uganda, Malawi, Nigeria, Canada and South Africa;
	-- * "Western Region" also occurs at least in Abu Dhabi, Bahrain, South Africa, Ghana, Iceland, Nepal, Nigeria,
	--   Serbia and Uganda;
	-- * "Southern Region" also occurs at least in Nigeria, Eritrea, Iceland, Ireland, Malawi and Serbia.
	["Eastern Region, Malta"] = {no_auto_augment_container = true},
	["Gozo Region, Malta"] = {wp = "%l"},
	["Northern Region, Malta"] = {no_auto_augment_container = true},
	["Port Region, Malta"] = {},
	["Southern Region, Malta"] = {no_auto_augment_container = true},
	["Western Region, Malta"] = {no_auto_augment_container = true},
}

-- regions of Malta
export.malta_group = {
	key_to_placename = make_key_to_placename(", Malta$", " Region"),
	placename_to_key = make_placename_to_key(", Malta", " Region"),
	default_container = "Malta",
	default_placetype = "region",
	default_wp = "%l, %c",
	default_the = true,
	data = export.malta_regions,
}

export.mexico_states = {
	["Aguascalientes, Mexico"] = {},
	["Baja California, Mexico"] = {},
	-- not display-canonicalizing because the "Norte" could be for emphasis
	["Baja California Norte, Mexico"] = {alias_of = "Baja California, Mexico"},
	["Baja California Sur, Mexico"] = {},
	["Campeche, Mexico"] = {},
	["Chiapas, Mexico"] = {},
	["Chihuahua, Mexico"] = {wp = "%l (state)"},
	["Coahuila, Mexico"] = {},
	["Colima, Mexico"] = {},
	["Durango, Mexico"] = {},
	["Guanajuato, Mexico"] = {},
	["Guerrero, Mexico"] = {},
	["Hidalgo, Mexico"] = {wp = "%l (state)"},
	["Jalisco, Mexico"] = {},
	["State of Mexico, Mexico"] = {the = true},
	["Mexico, Mexico"] = {alias_of = "State of Mexico, Mexico"}, -- differs in "the"
	-- ["Mexico City, Mexico"] = {}, doesn't belong here because it's a city
	["Michoacán, Mexico"] = {},
	["Michoacan, Mexico"] = {alias_of = "Michoacán, Mexico", display = true},
	["Morelos, Mexico"] = {},
	["Nayarit, Mexico"] = {},
	["Nuevo León, Mexico"] = {},
	["Nuevo Leon, Mexico"] = {alias_of = "Nuevo León, Mexico", display = true},
	["Oaxaca, Mexico"] = {},
	["Puebla, Mexico"] = {},
	["Querétaro, Mexico"] = {},
	["Queretaro, Mexico"] = {alias_of = "Querétaro, Mexico", display = true},
	["Quintana Roo, Mexico"] = {},
	["San Luis Potosí, Mexico"] = {},
	["San Luis Potosi, Mexico"] = {alias_of = "San Luis Potosí, Mexico", display = true},
	["Sinaloa, Mexico"] = {},
	["Sonora, Mexico"] = {},
	["Tabasco, Mexico"] = {},
	["Tamaulipas, Mexico"] = {},
	["Tlaxcala, Mexico"] = {},
	["Veracruz, Mexico"] = {},
	["Yucatán, Mexico"] = {},
	["Yucatan, Mexico"] = {alias_of = "Yucatán, Mexico", display = true},
	["Zacatecas, Mexico"] = {},
}

-- Mexican states
export.mexico_group = {
	default_container = "Mexico",
	default_placetype = "state",
	data = export.mexico_states,
}

export.moldova_districts_and_autonomous_territorial_units = {
	["Anenii Noi District, Moldova"] = {}, -- capital [[Anenii Noi]]
	["Basarabeasca District, Moldova"] = {}, -- capital [[Basarabeasca]]
	["Briceni District, Moldova"] = {}, -- capital [[Briceni]]
	["Cahul District, Moldova"] = {}, -- capital [[Cahul]]
	["Cantemir District, Moldova"] = {}, -- capital [[Cantemir, Moldova|Cantemir]]
	["Călărași District, Moldova"] = {}, -- capital [[Călărași, Moldova|Călărași]]
	["Căușeni District, Moldova"] = {}, -- capital [[Căușeni]]
	["Cimișlia District, Moldova"] = {}, -- capital [[Cimișlia]]
	["Criuleni District, Moldova"] = {}, -- capital [[Criuleni]]
	["Dondușeni District, Moldova"] = {}, -- capital [[Dondușeni]]
	["Drochia District, Moldova"] = {}, -- capital [[Drochia]]
	["Dubăsari District, Moldova"] = {}, -- capital [[Cocieri]]
	["Edineț District, Moldova"] = {}, -- capital [[Edineț]]
	["Fălești District, Moldova"] = {}, -- capital [[Fălești]]
	["Florești District, Moldova"] = {}, -- capital [[Florești, Moldova|Florești]]
	["Glodeni District, Moldova"] = {}, -- capital [[Glodeni]]
	["Hîncești District, Moldova"] = {}, -- capital [[Hîncești]]
	["Ialoveni District, Moldova"] = {}, -- capital [[Ialoveni]]
	["Leova District, Moldova"] = {}, -- capital [[Leova]]
	["Nisporeni District, Moldova"] = {}, -- capital [[Nisporeni]]
	["Ocnița District, Moldova"] = {}, -- capital [[Ocnița]]
	["Orhei District, Moldova"] = {}, -- capital [[Orhei]]
	["Rezina District, Moldova"] = {}, -- capital [[Rezina]]
	["Rîșcani District, Moldova"] = {}, -- capital [[Rîșcani]]
	["Sîngerei District, Moldova"] = {}, -- capital [[Sîngerei]]
	["Soroca District, Moldova"] = {}, -- capital [[Soroca]]
	["Strășeni District, Moldova"] = {}, -- capital [[Strășeni]]
	["Șoldănești District, Moldova"] = {}, -- capital [[Șoldănești]]
	["Ștefan Vodă District, Moldova"] = {}, -- capital [[Ștefan Vodă]]
	["Taraclia District, Moldova"] = {}, -- capital [[Taraclia]]
	["Telenești District, Moldova"] = {}, -- capital [[Telenești]]
	["Ungheni District, Moldova"] = {}, -- capital [[Ungheni]]
	["Chișinău, Moldova"] = {placetype = "municipality"},
	["Bălți, Moldova"] = {placetype = "municipality"},
	["Gagauzia, Moldova"] = {placetype = {"autonomous territorial unit", "autonomous region", "region"}}, -- capital [[Comrat]]
	-- the remainder are under the de-facto control of the unrecognized state of Transnistria
	["Bender, Moldova"] = {placetype = "municipality"},
	["Tighina, Moldova"] = {alias_of = "Bender, Moldova"},
	["Transnistria, Moldova"] = {placetype = {"autonomous territorial unit", "autonomous region", "region"}}, -- capital [[Tiraspol]]
	["Left Bank of the Dniester, Moldova"] = {alias_of = "Transnistria, Moldova", the = true},
	["Administrative-Territorial Units of the Left Bank of the Dniester, Moldova"] = {alias_of = "Transnistria, Moldova", the = true},
}

local function moldova_placename_to_key(placename)
	local elliptical_key = placename .. ", Moldova"
	if export.moldova_districts_and_autonomous_territorial_units[elliptical_key] then
		return elliptical_key
	end
	if placename:find(" District$") then
		return placename .. ", Moldova"
	end
	return placename .. " District, Moldova"
end

-- Moldovan districts (raions) and autonomous territorial units
export.moldova_group = {
	key_to_placename = make_key_to_placename(", Moldova$", " District"),
	placename_to_key = moldova_placename_to_key,
	default_container = "Moldova",
	default_placetype = {"district", "raion"},
	default_divs = "communes",
	data = export.moldova_districts_and_autonomous_territorial_units,
}

export.morocco_regions = {
	["Tangier-Tetouan-Al Hoceima, Morocco"] = {},
	["Oriental, Morocco"] = {wp = "%l (%c)"},
	["L'Oriental, Morocco"] = {alias_of = "Oriental, Morocco", display = true},
	["Fez-Meknes, Morocco"] = {},
	["Rabat-Sale-Kenitra, Morocco"] = {wp = "Rabat-Salé-Kénitra"},
	["Rabat-Salé-Kénitra, Morocco"] = {alias_of = "Rabat-Sale-Kenitra, Morocco", display = true},
	["Beni Mellal-Khenifra, Morocco"] = {wp = "Béni Mellal-Khénifra"},
	["Béni Mellal-Khénifra, Morocco"] = {alias_of = "Beni Mellal-Khenifra, Morocco", display = true},
	["Casablanca-Settat, Morocco"] = {},
	["Marrakesh-Safi, Morocco"] = {wp = "Marrakesh–Safi"}, -- WP title has en-dash
	["Marrakech-Safi, Morocco"] = {alias_of = "Marrakesh-Safi, Morocco", display = true},
	["Draa-Tafilalet, Morocco"] = {wp = "Drâa-Tafilalet"},
	["Drâa-Tafilalet, Morocco"] = {alias_of = "Draa-Tafilalet, Morocco", display = true},
	["Souss-Massa, Morocco"] = {},
	["Guelmim-Oued Noun, Morocco"] = {
		keydesc = "+++. '''NOTE:''' This region lies partly within the disputed territory of [[Western Sahara]]"
	},
	["Laayoune-Sakia El Hamra, Morocco"] = {
		wp = "Laâyoune-Sakia El Hamra",
		keydesc = "+++. '''NOTE:''' This region lies almost completely within the disputed territory of [[Western Sahara]]",
	},
	["Laâyoune-Sakia El Hamra, Morocco"] = {alias_of = "Laayoune-Sakia El Hamra, Morocco", display = true},
	["Dakhla-Oued Ed-Dahab, Morocco"] = {
		keydesc = "+++. '''NOTE:''' This region lies completely within the disputed territory of [[Western Sahara]]",
	},
}

-- regions of Morocco
export.morocco_group = {
	default_container = "Morocco",
	default_placetype = "region",
	data = export.morocco_regions,
}

export.netherlands_provinces = {
	["Drenthe, Netherlands"] = {},
	["Flevoland, Netherlands"] = {},
	["Friesland, Netherlands"] = {},
	["Gelderland, Netherlands"] = {},
	["Groningen, Netherlands"] = {wp = "%l (province)"},
	["Limburg, Netherlands"] = {wp = "%l (%c)"},
	["North Brabant, Netherlands"] = {},
	-- Foreign forms get display-canonicalized.
	["Noord-Brabant, Netherlands"] = {alias_of = "North Brabant, Netherlands", display = true},
	["North Holland, Netherlands"] = {},
	["Noord-Holland, Netherlands"] = {alias_of = "North Holland, Netherlands", display = true},
	["Overijssel, Netherlands"] = {},
	["South Holland, Netherlands"] = {},
	["Zuid-Holland, Netherlands"] = {alias_of = "South Holland, Netherlands", display = true},
	["Utrecht, Netherlands"] = {wp = "%l (province)"},
	["Zeeland, Netherlands"] = {},
}

-- provinces of the Netherlands
export.netherlands_group = {
	default_container = "Netherlands",
	default_placetype = "province",
	default_divs = "municipalities",
	data = export.netherlands_provinces,
}

export.new_zealand_regions = {
	-- North Island regions
	["Northland, New Zealand"] = {wp = "%l Region"}, -- ISO 3166-2 code NZ-NTL, number 1, capital [[Whangārei]]
	["Auckland, New Zealand"] = {wp = "%l Region"}, -- ISO 3166-2 code NZ-AUK, number 2, capital [[Auckland]]
	["Waikato, New Zealand"] = {}, -- ISO 3166-2 code NZ-WKO, number 3, capital [[Hamilton, New Zealand|Hamilton]]
	["Bay of Plenty, New Zealand"] = {the = true, wp = "%l Region"}, -- ISO 3166-2 code NZ-BOP, number 4, capital [[Whakatāne]]
	["Gisborne, New Zealand"] = {placetype = {"region", "district"}, wp = "%l District"}, -- ISO 3166-2 code NZ-GIS, number 5, capital [[Gisborne, New Zealand|Gisborne]]
	["Hawke's Bay, New Zealand"] = {}, -- ISO 3166-2 code NZ-HKB, number 6, capital [[Napier, New Zealand|Napier]]
	["Taranaki, New Zealand"] = {}, -- ISO 3166-2 code NZ-TKI, number 7, capital [[Stratford, New Zealand|Stratford]]
	["Manawatū-Whanganui, New Zealand"] = {}, -- ISO 3166-2 code NZ-MWT, number 8, capital [[Palmerston North]]
	["Manawatu-Whanganui, New Zealand"] = {alias_of = "Manawatū-Whanganui, New Zealand", display = true},
	["Manawatu-Wanganui, New Zealand"] = {alias_of = "Manawatū-Whanganui, New Zealand", display = true},
	["Wellington, New Zealand"] = {wp = "%l Region"}, -- ISO 3166-2 code NZ-WGN, number 9, capital [[Wellington]]
	-- South Island regions
	["Tasman, New Zealand"] = {placetype = {"region", "district"}, wp = "%l District"}, -- ISO 3166-2 code NZ-TAS, number 10, capital [[Richmond, New Zealand|Richmond]]
	["Nelson, New Zealand"] = {placetype = {"region", "city"}, wp = "%l, %c", is_city = true}, -- ISO 3166-2 code NZ-NSN, number 11, capital [[Nelson, New Zealand|Nelson]]
	["Marlborough, New Zealand"] = {placetype = {"region", "district"}, wp = "%l District"}, -- ISO 3166-2 code NZ-MBH, number 12, capital [[Blenheim, New Zealand|Blenheim]]
	["West Coast, New Zealand"] = {the = true, wp = "%l Region"}, -- ISO 3166-2 code NZ-WTC, number 13, capital [[Greymouth]]
	["Canterbury, New Zealand"] = {wp = "%l Region"}, -- ISO 3166-2 code NZ-CAN, number 14, capital [[Christchurch]]
	["Otago, New Zealand"] = {}, -- ISO 3166-2 code NZ-OTA, number 15, capital [[Dunedin]]
	["Southland, New Zealand"] = {wp = "%l Region"}, -- ISO 3166-2 code NZ-STL, number 16, capital [[Invercargill]]
}

-- regions of New Zealand
export.new_zealand_group = {
	default_container = "New Zealand",
	default_placetype = "region",
	data = export.new_zealand_regions,
}

export.nigeria_states = {
	["Abia State, Nigeria"] = {},
	["Adamawa State, Nigeria"] = {},
	["Akwa Ibom State, Nigeria"] = {},
	["Anambra State, Nigeria"] = {},
	["Bauchi State, Nigeria"] = {},
	["Bayelsa State, Nigeria"] = {},
	["Benue State, Nigeria"] = {},
	["Borno State, Nigeria"] = {},
	["Cross River State, Nigeria"] = {},
	["Delta State, Nigeria"] = {},
	["Ebonyi State, Nigeria"] = {},
	["Edo State, Nigeria"] = {},
	["Ekiti State, Nigeria"] = {},
	["Enugu State, Nigeria"] = {},
	["Federal Capital Territory, Nigeria"] = {
		-- not a state but allow it to be referenced as one in holonyms
		placetype = {"federal territory", "territory", "state"}, the = true, wp = "%l (%c)",
	},
	["Gombe State, Nigeria"] = {},
	["Imo State, Nigeria"] = {},
	["Jigawa State, Nigeria"] = {},
	["Kaduna State, Nigeria"] = {},
	["Kano State, Nigeria"] = {},
	["Katsina State, Nigeria"] = {},
	["Kebbi State, Nigeria"] = {},
	["Kogi State, Nigeria"] = {},
	["Kwara State, Nigeria"] = {},
	["Lagos State, Nigeria"] = {},
	["Nasarawa State, Nigeria"] = {},
	["Niger State, Nigeria"] = {},
	["Ogun State, Nigeria"] = {},
	["Ondo State, Nigeria"] = {},
	["Osun State, Nigeria"] = {},
	["Oyo State, Nigeria"] = {},
	["Plateau State, Nigeria"] = {},
	["Rivers State, Nigeria"] = {},
	["Sokoto State, Nigeria"] = {},
	["Taraba State, Nigeria"] = {},
	["Yobe State, Nigeria"] = {},
	["Zamfara State, Nigeria"] = {},
}

-- states of Nigeria
export.nigeria_group = {
	key_to_placename = make_key_to_placename(", Nigeria$", " State$"),
	placename_to_key = make_placename_to_key(", Nigeria", " State"),
	default_container = "Nigeria",
	default_placetype = "state",
	data = export.nigeria_states,
}

export.north_korea_provinces = {
	["Chagang Province, North Korea"] = {},
	["North Hamgyong Province, North Korea"] = {},
	["South Hamgyong Province, North Korea"] = {},
	["North Hwanghae Province, North Korea"] = {},
	["South Hwanghae Province, North Korea"] = {},
	["Kangwon Province, North Korea"] = {wp = "%l (%c)"},
	["North Pyongan Province, North Korea"] = {},
	["South Pyongan Province, North Korea"] = {},
	["Ryanggang Province, North Korea"] = {},
}

-- provinces of North Korea
export.north_korea_group = {
	key_to_placename = make_key_to_placename(", North Korea$", " Province$"),
	placename_to_key = make_placename_to_key(", North Korea", " Province"),
	default_container = "North Korea",
	default_placetype = "province",
	data = export.north_korea_provinces,
}

export.norwegian_counties = {
	["Oslo, Norway"] = {},
	["Rogaland, Norway"] = {},
	["Møre og Romsdal, Norway"] = {},
	["Nordland, Norway"] = {},
	["Østfold, Norway"] = {},
	["Akershus, Norway"] = {},
	["Buskerud, Norway"] = {},
	-- the following two were merged into Innlandet
	-- ["Hedmark, Norway"] = {},
	-- ["Oppland, Norway"] = {},
	["Innlandet, Norway"] = {},
	["Vestfold, Norway"] = {},
	["Telemark, Norway"] = {},
	-- the following two were merged into Agder
	-- ["Aust-Agder, Norway"] = {},
	-- ["Vest-Agder, Norway"] = {},
	["Agder, Norway"] = {},
	-- the following two were merged into Vestland
	-- ["Hordaland, Norway"] = {},
	-- ["Sogn og Fjordane, Norway"] = {},
	["Vestland, Norway"] = {},
	["Trøndelag, Norway"] = {},
	["Troms, Norway"] = {},
	["Finnmark, Norway"] = {},
}

-- counties of Norway
export.norway_group = {
	default_container = "Norway",
	default_placetype = "county",
	data = export.norwegian_counties,
}

export.pakistan_provinces_and_territories = {
	["Azad Kashmir, Pakistan"] = {
		placetype = {"administrative territory", "autonomous territory", "territory"},
	},
	["Azad Jammu and Kashmir, Pakistan"] = {alias_of = "Azad Kashmir, Pakistan", display = true},
	["Balochistan, Pakistan"] = {wp = "%l, %c"},
	["Gilgit-Baltistan, Pakistan"] = {
		placetype = {"administrative territory", "territory"},
	},
	["Islamabad Capital Territory, Pakistan"] = {
		the = true,
		divs = {}, -- no divisions
		placetype = {"federal territory", "administrative territory", "territory"},
	},
	-- Islamabad is an accepted alias for Islamabad Capital Territory given the above placetypes
	["Islamabad, Pakistan"] = {alias_of = "Islamabad Capital Territory, Pakistan"},
	["Khyber Pakhtunkhwa, Pakistan"] = {},
	["Punjab, Pakistan"] = {wp = "%l, %c"},
	["Sindh, Pakistan"] = {},
}

-- provinces and territories of Pakistan
export.pakistan_group = {
	default_container = "Pakistan",
	default_placetype = "province",
	default_divs = "divisions",
	data = export.pakistan_provinces_and_territories,
}

export.philippines_provinces = {
	["Abra, Philippines"] = {wp = "%l (province)"},
	["Agusan del Norte, Philippines"] = {},
	["Agusan del Sur, Philippines"] = {},
	["Aklan, Philippines"] = {},
	["Albay, Philippines"] = {},
	["Antique, Philippines"] = {wp = "%l (province)"},
	["Apayao, Philippines"] = {},
	["Aurora, Philippines"] = {wp = "%l (province)"},
	["Basilan, Philippines"] = {},
	["Bataan, Philippines"] = {},
	["Batanes, Philippines"] = {},
	["Batangas, Philippines"] = {},
	["Benguet, Philippines"] = {},
	["Biliran, Philippines"] = {},
	["Bohol, Philippines"] = {},
	["Bukidnon, Philippines"] = {},
	["Bulacan, Philippines"] = {},
	["Cagayan, Philippines"] = {},
	["Camarines Norte, Philippines"] = {},
	["Camarines Sur, Philippines"] = {},
	["Camiguin, Philippines"] = {},
	["Capiz, Philippines"] = {},
	["Catanduanes, Philippines"] = {},
	["Cavite, Philippines"] = {},
	["Cebu, Philippines"] = {},
	["Cotabato, Philippines"] = {},
	["Davao de Oro, Philippines"] = {},
	["Davao del Norte, Philippines"] = {},
	["Davao del Sur, Philippines"] = {},
	["Davao Occidental, Philippines"] = {},
	["Davao Oriental, Philippines"] = {},
	["Dinagat Islands, Philippines"] = {the = true},
	["Eastern Samar, Philippines"] = {},
	["Guimaras, Philippines"] = {},
	["Ifugao, Philippines"] = {},
	["Ilocos Norte, Philippines"] = {},
	["Ilocos Sur, Philippines"] = {},
	["Iloilo, Philippines"] = {},
	["Isabela, Philippines"] = {wp = "%l (province)"},
	["Kalinga, Philippines"] = {wp = "%l (province)"},
	["La Union, Philippines"] = {},
	["Laguna, Philippines"] = {wp = "%l (province)"},
	["Lanao del Norte, Philippines"] = {},
	["Lanao del Sur, Philippines"] = {},
	["Leyte, Philippines"] = {wp = "%l (province)"},
	["Maguindanao del Norte, Philippines"] = {},
	["Maguindanao del Sur, Philippines"] = {},
	["Marinduque, Philippines"] = {},
	["Masbate, Philippines"] = {},
	["Misamis Occidental, Philippines"] = {},
	["Misamis Oriental, Philippines"] = {},
	["Mountain Province, Philippines"] = {},
	["Negros Occidental, Philippines"] = {},
	["Negros Oriental, Philippines"] = {},
	["Northern Samar, Philippines"] = {},
	["Nueva Ecija, Philippines"] = {},
	["Nueva Vizcaya, Philippines"] = {},
	["Occidental Mindoro, Philippines"] = {},
	["Oriental Mindoro, Philippines"] = {},
	["Palawan, Philippines"] = {},
	["Pampanga, Philippines"] = {},
	["Pangasinan, Philippines"] = {},
	["Quezon, Philippines"] = {},
	["Quirino, Philippines"] = {},
	["Rizal, Philippines"] = {wp = "%l (province)"},
	["Romblon, Philippines"] = {},
	["Samar, Philippines"] = {wp = "%l (province)"},
	["Sarangani, Philippines"] = {},
	["Siquijor, Philippines"] = {},
	["Sorsogon, Philippines"] = {},
	["South Cotabato, Philippines"] = {},
	["Southern Leyte, Philippines"] = {},
	["Sultan Kudarat, Philippines"] = {},
	["Sulu, Philippines"] = {},
	["Surigao del Norte, Philippines"] = {},
	["Surigao del Sur, Philippines"] = {},
	["Tarlac, Philippines"] = {},
	["Tawi-Tawi, Philippines"] = {},
	["Zambales, Philippines"] = {},
	["Zamboanga del Norte, Philippines"] = {},
	["Zamboanga del Sur, Philippines"] = {},
	["Zamboanga Sibugay, Philippines"] = {},
	-- not a province but treated as one; allow it to be referred to as a province in holonyms
	["Metro Manila, Philippines"] = {placetype = {"region", "province"}},
}

-- provinces of the Philippines
export.philippines_group = {
	default_container = "Philippines",
	default_placetype = "province",
	default_divs = {"municipalities", "barangays"},
	data = export.philippines_provinces,
}

export.poland_voivodeships = {
	["Lower Silesian Voivodeship, Poland"] = {}, -- abbr DS, code 02, capital Wrocław
	["Kuyavian-Pomeranian Voivodeship, Poland"] = {}, -- abbr KP, code 04, capital Bydgoszcz (seat of voivode), Toruń (seat of sejmik and marshal)
	["Lublin Voivodeship, Poland"] = {}, -- abbr LU, code 06, capital Lublin
	["Lubusz Voivodeship, Poland"] = {}, -- abbr LB, code 08, capital Gorzów Wielkopolski (seat of voivode), Zielona Góra (seat of sejmik and marshal)
	["Lodz Voivodeship, Poland"] = {wp = "Łódź Voivodeship"}, -- abbr LD, code 10, capital Łódź
	["Łódź Voivodeship, Poland"] = {alias_of = "Lodz Voivodeship, Poland", display = true, display_as_full = true},
	["Lesser Poland Voivodeship, Poland"] = {}, -- abbr MA, code 12, capital Kraków
	["Masovian Voivodeship, Poland"] = {}, -- abbr MZ, code 14, capital Warsaw
	["Opole Voivodeship, Poland"] = {}, -- abbr OP, code 16, capital Opole
	["Subcarpathian Voivodeship, Poland"] = {}, -- abbr PK, code 18, capital Rzeszów
	["Podlaskie Voivodeship, Poland"] = {}, -- abbr PD, code 20, capital Białystok
	["Pomeranian Voivodeship, Poland"] = {}, -- abbr PM, code 22, capital Gdańsk
	["Silesian Voivodeship, Poland"] = {}, -- abbr SL, code 24, capital Katowice
	["Holy Cross Voivodeship, Poland"] = {wp = "Świętokrzyskie Voivodeship"}, -- abbr SK, code 26, capital Kielce
	["Świętokrzyskie Voivodeship, Poland"] = {alias_of = "Holy Cross Voivodeship, Poland", display = true, display_as_full = true},
	["Warmian-Masurian Voivodeship, Poland"] = {}, -- abbr WN, code 28, capital Olsztyn
	["Greater Poland Voivodeship, Poland"] = {}, -- abbr WP, code 30, capital Poznań
	["West Pomeranian Voivodeship, Poland"] = {}, -- abbr ZP, code 32, capital Szczecin
}

-- voivodeships of Poland
export.poland_group = {
	key_to_placename = make_key_to_placename(", Poland$", " Voivodeship$"),
	placename_to_key = make_placename_to_key(", Poland", " Voivodeship"),
	default_container = "Poland",
	default_placetype = "voivodeship",
	default_divs = {
		-- "counties", -- not enough of them currently
		{type = "Polish colonies", cat_as = {{type = "villages", prep = "in"}}},
	},
	data = export.poland_voivodeships,
}

export.portugal_districts_and_autonomous_regions = {
	["Azores, Portugal"] = {the = true, placetype = {"autonomous region", "region"}},
	["Aveiro District, Portugal"] = {},
	["Beja District, Portugal"] = {},
	["Braga District, Portugal"] = {},
	["Bragança District, Portugal"] = {},
	["Castelo Branco District, Portugal"] = {},
	["Coimbra District, Portugal"] = {},
	["Évora District, Portugal"] = {},
	["Faro District, Portugal"] = {},
	["Guarda District, Portugal"] = {},
	["Leiria District, Portugal"] = {},
	["Lisbon District, Portugal"] = {},
	["Lisboa District, Portugal"] = {alias_of = "Lisbon District, Portugal", display = true},
	["Madeira, Portugal"] = {placetype = {"autonomous region", "region"}},
	["Portalegre District, Portugal"] = {},
	["Porto District, Portugal"] = {},
	["Santarém District, Portugal"] = {},
	["Setúbal District, Portugal"] = {},
	["Viana do Castelo District, Portugal"] = {},
	["Vila Real District, Portugal"] = {},
	["Viseu District, Portugal"] = {},
}

local function portugal_placename_to_key(placename)
	if placename == "Azores" or placename == "Madeira" then
		return placename .. ", Portugal"
	end
	if placename:find(" District$") then
		return placename .. ", Portugal"
	end
	return placename .. " District, Portugal"
end

-- districts and autonomous regions of Portugal
export.portugal_group = {
	key_to_placename = make_key_to_placename(", Portugal$", " District$"),
	placename_to_key = portugal_placename_to_key,
	default_container = "Portugal",
	default_placetype = "district",
	default_divs = "municipalities",
	data = export.portugal_districts_and_autonomous_regions,
}

export.romania_counties = {
	["Alba County, Romania"] = {},
	["Arad County, Romania"] = {},
	["Argeș County, Romania"] = {},
	["Bacău County, Romania"] = {},
	["Bihor County, Romania"] = {},
	["Bistrița-Năsăud County, Romania"] = {},
	["Botoșani County, Romania"] = {},
	["Brașov County, Romania"] = {},
	["Brăila County, Romania"] = {},
	-- Bucharest: not in a county
	["Buzău County, Romania"] = {},
	["Caraș-Severin County, Romania"] = {},
	["Cluj County, Romania"] = {},
	["Constanța County, Romania"] = {},
	["Covasna County, Romania"] = {},
	["Călărași County, Romania"] = {},
	["Dolj County, Romania"] = {},
	["Dâmbovița County, Romania"] = {},
	["Galați County, Romania"] = {},
	["Giurgiu County, Romania"] = {},
	["Gorj County, Romania"] = {},
	["Harghita County, Romania"] = {},
	["Hunedoara County, Romania"] = {},
	["Ialomița County, Romania"] = {},
	["Iași County, Romania"] = {},
	["Ilfov County, Romania"] = {},
	["Maramureș County, Romania"] = {},
	["Mehedinți County, Romania"] = {},
	["Mureș County, Romania"] = {},
	["Neamț County, Romania"] = {},
	["Olt County, Romania"] = {},
	["Prahova County, Romania"] = {},
	["Satu Mare County, Romania"] = {},
	["Sibiu County, Romania"] = {},
	["Suceava County, Romania"] = {},
	["Sălaj County, Romania"] = {},
	["Teleorman County, Romania"] = {},
	["Timiș County, Romania"] = {},
	["Tulcea County, Romania"] = {},
	["Vaslui County, Romania"] = {},
	["Vrancea County, Romania"] = {},
	["Vâlcea County, Romania"] = {},
}

-- counties of Romania
export.romania_group = {
	key_to_placename = make_key_to_placename(", Romania$", " County$"),
	placename_to_key = make_placename_to_key(", Romania", " County"),
	default_container = "Romania",
	default_placetype = "county",
	default_divs = "communes",
	data = export.romania_counties,
}

local function make_russia_federal_subject_spec(spectype, use_the, wp)
	return {
		placetype = spectype,
		the = not not use_the,
		bare_category_parent_type = {"federal subjects", spectype .. "s"},
		wp = wp,
	}
end

local russia_autonomous_okrug_no_the =
	{placetype = {"autonomous okrug", "okrug"}, bare_category_parent_type = {"federal subjects", "autonomous okrugs"}}
local russia_autonomous_okrug_the =
	{placetype = {"autonomous okrug", "okrug"}, bare_category_parent_type = {"federal subjects", "autonomous okrugs"},
	 the = true}
local russia_krai = make_russia_federal_subject_spec("krai")
local russia_oblast = make_russia_federal_subject_spec("oblast")
local russia_republic_the = make_russia_federal_subject_spec("republic", "use the")
local russia_republic_no_the = make_russia_federal_subject_spec("republic")
export.russia_federal_subjects = {
	-- autonomous oblasts
	["Jewish Autonomous Oblast, Russia"] =
		{the = true, placetype = {"autonomous oblast", "oblast"},
		 bare_category_parent_type = {"federal subjects", "autonomous oblasts"}},
	-- autonomous okrugs
	["Chukotka Autonomous Okrug, Russia"] = russia_autonomous_okrug_the,
	["Chukotka, Russia"] = {alias_of = "Chukotka Autonomous Okrug, Russia"},
	["Khanty-Mansi Autonomous Okrug, Russia"] = russia_autonomous_okrug_the,
	["Khanty-Mansia, Russia"] = {alias_of = "Khanty-Mansi Autonomous Okrug, Russia"},
	["Khantia-Mansia, Russia"] = {alias_of = "Khanty-Mansi Autonomous Okrug, Russia"},
	["Yugra, Russia"] = {alias_of = "Khanty-Mansi Autonomous Okrug, Russia"},
	["Nenets Autonomous Okrug, Russia"] = russia_autonomous_okrug_the,
	["Nenetsia, Russia"] = {alias_of = "Nenets Autonomous Okrug, Russia"},
	["Yamalo-Nenets Autonomous Okrug, Russia"] = russia_autonomous_okrug_the,
	["Yamalia, Russia"] = {alias_of = "Yamalo-Nenets Autonomous Okrug, Russia"},
	-- krais
	["Altai Krai, Russia"] = russia_krai,
	["Kamchatka Krai, Russia"] = russia_krai,
	["Khabarovsk Krai, Russia"] = russia_krai,
	["Krasnodar Krai, Russia"] = russia_krai,
	["Krasnoyarsk Krai, Russia"] = russia_krai,
	["Perm Krai, Russia"] = russia_krai,
	["Primorsky Krai, Russia"] = russia_krai,
	["Stavropol Krai, Russia"] = russia_krai,
	["Zabaykalsky Krai, Russia"] = russia_krai,
	-- oblasts
	["Amur Oblast, Russia"] = russia_oblast,
	["Arkhangelsk Oblast, Russia"] = russia_oblast,
	["Astrakhan Oblast, Russia"] = russia_oblast,
	["Belgorod Oblast, Russia"] = russia_oblast,
	["Bryansk Oblast, Russia"] = russia_oblast,
	["Chelyabinsk Oblast, Russia"] = russia_oblast,
	["Irkutsk Oblast, Russia"] = russia_oblast,
	["Ivanovo Oblast, Russia"] = russia_oblast,
	["Kaliningrad Oblast, Russia"] = russia_oblast,
	["Kaluga Oblast, Russia"] = russia_oblast,
	["Kemerovo Oblast, Russia"] = russia_oblast,
	["Kirov Oblast, Russia"] = russia_oblast,
	["Kostroma Oblast, Russia"] = russia_oblast,
	["Kurgan Oblast, Russia"] = russia_oblast,
	["Kursk Oblast, Russia"] = russia_oblast,
	["Leningrad Oblast, Russia"] = russia_oblast,
	["Lipetsk Oblast, Russia"] = russia_oblast,
	["Magadan Oblast, Russia"] = russia_oblast,
	["Moscow Oblast, Russia"] = russia_oblast,
	["Murmansk Oblast, Russia"] = russia_oblast,
	["Nizhny Novgorod Oblast, Russia"] = russia_oblast,
	["Novgorod Oblast, Russia"] = russia_oblast,
	["Novosibirsk Oblast, Russia"] = russia_oblast,
	["Omsk Oblast, Russia"] = russia_oblast,
	["Orenburg Oblast, Russia"] = russia_oblast,
	["Oryol Oblast, Russia"] = russia_oblast,
	["Penza Oblast, Russia"] = russia_oblast,
	["Pskov Oblast, Russia"] = russia_oblast,
	["Rostov Oblast, Russia"] = russia_oblast,
	["Ryazan Oblast, Russia"] = russia_oblast,
	["Sakhalin Oblast, Russia"] = russia_oblast,
	["Samara Oblast, Russia"] = russia_oblast,
	["Saratov Oblast, Russia"] = russia_oblast,
	["Smolensk Oblast, Russia"] = russia_oblast,
	["Sverdlovsk Oblast, Russia"] = russia_oblast,
	["Tambov Oblast, Russia"] = russia_oblast,
	["Tomsk Oblast, Russia"] = russia_oblast,
	["Tula Oblast, Russia"] = russia_oblast,
	["Tver Oblast, Russia"] = russia_oblast,
	["Tyumen Oblast, Russia"] = russia_oblast,
	["Ulyanovsk Oblast, Russia"] = russia_oblast,
	["Vladimir Oblast, Russia"] = russia_oblast,
	["Volgograd Oblast, Russia"] = russia_oblast,
	["Vologda Oblast, Russia"] = russia_oblast,
	["Voronezh Oblast, Russia"] = russia_oblast,
	["Yaroslavl Oblast, Russia"] = russia_oblast,
	-- republics
	--
	-- We only need to include cases that aren't just shortened versions of the full federal subject name (i.e. where
	-- words like "Republic" and "Oblast" are omitted but the name is not otherwise modified; these are handled by
	-- key_to_placename). Non-display-canonicalizing aliases are generally due to differences in the presence or absence
	-- of "the".
	["Adygea, Russia"] = russia_republic_no_the,
	["Republic of Adygea, Russia"] = {alias_of = "Adygea, Russia", the = true},
	["Bashkortostan, Russia"] = russia_republic_no_the,
	["Republic of Bashkortostan, Russia"] = {alias_of = "Bashkortostan, Russia", the = true},
	["Bashkiria, Russia"] = {alias_of = "Bashkortostan, Russia"},
	["Buryatia, Russia"] = russia_republic_no_the,
	["Republic of Buryatia, Russia"] = {alias_of = "Buryatia, Russia", the = true},
	["Dagestan, Russia"] = russia_republic_no_the,
	["Republic of Dagestan, Russia"] = {alias_of = "Dagestan, Russia", the = true},
	["Ingushetia, Russia"] = russia_republic_no_the,
	["Republic of Ingushetia, Russia"] = {alias_of = "Ingushetia, Russia", the = true},
	["Kalmykia, Russia"] = russia_republic_no_the,
	["Republic of Kalmykia, Russia"] = {alias_of = "Kalmykia, Russia", the = true},
	["Karelia, Russia"] = make_russia_federal_subject_spec("republic", nil, "Republic of Karelia"),
	["Republic of Karelia, Russia"] = {alias_of = "Karelia, Russia", the = true},
	["Khakassia, Russia"] = russia_republic_no_the,
	["Republic of Khakassia, Russia"] = {alias_of = "Khakassia, Russia", the = true},
	["Mordovia, Russia"] = russia_republic_no_the,
	["Republic of Mordovia, Russia"] = {alias_of = "Mordovia, Russia", the = true},
	["North Ossetia-Alania, Russia"] = make_russia_federal_subject_spec("republic", nil, "North Ossetia–Alania"), -- with en-dash
	["Republic of North Ossetia-Alania, Russia"] = {alias_of = "North Ossetia-Alania, Russia", the = true},
	["North Ossetia, Russia"] = {alias_of = "North Ossetia-Alania, Russia", display = true},
	["Alania, Russia"] = {alias_of = "North Ossetia-Alania, Russia", display = true},
	["Tatarstan, Russia"] = russia_republic_no_the,
	["Republic of Tatarstan, Russia"] = {alias_of = "Tatarstan, Russia", the = true},
	["Altai Republic, Russia"] = russia_republic_the,
	["Chechnya, Russia"] = russia_republic_no_the,
	["Chechen Republic, Russia"] = {alias_of = "Chechnya, Russia", the = true},
	["Chuvashia, Russia"] = russia_republic_no_the,
	["Chuvash Republic, Russia"] = {alias_of = "Chuvashia, Russia", the = true},
	["Kabardino-Balkaria, Russia"] = russia_republic_no_the,
	["Kabardino-Balkariya, Russia"] = {alias_of = "Kabardino-Balkaria, Russia", display = true},
	["Kabardino-Balkarian Republic, Russia"] = {alias_of = "Kabardino-Balkaria, Russia", the = true},
	["Kabardino-Balkar Republic, Russia"] = {alias_of = "Kabardino-Balkaria, Russia",
		display = "Kabardino-Balkarian Republic, Russia", the = true},
	["Karachay-Cherkessia, Russia"] = russia_republic_no_the,
	["Karachay-Cherkess Republic, Russia"] = {alias_of = "Karachay-Cherkessia, Russia"},
	["Komi, Russia"] = make_russia_federal_subject_spec("republic", nil, "Komi Republic"),
	["Komi Republic, Russia"] = {alias_of = "Komi, Russia", the = true},
	["Mari El, Russia"] = russia_republic_no_the,
	["Mari El Republic, Russia"] = {alias_of = "Mari El, Russia", the = true},
	["Sakha, Russia"] = make_russia_federal_subject_spec("republic", nil, "Sakha Republic"),
	["Sakha Republic, Russia"] = {alias_of = "Sakha, Russia", the = true},
	["Yakutia, Russia"] = {alias_of = "Sakha, Russia"},
	["Yakutiya, Russia"] = {alias_of = "Sakha, Russia", display = "Yakutia, Russia"},
	["Republic of Yakutia (Sakha), Russia"] = {alias_of = "Sakha, Russia", display = "Sakha Republic, Russia",
		the = true},
	["Tuva, Russia"] = russia_republic_no_the,
	["Tyva, Russia"] = {alias_of = "Tuva, Russia", display = true},
	["Tuva Republic, Russia"] = {alias_of = "Tuva, Russia", the = true},
	["Tyva Republic, Russia"] = {alias_of = "Tuva, Russia", display= "Tuva Republic, Russia", the = true},
	["Udmurtia, Russia"] = russia_republic_no_the,
	["Udmurt Republic, Russia"] = {alias_of = "Udmurtia, Russia", the = true},
	-- Not included due to being unrecognized and only partly controlled:
	-- ["Crimea, Russia"] = make_russia_federal_subject_spec("republic", nil, "Republic of Crimea (Russia)")
	-- ["Donetsk People's Republic, Russia"] = russia_republic_the,
	-- ["Luhansk People's Republic, Russia"] = russia_republic_the,
	-- ["Zaporozhye Oblast, Russia"] = make_russia_federal_subject_spec("oblast", nil, "Russian occupation of Zaporizhzhia Oblast"),
	-- ["Kherson Oblast, Russia"] = make_russia_federal_subject_spec("oblast", nil, "Russian occupation of Kherson Oblast"),
	-- There are also federal cities (not included because they're cities):
	-- Moscow, Saint Petersburg; Sevastopol (unrecognized; same status as for "Crimea, Russia" above)
}

local function russia_key_to_placename(key)
	key = key:gsub(",.*", "")
	local full_placename = key
	if key == "Jewish Autonomous Oblast" then
		return full_placename, full_placename
	end
	local elliptical_placename
	for _, suffix in ipairs({"Krai", "Oblast"}) do
		elliptical_placename = key:match("^(.*) " .. suffix .. "$")
		if elliptical_placename then
			return full_placename, elliptical_placename
		end
	end
	return full_placename, full_placename
end

local function russia_placename_to_key(placename)
	local key = placename .. ", Russia"
	if export.russia_federal_subjects[key] then
		return key
	end
	-- We allow the user to say e.g. "obl/Samara" in place of "obl/Samara Oblast".
	for _, suffix in ipairs({"Krai", "Oblast"}) do
		local suffixed_key = placename .. " " .. suffix .. ", Russia"
		if export.russia_federal_subjects[suffixed_key] then
			return suffixed_key
		end
	end
	return placename .. ", Russia"
end

local function construct_russia_federal_subject_keydesc(group, key, spec)
	local placename = key:gsub(",.*", "")
	local linked_placename = export.construct_linked_placename(spec, placename)
	local placetype = spec.placetype
	if type(placetype) == "table" then
		placetype = placetype[1]
	end
	if placetype == "oblast" then
		-- Hack: Oblasts generally don't have entries under "Foo Oblast"
		-- but just under "Foo", so fix the linked key appropriately;
		-- doesn't apply to the Jewish Autonomous Oblast
		linked_placename = linked_placename:gsub(" Oblast%]%]", "%]%] Oblast")
	end
	return linked_placename .. ", a [[federal subject]] ([[" .. placetype .. "]]) of [[Russia]]"
end

-- federal subjects of Russia
export.russia_group = {
	key_to_placename = russia_key_to_placename,
	placename_to_key = russia_placename_to_key,
	default_container = "Russia",
	default_keydesc = construct_russia_federal_subject_keydesc,
	default_overriding_bare_label_parents = {"federal subjects of Russia", "+++"},
	data = export.russia_federal_subjects,
}

export.saudi_arabia_provinces = {
	["Riyadh Province, Saudi Arabia"] = {},
	["Mecca Province, Saudi Arabia"] = {},
	-- Name is too generic to assume it's in Saudi Arabia if not specified.
	["Eastern Province, Saudi Arabia"] = {no_auto_augment_container = true, wp = "%l, %c"},
	["Medina Province, Saudi Arabia"] = {wp = "%l (%c)"},
	["Aseer Province, Saudi Arabia"] = {wp = "Asir"},
	["Asir Province, Saudi Arabia"] = {alias_of = "Aseer Province, Saudi Arabia", display = true},
	["Jazan Province, Saudi Arabia"] = {},
	["Qassim Province, Saudi Arabia"] = {wp = "Al-Qassim Province"},
	["Al-Qassim Province, Saudi Arabia"] = {alias_of = "Qassim Province, Saudi Arabia", display = true},
	["Tabuk Province, Saudi Arabia"] = {},
	["Hail Province, Saudi Arabia"] = {wp = "Ḥa'il Province"},
	["Ha'il Province, Saudi Arabia"] = {alias_of = "Hail Province, Saudi Arabia", display = true},
	["Ḥa'il Province, Saudi Arabia"] = {alias_of = "Hail Province, Saudi Arabia", display = true},
	["Al-Jouf Province, Saudi Arabia"] = {wp = "Al-Jawf Province"},
	["Al-Jawf Province, Saudi Arabia"] = {alias_of = "Al-Jouf Province, Saudi Arabia", display = true},
	["Najran Province, Saudi Arabia"] = {},
	["Northern Borders Province, Saudi Arabia"] = {},
	["Al-Bahah Province, Saudi Arabia"] = {},
}

-- provinces of Saudi Arabia
export.saudi_arabia_group = {
	key_to_placename = make_key_to_placename(", Saudi Arabia$", " Province$"),
	placename_to_key = make_placename_to_key(", Saudi Arabia", " Province"),
	default_container = "Saudi Arabia",
	default_placetype = "province",
	data = export.saudi_arabia_provinces,
}

export.south_africa_provinces = {
	["Eastern Cape, South Africa"] = {the = true},
	["Free State, South Africa"] = {the = true, wp = "%l (province)"},
	["Gauteng, South Africa"] = {},
	["KwaZulu-Natal, South Africa"] = {},
	["Limpopo, South Africa"] = {},
	["Mpumalanga, South Africa"] = {},
	-- per Wikipedia and other sources, `North West` doesn't normally have `the` before it
	["North West, South Africa"] = {wp = "%l (South African province)"},
	["Northern Cape, South Africa"] = {the = true},
	["Western Cape, South Africa"] = {the = true},
}

-- provinces of South Africa
export.south_africa_group = {
	default_container = "South Africa",
	default_placetype = "province",
	default_divs = "municipalities",
	data = export.south_africa_provinces,
}

export.south_korea_provinces = {
	["North Chungcheong Province, South Korea"] = {},
	["South Chungcheong Province, South Korea"] = {},
	["Gangwon Province, South Korea"] = {wp = "%l, %c"},
	["Gyeonggi Province, South Korea"] = {},
	["North Gyeongsang Province, South Korea"] = {},
	["South Gyeongsang Province, South Korea"] = {},
	["North Jeolla Province, South Korea"] = {},
	["South Jeolla Province, South Korea"] = {},
	["Jeju Province, South Korea"] = {},
}

-- provinces of South Korea
export.south_korea_group = {
	key_to_placename = make_key_to_placename(", South Korea$", " Province$"),
	placename_to_key = make_placename_to_key(", South Korea", " Province"),
	default_container = "South Korea",
	default_placetype = "province",
	data = export.south_korea_provinces,
}

export.spain_autonomous_communities = {
	["Andalusia, Spain"] = {},
	["Aragon, Spain"] = {},
	["Asturias, Spain"] = {},
	["Balearic Islands, Spain"] = {the = true},
	["Basque Country, Spain"] = {the = true, wp = "%l (autonomous community)"},
	["Canary Islands, Spain"] = {the = true},
	["Cantabria, Spain"] = {},
	["Castile and León, Spain"] = {},
	["Castilla-La Mancha, Spain"] = {wp = "Castilla–La Mancha"}, -- with en-dash
	["Catalonia, Spain"] = {},
	["Community of Madrid, Spain"] = {the = true},
	["Extremadura, Spain"] = {},
	["Galicia, Spain"] = {wp = "%l (Spain)"},
	["La Rioja, Spain"] = {},
	["Murcia, Spain"] = {wp = "Region of %l"},
	["Navarre, Spain"] = {},
	["Valencia, Spain"] = {wp = "Valencian Community"},
	["Valencian Community, Spain"] = {alias_of = "Valencia, Spain", the = true},
}

-- autonomous communities of Spain
export.spain_group = {
	default_container = "Spain",
	default_placetype = "autonomous community",
	default_divs = {"municipalities", "comarcas"},
	data = export.spain_autonomous_communities,
}

export.taiwan_counties = {
	["Changhua County, Taiwan"] = {},
	["Chiayi County, Taiwan"] = {},
	["Hsinchu County, Taiwan"] = {},
	["Hualien County, Taiwan"] = {},
	["Kinmen County, Taiwan"] = {wp = "Kinmen"},
	["Lienchiang County, Taiwan"] = {wp = "Matsu Islands"},
	["Miaoli County, Taiwan"] = {},
	["Nantou County, Taiwan"] = {},
	["Penghu County, Taiwan"] = {wp = "Penghu"},
	["Pingtung County, Taiwan"] = {},
	["Taitung County, Taiwan"] = {},
	["Yilan County, Taiwan"] = {wp = "%l, %c"},
	["Yunlin County, Taiwan"] = {},
}

-- counties of Taiwan
export.taiwan_group = {
	key_to_placename = make_key_to_placename(", Taiwan$", " County$"),
	placename_to_key = make_placename_to_key(", Taiwan", " County"),
	default_container = "Taiwan",
	default_placetype = "county",
	default_divs = {"districts", "townships"},
	data = export.taiwan_counties,
}

export.thailand_provinces = {
	-- Bangkok (special administrative area)
	["Amnat Charoen Province, Thailand"] = {},
	["Ang Thong Province, Thailand"] = {},
	["Bueng Kan Province, Thailand"] = {},
	["Buriram Province, Thailand"] = {},
	["Chachoengsao Province, Thailand"] = {},
	["Chai Nat Province, Thailand"] = {},
	["Chaiyaphum Province, Thailand"] = {},
	["Chanthaburi Province, Thailand"] = {},
	["Chiang Mai Province, Thailand"] = {},
	["Chiang Rai Province, Thailand"] = {},
	["Chonburi Province, Thailand"] = {},
	["Chumphon Province, Thailand"] = {},
	["Kalasin Province, Thailand"] = {},
	["Kamphaeng Phet Province, Thailand"] = {},
	["Kanchanaburi Province, Thailand"] = {},
	["Khon Kaen Province, Thailand"] = {},
	["Krabi Province, Thailand"] = {},
	["Lampang Province, Thailand"] = {},
	["Lamphun Province, Thailand"] = {},
	["Loei Province, Thailand"] = {},
	["Lopburi Province, Thailand"] = {},
	["Mae Hong Son Province, Thailand"] = {},
	["Maha Sarakham Province, Thailand"] = {},
	["Mukdahan Province, Thailand"] = {},
	["Nakhon Nayok Province, Thailand"] = {},
	["Nakhon Pathom Province, Thailand"] = {},
	["Nakhon Phanom Province, Thailand"] = {},
	["Nakhon Ratchasima Province, Thailand"] = {},
	["Nakhon Sawon Province, Thailand"] = {},
	["Nakhon Si Thammarat Province, Thailand"] = {},
	["Nan Province, Thailand"] = {},
	["Narathiwat Province, Thailand"] = {},
	["Nong Bua Lamphu Province, Thailand"] = {},
	["Nong Khai Province, Thailand"] = {},
	["Nonthaburi Province, Thailand"] = {},
	["Pathum Thani Province, Thailand"] = {},
	["Pattani Province, Thailand"] = {},
	["Phang Nga Province, Thailand"] = {},
	["Phatthalung Province, Thailand"] = {},
	["Phayao Province, Thailand"] = {},
	["Phetchabun Province, Thailand"] = {},
	["Phetchaburi Province, Thailand"] = {},
	["Phichit Province, Thailand"] = {},
	["Phitsanulok Province, Thailand"] = {},
	["Phra Nakhon Si Ayutthaya Province, Thailand"] = {},
	["Phrae Province, Thailand"] = {},
	["Phuket Province, Thailand"] = {},
	["Prachinburi Province, Thailand"] = {},
	["Prachuap Khiri Khan Province, Thailand"] = {},
	["Ranong Province, Thailand"] = {},
	["Ratchaburi Province, Thailand"] = {},
	["Rayong Province, Thailand"] = {},
	["Roi Et Province, Thailand"] = {},
	["Sa Kaeo Province, Thailand"] = {},
	["Sakon Nakhon Province, Thailand"] = {},
	["Samut Prakan Province, Thailand"] = {},
	["Samut Sakhon Province, Thailand"] = {},
	["Samut Songkhram Province, Thailand"] = {},
	["Saraburi Province, Thailand"] = {},
	["Satun Province, Thailand"] = {},
	["Sing Buri Province, Thailand"] = {},
	["Sisaket Province, Thailand"] = {},
	["Songkhla Province, Thailand"] = {},
	["Sukhothai Province, Thailand"] = {},
	["Suphan Buri Province, Thailand"] = {},
	["Surat Thani Province, Thailand"] = {},
	["Surin Province, Thailand"] = {},
	["Tak Province, Thailand"] = {},
	["Trang Province, Thailand"] = {},
	["Trat Province, Thailand"] = {},
	["Ubon Ratchathani Province, Thailand"] = {},
	["Udon Thani Province, Thailand"] = {},
	["Uthai Thani Province, Thailand"] = {},
	["Uttaradit Province, Thailand"] = {},
	["Yala Province, Thailand"] = {},
	["Yasothon Province, Thailand"] = {},
}

-- provinces of Thailand
export.thailand_group = {
	key_to_placename = make_key_to_placename(", Thailand$", " Province$"),
	placename_to_key = make_placename_to_key(", Thailand", " Province"),
	default_container = "Thailand",
	default_placetype = "province",
	default_divs = "districts",
	-- For obscure reasons, provinces of Iran, Laos, Thailand and Vietnam use lowercase 'province'
	default_wp = "%e province",
	data = export.thailand_provinces,
}

export.turkey_provinces = {
	["Adana Province, Turkey"] = {}, -- code 01
	["Adıyaman Province, Turkey"] = {}, -- code 02
	["Afyonkarahisar Province, Turkey"] = {}, -- code 03
	["Ağrı Province, Turkey"] = {}, -- code 04
	["Amasya Province, Turkey"] = {}, -- code 05
	["Ankara Province, Turkey"] = {}, -- code 06
	["Antalya Province, Turkey"] = {}, -- code 07
	["Artvin Province, Turkey"] = {}, -- code 08
	["Aydın Province, Turkey"] = {}, -- code 09
	["Balıkesir Province, Turkey"] = {}, -- code 10
	["Bilecik Province, Turkey"] = {}, -- code 11
	["Bingöl Province, Turkey"] = {}, -- code 12
	["Bitlis Province, Turkey"] = {}, -- code 13
	["Bolu Province, Turkey"] = {}, -- code 14
	["Burdur Province, Turkey"] = {}, -- code 15
	["Bursa Province, Turkey"] = {}, -- code 16
	["Çanakkale Province, Turkey"] = {}, -- code 17
	["Çankırı Province, Turkey"] = {}, -- code 18
	["Çorum Province, Turkey"] = {}, -- code 19
	["Denizli Province, Turkey"] = {}, -- code 20
	["Diyarbakır Province, Turkey"] = {}, -- code 21
	["Edirne Province, Turkey"] = {}, -- code 22
	["Elazığ Province, Turkey"] = {}, -- code 23
	["Elâzığ Province, Turkey"] = {alias_of = "Elazığ Province, Turkey", display = true},
	["Erzincan Province, Turkey"] = {}, -- code 24
	["Erzurum Province, Turkey"] = {}, -- code 25
	["Eskişehir Province, Turkey"] = {}, -- code 26
	["Gaziantep Province, Turkey"] = {}, -- code 27
	["Giresun Province, Turkey"] = {}, -- code 28
	["Gümüşhane Province, Turkey"] = {}, -- code 29
	["Hakkâri Province, Turkey"] = {}, -- code 30
	["Hakkari Province, Turkey"] = {alias_of = "Hakkâri Province, Turkey", display = true},
	["Hatay Province, Turkey"] = {}, -- code 31
	["Isparta Province, Turkey"] = {}, -- code 32
	["Mersin Province, Turkey"] = {}, -- code 33
	-- ["Istanbul Province, Turkey"] = {}, -- code 34; this is coextensive with the city itself
	["İzmir Province, Turkey"] = {}, -- code 35
	["Izmir Province, Turkey"] = {alias_of = "İzmir Province, Turkey", display = true},
	["Kars Province, Turkey"] = {}, -- code 36
	["Kastamonu Province, Turkey"] = {}, -- code 37
	["Kayseri Province, Turkey"] = {}, -- code 38
	["Kırklareli Province, Turkey"] = {}, -- code 39
	["Kırşehir Province, Turkey"] = {}, -- code 40
	["Kocaeli Province, Turkey"] = {}, -- code 41
	["Konya Province, Turkey"] = {}, -- code 42
	["Kütahya Province, Turkey"] = {}, -- code 43
	["Malatya Province, Turkey"] = {}, -- code 44
	["Manisa Province, Turkey"] = {}, -- code 45
	["Kahramanmaraş Province, Turkey"] = {}, -- code 46
	["Mardin Province, Turkey"] = {}, -- code 47
	["Muğla Province, Turkey"] = {}, -- code 48
	["Muş Province, Turkey"] = {}, -- code 49
	["Nevşehir Province, Turkey"] = {}, -- code 50
	["Niğde Province, Turkey"] = {}, -- code 51
	["Ordu Province, Turkey"] = {}, -- code 52
	["Rize Province, Turkey"] = {}, -- code 53
	["Sakarya Province, Turkey"] = {}, -- code 54
	["Samsun Province, Turkey"] = {}, -- code 55
	["Siirt Province, Turkey"] = {}, -- code 56
	["Sinop Province, Turkey"] = {}, -- code 57
	["Sivas Province, Turkey"] = {}, -- code 58
	["Tekirdağ Province, Turkey"] = {}, -- code 59
	["Tokat Province, Turkey"] = {}, -- code 60
	["Trabzon Province, Turkey"] = {}, -- code 61
	["Tunceli Province, Turkey"] = {}, -- code 62
	["Şanlıurfa Province, Turkey"] = {}, -- code 63
	["Uşak Province, Turkey"] = {}, -- code 64
	["Van Province, Turkey"] = {}, -- code 65
	["Yozgat Province, Turkey"] = {}, -- code 66
	["Zonguldak Province, Turkey"] = {}, -- code 67
	["Aksaray Province, Turkey"] = {}, -- code 68
	["Bayburt Province, Turkey"] = {}, -- code 69
	["Karaman Province, Turkey"] = {}, -- code 70
	["Kırıkkale Province, Turkey"] = {}, -- code 71
	["Batman Province, Turkey"] = {}, -- code 72
	["Şırnak Province, Turkey"] = {}, -- code 73
	["Bartın Province, Turkey"] = {}, -- code 74
	["Ardahan Province, Turkey"] = {}, -- code 75
	["Iğdır Province, Turkey"] = {}, -- code 76
	["Yalova Province, Turkey"] = {}, -- code 77
	["Karabük Province, Turkey"] = {}, -- code 78
	["Kilis Province, Turkey"] = {}, -- code 79
	["Osmaniye Province, Turkey"] = {}, -- code 80
	["Düzce Province, Turkey"] = {}, -- code 81
}

-- provinces of Turkey
export.turkey_group = {
	key_to_placename = make_key_to_placename(", Turkey$", " Province$"),
	placename_to_key = make_placename_to_key(", Turkey", " Province"),
	default_container = "Turkey",
	default_placetype = "province",
	default_divs = "districts",
	data = export.turkey_provinces,
}

export.ukraine_oblasts = {
	["Cherkasy Oblast, Ukraine"] = {}, -- capital [[Cherkasy]], license plate prefix CA, IA
	["Chernihiv Oblast, Ukraine"] = {}, -- capital [[Chernihiv]], license plate prefix CB, IB
	["Chernivtsi Oblast, Ukraine"] = {}, -- capital [[Chernivtsi]], license plate prefix CE, IE
	-- apparently will be renamed to 'Dnipro Oblast'
	["Dnipropetrovsk Oblast, Ukraine"] = {}, -- capital [[Dnipro]], license plate prefix AE, KE
	["Donetsk Oblast, Ukraine"] = {}, -- capital ''[[Donetsk]] ([[Kramatorsk]])'', license plate prefix AH, KH
	["Ivano-Frankivsk Oblast, Ukraine"] = {}, -- capital [[Ivano-Frankivsk]], license plate prefix AT, KT
	["Kharkiv Oblast, Ukraine"] = {}, -- capital [[Kharkiv]], license plate prefix AX, KX
	["Kherson Oblast, Ukraine"] = {}, -- capital ''[[Kherson]]'', license plate prefix ''BT, HT''
	["Khmelnytskyi Oblast, Ukraine"] = {}, -- capital [[Khmelnytskyi]], license plate prefix BX, HX
	-- apparently will be renamed to 'Kropyvnytskyi Oblast'
	["Kirovohrad Oblast, Ukraine"] = {}, -- capital [[Kropyvnytskyi]], license plate prefix BA, HA
	["Kyiv Oblast, Ukraine"] = {}, -- capital [[Kyiv]], license plate prefix AI, KI
	["Kiev Oblast, Ukraine"] = {alias_of = "Kyiv Oblast, Ukraine", display = true},
	["Luhansk Oblast, Ukraine"] = {}, -- capital ''[[Luhansk]] ([[Sievierodonetsk]])'', license plate prefix BB, HB
	["Lviv Oblast, Ukraine"] = {}, -- capital [[Lviv]], license plate prefix BC, HC
	["Mykolaiv Oblast, Ukraine"] = {}, -- capital [[Mykolaiv]], license plate prefix BE, HE
	["Odesa Oblast, Ukraine"] = {}, -- capital [[Odesa]], license plate prefix BH, HH
	["Odessa Oblast, Ukraine"] = {alias_of = "Odesa Oblast, Ukraine", display = true},
	["Poltava Oblast, Ukraine"] = {}, -- capital [[Poltava]], license plate prefix BI, HI
	["Rivne Oblast, Ukraine"] = {}, -- capital [[Rivne]], license plate prefix BK, HK
	["Sumy Oblast, Ukraine"] = {}, -- capital [[Sumy]], license plate prefix BM, HM
	["Ternopil Oblast, Ukraine"] = {}, -- capital [[Ternopil]], license plate prefix BO, HO
	["Vinnytsia Oblast, Ukraine"] = {}, -- capital [[Vinnytsia]], license plate prefix AB, KB
	["Volyn Oblast, Ukraine"] = {}, -- capital [[Lutsk]], license plate prefix AC, KC
	["Zakarpattia Oblast, Ukraine"] = {}, -- capital [[Uzhhorod]], license plate prefix AO, KO
	["Zaporizhzhia Oblast, Ukraine"] = {}, -- capital ''[[Zaporizhzhia]]'', license plate prefix AP, KP
	["Zaporizhia Oblast, Ukraine"] = {alias_of = "Zaporizhzhia Oblast, Ukraine", display = true},
	["Zhytomyr Oblast, Ukraine"] = {}, -- capital [[Zhytomyr]], license plate prefix AM, KM
}

-- oblasts of Ukraine
export.ukraine_group = {
	key_to_placename = make_key_to_placename(", Ukraine$", " Oblast$"),
	placename_to_key = make_placename_to_key(", Ukraine", " Oblast"),
	default_container = "Ukraine",
	default_placetype = "oblast",
	default_divs = {"raions", "hromadas"},
	data = export.ukraine_oblasts,
}

export.united_kingdom_constituent_countries = {
	["England"] = {divs = {
		"counties",
		"districts",
		{type = "local government districts", cat_as = "districts"},
		{
			type = "local government districts with borough status",
			cat_as = {"districts", "boroughs"},
		},
		{type = "boroughs", cat_as = {"districts", "boroughs"}},
		{type = "civil parishes", container_parent_type = false},
	}},
	["Northern Ireland"] = {
		placetype = {"constituent country", "province", "country"},
		divs = {"counties", "districts"},
	},
	["Scotland"] = {divs = {
		{type = "council areas", container_parent_type = false},
		"districts",
	}},
	["Wales"] = {divs = {
		"counties",
		{type = "county boroughs", container_parent_type = false},
		{type = "communities", container_parent_type = false},
		{type = "Welsh communities", cat_as = {{type = "communities", container_parent_type = false}}},
	}},
}

-- constituent countries and provinces of the United Kingdom
export.united_kingdom_group = {
	placename_to_key = false,
	default_container = "United Kingdom",
	default_placetype = {"constituent country", "country"},
	addl_divs = {
		"traditional counties",
		{type = "historical counties", cat_as = "traditional counties"},
	},
	-- Don't create categories like 'Category:en:Towns in the United Kingdom'
	-- or 'Category:en:Places in the United Kingdom'.
	default_no_container_cat = true,
	data = export.united_kingdom_constituent_countries,
}

export.england_counties = {
	-- NOTE: We used to have various other "no longer" counties commented out, which seems to refer to counties that
	-- existed officially at some point between 1889 and 1974, which I have removed. I have only kept the three
	-- ceremonial counties that existed from 1974 (when ceremonial counties were created) to 1996, as well as those
	-- still considered "historic counties" per [[w:Historic counties of England]].
	-- ["Avon, England"] = {wp = "%l (county)"}, -- no longer (1974 to 1996)
	["Bedfordshire, England"] = {},
	["Berkshire, England"] = {},
	-- ["Brighton and Hove, England"] = {}, -- city
	-- ["Bristol, England"] = {}, -- city
	["Buckinghamshire, England"] = {},
	["Cambridgeshire, England"] = {},
	["Cheshire, England"] = {},
	-- ["Cleveland, England"] = {wp = "%l (county)"}, -- no longer (1974 to 1996)
	["Cornwall, England"] = {},
	-- ["Cumberland, England"] = {}, -- no longer (historic county)
	["Cumbria, England"] = {},
	["Derbyshire, England"] = {},
	["Devon, England"] = {},
	["Dorset, England"] = {},
	["County Durham, England"] = {},
	["East Sussex, England"] = {},
	["Essex, England"] = {},
	["Gloucestershire, England"] = {},
	["Greater London, England"] = {},
	["Greater Manchester, England"] = {},
	["Hampshire, England"] = {},
	["Herefordshire, England"] = {},
	["Hertfordshire, England"] = {},
	-- ["Humberside, England"] = {}, -- no longer (1974 to 1996)
	-- ["Huntingdonshire, England"] = {}, -- no longer (historic county)
	["Isle of Wight, England"] = {the = true},
	["Kent, England"] = {},
	["Lancashire, England"] = {},
	["Leicestershire, England"] = {},
	["Lincolnshire, England"] = {},
	["Merseyside, England"] = {},
	-- ["Middlesex, England"] = {}, -- no longer (historic county)
	["Norfolk, England"] = {},
	["Northamptonshire, England"] = {},
	["Northumberland, England"] = {},
	["North Yorkshire, England"] = {},
	["Nottinghamshire, England"] = {},
	["Oxfordshire, England"] = {},
	["Rutland, England"] = {},
	["Shropshire, England"] = {},
	["Somerset, England"] = {},
	["South Humberside, England"] = {},
	["South Yorkshire, England"] = {},
	["Staffordshire, England"] = {},
	["Suffolk, England"] = {},
	["Surrey, England"] = {},
	-- ["Sussex, England"] = {}, -- no longer (historic county)
	["Tyne and Wear, England"] = {},
	["Warwickshire, England"] = {},
	["West Midlands, England"] = {the = true, wp = "%l (county)"},
	-- ["Westmorland, England"] = {}, -- no longer (historic county)
	["West Sussex, England"] = {},
	["West Yorkshire, England"] = {},
	["Wiltshire, England"] = {},
	["Worcestershire, England"] = {},
	-- ["Yorkshire, England"] = {}, -- no longer (historic county)
	["East Riding of Yorkshire, England"] = {the = true},
}

-- counties of England
export.england_group = {
	default_container = {key = "England", placetype = "constituent country"},
	default_placetype = "county",
	default_divs = {
		"districts",
		{type = "local government districts", cat_as = "districts"},
		{
			type = "local government districts with borough status",
			cat_as = {"districts", "boroughs"},
		},
		{type = "boroughs", cat_as = {"districts", "boroughs"}},
		"civil parishes",
	},
	data = export.england_counties,
}

export.northern_ireland_counties = {
	["County Antrim, Northern Ireland"] = {},
	["County Armagh, Northern Ireland"] = {},
	["City of Belfast, Northern Ireland"] = {the = true, is_city = true, wp = "Belfast"},
	["County Down, Northern Ireland"] = {},
	["County Fermanagh, Northern Ireland"] = {},
	["County Londonderry, Northern Ireland"] = {},
	["City of Derry, Northern Ireland"] = {the = true, is_city = true, wp = "Derry"},
	["County Tyrone, Northern Ireland"] = {},
}

-- counties of Northern Ireland
export.northern_ireland_group = {
	key_to_placename = make_irish_type_key_to_placename(", Northern Ireland$"),
	placename_to_key = make_irish_type_placename_to_key(", Northern Ireland"),
	default_container = {key = "Northern Ireland", placetype = "constituent country"},
	default_placetype = "county",
	data = export.northern_ireland_counties,
}

export.scotland_council_areas = {
	["Aberdeenshire, Scotland"] = {},
	["Angus, Scotland"] = {wp = "%l, %c"},
	["Argyll and Bute, Scotland"] = {},
	["City of Aberdeen, Scotland"] = {the = true, wp = "Aberdeen"},
	["Aberdeen"] = {alias_of = "City of Aberdeen, Scotland"},
	["Aberdeen City"] = {alias_of = "City of Aberdeen, Scotland"},
	["City of Dundee, Scotland"] = {the = true, wp = "Dundee"},
	["Dundee"] = {alias_of = "City of Dundee, Scotland"},
	["Dundee City"] = {alias_of = "City of Dundee, Scotland"},
	["City of Edinburgh, Scotland"] = {the = true, wp = "%l council area"},
	["Edinburgh"] = {alias_of = "City of Edinburgh, Scotland"},
	["City of Glasgow, Scotland"] = {the = true, wp = "Glasgow"},
	["Glasgow"] = {alias_of = "City of Glasgow, Scotland"},
	["Clackmannanshire, Scotland"] = {},
	["Dumfries and Galloway, Scotland"] = {},
	["East Ayrshire, Scotland"] = {},
	["East Dunbartonshire, Scotland"] = {},
	["East Lothian, Scotland"] = {},
	["East Renfrewshire, Scotland"] = {},
	["Falkirk, Scotland"] = {wp = "%l council area"},
	["Fife, Scotland"] = {},
	["Highland, Scotland"] = {wp = "%l council area"},
	["Inverclyde, Scotland"] = {},
	["Midlothian, Scotland"] = {},
	["Moray, Scotland"] = {},
	["North Ayrshire, Scotland"] = {},
	["North Lanarkshire, Scotland"] = {},
	["Orkney Islands, Scotland"] = {the = true},
	["Perth and Kinross, Scotland"] = {},
	["Renfrewshire, Scotland"] = {},
	["Scottish Borders, Scotland"] = {the = true},
	["Shetland Islands, Scotland"] = {the = true},
	["South Ayrshire, Scotland"] = {},
	["South Lanarkshire, Scotland"] = {},
	["Stirling, Scotland"] = {wp = "%l council area"},
	["West Dunbartonshire, Scotland"] = {},
	["West Lothian, Scotland"] = {},
	["Western Isles, Scotland"] = {the = true, wp = "Outer Hebrides"},
	["Na h-Eileanan Siar, Scotland"] = {alias_of = "Western Isles, Scotland"},
}

-- council areas of Scotland
export.scotland_group = {
	default_container = {key = "Scotland", placetype = "constituent country"},
	default_placetype = "council area",
	data = export.scotland_council_areas,
}

export.wales_principal_areas = {
	["Blaenau Gwent, Wales"] = {},
	["Bridgend, Wales"] = {wp = "%l County Borough"},
	["Caerphilly, Wales"] = {wp = "%l County Borough"},
	-- ["Cardiff, Wales"] = {placetype = "city"},
	["Carmarthenshire, Wales"] = {placetype = "county"},
	["Ceredigion, Wales"] = {placetype = "county"},
	["Conwy, Wales"] = {wp = "%l County Borough"},
	["Denbighshire, Wales"] = {placetype = "county"},
	["Flintshire, Wales"] = {placetype = "county"},
	["Gwynedd, Wales"] = {placetype = "county"},
	["Isle of Anglesey, Wales"] = {the = true, placetype = "county"},
	["Anglesey, Wales"] = {alias_of = "Isle of Anglesey, Wales"}, -- differs in "the"
	["Merthyr Tydfil, Wales"] = {wp = "%l County Borough"},
	["Monmouthshire, Wales"] = {placetype = "county"},
	["Neath Port Talbot, Wales"] = {},
	-- ["Newport, Wales"] = {placetype = "city", wp = "%l, %c"},
	["Pembrokeshire, Wales"] = {placetype = "county"},
	["Powys, Wales"] = {placetype = "county"},
	["Rhondda Cynon Taf, Wales"] = {},
	-- ["Swansea, Wales"] = {placetype = "city"},
	["Torfaen, Wales"] = {},
	["Vale of Glamorgan, Wales"] = {the = true},
	["Wrexham, Wales"] = {wp = "%l County Borough"},
}

-- principal areas (cities, counties and county boroughs) of Wales
export.wales_group = {
	default_container = {key = "Wales", placetype = "constituent country"},
	default_placetype = "county borough",
	data = export.wales_principal_areas,
}

export.united_states_states = {
	["Alabama, USA"] = {},
	["Alaska, USA"] = {divs = {
		{type = "boroughs", container_parent_type = "counties"},
		{type = "borough seats", container_parent_type = "county seats"},
	}},
	["Arizona, USA"] = {},
	["Arkansas, USA"] = {},
	["California, USA"] = {},
	["Colorado, USA"] = {divs = {"counties", "county seats", "municipalities"}},
	["Connecticut, USA"] = {divs = {"counties", "county seats", "municipalities"}},
	["Delaware, USA"] = {},
	["Florida, USA"] = {},
	["Georgia, USA"] = {wp = "%l (U.S. state)"},
	["Hawaii, USA"] = {addl_parents = {"Polynesia"}},
	["Idaho, USA"] = {},
	["Illinois, USA"] = {},
	["Indiana, USA"] = {},
	["Iowa, USA"] = {},
	["Kansas, USA"] = {},
	["Kentucky, USA"] = {},
	["Louisiana, USA"] = {divs = {
		{type = "parishes", container_parent_type = "counties"},
		{type = "parish seats", container_parent_type = "county seats"},
	}},
	["Maine, USA"] = {},
	["Maryland, USA"] = {},
	["Massachusetts, USA"] = {},
	["Michigan, USA"] = {},
	["Minnesota, USA"] = {},
	["Mississippi, USA"] = {},
	["Missouri, USA"] = {},
	["Montana, USA"] = {},
	["Nebraska, USA"] = {},
	["Nevada, USA"] = {},
	["New Hampshire, USA"] = {},
	["New Jersey, USA"] = {divs = {
		"counties", "county seats",
		{type = "boroughs", prep = "in"},
	}},
	["New Mexico, USA"] = {},
	["New York, USA"] = {wp = "%l (state)"},
	["North Carolina, USA"] = {},
	["North Dakota, USA"] = {},
	["Ohio, USA"] = {},
	["Oklahoma, USA"] = {},
	["Oregon, USA"] = {},
	["Pennsylvania, USA"] = {divs = {
		"counties", "county seats",
		{type = "boroughs", prep = "in"},
	}},
	["Rhode Island, USA"] = {},
	["South Carolina, USA"] = {},
	["South Dakota, USA"] = {},
	["Tennessee, USA"] = {},
	["Texas, USA"] = {},
	["Utah, USA"] = {},
	["Vermont, USA"] = {},
	["Virginia, USA"] = {},
	["Washington, USA"] = {wp = "%l (state)"},
	["West Virginia, USA"] = {},
	["Wisconsin, USA"] = {},
	["Wyoming, USA"] = {},
}

-- states of the United States
export.united_states_group = {
	placename_to_key = make_placename_to_key(", USA"),
	default_container = "United States",
	default_placetype = "state",
	default_divs = {"counties", "county seats"},
	addl_divs = {
		{type = "census-designated places", prep = "in"},
		{type = "unincorporated communities", prep = "in"},
	},
	data = export.united_states_states,
}

export.vietnam_provinces = {
	-- [[Northeast (Vietnam)|Northeast]] region
	["Bắc Giang Province, Vietnam"] = {}, -- capital [[Bắc Giang]]
	["Bắc Kạn Province, Vietnam"] = {}, -- capital [[Bắc Kạn]]
	["Cao Bằng Province, Vietnam"] = {}, -- capital [[Cao Bằng]]
	["Hà Giang Province, Vietnam"] = {}, -- capital [[Hà Giang]]
	["Lạng Sơn Province, Vietnam"] = {}, -- capital [[Lạng Sơn]]
	["Phú Thọ Province, Vietnam"] = {}, -- capital [[Việt Trì]]
	["Quảng Ninh Province, Vietnam"] = {}, -- capital [[Hạ Long]]
	["Thái Nguyên Province, Vietnam"] = {}, -- capital [[Thái Nguyên]]
	["Tuyên Quang Province, Vietnam"] = {}, -- capital [[Tuyên Quang]]

	-- [[Northwest (Vietnam)|Northwest]] region
	["Lào Cai Province, Vietnam"] = {}, -- capital [[Lào Cai]]
	["Yên Bái Province, Vietnam"] = {}, -- capital [[Yên Bái]]
	["Điện Biên Province, Vietnam"] = {}, -- capital [[Điện Biên Phủ]]
	["Hoà Bình Province, Vietnam"] = {}, -- capital [[Hoà Bình City|Hoà Bình]]
	["Hòa Bình Province, Vietnam"] = {alias_of = "Hoà Bình Province, Vietnam", display = true},
	["Lai Châu Province, Vietnam"] = {}, -- capital [[Lai Châu]]
	["Sơn La Province, Vietnam"] = {}, -- capital [[Sơn La]]

	-- [[Red River Delta]] region
	["Bắc Ninh Province, Vietnam"] = {}, -- capital [[Bắc Ninh]]
	["Hà Nam Province, Vietnam"] = {}, -- capital [[Phủ Lý]]
	["Hải Dương Province, Vietnam"] = {}, -- capital [[Hải Dương]]
	["Hưng Yên Province, Vietnam"] = {}, -- capital [[Hưng Yên]]
	["Nam Định Province, Vietnam"] = {}, -- capital [[Nam Định]]
	["Ninh Bình Province, Vietnam"] = {}, -- capital [[Ninh Bình|Hoa Lư]]
	["Thái Bình Province, Vietnam"] = {}, -- capital [[Thái Bình]]
	["Vĩnh Phúc Province, Vietnam"] = {}, -- capital [[Vĩnh Yên]]
	-- ["Hanoi"] = {placetype = {"municipality", "city"}}, -- capital [[Hoàn Kiếm district]]
	-- ["Haiphong"] = {placetype = {"municipality", "city"}}, -- capital [[Hồng Bàng district]]

	-- [[North Central Coast]] region
	["Hà Tĩnh Province, Vietnam"] = {}, -- capital [[Hà Tĩnh]]
	["Nghệ An Province, Vietnam"] = {}, -- capital [[Vinh]]
	["Quảng Bình Province, Vietnam"] = {}, -- capital [[Đồng Hới]]
	["Quảng Trị Province, Vietnam"] = {}, -- capital [[Đông Hà]]
	["Thanh Hoá Province, Vietnam"] = {}, -- capital [[Thanh Hoá]]
	["Thanh Hóa Province, Vietnam"] = {alias_of = "Thanh Hoá Province, Vietnam", display = true},
	-- ["Hue"] = {placetype = {"municipality", "city"}, wp = "Huế"}, -- capital [[Thuận Hoá district]]

	-- [[Central Highlands (Vietnam)|Central Highlands]] region
	["Đắk Lắk Province, Vietnam"] = {}, -- capital [[Buôn Ma Thuột]]
	["Đăk Nông Province, Vietnam"] = {}, -- capital [[Gia Nghĩa]]
	["Gia Lai Province, Vietnam"] = {}, -- capital [[Pleiku]]
	["Kon Tum Province, Vietnam"] = {}, -- capital [[Kon Tum]]
	["Lâm Đồng Province, Vietnam"] = {}, -- capital [[Đà Lạt]]

	-- [[South Central Coast]] region
	["Bình Định Province, Vietnam"] = {}, -- capital [[Quy Nhon]]
	["Bình Thuận Province, Vietnam"] = {}, -- capital [[Phan Thiết]]
	["Khánh Hoà Province, Vietnam"] = {}, -- capital [[Nha Trang]]
	["Khánh Hòa Province, Vietnam"] = {alias_of = "Khánh Hoà Province, Vietnam", display = true},
	["Ninh Thuận Province, Vietnam"] = {}, -- capital [[Phan Rang–Tháp Chàm]]
	["Phú Yên Province, Vietnam"] = {}, -- capital [[Tuy Hoà]]
	["Quảng Nam Province, Vietnam"] = {}, -- capital [[Tam Kỳ]]
	["Quảng Ngãi Province, Vietnam"] = {}, -- capital [[Quảng Ngãi]]
	-- ["Da Nang"] = {placetype = {"municipality", "city"}}, -- capital [[Hải Châu district]]

	-- [[Southeast (Vietnam)|Southeast]] region
	["Bà Rịa–Vũng Tàu Province, Vietnam"] = {}, -- capital [[Bà Rịa]]
	["Bình Dương Province, Vietnam"] = {}, -- capital [[Thủ Dầu Một]]
	["Bình Phước Province, Vietnam"] = {}, -- capital [[Đồng Xoài]]
	["Đồng Nai Province, Vietnam"] = {}, -- capital [[Biên Hoà]]
	["Tây Ninh Province, Vietnam"] = {}, -- capital [[Tây Ninh]]
	-- ["Ho Chi Minh City"] = {placetype = {"municipality", "city"}}, -- capital [[District 1, Ho Chi Minh City|'''District 1''']]

	-- [[Mekong Delta]] region
	["An Giang Province, Vietnam"] = {}, -- capital [[Long Xuyên]]
	["Bạc Liêu Province, Vietnam"] = {}, -- capital [[Bạc Liêu]]
	["Bến Tre Province, Vietnam"] = {}, -- capital [[Bến Tre]]
	["Cà Mau Province, Vietnam"] = {}, -- capital [[Cà Mau]]
	["Đồng Tháp Province, Vietnam"] = {}, -- capital [[Cao Lãnh City|Cao Lãnh]]
	["Hậu Giang Province, Vietnam"] = {}, -- capital [[Vị Thanh]]
	["Kiên Giang Province, Vietnam"] = {}, -- capital [[Rạch Giá]]
	["Long An Province, Vietnam"] = {}, -- capital [[Tân An]]
	["Sóc Trăng Province, Vietnam"] = {}, -- capital [[Sóc Trăng]]
	["Tiền Giang Province, Vietnam"] = {}, -- capital [[Mỹ Tho]]
	["Trà Vinh Province, Vietnam"] = {}, -- capital [[Trà Vinh]]
	["Vĩnh Long Province, Vietnam"] = {}, -- capital [[Vĩnh Long]]
	-- ["Can Tho"] = {placetype = {"municipality", "city"}, wp = "Cần Thơ"}, -- capital [[Ninh Kiều district]]
}

-- provinces of Vietnam
export.vietnam_group = {
	key_to_placename = make_key_to_placename(", Vietnam$", " Province$"),
	placename_to_key = make_placename_to_key(", Vietnam", " Province"),
	default_container = "Vietnam",
	default_placetype = "province",
	-- There may not be enough districts to subcategorize like this.
	-- default_divs = "districts",
	-- For obscure reasons, provinces of Iran, Laos, Thailand and Vietnam use lowercase 'province'
	default_wp = "%e province",
	data = export.vietnam_provinces,
}


-----------------------------------------------------------------------------------
--                                      City data                                --
-----------------------------------------------------------------------------------

export.australia_cities = {
	["Adelaide"] = {container = "South Australia"}, -- 1,450,000 (Agglomeration)
	["Brisbane"] = {container = "Queensland"}, -- 3,450,000 (Conglomeration; including the Gold Coast [750,997 2024 estiamte])
	["Canberra"] = {container = {key = "Australian Capital Territory, Australia", placetype = "territory"}}, -- 510,641 (2024 estimate)
	["Melbourne"] = {container = "Victoria"}, -- 5,200,000 (Agglomeration)
	["Newcastle, New South Wales"] = {container = "New South Wales", wp = "%l, %c"}, -- 534,033 (2024 estimate)
	["Newcastle"] = {alias_of = "Newcastle, New South Wales"},
	["Perth"] = {container = "Western Australia"}, -- 2,350,000 (Agglomeration)
	["Sydney"] = {container = "New South Wales"}, -- 5,100,000 (Agglomeration)
}

export.australia_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Australia", "state"),
	default_placetype = "city",
	data = export.australia_cities,
}

export.brazil_cities = {
	-- Figures from citypopulation.de; retrieved 2025-04-27; reference date 2025-01-01.
	["São Paulo"] = {container = "São Paulo"}, -- 22,600,000 (Consolidated Urban Area; including Guarulhos)
	["Sao Paulo"] = {alias_of = "São Paulo", display = true},
	["Rio de Janeiro"] = {container = "Rio de Janeiro"}, -- 13,600,000 (Consolidated Urban Area)
	["Belo Horizonte"] = {container = "Minas Gerais"}, -- 5,300,000
	["Recife"] = {container = "Pernambuco"}, -- 4,100,000
	["Porto Alegre"] = {container = "Rio Grande do Sul"}, -- 3,950,000 (Consolidated Urban Area)
	["Brasília"] = {container = "Distrito Federal"}, -- 3,850,000
	["Brasilia"] = {alias_of = "Brasília", display = true},
	["Fortaleza"] = {container = "Ceará"}, -- 3,825,000
	["Salvador"] = {container = "Bahia", wp = "%l, %c", commonscat = "%l (%c)"}, -- 3,400,000
	["Curitiba"] = {container = "Paraná"}, -- 3,375,000
	["Campinas"] = {container = "São Paulo"}, -- 3,250,000
	["Goiânia"] = {container = "Goiás"}, -- 2,525,000
	["Goiania"] = {alias_of = "Goiânia", display = true},
	["Manaus"] = {container = "Amazonas"}, -- 2,275,000
	["Belém"] = {container = "Pará"}, -- 2,200,000
	["Belem"] = {alias_of = "Belém", display = true},
	["Vitória"] = {container = "Espírito Santo", wp = "%l, %c"}, -- 1,870,000
	["Vitoria"] = {alias_of = "Vitória", display = true},
	["Santos"] = {container = "São Paulo", wp = "%l, %c"}, -- 1,760,000
	["São Luís"] = {container = "Maranhão", wp = "%l, %c"}, -- 1,530,000
	["Sao Luis"] = {alias_of = "São Luís", display = true},
	["Natal"] = {container = "Rio Grande do Norte", wp = "%l, %c"}, -- 1,360,000
	["Florianópolis"] = {container = "Santa Catarina"}, -- 1,260,000
	["Florianopolis"] = {alias_of = "Florianópolis", display = true},
	["Maceió"] = {container = "Alagoas"}, -- 1,220,000
	["Maceio"] = {alias_of = "Maceió", display = true},
	["João Pessoa"] = {container = "Paraíba", wp = "%l, %c"}, -- 1,210,000
	["Joao Pessoa"] = {alias_of = "João Pessoa", display = true},
	["São José dos Campos"] = {container = "São Paulo"}, -- 1,090,000
	["Sao Jose dos Campos"] = {alias_of = "São José dos Campos", display = true},
	["Londrina"] = {container = "Paraná"}, -- 1,050,000
	["Teresina"] = {container = "Piauí"}, -- 1,040,000
}

export.brazil_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Brazil", "state"),
	default_placetype = "city",
	data = export.brazil_cities,
}

export.canada_cities = {
	-- Figures from citypopulation.de; retrieved 2025-04-27; reference date 2025-01-01.
	["Toronto"] = {container = "Ontario"}, -- 7,850,000 (Consolidated Urban Area; including Hamilton)
	["Montreal"] = {container = "Quebec"}, -- 4,500,000 (Consolidated Urban Area)
	["Vancouver"] = {container = "British Columbia"}, -- 3,175,000 (Consolidated Urban Area)
	["Calgary"] = {container = "Alberta"}, -- 1,510,000 (Consolidated Urban Area)
	["Edmonton"] = {container = "Alberta"}, -- 1,460,000 (Consolidated Urban Area)
	["Ottawa"] = {container = "Ontario"}, -- 1,390,000 (Consolidated Urban Area)
	["Quebec City"] = {container = "Quebec"}, -- 839,311 metro per Wikipedia (2021 census)
	["Winnipeg"] = {container = "Manitoba"}, -- 834,678 metro per Wikipedia (2021 census)
	["Hamilton"] = {container = "Ontario", wp = "%l, %c"}, -- 785,184 metro per Wikipedia (2021 census)
	["Kitchener"] = {container = "Ontario", wp = "%l, %c"}, -- 575,847 metro per Wikipedia (2021 census)
}

export.canada_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Canada", "province"),
	default_placetype = "city",
	data = export.canada_cities,
}

export.france_cities = {
	-- Figures from citypopulation.de unless otherwise indicated; retrieved 2025-04-26; reference date 2025-01-01.
	["Paris"] = {container = "Île-de-France"}, -- 11,500,000 (Conglomeration)
	["Lyon"] = {container = "Auvergne-Rhône-Alpes"}, -- 2,050,000 (Conglomeration)
	["Lyons"] = {alias_of = "Lyon", display = true},
	["Marseille"] = {container = "Provence-Alpes-Côte d'Azur"}, -- 1,710,000 (Conglomeration)
	["Marseilles"] = {alias_of = "Marseille", display = true},
	["Lille"] = {container = "Hauts-de-France"}, -- 1,320,000 (Conglomeration)
	["Bordeaux"] = {container = "Nouvelle-Aquitaine"}, -- 1,160,000 (Conglomeration)
	["Toulouse"] = {container = "Occitania"}, -- 1,150,000 (Conglomeration)
	["Nice"] = {container = "Provence-Alpes-Côte d'Azur"},
	["Nantes"] = {container = "Pays de la Loire"},
	["Strasbourg"] = {container = "Grand Est"},
	["Rennes"] = {container = "Brittany"},
}

export.france_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", France", "region"),
	default_placetype = "city",
	data = export.france_cities,
}

export.germany_cities = {
	-- Figures from citypopulation.de unless otherwise indicated; retrieved 2025-04-26; reference date 2025-01-01.
	-- listed under Rhein-Ruhr Area, total population 10,900,000 (Consolidated Urban Area)
	["Cologne"] = {container = "North Rhine-Westphalia"},
	["Köln"] = {alias_of = "Cologne", display = true},
	["Düsseldorf"] = {container = "North Rhine-Westphalia"},
	["Dusseldorf"] = {alias_of = "Düsseldorf", display = true},
	["Dortmund"] = {container = "North Rhine-Westphalia"},
	["Essen"] = {container = "North Rhine-Westphalia"},
	["Duisberg"] = {container = "North Rhine-Westphalia"},
	["Berlin"] = {}, -- 4,700,000
	["Frankfurt"] = {container = "Hesse"}, -- 3,225,000
	["Frankfurt am Main"] = {alias_of = "Frankfurt"}, -- not a display alias as it's longer
	["Hamburg"] = {}, -- 2,900,000
	["Munich"] = {container = "Bavaria"}, -- 2,300,000
	["Stuttgart"] = {container = "Baden-Württemberg"}, -- 2,300,000
	["Mannheim"] = {container = "Baden-Württemberg"}, -- 1,550,000
	["Nuremberg"] = {container = "Bavaria"}, -- 1,120,000
	["Hanover"] = {"Lower Saxony"}, -- 1,090,000
	["Bielefeld"] = {container = "North Rhine-Westphalia"}, -- 1,080,000
	["Leipzig"] = {container = "Saxony"}, -- 1,080,000
	["Aachen"] = {container = "North Rhine-Westphalia"}, -- 1,000,000
	["Aix-la-Chapelle"] = {alias_of = "Aachen"}, -- historical; not a display alias
	["Bremen"] = {},
}

export.germany_cities_group = {
	default_container = "Germany",
	canonicalize_key_container = make_canonicalize_key_container(", Germany", "state"),
	default_placetype = "city",
	data = export.germany_cities,
}

export.india_cities = {
	-- This lists the 65 metro areas per Demographia's 2023 estimates, as found in
	-- [[w:List_of_million-plus_urban_agglomerations_in_India]]. The last census in India (as of April 2025) was
	-- conducted in 2011, and the results are not accurate any more.
	["Delhi"] = {container = {key = "Delhi, India", placetype = "union territory"}}, -- 31,190,000
	["Mumbai"] = {container = "Maharashtra"}, -- 25,189,000
	["Kolkata"] = {container = "West Bengal"}, -- 21,747,000
	["Bangalore"] = {container = "Karnataka", wp = "Bengaluru"}, -- 15,257,000
	["Bengaluru"] = {alias_of = "Bangalore"},
	["Chennai"] = {container = "Tamil Nadu"}, -- 11,570,000
	["Hyderabad"] = {container = "Telangana"}, -- 9,797,000
	["Ahmedabad"] = {container = "Gujarat"}, -- 8,006,000
	["Pune"] = {container = "Maharashtra"}, -- 6,819,000
	["Surat"] = {container = "Gujarat"}, -- 6,601,000
	["Lucknow"] = {container = "Uttar Pradesh"}, -- 4,661,000
	["Jaipur"] = {container = "Rajasthan"}, -- 4,360,000
	["Kanpur"] = {container = "Uttar Pradesh"}, -- 4,350,000
	["Indore"] = {container = "Madhya Pradesh"}, -- 3,765,000
	["Nagpur"] = {container = "Maharashtra"}, -- 3,493,000
	["Patna"] = {container = "Bihar"}, -- 3,331,000
	["Varanasi"] = {container = "Uttar Pradesh"}, -- 3,229,000
	["Kozhikode"] = {container = "Kerala"}, -- 3,049,000
	["Thiruvananthapuram"] = {container = "Kerala"}, -- 2,851,000
	["Agra"] = {container = "Uttar Pradesh"}, -- 2,737,000
	["Bhopal"] = {container = "Madhya Pradesh"}, -- 2,562,000
	["Coimbatore"] = {container = "Tamil Nadu"}, -- 2,551,000
	["Allahabad"] = {container = "Uttar Pradesh", wp = "Prayagraj"}, -- 2,438,000
	["Prayagraj"] = {alias_of = "Allahabad"},
	["Kochi"] = {container = "Kerala"}, -- 2,381,000
	["Ludhiana"] = {container = "Punjab"}, -- 2,205,000
	["Vadodara"] = {container = "Gujarat"}, -- 2,182,000
	["Chandigarh"] = {container = {key = "Chandigarh, India", placetype = "union territory"}}, -- 2,168,000
	["Madurai"] = {container = "Tamil Nadu"}, -- 2,048,000
	["Meerut"] = {container = "Uttar Pradesh"}, -- 2,011,000
	["Visakhapatnam"] = {container = "Andhra Pradesh"}, -- 2,005,000
	["Jamshedpur"] = {container = "Jharkhand"}, -- 1,925,000
	["Malappuram"] = {container = "Kerala"}, -- 1,868,000
	["Nashik"] = {container = "Maharashtra"}, -- 1,810,000
	["Asansol"] = {container = "West Bengal"}, -- 1,720,000
	["Aligarh"] = {container = "Uttar Pradesh"}, -- 1,660,000
	["Ranchi"] = {container = "Jharkhand"}, -- 1,638,000
	["Thrissur"] = {container = "Kerala"}, -- 1,578,000
	["Kollam"] = {container = "Kerala"}, -- 1,576,000
	["Jabalpur"] = {container = "Madhya Pradesh"}, -- 1,533,000
	["Dhanbad"] = {container = "Jharkhand"}, -- 1,503,000
	["Jodhpur"] = {container = "Rajasthan"}, -- 1,497,000
	["Aurangabad"] = {container = "Maharashtra"}, -- 1,490,000
	["Chhatrapati Sambhajinagar"] = {alias_of = "Aurangabad"},
	["Rajkot"] = {container = "Gujarat"}, -- 1,487,000
	["Gwalior"] = {container = "Madhya Pradesh"}, -- 1,477,000
	["Raipur"] = {container = "Chhattisgarh"}, -- 1,429,000
	["Gorakhpur"] = {container = "Uttar Pradesh"}, -- 1,410,000
	["Kannur"] = {container = "Kerala"}, -- 1,360,000
	["Bareilly"] = {container = "Uttar Pradesh"}, -- 1,355,000
	["Guwahati"] = {container = "Assam"}, -- 1,355,000
	["Moradabad"] = {container = "Uttar Pradesh"}, -- 1,345,000
	["Amritsar"] = {container = "Punjab"}, -- 1,313,000
	["Mysore"] = {container = "Karnataka"}, -- 1,296,000
	["Bhilai"] = {container = "Chhattisgarh"}, -- 1,293,000
	["Durg-Bhilainagar"] = {alias_of = "Bhilai"},
	["Durg-Bhilai"] = {alias_of = "Bhilai"},
	["Durg"] = {alias_of = "Bhilai"},
	["Bhilainagar"] = {alias_of = "Bhilai"},
	["Vijayawada"] = {container = "Andhra Pradesh"}, -- 1,232,000
	["Srinagar"] = {container = {key = "Jammu and Kashmir, India", placetype = "union territory"}}, -- 1,212,000
	["Salem"] = {container = "Tamil Nadu", wp = "%l, %c"}, -- 1,189,000
	["Kota"] = {container = "Rajasthan"}, -- 1,172,000
	["Jalandhar"] = {container = "Punjab"}, -- 1,165,000
	["Saharanpur"] = {container = "Uttar Pradesh"}, -- 1,152,000
	["Dehradun"] = {container = "Uttarakhand"}, -- 1,136,000
	["Tiruchirappalli"] = {container = "Tamil Nadu"}, -- 1,131,000
	["Bhubaneswar"] = {container = "Odisha"}, -- 1,112,000
	["Jammu"] = {container = {key = "Jammu and Kashmir, India", placetype = "union territory"}}, -- 1,103,000
	["Solapur"] = {container = "Maharashtra"}, -- 1,082,000
	["Hubli-Dharwad"] = {container = "Karnataka", wp = "Hubli–Dharwad"}, -- 1,062,000; wp with en dash
	["Hubli"] = {alias_of = "Hubli-Dharwad"},
	["Dharwad"] = {alias_of = "Hubli-Dharwad"},
	["Puducherry"] = {container = {key = "Puducherry, India", placetype = "union territory"}}, -- 1,024,000
	["Pondicherry"] = {alias_of = "Puducherry", display = true},
	-- satellite/secondary cities of metro area (none in citypopulation.de)
	["Ghaziabad"] = {container = "Uttar Pradesh"}, -- 1,729,000 city, 2,358,525 urban agglomeration per 2011 census; 3,406,061 2025 estimate from official website; part of Delhi metro area
	["Faridabad"] = {container = "Haryana"}, -- 1,414,050 city per 2011 census; part of Delhi metro area
	["Thane"] = {container = "Maharashtra"}, -- 1,841,488 city per 2011 census; part of Mumbai metro area
	["Kalyan-Dombivli"] = {container = "Maharashtra"}, -- 1,246,381 city per 2011 census; part of Mumbai metro area
	["Kalyan-Dombivali"] = {alias_of = "Kalyan-Dombivli", display = true},
	["Kalyan"] = {alias_of = "Kalyan-Dombivli"},
	["Dombivli"] = {alias_of = "Kalyan-Dombivli"},
	["Dombivali"] = {alias_of = "Kalyan-Dombivli"},
	["Vasai-Virar"] = {container = "Maharashtra"}, -- 1,221,233 city per 2011 census; part of Mumbai metro area
	["Vasai"] = {alias_of = "Vasai-Virar"},
	["Virar"] = {alias_of = "Vasai-Virar"},
	["Navi Mumbai"] = {container = "Maharashtra"}, -- 1,120,547 city per 2011 census; part of Mumbai metro area
	["Howrah"] = {container = "West Bengal"}, -- 1,077,075 city ("metropolis"), 2,811,344 "metro" per 2011 census; part of Kolkata metro area
	["Pimpri-Chinchwad"] = {container = "Maharashtra"}, -- 1,727,692 per 2011 census; part of Pune metro area
	["Pimpri Chinchwad"] = {alias_of = "Pimpri-Chinchwad", display = true},
}

export.india_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", India", "state"),
	default_placetype = "city",
	data = export.india_cities,
}

export.indonesia_cities = {
	-- cities where the city proper has more than 1,000,000 people as of mid-2023 estimate
	["Jakarta"] = {container = "Special Capital Region of Jakarta", divs = {
		{type = "subdistricts", container_parent_type = false},
	}},
	["Surabaya"] = {container = "East Java"},
	["Bekasi"] = {container = "West Java"}, -- part of Jakarta metro area
	["Bandung"] = {container = "West Java"},
	["Medan"] = {container = "North Sumatra"},
	["Depok"] = {container = "West Java"}, -- part of Jakarta metro area
	["Tangerang"] = {container = "Banten"}, -- part of Jakarta metro area
	["Palembang"] = {container = "South Sumatra"},
	["Semarang"] = {container = "Central Java"},
	["Makassar"] = {container = "South Sulawesi"},
	["South Tangerang"] = {container = "Banten"}, -- part of Jakarta metro area
	["Batam"] = {container = "Riau Islands"},
	["Bogor"] = {container = "West Java"}, -- part of Jakarta metro area
	["Pekanbaru"] = {container = "Riau"},
	["Bandar Lampung"] = {container = "Lampung"},
	-- other metro areas over 1,000,000 people
	["Padang"] = {container = "West Sumatra"},
	["Samarinda"] = {container = "East Kalimantan"},
	["Malang"] = {container = "East Java"},
	["Yogyakarta"] = {container = "Special Region of Yogyakarta"},
	["Denpasar"] = {container = "Bali"},
	["Cirebon"] = {container = "West Java"},
	["Surakarta"] = {container = "Central Java"},
	["Banjarmasin"] = {container = "South Kalimantan"},
	["Tasikmalaya"] = {container = "West Java"},
}

export.indonesia_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Indonesia", "province"),
	default_placetype = "city",
	data = export.indonesia_cities,
}

export.italy_cities = {
	-- Data per [[w:List_of_metropolitan_areas_of_Italy]]. There are several lists given; the most recent one, used
	-- here, only gives estimates as of Jan 1, 2014.
	["Milan"] = {container = "Lombardy"}, -- 6,623,798
	["Naples"] = {container = "Campania"}, -- 5,294,546
	["Rome"] = {container = "Lazio"}, -- 4,447,881
	["Turin"] = {container = "Piedmont"}, -- 1,865,284
	["Venice"] = {container = "Veneto"}, -- 1,645,900
	["Florence"] = {container = "Tuscany"}, -- 1,485,030
	["Bari"] = {container = "Apulia"}, -- 1,257,459
	["Palermo"] = {container = "Sicily"}, -- 1,183,084
	-- include a few just below 1,000,000 metro area that may be above it by now (depending on the definition).
	["Catania"] = {container = "Sicily"}, -- 988,240
	["Brescia"] = {container = "Lombardy"}, -- 924,090
	["Genoa"] = {container = "Liguria"}, -- 861,318
}

export.italy_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Italy", "region"),
	default_placetype = "city",
	data = export.italy_cities,
}

export.japan_cities = {
	-- Population figures from [[w:List of cities in Japan]]. Metro areas from
	-- [[w:List of metropolitan areas in Japan]].
	["Tokyo"] = {keydesc = "[[Tokyo]] Metropolis, the [[capital city]] and a [[prefecture]] of [[Japan]] (which is a country in [[Asia]])",
		placetype = {"city", "prefecture"},
		divs = {
			{type = "special wards", container_parent_type = false},
			{type = "cities", prep = "in"},
		},
	},
	["Yokohama"] = {container = "Kanagawa"}, -- 3,697,894
	["Osaka"] = {container = "Osaka"}, -- 2,668,586
	["Nagoya"] = {container = "Aichi"}, -- 2,283,289
	-- FIXME, Hokkaido is handled specially.
	["Sapporo"] = {container = "Hokkaido"}, -- 1,918,096
	["Fukuoka"] = {container = "Fukuoka"}, -- 1,581,527
	["Kobe"] = {container = "Hyōgo"}, -- 1,530,847
	["Kyoto"] = {container = "Kyoto"}, -- 1,474,570
	["Kawasaki"] = {container = "Kanagawa", wp = "%l, Kanagawa"}, -- 1,373,630
	["Saitama"] = {container = "Saitama", wp = "%l (city)", commonscat = "%l, %c"}, -- 1,192,418
	["Hiroshima"] = {container = "Hiroshima"}, -- 1,163,806
	["Sendai"] = {container = "Miyagi"}, -- 1,029,552
	-- the remaining cities are considered "central cities" in a 1,000,000+ metro area
	-- (sometimes there is more than one central city in the area).
	["Kitakyushu"] = {container = "Fukuoka"}, -- 986,998
	["Chiba"] = {container = "Chiba", wp = "%l (city)", commonscat = "%l, %c"}, -- 938,695
	["Sakai"] = {container = "Osaka"}, -- 835,333
	["Niigata"] = {container = "Niigata", wp = "%l (city)", commonscat = "%l, %c"}, -- 813,053
	["Hamamatsu"] = {container = "Shizuoka"}, -- 811,431
	["Shizuoka"] = {container = "Shizuoka", wp = "%l (city)", commonscat = "%l, %c"}, -- 710,944
	["Sagamihara"] = {container = "Kanagawa"}, -- 706,342
	["Okayama"] = {container = "Okayama"}, -- 701,293
	["Kumamoto"] = {container = "Kumamoto"}, -- 670,348
	["Kagoshima"] = {container = "Kagoshima"}, -- 605,196
	-- skipped 6 cities (Funabashi, Hachiōji, Kawaguchi, Himeji, Matsuyama, Higashiōsaka)
	-- with population in the range 509k - 587k because not central cities in any
	-- 1,000,000+ metro area.
	["Utsunomiya"] = {container = "Tochigi"}, -- 507,833
}

export.japan_cities_group = {
	default_container = "Japan",
	canonicalize_key_container = make_canonicalize_key_container(" Prefecture, Japan", "prefecture"),
	default_placetype = "city",
	data = export.japan_cities,
}

export.mexico_cities = {
	["Mexico City"] = {}, -- its own state
	["Monterrey"] = {container = "Nuevo León"},
	["Guadalajara"] = {container = "Jalisco"},
	["Puebla"] = {container = "Puebla", wp = "%l (city)"},
	["Toluca"] = {container = "State of Mexico"},
	["Tijuana"] = {container = "Baja California"},
	-- Include the state in the category for León due to possible confusion with León, Spain.
	["León, Guanajuato"] = {container = "Guanajuato", wp = "%l, %c"},
	["León"] = {alias_of = "León, Guanajuato"},
	["Leon"] = {alias_of = "León, Guanajuato", display = true},
	["Querétaro"] = {container = "Querétaro", wp = "%l (city)"},
	["Queretaro"] = {alias_of = "Querétaro", display = true},
	["Ciudad Juárez"] = {container = "Chihuahua"},
	["Juárez"] = {alias_of = "Ciudad Juárez"},
	["Juarez"] = {alias_of = "Ciudad Juárez", display = "Juárez"},
	["Torreón"] = {container = "Coahuila"},
	["Torreon"] = {alias_of = "Torreón", display = true},
	-- Include the state in the category for Mérida due to possible confusion with Mérida, Spain or
	-- Mérida, Venezuela.
	["Mérida, Yucatán"] = {container = "Yucatán", wp = "%l, %c"},
	["Mérida"] = {alias_of = "Mérida, Yucatán"},
	["Merida"] = {alias_of = "Mérida, Yucatán", display = true},
	["San Luis Potosí"] = {container = "San Luis Potosí", wp = "%l (city)"},
	["San Luis Potosi"] = {alias_of = "San Luis Potosí", display = true},
	["Aguascalientes"] = {container = "Aguascalientes", wp = "%l (city)"},
	["Mexicali"] = {container = "Baja California"},
}

export.mexico_cities_group = {
	default_container = "Mexico",
	canonicalize_key_container = make_canonicalize_key_container(", Mexico", "state"),
	default_placetype = "city",
	data = export.mexico_cities,
}

export.nigeria_cities = {
	-- Figures from citypopulation.de unless otherwise indicated; retrieved 2025-04-26; reference date 2025-01-01.
	["Lagos"] = {container = "Lagos"}, -- 21,300,000 (unindicated; population of low reliability)
	["Kano"] = {container = "Kano", wp = "%l (city)"}, -- 5,350,000 (unindicated; population of low reliability)
	["Ibadan"] = {container = "Oyo"}, -- 3,400,000 (unindicated; population of low reliability)
	["Abuja"] = {container = {key = "Federal Capital Territory, Nigeria", placetype = "federal territory"}}, -- 3,050,000 (unindicated; population of low reliability)
	["Port Harcourt"] = {container = "Rivers"}, -- 2,250,000 (unindicated; population of low reliability)
	["Kaduna"] = {container = "Kaduna"}, -- 1,980,000 (unindicated; population of low reliability)
	["Benin City"] = {container = "Edo"}, -- 1,790,000 (unindicated; population of low reliability)
	["Aba"] = {container = "Abia", wp = "%l, Nigeria"}, -- 1,280,000 (unindicated; population of low reliability)
	["Onitsha"] = {container = "Anambra"}, -- 1,230,000 (unindicated; population of low reliability)
	["Maiduguri"] = {container = "Borno"}, -- 1,190,000 (unindicated; population of low reliability)
	["Ilorin"] = {container = "Kwara"}, -- 1,160,000 (unindicated; population of low reliability)
	["Sokoto"] = {container = "Sokoto", wp = "%l (city)"}, -- 1,140,000 (unindicated; population of low reliability)
	["Jos"] = {container = "Plateau"}, -- 1,110,000 (unindicated; population of low reliability)
	["Zaria"] = {container = "Kaduna"}, -- 1,050,000 (unindicated; population of low reliability)
	["Enugu"] = {container = "Enugu", wp = "%l (city)"}, -- 1,010,000 (unindicated; population of low reliability)
}

export.nigeria_cities_group = {
	default_container = "Nigeria",
	canonicalize_key_container = make_canonicalize_key_container(" State, Nigeria", "state"),
	default_placetype = "city",
	data = export.nigeria_cities,
}

export.pakistan_cities = {
	-- Figures from citypopulation.de; retrieved 2025-04-26; reference date 2025-01-01.
	["Karachi"] = {container = "Sindh"}, -- 21,000,000 (Consolidated Urban Area)
	["Lahore"] = {container = "Punjab"}, -- 14,600,000 (Consolidated Urban Area)
	["Rawalpindi"] = {container = "Punjab"}, -- 5,600,000 (Consolidated Urban Area; including Islamabad)
	["Islamabad"] = {container = {key = "Islamabad Capital Territory, Pakistan", placetype = "federal territory"}}, -- 5,600,000 (Consolidated Urban Area; including Rawalpindi)
	["Faisalabad"] = {container = "Punjab"}, -- 4,125,000 (Consolidated Urban Area)
	["Gujranwala"] = {container = "Punjab"}, -- 3,450,000 (Consolidated Urban Area)
	-- there is also Hyderabad in India (very confusing)
	["Hyderabad, Pakistan"] = {container = "Sindh", wp = "%l, %c"}, -- 2,475,000 (Consolidated Urban Area)
	["Hyderabad"] = {alias_of = "Hyderabad, Pakistan"},
	["Multan"] = {container = "Punjab"}, -- 2,425,000 (Consolidated Urban Area)
	["Peshawar"] = {container = "Khyber Pakhtunkhwa"}, -- 2,150,000 (Consolidated Urban Area)
	["Quetta"] = {container = "Balochistan"}, -- 1,720,000 (Urban Area)
	["Sargodha"] = {container = "Punjab"}, -- 1,080,000 (Urban Area)
	["Sialkot"] = {container = "Punjab"}, -- 1,050,000 (Consolidated Urban Area)
}

export.pakistan_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Pakistan", "province"),
	default_placetype = "city",
	data = export.pakistan_cities,
}

export.philippines_cities = {
	 -- Skipped some cities in Metro Manila (Taguig, Pasig) which don't have districts.
	 -- Other cities outside Metro Manila skipped as not central city in their urban area.
	["Quezon City"] = {container = {key = "Metro Manila, Philippines", placetype = "region"}},
	-- Don't display-canonicalize Foo to Foo City as it may make the display weird.
	["Quezon"] = {alias_of = "Quezon City"},
	["Manila"] = {container = {key = "Metro Manila, Philippines", placetype = "region"}},
	["Davao City"] = {container = "Davao del Sur"},
	["Davao"] = {alias_of = "Davao City"},
	["Caloocan"] = {container = {key = "Metro Manila, Philippines", placetype = "region"}},
	["Zamboanga City"] = {container = "Zamboanga del Sur"},
	["Zamboanga"] = {alias_of = "Zamboanga City"},
	["Cebu City"] = {container = "Cebu"},
	["Cebu"] = {alias_of = "Cebu City"},
	["Antipolo"] = {container = "Rizal"},
	["Cagayan de Oro"] = {container = "Misamis Oriental"},
	["Dasmariñas"] = {container = "Cavite"},
	["Dasmarinas"] = {alias_of = "Dasmariñas", display = true},
	["General Santos"] = {container = "South Cotabato"},
	["San Jose del Monte"] = {container = "Bulacan"},
	["Bacolod"] = {container = "Negros Occidental"},
	["Calamba"] = {container = "Laguna", wp = "%l, %c"},
	["Angeles"] = {container = "Pampanga", wp = "Angeles City"},
	["Angeles City"] = {alias_of = "Angeles"},
	["Iloilo City"] = {container = "Iloilo"},
	["Iloilo"] = {alias_of = "Iloilo City"},
}

export.philippines_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Philippines", "province"),
	default_placetype = "city",
	data = export.philippines_cities,
}

export.russia_cities = {
	-- Figures from citypopulation.de; retrieved 2025-04-26; reference date 2025-01-01.
	["Moscow"] = {}, --  18,800,000 (Agglomeration)
	["Saint Petersburg"] = {}, -- 6,350,000 (Agglomeration)
	["Novosibirsk"] = {container = "Novosibirsk Oblast"}, -- 1,820,000 (Agglomeration)
	["Yekaterinburg"] = {container = "Sverdlovsk Oblast"}, -- 1,810,000 (Agglomeration)
	["Nizhny Novgorod"] = {container = "Nizhny Novgorod Oblast"}, -- 1,620,000 (Agglomeration)
	["Kazan"] = {container = {key = "Tatarstan, Russia", placetype = "republic"}}, -- 1,560,000 (Agglomeration)
	["Chelyabinsk"] = {container = "Chelyabinsk Oblast"}, -- 1,430,000 (Agglomeration)
	["Rostov-on-Don"] = {container = "Rostov Oblast"}, -- 1,390,000 (Agglomeration)
	["Rostov-na-Donu"] = {alias_of = "Rostov-on-Don", display = true},
	["Krasnodar"] = {container = {key = "Krasnodar Krai, Russia", placetype = "krai"}}, -- 1,370,000 (Agglomeration)
	["Samara"] = {container = "Samara Oblast"}, -- 1,350,000 (Agglomeration)
	["Krasnoyarsk"] = {container = {key = "Krasnoyarsk Krai, Russia", placetype = "krai"}}, -- 1,270,000 (Agglomeration)
	["Ufa"] = {container = {key = "Bashkortostan, Russia", placetype = "republic"}}, -- 1,230,000 (Agglomeration)
	["Saratov"] = {container = "Saratov Oblast"}, -- 1,170,000 (Agglomeration)
	["Omsk"] = {container = "Omsk Oblast"}, -- 1,140,000 (Agglomeration)
	["Voronezh"] = {container = "Voronezh Oblast"}, -- 1,130,000 (Agglomeration)
	["Volgograd"] = {container = "Volgograd Oblast"}, -- 1,080,000 (Agglomeration)
	["Perm"] = {container = {key = "Perm Krai, Russia", placetype = "krai"}, wp = "%l, Russia"}, -- 1,070,000 (Agglomeration)
}

export.russia_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Russia", "oblast"),
	default_container = "Russia",
	default_placetype = "city",
	data = export.russia_cities,
}

export.saudi_arabia_cities = {
	-- Figures for the first five from [[w:List of cities and towns in Saudi Arabia]] as of 2022. Unclear if these are
	-- metro, urban or city proper figures.
	["Riyadh"] = {container = "Riyadh"}, -- 7,000,100; 7,700,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Jeddah"] = {container = "Mecca"}, -- 3,751,917; 3,950,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Jedda"] = {alias_of = "Jeddah", display = true},
	["Jiddah"] = {alias_of = "Jeddah", display = true},
	["Jidda"] = {alias_of = "Jeddah", display = true},
	["Dammam"] = {container = "Eastern"}, -- 2,638,166; 2,925,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Mecca"] = {container = "Mecca"}, -- 2,385,509; 2,675,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Makkah"] = {alias_of = "Mecca", display = true},
	["Medina"] = {container = "Medina"}, -- 1,477,023; 1,530,000 per citypopulation.de 2025-01-01 (City)
	["Hofuf"] = {container = "Eastern"}, -- 1,060,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Khamis Mushait"] = {container = "Aseer"}, -- 1,030,000 per citypopulation.de 2025-01-01 (Agglomeration)
	["Khamis Mushayt"] = {alias_of = "Khamis Mushait", display = true},
}

export.saudi_arabia_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(" Province, Saudi Arabia", "province"),
	default_placetype = "city",
	data = export.saudi_arabia_cities,
}

export.south_korea_cities = {
	-- All cities listed are not associated with any county.
	["Seoul"] = {},
	["Busan"] = {},
	["Incheon"] = {},
	["Daegu"] = {},
	["Daejeon"] = {},
	["Gwangju"] = {},
	["Ulsan"] = {},
}

export.south_korea_cities_group = {
	default_container = "South Korea",
	canonicalize_key_container = make_canonicalize_key_container(" County, South Korea", "province"),
	default_placetype = "city",
	data = export.south_korea_cities,
}

export.spain_cities = {
	["Madrid"] = {container = "Community of Madrid"},
	["Barcelona"] = {container = "Catalonia"},
	["Valencia"] = {container = "Valencia"},
	["Seville"] = {container = "Andalusia"},
	["Bilbao"] = {container = "Basque Country"},
}

export.spain_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", Spain", "autonomous community"),
	default_placetype = "city",
	data = export.spain_cities,
}

export.taiwan_cities = {
	["New Taipei City"] = {},
	["New Taipei"] = {alias_of = "New Taipei City", display = true},
	["Taichung"] = {},
	["Kaohsiung"] = {wp = "%l, Taiwan"},
	["Taipei"] = {},
	["Taoyuan"] = {},
	["Tainan"] = {},
	-- these last three are not special municipalities
	["Chiayi"] = {placetype = "city"},
	["Hsinchu"] = {placetype = "city"},
	["Keelung"] = {placetype = "city"},
}

export.taiwan_cities_group = {
	placename_to_key = false, -- don't add ", Taiwan" to make the key
	canonicalize_key_container = make_canonicalize_key_container(", Taiwan", "county"),
	default_container = "Taiwan",
	default_placetype = {"special municipality", "municipality", "city"},
	default_is_city = true,
	default_divs = {"districts"},
	data = export.taiwan_cities,
}

-- NOTE: It's OK to mix cities from different constituent countries; as long as the immediate container is correct,
-- everything else will be figured out.
export.united_kingdom_cities = {
	["London"] = {container = "Greater London"},
	["Manchester"] = {container = "Greater Manchester"},
	["Birmingham"] = {container = "West Midlands"},
	["Liverpool"] = {container = "Merseyside"},
	["Glasgow"] = {container = {key = "City of Glasgow, Scotland", placetype = "council area"}},
	["Leeds"] = {container = "West Yorkshire"},
	["Newcastle upon Tyne"] = {container = "Tyne and Wear"},
	["Newcastle"] = {alias_of = "Newcastle upon Tyne"},
	["Bristol"] = {container = {key = "England", placetype = "constituent country"}},
	["Cardiff"] = {container = {key = "Wales", placetype = "constituent country"}},
	["Portsmouth"] = {container = "Hampshire"},
	["Edinburgh"] = {container = {key = "City of Edinburgh, Scotland", placetype = "council area"}},
	-- under 1,000,000 people but principal areas of Wales; requested by [[User:Donnanz]]
	["Swansea"] = {container = {key = "Wales", placetype = "constituent country"}},
	["Newport"] = {container = {key = "Wales", placetype = "constituent country"}, wp = "Newport, Wales"},
}

export.united_kingdom_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(", England", "county"),
	default_placetype = "city",
	data = export.united_kingdom_cities,
}

export.united_states_cities = {
	-- top 50 CSA's by population, with the top and sometimes 2nd or 3rd city listed
	["New York City"] = {container = "New York", wp = "%l", divs = {
		{type = "boroughs", container_parent_type = false},
	}},
	-- Don't display-canonicalize as it may make the display weird (e.g. in the context New York, New York).
	["New York"] = {alias_of = "New York City"},
	["Newark"] = {container = "New Jersey"},
	["Los Angeles"] = {container = "California", wp = "%l"},
	["Long Beach"] = {container = "California"},
	["Riverside"] = {container = "California"},
	["Chicago"] = {container = "Illinois", wp = "%l"},
	["Washington, D.C."] = {wp = "%l"},
	["Washington, DC"] = {alias_of = "Washington, D.C.", display = true},
	["Washington D.C."] = {alias_of = "Washington, D.C.", display = true},
	["Washington DC"] = {alias_of = "Washington, D.C.", display = true},
	-- Don't display-canonicalize as it may make the display weird (e.g. if the holonym is followed by a District of
	-- Columbia holonym).
	["Washington"] = {alias_of = "Washington, D.C."},
	["Baltimore"] = {container = "Maryland", wp = "%l"},
	-- to avoid conflict with San Jose in Costa Rica
	["San Jose, California"] = {container = "California"},
	["San Jose"] = {alias_of = "San Jose, California"},
	["San Francisco"] = {container = "California", wp = "%l"},
	["Oakland"] = {container = "California"},
	["Boston"] = {container = "Massachusetts", wp = "%l"},
	["Providence"] = {container = "Rhode Island"},
	["Dallas"] = {container = "Texas", wp = "%l", commonscat = "%l, %c"},
	["Fort Worth"] = {container = "Texas"},
	["Philadelphia"] = {container = "Pennsylvania", wp = "%l"},
	["Houston"] = {container = "Texas", wp = "%l"},
	["Miami"] = {container = "Florida", wp = "%l", commonscat = "%l, %c"},
	["Atlanta"] = {container = "Georgia", wp = "%l"},
	["Detroit"] = {container = "Michigan", wp = "%l"},
	["Phoenix"] = {container = "Arizona", wp = "%l", commonscat = "%l, %c"},
	["Mesa"] = {container = "Arizona"},
	["Seattle"] = {container = "Washington", wp = "%l"},
	["Orlando"] = {container = "Florida"},
	["Minneapolis"] = {container = "Minnesota", wp = "%l"},
	["Cleveland"] = {container = "Ohio", wp = "%l", commonscat = "%l, %c"},
	["Denver"] = {container = "Colorado", wp = "%l", commonscat = "%l, %c"},
	["San Diego"] = {container = "California", wp = "%l", commonscat = "%l, %c"},
	["Portland"] = {container = "Oregon"},
	["Tampa"] = {container = "Florida"},
	["St. Louis"] = {container = "Missouri", wp = "%l", commonscat = "%l, %c"},
	["Saint Louis"] = {alias_of = "St. Louis", display = true},
	["Charlotte"] = {container = "North Carolina"},
	["Sacramento"] = {container = "California"},
	["Pittsburgh"] = {container = "Pennsylvania", wp = "%l"},
	["Salt Lake City"] = {container = "Utah", wp = "%l"},
	["San Antonio"] = {container = "Texas", wp = "%l", commonscat = "%l, %c"},
	["Columbus"] = {container = "Ohio"},
	["Kansas City"] = {container = "Missouri", wp = "%l metropolitan area", commonscat = "%l, %c"},
	["Indianapolis"] = {container = "Indiana", wp = "%l"},
	["Las Vegas"] = {container = "Nevada", wp = "%l"},
	["Cincinnati"] = {container = "Ohio", wp = "%l", commonscat = "%l, %c"},
	["Austin"] = {container = "Texas"},
	["Milwaukee"] = {container = "Wisconsin", wp = "%l", commonscat = "%l, %c"},
	["Raleigh"] = {container = "North Carolina"},
	["Nashville"] = {container = "Tennessee"},
	["Virginia Beach"] = {container = "Virginia"},
	["Norfolk"] = {container = "Virginia"},
	["Greensboro"] = {container = "North Carolina"},
	["Winston-Salem"] = {container = "North Carolina"},
	["Jacksonville"] = {container = "Florida"},
	["New Orleans"] = {container = "Louisiana", wp = "%l"},
	["Louisville"] = {container = "Kentucky"},
	["Greenville"] = {container = "South Carolina"},
	["Hartford"] = {container = "Connecticut"},
	["Oklahoma City"] = {container = "Oklahoma", wp = "%l"},
	["Grand Rapids"] = {container = "Michigan"},
	["Memphis"] = {container = "Tennessee"},
	["Birmingham, Alabama"] = {container = "Alabama"},
	["Birmingham"] = {alias_of = "Birmingham, Alabama"},
	["Fresno"] = {container = "California"},
	["Richmond"] = {container = "Virginia"},
	["Harrisburg"] = {container = "Pennsylvania"},
	-- any major city of top 50 MSA's that's missed by previous
	["Buffalo"] = {container = "New York"},
	-- any of the top 50 city by city population that's missed by previous
	["El Paso"] = {container = "Texas"},
	["Albuquerque"] = {container = "New Mexico"},
	["Tucson"] = {container = "Arizona"},
	["Colorado Springs"] = {container = "Colorado"},
	["Omaha"] = {container = "Nebraska"},
	["Tulsa"] = {container = "Oklahoma"},
	-- skip Arlington, Texas; too obscure and likely to be interpreted as Arlington, Virginia
}

export.united_states_cities_group = {
	default_container = "United States",
	canonicalize_key_container = make_canonicalize_key_container(", USA", "state"),
	default_placetype = "city",
	default_wp = "%l, %c",
	data = export.united_states_cities,
}

export.new_york_boroughs = {
	["Bronx"] = {the = true, wp = "The Bronx"},
	["Brooklyn"] = {},
	["Manhattan"] = {},
	["Queens"] = {},
	["Staten Island"] = {},
}

export.new_york_boroughs_group = {
	default_container = {key = "New York City", placetype = "city"},
	default_placetype = "borough",
	default_is_city = true,
	data = export.new_york_boroughs,
}

export.vietnam_cities = {
	-- Figures from citypopulation.de (retrieved 2025-04-26; reference date 2025-01-01) unless otherwise indicated.
	["Ho Chi Minh City"] = {}, -- 14,300,000 (Agglomeration; inclunding Bien Hoa)
	["Saigon"] = {alias_of = "Ho Chi Minh City"},
	["Hanoi"] = {}, -- 7,350,000 (Agglomeration)
	["Da Nang"] = {}, -- 1,500,000 (Agglomeration)
	["Danang"] = {alias_of = "Da Nang", display = true},
	["Haiphong"] = {}, -- 1,450,000 (Agglomeration)
	["Hai Phong"] = {alias_of = "Haiphong", display = true},
	-- This is the one entry in this list that is not a province-level municipality; instead it's a "provincial city"
	-- meaning it is directly under its province as opposed to being contained in a district.
	["Bien Hoa"] = {placetype = "city", container = "Đồng Nai", wp = "Biên Hòa"}, -- 1,272,235 (2022 city population per Wikipedia)
	["Biên Hòa"] = {alias_of = "Bien Hoa", display = true},
	["Biên Hoà"] = {alias_of = "Bien Hoa", display = true},
	-- These two not in citypopulation.de because the urban population may be slightly under 1,000,000, but they are
	-- both province-level municipalities and close to the 1,000,000 mark.
	["Can Tho"] = {wp = "Cần Thơ"}, -- 1,456,000 municipality (2019 census), 994,704 urban (2022 General Statistics Office of Vietnam estimate); capital [[Ninh Kiều district]]
	["Cần Thơ"] = {alias_of = "Can Tho", display = true},
	["Hue"] = {wp = "Huế"}, -- 1,257,000 municipality (2019 census), 840,000 urban (2022 General Statistics Office of Vietnam estimate); -- capital [[Thuận Hóa district]]
	["Huế"] = {alias_of = "Hue", display = true},
}

export.vietnam_cities_group = {
	placename_to_key = false, -- don't add ", Vietnam" to make the key
	default_container = "Vietnam",
	canonicalize_key_container = make_canonicalize_key_container(" Province, Vietnam", "province"),
	-- Most of the cities listed are province-level municipalities in addition, which contain a certain amount of
	-- rural territory surrounding the city, but not enough to separate the municipality from the city as distinct
	-- known locations.
	default_placetype = {"municipality", "city"},
	default_is_city = true,
	-- There may not be enough districts to subcategorize like this.
	-- default_divs = "districts",
	data = export.vietnam_cities,
}

export.misc_cities = {
	------------------ Africa -------------------
	-- Sorted by country and then within the country, by decreasing population; figures from citypopulation.de
	-- (retrieved 2025-04-26; reference date 2025-01-01) unless otherwise indicated; combined with data from
	-- [[w:List of urban areas in Africa by population]].
	["Algiers"] = {container = "Algeria"}, -- 4,325,000 (Consolidated Urban Area)
	["Oran"] = {container = "Algeria"}, -- 1,640,000 (Consolidated Urban Area)
	["Luanda"] = {container = "Angola"}, -- 9,650,000 (Urban Area)
	["Benguela"] = {container = "Angola"}, -- 1,420,000 (Urban Area)
	["Cotonou"] = {container = "Benin"}, -- 2,150,000 (Agglomeration)
	["Ouagadougou"] = {container = "Burkina Faso"}, -- 3,425,000 (Agglomeration)
	["Bobo-Dioulasso"] = {container = "Burkina Faso"}, -- 1,100,000 (Agglomeration)
	["Bujumbura"] = {container = "Burundi"}, -- 1,143,202 (Urban Area 2023 per PopulationStat, cited in Wikipedia)
	["Yaoundé"] = {container = "Cameroon"}, -- 3,975,000 (City)
	["Yaounde"] = {alias_of = "Yaoundé", display = true},
	["Douala"] = {container = "Cameroon"}, -- 3,900,000 (City)
	["Bangui"] = {container = "Central African Republic"}, -- 1,680,000 (Agglomeration)
	["N'Djamena"] = {container = "Chad"}, -- 1,950,000 (City)
	["Ndjamena"] = {alias_of = "N'Djamena", display = true},
	["Kinshasa"] = {container = "Democratic Republic of the Congo"}, -- 16,300,000 (City; population of low reliability)
	["Lubumbashi"] = {container = "Democratic Republic of the Congo"}, -- 2,875,000 (City; population of low reliability)
	["Mbuji-Mayi"] = {container = "Democratic Republic of the Congo"}, -- 2,500,000 (City; population of low reliability)
	["Kananga"] = {container = "Democratic Republic of the Congo"}, -- 1,370,000 (City; population of low reliability)
	["Kisangani"] = {container = "Democratic Republic of the Congo"}, -- 1,300,000 (City; population of low reliability)
	["Bukavu"] = {container = "Democratic Republic of the Congo"}, -- 1,100,000 (City; population of low reliability)
	["Goma"] = {container = "Democratic Republic of the Congo"}, -- 1,010,000 (City; population of low reliability)
	["Tshikapa"] = {container = "Democratic Republic of the Congo"}, -- 1,020,468 (2023 Wikipedia [[w:List of cities with over one million inhabitants]] from populationstat.com; not in citypopulation.de)
	["Cairo"] = {container = "Egypt"}, -- 22,800,000 (Agglomeration, including Giza and Subhra El Kheima)
	["Alexandria"] = {container = "Egypt"}, -- 6,250,000 (Agglomeration)
	["Giza"] = {container = "Egypt"}, -- 4,458,135 (2023 from citypopulation.de)
	["Shubra El Kheima"] = {container = "Egypt"}, -- 1,240,239 (2021 from citypopulation.de)
	["Asmara"] = {container = "Eritrea"}, -- 1,090,000 (City; population of low reliability)
	["Asmera"] = {alias_of = "Asmara", display = true},
	["Addis Ababa"] = {container = "Ethiopia"}, -- 4,825,000 (Agglomeration)
	["Banjul"] = {container = "Gambia"}, -- 1,170,000 (Agglomeration)
	["Accra"] = {container = "Ghana"}, -- 6,800,000 (Agglomeration)
	["Kumasi"] = {container = "Ghana"}, -- 2,900,000 (Agglomeration)
	["Conakry"] = {container = "Guinea"}, -- 2,975,000 (Consolidated Urban Area)
	["Abidjan"] = {container = "Ivory Coast"}, -- 7,050,000 (Agglomeration)
	["Nairobi"] = {container = "Kenya"}, -- 6,900,000 (unindicated)
	["Mombasa"] = {container = "Kenya"}, -- 1,370,000 (City)
	["Monrovia"] = {container = "Liberia"}, -- 1,940,000 (Urban Area)
	["Tripoli"] = {container = "Libya", wp = "%l, %c"}, -- 1,870,000 (unindicated)
	["Antananarivo"] = {container = "Madagascar"}, -- 3,150,000 (Agglomeration)
	["Lilongwe"] = {container = "Malawi"}, -- 1,210,000 (City)
	["Bamako"] = {container = "Mali"}, -- 5,700,000 (Agglomeration)
	["Nouakchott"] = {container = "Mauritania"}, -- 1,500,000 (City)
	["Casablanca"] = {container = {key = "Casablanca-Settat, Morocco", placetype = "region"}}, -- 4,450,000 (Municipality (urban population))
	["Rabat"] = {container = {key = "Rabat-Sale-Kenitra, Morocco", placetype = "region"}}, -- 2,125,000 (Municipality (urban population))
	["Tangier"] = {container = {key = "Tangier-Tetouan-Al Hoceima, Morocco", placetype = "region"}}, -- 1,410,000 (Municipality (urban population))
	["Tanger"] = {alias_of = "Tangier", display = true},
	["Tangiers"] = {alias_of = "Tangier", display = true},
	["Fez"] = {container = {key = "Fez-Meknes, Morocco", placetype = "region"}, wp = "%l, Morocco"}, -- 1,310,000 (Municipality (urban population))
	["Fes"] = {alias_of = "Fez", display = true},
	["Fès"] = {alias_of = "Fez", display = true},
	["Agadir"] = {container = {key = "Souss-Massa, Morocco", placetype = "region"}}, -- 1,270,000 (Municipality (urban population))
	["Marrakesh"] = {container = {key = "Marrakesh-Safi, Morocco", placetype = "region"}}, -- 1,140,000 (Municipality (urban population))
	["Marrakech"] = {alias_of = "Marrakesh", display = true},
	["Maputo"] = {container = "Mozambique"}, -- 2,575,000 (Agglomeration)
	["Niamey"] = {container = "Niger"}, -- 1,530,000 (City)
	["Brazzaville"] = {container = "Republic of the Congo"}, -- 2,475,000 (Agglomeration)
	["Pointe-Noire"] = {container = "Republic of the Congo"}, -- 1,480,000 (City)
	["Kigali"] = {container = "Rwanda"}, -- 1,960,000 (Municipality (urban population))
	["Dakar"] = {container = "Senegal"}, -- 4,225,000 (Agglomeration)
	["Touba"] = {container = "Senegal"}, -- 1,320,000 (Agglomeration)
	["Freetown"] = {container = "Sierra Leone"}, -- 1,420,000 (Agglomeration)
	["Mogadishu"] = {container = "Somalia"}, -- 2,250,000 (unindicated; population of low reliability)
	["Johannesburg"] = {container = {key = "Gauteng, South Africa", placetype = "province"}}, -- 14,800,000 (Consolidated Urban Area; including Pretoria, Soweto, etc.)
	["Cape Town"] = {container = {key = "Western Cape, South Africa", placetype = "province"}}, -- 5,100,000 (Consolidated Urban Area)
	["Durban"] = {container = {key = "KwaZulu-Natal, South Africa", placetype = "province"}}, -- 3,900,000 (Consolidated Urban Area)
	["Pretoria"] = {container = {key = "Gauteng, South Africa", placetype = "province"}}, -- 2,921,488 (2011 census)
	["Port Elizabeth"] = {container = {key = "Eastern Cape, South Africa", placetype = "province"}, wp = "Gqeberha"}, -- 1,200,000 (Consolidated Urban Area)
	["Gqeberha"] = {alias_of = "Port Elizabeth"}, -- official name; not a display alias
	["Khartoum"] = {container = "Sudan"}, -- 7,200,000 (unindicated; population of low reliability)
	["Dar es Salaam"] = {container = "Tanzania"}, -- 6,650,000 (Agglomeration)
	["Mwanza"] = {container = "Tanzania"}, -- 1,340,000 (Agglomeration)
	["Mwanza City"] = {alias_of = "Mwanza", display = true},
	["Arusha"] = {container = "Tanzania"}, -- 1,190,000 (Agglomeration)
	["Zanzibar"] = {container = "Tanzania"}, -- 1,030,000 (Agglomeration)
	["Lomé"] = {container = "Togo"}, -- 2,625,000 (unindicated)
	["Lome"] = {alias_of = "Lomé", display = true},
	["Tunis"] = {container = "Tunisia"}, -- 2,725,000 (Municipality (urban population))
	["Sousse"] = {container = "Tunisia"}, -- 1,180,000 (Municipality (urban population))
	["Soussa"] = {alias_of = "Sousse", display = true},
	["Kampala"] = {container = "Uganda"}, -- 4,300,000 (unindicated)
	["Lusaka"] = {container = "Zambia"}, -- 3,000,000 (Consolidated Urban Area)
	["Harare"] = {container = "Zimbabwe"}, -- 2,675,000 (Agglomeration)

	------------------ Asia -------------------
	-- sorted by country and then within the country, by decreasing population; figures from citypopulation.de
	-- (retrieved 2025-04-26; reference date 2025-01-01) unless otherwise indicated.
	["Kabul"] = {container = "Afghanistan"}, -- 5,250,000 (Agglomeration)
	["Baku"] = {container = "Azerbaijan"}, -- 3,725,000 (Administrative Area (urban population))
	["Manama"] = {container = "Bahrain"}, -- 1,560,000 (unindicated)
	["Dhaka"] = {container = {key = "Dhaka Division, Bangladesh", placetype = "division"}}, -- 23,100,000 (Agglomeration)
	["Dacca"] = {alias_of = "Dhaka", display = true},
	["Chittagong"] = {container = {key = "Chittagong Division, Bangladesh", placetype = "division"}}, -- 5,050,000 (Agglomeration)
	["Gazipur"] = {container = {key = "Dhaka Division, Bangladesh", placetype = "division"}}, -- 2,674,697 (City per 2022; countied in citypopulation.de as part of Dhaka metro area)
	["Khulna"] = {container = {key = "Khulna Division, Bangladesh", placetype = "division"}}, -- 1,210,000 (Agglomeration)
	["Phnom Penh"] = {container = "Cambodia"}, -- 2,925,000 (Agglomeration)
	["Tehran"] = {container = {key = "Tehran Province, Iran", placetype = "province"}}, -- 16,800,000 (Agglomeration)
	["Teheran"] = {alias_of = "Tehran", display = true},
	["Mashhad"] = {container = {key = "Razavi Khorasan Province, Iran", placetype = "province"}}, -- 3,475,000 (Agglomeration)
	["Mashad"] = {alias_of = "Mashhad", display = true},
	["Meshhed"] = {alias_of = "Mashhad", display = true},
	["Meshed"] = {alias_of = "Mashhad", display = true},
	["Isfahan"] = {container = {key = "Isfahan Province, Iran", placetype = "province"}}, -- 3,425,000 (Agglomeration)
	["Esfahan"] = {alias_of = "Isfahan", display = true},
	["Tabriz"] = {container = {key = "East Azerbaijan Province, Iran", placetype = "province"}}, -- 1,970,000 (Agglomeration)
	["Shiraz"] = {container = {key = "Fars Province, Iran", placetype = "province"}}, -- 1,950,000 (Agglomeration)
	["Ahvaz"] = {container = {key = "Khuzestan Province, Iran", placetype = "province"}}, -- 1,550,000 (Agglomeration)
	["Qom"] = {container = {key = "Qom Province, Iran", placetype = "province"}}, -- 1,450,000 (City)
	["Kermanshah"] = {container = {key = "Kermanshah Province, Iran", placetype = "province"}}, -- 1,130,000 (City)
	["Baghdad"] = {container = "Iraq"}, -- 7,800,000 (Administrative Area (urban population))
	["Basra"] = {container = "Iraq"}, -- 1,710,000 (Administrative Area (urban population))
	["Mosul"] = {container = "Iraq"}, -- 1,550,000 (Administrative Area (urban population))
	["Erbil"] = {container = "Iraq"}, -- 1,220,000 (Administrative Area (urban population))
	["Kirkuk"] = {container = "Iraq"}, -- 1,160,000 (Administrative Area (urban population))
	["Najaf"] = {container = "Iraq"}, -- 1,050,000 (Administrative Area (urban population))
	["Tel Aviv"] = {container = "Israel"}, -- 3,000,000 (Agglomeration)
	-- Jerusalem is not recognized internationally as part of either Israel or Palestine, but as a
	-- [[w:corpus separatum]], so put the container as "Asia" and list Israel and Palestine as additional parents for
	-- categorization purposes.
	["Jerusalem"] = {container = {key = "Asia", placetype = "continent"},
		addl_parents = {"Israel", "Palestine"}}, -- 1,080,000 (Agglomeration)
	["Amman"] = {container = "Jordan"}, -- 6,150,000 (unindicated)
	["Irbid"] = {container = "Jordan"}, -- 1,070,000 (unindicated)
	["Almaty"] = {container = "Kazakhstan"}, -- 2,700,000 (Agglomeration)
	["Alma-Ata"] = {alias_of = "Almaty"}, -- former name, sometimes still used; don't display-canonicalize
	["Astana"] = {container = "Kazakhstan"}, -- 1,600,000 (Agglomeration)
	["Shymkent"] = {container = "Kazakhstan"}, -- 1,370,000 (Agglomeration)
	["Kuwait City"] = {container = "Kuwait"}, -- 5,050,000 (Agglomeration)
	["Bishkek"] = {container = "Kyrgyzstan"}, -- 1,540,000 (Agglomeration)
	["Beirut"] = {container = "Lebanon"}, -- 1,930,000 (unindicated; population of low reliability)
	-- Kuala Lumpur is a federal capital city, not in any state
	["Kuala Lumpur"] = {container = "Malaysia"}, -- 9,550,000 (Agglomeration)
	-- there are various George Towns and Georgetowns
	["George Town, Malaysia"] = {container = {key = "Penang, Malaysia", placetype = "state"}, wp = "%l, %c"}, -- 2,075,000 (Agglomeration)
	["George Town"] = {alias_of = "George Town, Malaysia"},
	["Ulaanbaatar"] = {container = "Mongolia"}, -- 1,610,000 (City)
	["Ulan Bator"] = {alias_of = "Ulaanbaatar", display = true},
	["Yangon"] = {container = "Myanmar"}, -- 5,650,000 (Municipality (urban population))
	["Rangoon"] = {alias_of = "Yangon", display = true},
	["Mandalay"] = {container = "Myanmar"}, -- 1,600,000 (Municipality (urban population))
	["Kathmandu"] = {container = "Nepal"}, -- 3,175,000 (Agglomeration)
	-- Pyongyang is a directly governed city, not in any province
	["Pyongyang"] = {container = "North Korea"}, -- 3,025,000 (Administrative Area (urban population))
	["Muscat"] = {container = "Oman"}, -- 1,620,000 (Agglomeration)
	["Gaza"] = {container = "Palestine", wp = "Gaza City"}, -- 2,275,000 (unindicated)
	["Gaza City"] = {alias_of = "Gaza"},
	["Doha"] = {container = "Qatar"}, -- 2,650,000 (Agglomeration)
	["Colombo"] = {container = "Sri Lanka"}, -- 4,975,000 (unindicated)
	["Damascus"] = {container = "Syria"}, -- 3,975,000 (unindicated; population of low reliability)
	["Aleppo"] = {container = "Syria"}, -- 1,980,000 (unindicated; population of low reliability)
	["Dushanbe"] = {container = "Tajikistan"}, -- 1,270,000 (City)
	["Bangkok"] = {container = "Thailand"}, -- 21,800,000 (Agglomeration)
	-- Chiang Mai not in citypopulation.de, but 1,198,000 urban population in 2021 per Wikipedia
	-- [[w:List_of_municipalities_in_Thailand#Largest_cities_by_urban_population]]
	["Chiang Mai"] = {container = {key = "Chiang Mai Province, Thailand", placetype = "province"}},
	["Chonburi"] = {container = {key = "Chonburi Province, Thailand", placetype = "province"}}, -- 1,570,000 (Agglomeration; including Pattaya)

	-- metro area population stats from https://www.statista.com/statistics/255483/biggest-cities-in-turkey/ as of 2021;
	-- second source is citypopulation.de reference date 2025-01-01.
	["Istanbul"] = {placetype = {"city", "province"}, divs = {"districts"}, container = "Turkey"}, -- 15.2 million; 16,000,000 (Agglomeration)
	["İstanbul"] = {alias_of = "Istanbul", display = true},
	["Ankara"] = {container = {key = "Ankara Province, Turkey", placetype = "province"}}, -- 5.15 million; 5,200,000 (Agglomeration)
	["Izmir"] = {container = {key = "İzmir Province, Turkey", placetype = "province"}, wp = "İzmir"}, -- 2.95 million; 3,025,000 (Agglomeration)
	["İzmir"] = {alias_of = "Izmir", display = true},
	["Bursa"] = {container = {key = "Bursa Province, Turkey", placetype = "province"}}, -- 2.02 million; 2,200,000 (Agglomeration)
	["Adana"] = {container = {key = "Adana Province, Turkey", placetype = "province"}}, -- 1.77 million; 1,780,000 (Agglomeration)
	["Gaziantep"] = {container = {key = "Gaziantep Province, Turkey", placetype = "province"}}, -- 1.71 million; 1,750,000 (Agglomeration)
	["Antalya"] = {container = {key = "Antalya Province, Turkey", placetype = "province"}}, -- 1.3 million; 1,400,000 (Agglomeration)
	["Konya"] = {container = {key = "Konya Province, Turkey", placetype = "province"}}, -- 1.35 million; 1,390,000 (Agglomeration)
	["Diyarbakır"] = {container = {key = "Diyarbakır Province, Turkey", placetype = "province"}}, -- 1.07 million; 1,100,000 (Agglomeration)
	-- Diyarbakır is more common per Ngrams and Google Scholar, but Diyarbakir is the Kurdish form, so we should not
	-- display-canonicalize to the Turkish form Diyarbakır.
	["Diyarbakir"] = {alias_of = "Diyarbakır"},
	["Mersin"] = {container = {key = "Mersin Province, Turkey", placetype = "province"}}, -- 1.03 million; 1,060,000 (Agglomeration)

	["Ashgabat"] = {container = "Turkmenistan"}, -- 1,150,000 (Agglomeration)
	["Dubai"] = {container = "United Arab Emirates"}, -- 6,050,000 (Agglomeration; including Sharjah)
	["Abu Dhabi"] = {container = "United Arab Emirates"}, -- 1,850,000 (City)
	["Sharjah"] = {container = "United Arab Emirates"}, -- 1,800,000 (Metro area 2022-2023 per Wikipedia; separate from Dubai)
	["Tashkent"] = {container = "Uzbekistan"}, -- 3,850,000 (unindicated)
	["Sanaa"] = {container = "Yemen"}, -- 3,275,000 (City; population of low reliability)
	["Sana'a"] = {alias_of = "Sanaa", display = true},
	["Aden"] = {container = "Yemen"}, -- 1,079,060 (?; 2023 estimate from World Population Review per Wikipedia)

	------------------ Europe or Europe-like (Caucasus etc.) ---------------------
	["Yerevan"] = {container = "Armenia"}, -- 1,520,000 (Agglomeration)
	["Vienna"] = {container = "Austria"}, -- 2,375,000 (Agglomeration)
	["Minsk"] = {container = "Belarus"}, -- 2,100,000 (unindicated)
	["Brussels"] = {container = "Belgium"}, -- 2,800,000 (Consolidated Urban Area)
	["Antwerp"] = {container = "Belgium"}, -- 1,270,000 (Consolidated Urban Area)
	["Sofia"] = {container = "Bulgaria"}, -- 1,260,000 (Agglomeration)
	["Zagreb"] = {container = "Croatia"},
	["Prague"] = {container = "Czech Republic"}, -- 1,470,000 (Agglomeration)
	["Brno"] = {container = "Czech Republic"}, -- 729,405 (metro area per Wikipedia as of 2024-01-01 Czech Statistical Office)
	["Olomouc"] = {container = "Czech Republic"}, -- 102,293 (city; included only because someone went crazy creating Olomouc-related terms)
	["Copenhagen"] = {container = "Denmark"}, -- 1,800,000 (Consolidated Urban Area)
	["Helsinki"] = {container = {key = "Uusimaa, Finland", placetype = "region"}}, -- 1,560,000 (Consolidated Urban Area)
	["Tbilisi"] = {container = "Georgia"}, -- 1,430,000 (Agglomeration)
	["Athens"] = {container = "Greece"},
	["Thessaloniki"] = {container = "Greece"},
	["Budapest"] = {container = "Hungary"},
	-- FIXME, per Wikipedia "County Dublin" is now the "Dublin Region"
	["Dublin"] = {container = {key = "County Dublin, Ireland", placetype = "county"}},
	["Riga"] = {container = "Latvia"},
	["Amsterdam"] = {container = {key = "North Holland, Netherlands", placetype = "province"}},
	["Rotterdam"] = {container = {key = "South Holland, Netherlands", placetype = "province"}},
	["The Hague"] = {container = {key = "South Holland, Netherlands", placetype = "province"}},
	-- Christchurch (metro 546,600) and Wellington (metro 439,800) are too small to make it.
	["Auckland"] = {container = {key = "Auckland, New Zealand", placetype = "region"}},
	["Oslo"] = {container = {key = "Oslo, Norway", placetype = "county"}},
	["Warsaw"] = {container = {key = "Masovian Voivodeship, Poland", placetype = "voivodeship"}},
	["Katowice"] = {container = {key = "Silesian Voivodeship, Poland", placetype = "voivodeship"}},
	--- Ngrams (up through 2022) and Google Scholar (>= 2024) confirms the common form "Krakow" without accent.
	["Krakow"] = {container = {key = "Lesser Poland Voivodeship, Poland", placetype = "voivodeship"}, wp = "Kraków"},
	["Kraków"] = {alias_of = "Krakow", display = true},
	["Cracow"] = {alias_of = "Krakow", display = true},
	--- Ngrams (up through 2022) and Google Scholar (>= 2024) confirm "Gdańsk" and "Poznań" with accent.
	["Gdańsk"] = {container = {key = "Pomeranian Voivodeship, Poland", placetype = "voivodeship"}},
	["Gdansk"] = {alias_of = "Gdańsk", display = true},
	["Poznań"] = {container = {key = "Greater Poland Voivodeship, Poland", placetype = "voivodeship"}},
	["Poznan"] = {alias_of = "Poznań", display = true},
	--- Ngrams (up through 2022) and Google Scholar (>= 2024) confirms the common form "Lodz" without accents.
	["Lodz"] = {container = {key = "Lodz Voivodeship, Poland", placetype = "voivodeship"}, wp = "Łódź"},
	["Łódź"] = {alias_of = "Lodz", display = true},
	["Lisbon"] = {container = {key = "Lisbon District, Portugal", placetype = "district"}},
	["Porto"] = {container = {key = "Porto District, Portugal", placetype = "district"}},
	["Oporto"] = {alias_of = "Porto", display = true},
	["Bucharest"] = {container = "Romania"},
	["Belgrade"] = {container = "Serbia"},
	["Stockholm"] = {container = "Sweden"},
	["Zurich"] = {container = "Switzerland"},
	--- Ngrams (up through 2022) and Google Scholar (>= 2024) confirms the common form "Zurich" without umlaut.
	--- Even Wikipedia uses the form without umlaut.
	["Zürich"] = {alias_of = "Zurich", display = true},
	["Kyiv"] = {container = "Ukraine"}, -- not in Kyiv Oblast
	-- Don't display-canonicalize Kiev -> Kyiv because in ancient contexts, Kiev is still more common.
	["Kiev"] = {alias_of = "Kyiv"},
	["Kharkiv"] = {container = {key = "Kharkiv Oblast, Ukraine", placetype = "oblast"}},
	["Odessa"] = {container = {key = "Odesa Oblast, Ukraine", placetype = "oblast"}, wp = "Odesa"},
	-- Don't display-canonicalize Odesa -> Odessa because it may be interpreted as a political statement.
	["Odesa"] = {alias_of = "Odessa"},
	
	------------------ North America, South America ---------------------
	-- Primary figures from citypopulation.de retrieved on 2025-04-26 (reference date 2025-01-01);
	-- Wikipedia metropolitan figures from [[w:List of metropolitan areas in the Americas]] based on per-country data;
	-- Wikipedia city limits figures from [[w:List of largest cities in the Americas]].
	["Buenos Aires"] = {container = "Argentina"}, -- 16,800,000 (Consolidated Urban Area; 13,985,794 metropolitan area per Wikipedia)
	["Córdoba, Argentina"] = {container = "Argentina", wp = "%l, %c"}, -- 1,810,000 (Consolidated Urban Area; 1,505,25 city limits per Wikipedia)
	-- to avoid confusion with Córdoba in Spain
	["Córdoba"] = {alias_of = "Córdoba, Argentina"},
	["Cordoba"] = {alias_of = "Córdoba, Argentina", display = "Córdoba"},
	["Rosario"] = {container = "Argentina", wp = "%l, Santa Fe"}, -- 1,510,000 (Consolidated Urban Area; 1,348,725 metropolitan area per Wikipedia)
	["Mendoza"] = {container = "Argentina", wp = "%l, %c"}, -- 1,180,000 (Consolidated Urban Area)
	["San Miguel de Tucumán"] = {container = "Argentina"}, -- 1,110,000 (Consolidated Urban Area)
	["Tucumán"] = {alias_of = "San Miguel de Tucumán"},
	["Tucuman"] = {alias_of = "San Miguel de Tucumán", display = "Tucumán"},
	["Santa Cruz de la Sierra"] = {container = "Bolivia"}, -- 1,960,000 (Consolidated Urban Area); 1,606,671 (city limits per Wikipedia)
	["Santa Cruz"] = {alias_of = "Santa Cruz de la Sierra"},
	["La Paz"] = {container = "Bolivia"}, -- 1,870,000 (Consolidated Urban Area; composed of El Alto, now slightly larger, and La Paz)
	["El Alto"] = {container = "Bolivia"},
	["Cochabamba"] = {container = "Bolivia"}, -- 1,280,000 (Consolidated Urban Area)
	["Santiago"] = {container = "Chile"}, -- 8,400,000 (Consolidated Urban Area; 6,903,479 city limits? per Wikipedia)
	["Valparaíso"] = {container = "Chile"}, -- 1,060,000 (Consolidated Urban Area)
	["Valparaiso"] = {alias_of = "Valparaíso"}, -- 1,060,000 (Consolidated Urban Area)
	["Bogotá"] = {container = "Colombia"}, -- 10,600,000 (Agglomeration; 12,772,828 metropolitan area per Wikipedia)
	["Bogota"] = {alias_of = "Bogotá", display = true},
	["Medellín"] = {container = "Colombia"}, -- 4,350,000 (Agglomeration; 4,068,000 metropolitan area per Wikipedia)
	["Medellin"] = {alias_of = "Medellín", display = true},
	["Cali"] = {container = "Colombia"}, -- 2,975,000 (Agglomeration; 2,837,000 metropolitan area per Wikipedia)
	["Barranquilla"] = {container = "Colombia"}, -- 2,375,000 (Agglomeration; 1,341,160 city limits per Wikipedia)
	["Bucaramanga"] = {container = "Colombia"}, -- 1,380,000 (Agglomeration)
	["Cartagena, Colombia"] = {container = "Colombia", wp = "%l, %c"}, -- 1,250,000 (Agglomeration)
	-- to avoid confusion with Cartagena, Spain
	["Cartagena"] = {alias_of = "Cartagena, Colombia"},
	["Cúcuta"] = {container = "Colombia"}, -- 1,130,000 (Agglomeration)
	["Cucuta"] = {alias_of = "Cúcuta", display = true},
	-- to avoid conflict with San Jose, California
	["San José, Costa Rica"] = {container = "Costa Rica", wp = "%l, %c"}, -- 2,450,000 (Municipality (urban population); 3,160,000 metropolitan area per Wikipedia)
	["San José"] = {alias_of = "San José, Costa Rica"},
	["San Jose"] = {alias_of = "San José, Costa Rica"}, -- display = "San José"; causes error due to San Jose alias for California city; FIXME
	["Havana"] = {container = "Cuba"}, -- 2,150,000 (City; 2,137,847 city limits? per Wikipedia)
	["Santo Domingo"] = {container = "Dominican Republic"}, -- 3,900,000 (Municipality (urban population); 4,274,651 ??? per Wikipedia)
	["Guayaquil"] = {container = "Ecuador"}, -- 3,350,000 (Agglomeration; 3,092,000 metro area? per Wikipedia)
	["Quito"] = {container = "Ecuador"}, -- 2,875,000 (Agglomeration; 2,889,703 metro area? per Wikipedia)
	["San Salvador"] = {container = "El Salvador"}, -- 1,580,000 (Municipality (urban population))
	["Guatemala City"] = {container = "Guatemala"}, -- 3,375,000 (Municipality (urban population); 3,160,000 metro area? per Wikipedia)
	["Port-au-Prince"] = {container = "Haiti"}, -- 3,050,000 (Agglomeration; population of low reliability; 2,915,000 metro area? per Wikipedia)
	["San Pedro Sula"] = {container = "Honduras"}, -- 1,330,000 (Consolidated Urban Area)
	["Tegucigalpa"] = {container = "Honduras"}, -- 1,220,000 (Urban Area)
	["Managua"] = {container = "Nicaragua"}, -- 1,400,000 (Consolidated Urban Area)
	["Panama City"] = {container = "Panama"}, -- 1,430,000 (Urban Area)
	["Asunción"] = {container = "Paraguay"}, -- 2,350,000 (Municipality (urban population))
	["Lima"] = {container = "Peru"}, -- 12,000,000 (Agglomeration; 11,283,787 ??? per Wikipedia)
	["Arequipa"] = {container = "Peru"}, -- 1,210,000 (Agglomeration)
	["San Juan"] = {container = {key = "Puerto Rico", placetype = "commonwealth"}, wp = "%l, %c"}, -- 1,910,000 (Consolidated Urban Area)
	["Montevideo"] = {container = "Uruguay"}, -- 1,810,000 (Agglomeration; 1,302,954 ??? per Wikipedia)
	["Caracas"] = {container = "Venezuela"}, -- 3,850,000 (Consolidated Urban Area; 5,243,301 ??? per Wikipedia)
	["Maracaibo"] = {container = "Venezuela"}, -- 2,825,000 (Consolidated Urban Area; 5,278,448 ??? per Wikipedia)
	-- to avoid confusion with Valencia (city and autonomous community of Spain)
	["Valencia, Venezuela"] = {container = "Venezuela", wp = "%l, %c"}, -- 2,100,000 (Consolidated Urban Area)
	["Valencia"] = {alias_of = "Valencia, Venezuela"},
	["Maracay"] = {container = "Venezuela"}, -- 1,480,000 (Consolidated Urban Area)
	["Barquisimeto"] = {container = "Venezuela"}, -- 1,360,000 (Consolidated Urban Area)
}

export.misc_cities_group = {
	canonicalize_key_container = make_canonicalize_key_container(nil, "country"),
	default_placetype = "city",
	data = export.misc_cities,
}

--[==[ var:
List of all known locations, in groups. The first group lists continents and continental regions, followed by three
groups listing top-level locations: countries, "country-like entities" (de-facto/unrecognized/etc. countries and
dependent territories) and former polities (countries, empires, etc.). After that come first-level subpolities
(administrative divisions) of several, mostly large, countries, followed by groups of cities. China and the United
Kingdom include second-level subpolities (in the case of China, only the largest ones as the full list runs in the
hundreds).
]==]
export.locations = {
	export.continents_group,
	export.countries_group,
	export.country_like_entities_group,
	export.former_countries_group,
	export.australia_group,
	export.austria_group,
	export.bangladesh_group,
	export.brazil_group,
	export.canada_group,
	export.china_group,
	export.china_prefecture_level_cities_group,
	export.china_prefecture_level_cities_group_2,
	export.finland_group,
	export.france_group,
	export.france_departments_group,
	export.germany_group,
	export.greece_group,
	export.india_group,
	export.indonesia_group,
	export.iran_group,
	export.ireland_group,
	export.italy_group,
	export.japan_group,
	export.laos_group,
	export.lebanon_group,
	export.malaysia_group,
	export.malta_group,
	export.mexico_group,
	export.moldova_group,
	export.morocco_group,
	export.netherlands_group,
	export.new_zealand_group,
	export.nigeria_group,
	export.north_korea_group,
	export.norway_group,
	export.pakistan_group,
	export.philippines_group,
	export.poland_group,
	export.portugal_group,
	export.romania_group,
	export.russia_group,
	export.saudi_arabia_group,
	export.south_africa_group,
	export.south_korea_group,
	export.spain_group,
	export.taiwan_group,
	export.thailand_group,
	export.turkey_group,
	export.ukraine_group,
	export.united_kingdom_group,
	export.united_states_group,
	export.england_group,
	export.northern_ireland_group,
	export.scotland_group,
	export.wales_group,
	export.vietnam_group,
	export.australia_cities_group,
	export.brazil_cities_group,
	export.canada_cities_group,
	export.france_cities_group,
	export.germany_cities_group,
	export.india_cities_group,
	export.indonesia_cities_group,
	export.italy_cities_group,
	export.japan_cities_group,
	export.mexico_cities_group,
	export.nigeria_cities_group,
	export.pakistan_cities_group,
	export.philippines_cities_group,
	export.russia_cities_group,
	export.saudi_arabia_cities_group,
	export.south_korea_cities_group,
	export.spain_cities_group,
	export.taiwan_cities_group,
	export.united_kingdom_cities_group,
	export.united_states_cities_group,
	export.new_york_boroughs_group,
	export.vietnam_cities_group,
	export.misc_cities_group,
}

return export