local export = {}

local m_locations = require("Module:place/locations")
local m_links = require("Module:links")
local m_table = require("Module:table")
local m_strutils = require("Module:string utilities")
local en_utilities_module = "Module:en-utilities"

local dump = mw.dumpObject
local insert = table.insert
local concat = table.concat
local unpack = unpack or table.unpack -- Lua 5.2 compatibility

local ucfirst = m_strutils.ucfirst
local ulower = m_strutils.lower
local rmatch = m_strutils.match
local split = m_strutils.split

function export.remove_links_and_html(text)
	text = m_links.remove_links(text)
	return text:gsub("<.->", "")
end


function export.maybe_singularize_placetype(placetype)
	if not placetype then
		return nil
	end
	if export.plural_placetype_to_singular[placetype] then
		return export.plural_placetype_to_singular[placetype]
	end
	local retval = require(en_utilities_module).singularize(placetype)
	if retval == placetype then
		return nil
	end
	return retval
end

function export.pluralize_placetype(placetype, do_ucfirst)
	local ptdata = export.placetype_data[placetype]
	if ptdata and ptdata.plural then
		placetype = ptdata.plural
	else
		placetype = require(en_utilities_module).pluralize(placetype)
	end
	if do_ucfirst then
		return ucfirst(placetype)
	else
		return placetype
	end
end


function export.get_placetype_data(placetype, from_category)
	local ptdata = export.placetype_data[placetype]
	if ptdata then
		return placetype, ptdata, "direct"
	end
	if from_category then
		ptdata = export.placetype_data[placetype .. "!"]
		if ptdata then
			return placetype .. "!", ptdata, "direct-category"
		end
	end
	local sg_placetype = export.maybe_singularize_placetype(placetype)
	if sg_placetype then
		ptdata = export.placetype_data[sg_placetype]
		if ptdata then
			return sg_placetype, ptdata, "plural"
		end
	end
	return nil
end


function export.placetype_is_ignorable(placetype)
	return placetype == "and" or placetype == "or" or placetype:find("^%(")
end


function export.resolve_placetype_aliases(placetype)
	return export.placetype_aliases[placetype] or placetype
end


function export.get_placetype_prop(placetype, key)
	-- Usually we are called on equivalent placetypes returned from `get_placetype_equivs`, in which case placetype
	-- aliases have been resolved, but sometimes not, e.g. when fetching the indefinite article in
	-- get_placetype_article(). `resolve_placetype_aliases` is just a simple lookup and it doesn't hurt to do it twice.
	placetype = export.resolve_placetype_aliases(placetype)
	if export.placetype_data[placetype] then
		return export.placetype_data[placetype][key]
	else
		return nil
	end
end

function export.split_qualifiers_from_placetype(placetype, no_canon_qualifiers)
	local splits = {{nil, nil, export.resolve_placetype_aliases(placetype)}}
	local prev_qualifier = nil
	while true do
		local qualifier, reduced_placetype = placetype:match("^(.-) (.*)$")
		if qualifier then
			local canon = export.placetype_qualifiers[qualifier]
			if canon == nil then
				break
			end
			local new_qualifier = qualifier
			if type(canon) == "table" then
				canon = canon.link
			end
			if not no_canon_qualifiers and canon ~= false then
				if canon == true then
					new_qualifier = "[[" .. qualifier .. "]]"
				else
					new_qualifier = canon
				end
			end
			insert(splits, {prev_qualifier, new_qualifier, export.resolve_placetype_aliases(reduced_placetype)})
			prev_qualifier = prev_qualifier and prev_qualifier .. " " .. new_qualifier or new_qualifier
			placetype = reduced_placetype
		else
			break
		end
	end
	return splits
end

function export.get_placetype_equivs(placetype, props)
	local no_fallback, no_split_qualifiers, no_check_for_inherently_former, from_category, register_former_as_non_former
	local form_of_directive
	if props then
		no_fallback, no_split_qualifiers, no_check_for_inherently_former, from_category, register_former_as_non_former =
			props.no_fallback, props.no_split_qualifiers, props.no_check_for_inherently_former, props.from_category,
			props.register_former_as_non_former
		form_of_directive = props.form_of_directive
	end
	local equivs = {}

	local function insert_placetype_and_fallbacks(qualifier, placetype, form_of_prefix)
		local function insert_equiv(pt)
			if form_of_prefix then
				-- Let's say the user says {{tl|place|pt|@official name of:Cuba|island country|r/Caribbean}} and we have
				-- no entry for `OFFICIAL_NAME_OF island country` but we do for `OFFICIAL_NAME_OF country` (which we end
				-- up processing because `island country` falls back to `country`), and that entry in turn is defined
				-- using a fallback. We have to insert that fallback-of-fallback, and the easiest/cleanest way of
				-- handling this is by calling ourselves recursively.
				insert_placetype_and_fallbacks(qualifier, form_of_prefix .. " " .. pt)
			else
				insert(equivs, {qualifier=qualifier, placetype=pt})
			end
		end

		-- Insert the placetype, along with any fallbacks.
		local canon_placetype, ptdata, ptmatch = export.get_placetype_data(placetype, from_category)
		if ptdata then
			insert_equiv(canon_placetype)
			if no_fallback then
				return
			end
			local first_placetype = #equivs + 1
			local prev_placetype = nil
			while true do
				local pt_value = export.placetype_data[canon_placetype]
				if pt_value.fallback then
					insert_equiv(pt_value.fallback)
					local last_placetype = #equivs
					if last_placetype - first_placetype >= 10 then
						local fallback_loop = {}
						for i = first_placetype, last_placetype do
							insert(fallback_loop, equivs[i].placetype)
						end
					end
					prev_placetype = canon_placetype
					canon_placetype = pt_value.fallback
				else
					break
				end
			end
		end
	end

	local function process_and_insert_placetype(qualifier, reduced_placetype)
		if form_of_directive then
			-- First check for e.g. `OFFICIAL_NAME_OF island country` and its fallbacks; then we look for fallbacks of
			-- `island country` and check e.g. `OFFICIAL_NAME_OF country` and its fallbacks. All of this is handled by
			-- `insert_placetype_and_fallbacks()` with appropriate parameters. After that, check the general class of
			-- the directive, e.g. `subpolity` if something like `district` is given. (Eventually, we check for
			-- `OFFICIAL_NAME_OF place` as a backup, but this happens at the end outside the loop over qualifiers.)
			insert_placetype_and_fallbacks(qualifier, reduced_placetype, form_of_directive)
			if not no_fallback then
				local reduced_placetype_equivs = export.get_placetype_equivs(reduced_placetype)
				local directive_type = export.get_equiv_placetype_prop_from_equivs(reduced_placetype_equivs,
					function(pt) return export.get_placetype_prop(pt, form_of_directive .. "_type") or
						export.get_placetype_prop(pt, "class") end
				)
				if not directive_type then
					local pt_data = export.get_equiv_placetype_prop_from_equivs(reduced_placetype_equivs,
						function(pt) return export.placetype_data[pt] end
					)
				elseif directive_type ~= "!" then
					insert_placetype_and_fallbacks(qualifier, directive_type, form_of_directive)
				end
			end
		else
			insert_placetype_and_fallbacks(qualifier, reduced_placetype)
		end
	end

	-- Successively split off recognized qualifiers and loop over successively greater sets of qualifiers from the left
	-- (unless `no_split_qualifiers` is specified, in which case we don't check for qualifiers).
	local splits
	if no_split_qualifiers then
		splits = {{nil, nil, export.resolve_placetype_aliases(placetype)}}
	else
		splits = export.split_qualifiers_from_placetype(placetype)
	end

	for _, split in ipairs(splits) do
		local prev_qualifier, this_qualifier, reduced_placetype = unpack(split, 1, 3)

		-- If a special "former" qualifier like `former` or `historical` isn't present, and
		-- `no_check_for_inherently_former` is not given (this flag is used to avoid infinite loops), check for
		-- "inherently former" placetypes like `satrapy` and `treaty port` that always refer to no-longer-existing
		-- placetypes, and handle accordingly.
		local unlinked_this_qualifier
		if this_qualifier and this_qualifier:find("%[") then
			unlinked_this_qualifier = export.remove_links_and_html(this_qualifier)
		else
			unlinked_this_qualifier = this_qualifier
		end
		local former_qualifiers = this_qualifier and export.former_qualifiers[unlinked_this_qualifier] or nil
		if not former_qualifiers and not no_check_for_inherently_former then
			former_qualifiers = export.get_equiv_placetype_prop(reduced_placetype,
				function(pt) return export.get_placetype_prop(pt, "inherently_former") end,
				{no_check_for_inherently_former = true})
		end

		-- If a special "former" qualifier like `former` or `historical` is present, map it to the appropriate internal
		-- qualifiers (`ANCIENT` and/or `FORMER`, which are written in all-caps to distinguish them from user-specified
		-- qualifiers), fetch the `former_type` property, and treat the placetype as if a concatenation of the mapped
		-- qualifier(s) and the value of `former_type`. For example, if `medieval village` is given, we map `medieval`
		-- to `ANCIENT` and `FORMER`, and `village` to its `former_type` of `settlement`, and enter the placetypes
		-- `ANCIENT settlement` and `FORMER settlement` (in that order) into `equivs`. If the placetype following the
		-- "former" qualifier is recognized in `placetype_data` but has no `former_type` and no fallback with a
		-- `former_type` specified, it is an internal error; but if the placetype isn't recognized (e.g. something like
		-- `former greenhouse` is specified and we don't have an entry for `greenhouse`), just track the occurrence and
		-- don't enter anything into `equivs`.
		if former_qualifiers then
			-- FIXME: Should we respect `no_fallback` here? My instinct says no.
			local reduced_placetype_equivs = export.get_placetype_equivs(reduced_placetype, {
				no_check_for_inherently_former = true
			})
			local former_type = export.get_equiv_placetype_prop_from_equivs(reduced_placetype_equivs,
				function(pt) return export.get_placetype_prop(pt, "former_type") or
					export.get_placetype_prop(pt, "class") end
			)
			if not former_type then
				local pt_data = export.get_equiv_placetype_prop_from_equivs(reduced_placetype_equivs,
					function(pt) return export.placetype_data[pt] end
				)
			elseif former_type ~= "!" then
				-- First check directly for `ANCIENT/FORMER` + the original following placetype. This makes it possible
				-- for (e.g.) former provinces of the Roman empire to be categorized specially.
				for _, former_qualifier in ipairs(former_qualifiers) do
					process_and_insert_placetype(prev_qualifier, former_qualifier .. " " .. reduced_placetype)
				end
				for _, former_qualifier in ipairs(former_qualifiers) do
					process_and_insert_placetype(prev_qualifier, former_qualifier .. " " .. former_type)
				end
				-- HACK! See explanation above for `register_former_as_non_former`.
				if register_former_as_non_former then
					process_and_insert_placetype(prev_qualifier, reduced_placetype)
				end
				-- If we're processing a form-of directive, after doing everything else we do
				-- `DIRECTIVE ANCIENT/FORMER place` e.g. `OFFICIAL_NAME_OF FORMER place` as a backup.
				if form_of_directive and not no_fallback then
					for _, former_qualifier in ipairs(former_qualifiers) do
						insert_placetype_and_fallbacks(prev_qualifier, form_of_directive .. " " .. former_qualifier ..
							" place")
					end
				end

				-- Don't continue processing equivs. The reason is probably the same as the `break` below for
				-- qualifier_to_placetype_equivs[]; categories for `former BLAH` are set using `default`, and
				-- non-former equivs will otherwise take precedence.
				break
			end
		end

		-- Then see if the rightmost split-off qualifier is in qualifier_to_placetype_equivs
		-- (e.g. 'fictional *' -> 'fictional location'). If so, add the mapping.
		if this_qualifier and export.qualifier_to_placetype_equivs[unlinked_this_qualifier] then
			insert(equivs, {
				qualifier=prev_qualifier,
				placetype=export.qualifier_to_placetype_equivs[unlinked_this_qualifier]
			})
			-- Don't continue processing equivs; otherwise, if we specify 'mythological city', even though the
			-- equivalent entry for 'mythological location' gets inserted ahead of the entry for 'city', the
			-- latter ends up generating the category because the category for 'mythological location' is set as
			-- the default value, which is used only when no non-default category can be found.
			break
		end

		-- Finally, join the rightmost split-off qualifier to the previously split-off qualifiers to form a combined
		-- qualifier, and add it along with reduced_placetype and any mapping in placetype_data for reduced_placetype.
		-- NOTE: The first time through this loop, both `prev_qualifier` and `this_qualifier` are nil, and this inserts
		-- the full placetype into `equivs`.
		local qualifier = prev_qualifier and prev_qualifier .. " " .. this_qualifier or this_qualifier
		process_and_insert_placetype(qualifier, reduced_placetype)

		-- If `no_fallback` and there's an entry in `placetype_data` for this placetype, don't include any reduced
		-- placetypes to avoid the "overseas territory treated as a territory" issue describe above.
		if no_fallback then
			local canon_placetype, ptdata, ptmatch = export.get_placetype_data(reduced_placetype, from_category)
			if canon_placetype then
				break
			end
		end
	end

	-- If we're processing a form-of directive, after doing everything else we do `DIRECTIVE place` e.g.
	-- `OFFICIAL_NAME_OF place` as a backup; but only if either the placetype as a whole is recognized or the placetype
	-- begins with a recognized qualifier. This latter check is to avoid categorizing into e.g.
	-- [[Category:en:Former names of places]] in an invocation like
	-- {{place|en|@former name of:Democratic Republic of the Congo|country|r/Central Africa|;|used from 1971–1997}};
	-- the `used from 1971–1997` gets treated as a placetype and we're called on it.
	if form_of_directive and not no_fallback and (splits[2] or export.get_placetype_data(placetype, from_category)) then
		insert_placetype_and_fallbacks(nil, form_of_directive .. " place")
	end

	return equivs
end


function export.get_equiv_placetype_prop_from_equivs(equivs, fun, continue_on_nil_only)
	for _, equiv in ipairs(equivs) do
		local retval = fun(equiv.placetype)
		if continue_on_nil_only and retval ~= nil or not continue_on_nil_only and retval then
			return retval, equiv
		end
	end
	return nil, nil
end


function export.get_equiv_placetype_prop(placetype, fun, props)
	if not placetype then
		return fun(nil), nil
	end
	return export.get_equiv_placetype_prop_from_equivs(export.get_placetype_equivs(placetype, props), fun,
		props and props.continue_on_nil_only)
end


function export.get_placetype_article(placetype, ucfirst)
	local art
	local qualifier, reduced_placetype = placetype:match("^(.-) (.*)$")
	if qualifier then
		local canon = export.placetype_qualifiers[qualifier]
		if type(canon) == "table" then
			art = canon.article
		end
	end
	if art == false then
		return art
	end
	if art == nil then
		local placetype_use_the = export.get_equiv_placetype_prop(placetype,
			function(pt) return export.get_placetype_prop(pt, "entry_placetype_use_the") end)
		if placetype_use_the then
			art = "the"
		else
			art = export.get_placetype_prop(placetype, "entry_placetype_indefinite_article")
			if not art then
				art = require(en_utilities_module).get_indefinite_article(placetype)
			end
		end
	end

	if ucfirst then
		art = m_strutils.ucfirst(art)
	end

	return art
end


function export.get_placetype_entry_preposition(placetype)
	local pt_prep = export.get_equiv_placetype_prop(placetype,
		function(pt) return export.get_placetype_prop(pt, "preposition") end
	)
	return pt_prep or "in"
end


function export.key_holonym_into_place_desc(place_desc, holonym)
	if not holonym.placetype then
		return
	end

	-- Key in equivalent placetypes, so that e.g. `cities/San Francisco` gets keyed under `city`; but don't do
	-- fallbacks, as it doesn't seem correct for the "do other holonyms of the same placetype" algorithm to do holonyms
	-- of different types just because they have the same fallback.
	local equiv_placetypes = export.get_placetype_equivs(holonym.placetype, {no_fallback = true})
	local unlinked_placename = holonym.unlinked_placename
	for _, equiv in ipairs(equiv_placetypes) do
		local placetype = equiv.placetype
		if not place_desc.holonyms_by_placetype then
			place_desc.holonyms_by_placetype = {}
		end
		if not place_desc.holonyms_by_placetype[placetype] then
			place_desc.holonyms_by_placetype[placetype] = {unlinked_placename}
		else
			insert(place_desc.holonyms_by_placetype[placetype], unlinked_placename)
		end
	end
end

local function make_placetype_link(link, sg_placetype, orig_placetype, ptdata, from_category, noerror)
	if link == true then
		if orig_placetype then
			return ("[[%s|%s]]"):format(sg_placetype, orig_placetype)
		else
			return ("[[%s]]"):format(sg_placetype)
		end
	elseif link == "w" then
		return ("[[w:%s|%s]]"):format(sg_placetype, orig_placetype or sg_placetype)
	elseif link == "separately" then
		if orig_placetype then
			local sg_words = split(sg_placetype, " ")
			local orig_words = split(orig_placetype, " ")
            for i = 1, #sg_words do
                if sg_words[i] == orig_words[i] then
                    sg_words[i] = ("[[%s]]"):format(sg_words[i])
                else
                    sg_words[i] = ("[[%s|%s]]"):format(sg_words[i], orig_words[i])
                end
            end
            return concat(sg_words, " ")
		else
			return (sg_placetype:gsub("([^ ]+)", "[[%1]]"))
		end
	elseif link:find("^%+") then
		link = link:sub(2) -- discard initial +
		return ("[[%s|%s]]"):format(link, orig_placetype or sg_placetype)
	elseif not orig_placetype then
		return link
	else
		return require(en_utilities_module).pluralize(link)
	end
end

function export.get_placetype_display_form(placetype, category_type, return_full, noerror)
	local from_category = not not category_type
	local canon_placetype, ptdata, ptmatch = export.get_placetype_data(placetype, from_category)
	if canon_placetype then
		local raw_link
		local function is_linked_string(str)
			return type(str) == "string" and str:find("%[%[")
		end
		if category_type then
			local fetched_full
			local function fetch_maybe_full(prop)
				local retval = ptdata["full_" .. prop]
				if retval ~= nil then
					if return_full then
						return retval, true
					end
				end
				return ptdata[prop], false
			end
			local function maybe_prefix(str)
				if return_full and not fetched_full then
					return "names of " .. str
				else
					return str
				end
			end
			-- Careful with `false` as possible value.
			if category_type == "top-level" then
				raw_link, fetched_full = fetch_maybe_full("category_link_top_level")
			elseif category_type == "noncity" then
				raw_link, fetched_full = fetch_maybe_full("category_link_before_noncity")
			elseif category_type == "city" then
				raw_link, fetched_full = fetch_maybe_full("category_link_before_city")
			end
			if type(raw_link) == "string" then
				return maybe_prefix(raw_link), ptdata
			elseif raw_link ~= nil then
				return raw_link, ptdata
			end
			raw_link, fetched_full = fetch_maybe_full("category_link")
			if raw_link == false then
				return raw_link, ptdata
			end
			if is_linked_string(raw_link) then
				return maybe_prefix(raw_link), ptdata
			end
			if ptmatch == "plural" then
				raw_link, fetched_full = fetch_maybe_full("plural_link")
				if raw_link == false then
					return raw_link, ptdata
				end
				if is_linked_string(raw_link) then
					return maybe_prefix(raw_link), ptdata
				end
			end
			if raw_link == nil then
				raw_link, fetched_full = fetch_maybe_full("link")
			end
			if raw_link == false then
				return raw_link, ptdata
			end
			return maybe_prefix(make_placetype_link(raw_link, canon_placetype,
				placetype ~= canon_placetype and placetype or nil, ptdata, from_category, noerror)), ptdata
		else
			if ptmatch == "plural" then
				raw_link = ptdata.plural_link
				if is_linked_string(raw_link) then
					return raw_link, ptdata
				end
			end
			if raw_link == nil then
				raw_link = ptdata.link
			end
			return make_placetype_link(raw_link, canon_placetype,
				placetype ~= canon_placetype and placetype or nil, ptdata, from_category, noerror), ptdata
		end
	end

	return nil
end


local function resolve_unlinked_placename_display_aliases(placetype, placename)
	local equiv_placetypes = export.get_placetype_equivs(placetype)
	for i, equiv in ipairs(equiv_placetypes) do
		equiv_placetypes[i] = equiv.placetype
	end
	local all_display_aliases_found = {}
	local all_others_found = {}
	for group, key, spec in m_locations.iterate_matching_location {
		placetypes = equiv_placetypes,
		placename = placename,
		alias_resolution = "display",
	} do
		if spec.alias_of and spec.display then
			insert(all_display_aliases_found, {group, key, spec, spec.display_as_full})
		else
			insert(all_others_found, {group, key, spec})
		end
	end
	if not all_display_aliases_found[1] then
		return placename
	else
		local group, key, spec, as_full = unpack(all_display_aliases_found[1])
		local full, elliptical = m_locations.key_to_placename(group, key)
		return as_full and full or elliptical
	end
end

function export.resolve_placename_display_aliases(placetype, placename)
	-- If the placename is a link, apply the alias inside the link.
	-- This pattern matches both piped and unpiped links. If the link is not piped, the second capture (linktext) will
	-- be empty.
	local link, linktext = rmatch(placename, "^%[%[([^|%[%]]+)|?([^|%[%]]-)%]%]$")
	if link then
		if linktext ~= "" then
			local alias = resolve_unlinked_placename_display_aliases(placetype, linktext)
			return "[[" .. link .. "|" .. alias .. "]]"
		else
			local alias = resolve_unlinked_placename_display_aliases(placetype, link)
			return "[[" .. alias .. "]]"
		end
	else
		return resolve_unlinked_placename_display_aliases(placetype, placename)
	end
end

function export.get_prefixed_key(key, spec)
	if spec.the then
		return "the " .. key
	else
		return key
	end
end

-- Necessary for use by [[Module:place]]. FIXME: Reorganize the modules so this isn't necessary.
export.iterate_matching_location = m_locations.iterate_matching_location

function export.get_holonyms_to_check(place_desc, first_holonym_index, include_raw_text_holonyms)
	local stop_at_also = not not first_holonym_index
	return function(place_desc, index)
		while true do
			index = index + 1
			local this_holonym = place_desc.holonyms[index]
			-- If we were passed in a starting holonym index, go up to but not including a holonym marked with `:also`
			-- (continue_cat_loop); the categorization code will then restart the loop at that holonym. That holonym
			-- will have `:also` marked on it, so make sure not to stop immediately if the first holonym is marked with
			-- `:also`.
			if not this_holonym or stop_at_also and index > first_holonym_index and this_holonym.continue_cat_loop then
				return nil
			end
			-- If not placetype, we're processing raw text, which we normally want to skip.
			if include_raw_text_holonyms or this_holonym.placetype then
				return index, this_holonym
			end
		end
	end, place_desc, first_holonym_index and first_holonym_index - 1 or 0
end

function export.iterate_matching_holonym_location(data)
	local holonym_placetype, holonym_placename, holonym_index, place_desc =
		data.holonym_placetype, data.holonym_placename, data.holonym_index, data.place_desc
	local matching_location_iterator = m_locations.iterate_matching_location {
		placetypes = holonym_placetype,
		placename = holonym_placename,
	}
	return function()
		while true do
			local group, key, spec = matching_location_iterator()
			if not group then
				return nil
			end
			local container_trail = {}
			-- For each level of container, check that there are no mismatches (i.e. other location of the same
			-- placetype) mentioned. We allow a mismatch at a given level if there's also a match with the container
			-- at that level. For example, in the case of Kansas City, defined in [[Module:place/locations]] as a city
			-- in Missouri, if we define it as {{tl|place|city|s/Missouri,Kansas}}, we ignore the mismatching state of
			-- Kansas because the correct state of Missouri was also mentioned. But imagine we are defining Newark,
			-- Delaware as {{tl|place|city|s/Delaware|c/US}} and (as is the case) we have an entry for Newark, New
			-- Jersey in [[Module:place/locations]]. Just because the containing location `US` matches isn't enough,
			-- because Newark, NJ also has New Jersey as a containing location and there's a mismatch at that level. If
			-- there are no mismatches at any level we assume we're dealing with the right known location.
			--
			-- If at a given level there are multiple containing locations, we count a match if any holonym matches any
			-- containing location, and a mismatch only if a holonym exists of the same placetype that doesn't match any
			-- containing location.
			local containers_mismatch = false
			for containers in m_locations.iterate_containers(group, key, spec) do
				insert(container_trail, containers)
				local match_at_level = false
				local mismatch_at_level = false
				for other_holonym_index, other_holonym in export.get_holonyms_to_check(place_desc,
					holonym_index and holonym_index + 1 or nil) do
					local other_source_holonym = other_holonym.augmented_from_holonym
					if other_source_holonym and other_source_holonym.placetype == holonym_placetype and
						other_source_holonym.unlinked_placename ~= holonym_placename then
							-- Ignore holonyms added during the augmentation process for other holonyms of the same
							-- placetype as the placetype of the holonym we're considering. See comment in
							-- augment_holonyms_with_container() for why we do this.
							-- continue; grrr, no 'continue' in Lua
					else
						local holonym_matches_at_level = false
						local holonym_exists_with_same_placetype = false
						for _, container in ipairs(containers) do
							if not container.spec.no_check_holonym_mismatch then
								local full_container_placename, elliptical_container_placename =
									m_locations.key_to_placename(container.group, container.key)
								local placetypes = container.spec.placetype
								if type(placetypes) ~= "table" then
									placetypes = {placetypes}
								end
								local placetype_equivs = {}
								for _, pt in ipairs(placetypes) do
									m_table.extend(placetype_equivs, export.get_placetype_equivs(pt))
								end
								local this_holonym_matches = export.get_equiv_placetype_prop_from_equivs(
									placetype_equivs, function(placetype)
										return other_holonym.placetype == placetype and
											(other_holonym.unlinked_placename == full_container_placename or
											other_holonym.unlinked_placename == elliptical_container_placename)
									end
								)
								if this_holonym_matches then
									holonym_matches_at_level = true
									break
								end
								local this_holonym_exists_with_same_placetype = export.get_equiv_placetype_prop_from_equivs(
									placetype_equivs, function(placetype)
										return other_holonym.placetype == placetype
									end
								)
								if this_holonym_exists_with_same_placetype then
									-- We seem to have a mismatch at this level. But before we decide conclusively that this
									-- is the case, check to see whether the putative mismatch is an alias and matches when
									-- we resolve the alias.
									for oh_group, oh_key, oh_spec, oh_container_trail in 
										export.iterate_matching_holonym_location {
											holonym_placetype = other_holonym.placetype,
											holonym_placename = other_holonym.unlinked_placename,
											holonym_index = other_holonym_index,
											place_desc = place_desc,
										} do
										local oh_full_placename, oh_elliptical_placename =
											m_locations.key_to_placename(oh_group, oh_key)
										if oh_full_placename == full_container_placename or
											oh_elliptical_placename == elliptical_container_placename then
											-- Alias matched when resolved.
											this_holonym_matches = true
											break
										end
									end
									if this_holonym_matches then
										-- Alias matched above when resolved.
										holonym_matches_at_level = true
										break
									else
										-- Not an alias, or doesn't match when resolved. We have a true mismatch.
										holonym_exists_with_same_placetype = true
									end
								end
							end
						end
						if holonym_matches_at_level then
							match_at_level = true
							break
						end
						if holonym_exists_with_same_placetype then
							mismatch_at_level = true
						end
					end
				end
				if not match_at_level and mismatch_at_level then
					containers_mismatch = true
					break
				end
			end
			if not containers_mismatch then
				return group, key, spec, container_trail
			end
		end
	end
end

function export.find_matching_holonym_location(data)
	local all_found = {}
	for group, key, spec, container_trail in export.iterate_matching_holonym_location(data) do
		insert(all_found, {group, key, spec, container_trail})
	end
	if not all_found[1] then
		return nil
	elseif all_found[2] then
		local holonym_placetype = data.holonym_placetype
		if type(holonym_placetype) == "table" then
			holonym_placetype = concat(holonym_placetype, ",")
		end
		local found_keys = {}
		for _, found in ipairs(all_found) do
			local _, key, _, _ = unpack(found)
			insert(found_keys, key)
		end
		error(("Found multiple matching locations for holonym '%s/%s'; specify disambiguating context in the " ..
			"containing holonyms: %s"):format(holonym_placetype, data.holonym_placename, dump(found_keys)))
	else
		return unpack(all_found[1])
	end
end


export.placetype_aliases = {
	["acomm"] = "autonomous community",
	["adr"] = "administrative region",
	["adterr"] = "administrative territory", -- Pakistan
	["aobl"] = "autonomous oblast",
	["aokr"] = "autonomous okrug",
	["ap"] = "autonomous province",
	["apref"] = "autonomous prefecture",
	["aprov"] = "autonomous province",
	["ar"] = "autonomous region",
	["arch"] = "archipelago",
	["arep"] = "autonomous republic",
	["aterr"] = "autonomous territory",
	["atu"] = "autonomous territorial unit",
	["bor"] = "borough",
	["c"] = "country",
	["can"] = "canton",
	["carea"] = "council area",
	["cc"] = "constituent country",
	["cdblock"] = "community development block",
	["cdep"] = "Crown dependency",
	["CDP"] = "census-designated place",
	["cdp"] = "census-designated place",
	["clcity"] = "county-level city",
	["co"] = "county",
	["cobor"] = "county borough",
	["colcity"] = "county-level city",
	["coll"] = "collectivity",
	["comm"] = "community",
	["cont"] = "continent",
	["contr"] = "continental region",
	["contregion"] = "continental region",
	["cpar"] = "civil parish",
	["damun"] = "direct-administered municipality",
	["dep"] = "dependency",
	["department capital"] = "departmental capital",
	["dept"] = "department",
	["depterr"] = "dependent territory",
	["dist"] = "district",
	["distmun"] = "district municipality",
	["div"] = "division",
	["emp"] = "empire",
	["fpref"] = "French prefecture",
	["gov"] = "governorate",
	["govnat"] = "governorate",
	["home-rule city"] = "home rule city",
	["home-rule municipality"] = "home rule municipality",
	["inner-city area"] = "inner city area",
	["ires"] = "Indian reservation",
	["isl"] = "island",
	["lbor"] = "London borough",
	["lga"] = "local government area",
	["lgarea"] = "local government area",
	["lgd"] = "local government district",
	["lgdist"] = "local government district",
	["metbor"] = "metropolitan borough",
	["metcity"] = "metropolitan city",
	["metmun"] = "metropolitan municipality",
	["mtn"] = "mountain",
	["mun"] = "municipality",
	["mundist"] = "municipal district",
	["nonmetropolitan county"] = "non-metropolitan county",
	["obl"] = "oblast",
	["okr"] = "okrug",
	["p"] = "province",
	["par"] = "parish",
	["parmun"] = "parish municipality",
	["pen"] = "peninsula",
	["plcity"] = "prefecture-level city",
	["plcolony"] = "Polish colony",
	["pref"] = "prefecture",
	["prefcity"] = "prefecture-level city",
	["preflcity"] = "prefecture-level city",
	["prov"] = "province",
	["r"] = "region",
	["range"] = "mountain range",
	["rcm"] = "regional county municipality",
	["rcomun"] = "regional county municipality",
	["rdist"] = "regional district",
	["rep"] = "republic",
	["rhrom"] = "rural hromada",
	["riv"] = "river",
	["rmun"] = "regional municipality",
	["robor"] = "royal borough",
	["romp"] = "Roman province",
	["runit"] = "regional unit",
	["rurmun"] = "rural municipality",
	["s"] = "state",
	["sar"] = "special administrative region",
	["shrom"] = "settlement hromada",
	["spref"] = "subprefecture",
	["sprefcity"] = "sub-prefectural city",
	["sprovcity"] = "subprovincial city",
	["submet city"] = "sub-metropolitan city",
	["submetropolitan city"] = "sub-metropolitan city",
	["sub-prefecture-level city"] = "sub-prefectural city",
	["sub-provincial city"] = "subprovincial city",
	["sub-provincial district"] = "subprovincial district",
	["terr"] = "territory",
	["terrauth"] = "territorial authority",
	["twp"] = "township",
	["twpmun"] = "township municipality",
	["uauth"] = "unitary authority",
	["ucomm"] = "unincorporated community",
	["udist"] = "unitary district",
	["uhrom"] = "urban hromada",
	["uterr"] = "union territory",
	["utwpmun"] = "united township municipality",
	["val"] = "valley",
	["vdc"] = "village development committee",
	["vil"] = "village",
	["voi"] = "voivodeship",
	["wcomm"] = "Welsh community",
}

local no_link_def_article = {link = false, article = "the"}
local no_link_no_article = {link = false, article = false}

export.placetype_qualifiers = {
	-- generic qualifiers
	["huge"] = false,
	["tiny"] = false,
	["large"] = false,
	["big"] = false,
	["mid-size"] = false,
	["mid-sized"] = false,
	["small"] = false,
	["sizable"] = false,
	["important"] = false,
	["long"] = false,
	["short"] = false,
	["major"] = false,
	["minor"] = false,
	["high"] = false,
	["tall"] = false,
	["low"] = false,
	["left"] = false, -- left tributary
	["right"] = false, -- right tributary
	["modern"] = false, -- for use in opposition to "ancient" in another definition
	-- "former" qualifiers
	["abandoned"] = true,
	["ancient"] = true,
	["deserted"] = true,
	["extinct"] = true,
	["former"] = false,
	["historic"] = "historical",
	["historical"] = true,
	["medieval"] = true,
	["mediaeval"] = true,
	["ruined"] = true,
	["traditional"] = true,
	-- sea qualifiers
	["coastal"] = true,
	["inland"] = true, -- note, we also have an entry in placetype_data for 'inland sea' to get a link to [[inland sea]]
	["maritime"] = true,
	["overseas"] = true,
	["seaside"] = true,
	["beachfront"] = true,
	["beachside"] = true,
	["riverside"] = true,
	-- lake qualifiers
	["freshwater"] = true,
	["saltwater"] = true,
	["endorheic"] = true,
	["oxbow"] = true,
	["ox-bow"] = "[[oxbow]]", -- [[ox-bow]] is a red link
	["tidal"] = true,
	-- land qualifiers
	["hilltop"] = true,
	["hilly"] = true,
	["insular"] = true,
	["peninsular"] = true,
	["chalk"] = true,
	["karst"] = true,
	["limestone"] = true,
	["mountainous"] = true,
	["mountaintop"] = true,
	["alpine"] = true,
	["volcanic"] = true, -- for an island
	-- political status qualifiers
	["autonomous"] = true,
	["incorporated"] = true,
	["special"] = true,
	["unincorporated"] = true,
	["coterminous"] = true,
	-- monetary status/etc. qualifiers
	["fashionable"] = true,
	["wealthy"] = true,
	["affluent"] = true,
	["declining"] = true,
	-- city vs. rural qualifiers
	["urban"] = true,
	["suburban"] = true,
	["exurban"] = true,
	["outlying"] = true,
	["remote"] = true,
	["rural"] = true,
	["outback"] = true,
	["inner"] = false,
	["inner-city"] = true,
	["central"] = false,
	["outer"] = false,
	-- land use qualifiers
	["residential"] = true,
	["agricultural"] = true,
	["business"] = true,
	["commercial"] = true,
	["industrial"] = true,
	-- business use qualifiers
	["railroad"] = true,
	["railway"] = true,
	["farming"] = true,
	["fishing"] = true,
	["mining"] = true,
	["logging"] = true,
	["cattle"] = true,
	-- tourism use qualifiers
	["resort"] = true, -- note, we also have 'resort city' and 'resort town', that take precedecne
	["spa"] = true, -- note, we also have 'spa city' and 'spa town', that take precedecne
	["ski"] = true, -- note, we also have 'ski resort city' and 'ski resort town', that take precedecne
	-- religious qualifiers
	["holy"] = true,
	["sacred"] = true,
	["religious"] = true,
	["secular"] = true,
	-- qualifiers for nonexistent places
	["claimed"] = false,
	["fictional"] = true,
	["legendary"] = true,
	["mythical"] = true,
	["mythological"] = true,
	-- directional qualifiers
	["northern"] = false,
	["southern"] = false,
	["eastern"] = false,
	["western"] = false,
	["north"] = false,
	["south"] = false,
	["east"] = false,
	["west"] = false,
	["northeastern"] = false,
	["southeastern"] = false,
	["northwestern"] = false,
	["southwestern"] = false,
	["northeast"] = false,
	["southeast"] = false,
	["northwest"] = false,
	["southwest"] = false,
	-- seasonal qualifiers
	["summer"] = true, -- e.g. for 'summer capital'
	["winter"] = true,
	-- legal status qualifiers
	-- FIXME: Two-word qualifiers don't work yet. But you can enter "de-facto" and it's canonicalized to [[de facto]].
	["official"] = true,
	["unofficial"] = true,
	["de facto"] = true, -- 'de facto capital'
	["de-facto"] = "[[de facto]]", -- [[de-facto]] is a red link
	["de jure"] = true, -- 'de jure capital'
	["de-jure"] = "[[de jure]]", -- [[de-jure]] is a red link
	-- NOTE: 'unrecognized/unrecognised' are handled as placetypes 'unrecognized country', 'unrecognized state'
	-- misc. qualifiers
	["planned"] = true,
	["chartered"] = true,
	["landlocked"] = true,
	["uninhabited"] = true,
	-- superlative qualifiers
	["first"] = no_link_def_article,
	["second"] = no_link_def_article, -- for "second largest" etc.
	["third"] = no_link_def_article,
	["fourth"] = no_link_def_article,
	["last"] = no_link_def_article,
	["only"] = no_link_def_article,
	["sole"] = no_link_def_article,
	["main"] = no_link_def_article,
	["largest"] = no_link_def_article,
	["biggest"] = no_link_def_article,
	["smallest"] = no_link_def_article,
	["shortest"] = no_link_def_article,
	["longest"] = no_link_def_article,
	["tallest"] = no_link_def_article,
	["highest"] = no_link_def_article,
	["lowest"] = no_link_def_article,
	["leftmost"] = no_link_def_article,
	["rightmost"] = no_link_def_article,
	["innermost"] = no_link_def_article,
	["outermost"] = no_link_def_article,
	["northernmost"] = no_link_def_article,
	["southernmost"] = no_link_def_article,
	["westernmost"] = no_link_def_article,
	["easternmost"] = no_link_def_article,
	["northwesternmost"] = no_link_def_article,
	["southwesternmost"] = no_link_def_article,
	["northeasternmost"] = no_link_def_article,
	["southeasternmost"] = no_link_def_article,
	-- several/various
	["several"] = no_link_no_article,
	["various"] = no_link_no_article,
	["numerous"] = no_link_no_article,
	["multiple"] = no_link_no_article,
	["many"] = no_link_no_article,
	["other"] = no_link_no_article,
}

export.former_qualifiers = {
	["abandoned"] = {"FORMER"},
	["ancient"] = {"ANCIENT", "FORMER"},
	["former"] = {"FORMER"},
	["extinct"] = {"FORMER"},
	["historic"] = {"FORMER"},
	["historical"] = {"FORMER"},
	["medieval"] = {"ANCIENT", "FORMER"},
	["mediaeval"] = {"ANCIENT", "FORMER"},
	["ruined"] = {"ANCIENT", "FORMER"},
	["traditional"] = {"FORMER"},
}

export.qualifier_to_placetype_equivs = {
	["fictional"] = "fictional location",
	["legendary"] = "mythological location",
	["mythical"] = "mythological location",
	["mythological"] = "mythological location",
	-- For e.g. Taiwan as a "claimed province" of China; parts of Belize as claimed by Guatemala; various islands
	-- claimed by various parties in East Asia. FIXME: We should conditionalize on what is being claimed since there are
	-- also claimed capitals, e.g. Israel and Palestine claim Jerusalem as their capital.
	["claimed"] = "claimed political division",
}

export.placetype_to_capital_cat = {
	["autonomous community"] = "autonomous community capitals",
	["canton"] = "cantonal capitals",
	["comarca"] = "comarca capitals",
	["country"] = "national capitals",
	-- The following are not obviously different from 'county seats' but the latte terminology is used in the US.
	["county"] = "county capitals",
	["department"] = "departmental capitals",
	["district"] = "district capitals",
	["division"] = "division capitals",
	["emirate"] = "emirate capitals",
	["governorate"] = "governorate capitals",
	["hromada"] = "hromada capitals",
	["krai"] = "krai capitals",
	["metropolitan city"] = "metropolitan city capitals",
	["municipality"] = "municipal capitals",
	["oblast"] = "oblast capitals",
	["okrug"] = "okrug capitals",
	["prefecture"] = "prefectural capitals",
	["province"] = "provincial capitals",
	["raion"] = "raion capitals",
	["regency"] = "regency capitals",
	["region"] = "regional capitals",
	["regional unit"] = "regional unit capitals",
	["republic"] = "republic capitals",
	["state"] = "state capitals",
	["territory"] = "territorial capitals",
	["voivodeship"] = "voivodeship capitals",
}

export.placename_article = {
	-- This should only contain info that can't be inferred from [[Module:place/locations]].
	["archipelago"] = {
		["Cyclades"] = "the",
		["Dodecanese"] = "the",
	},
	["country"] = {
		["Holy Roman Empire"] = "the",
	},
	["empire"] = {
		["Holy Roman Empire"] = "the",
	},
	["island"] = {
		["North Island"] = "the",
		["South Island"] = "the",
	},
	["region"] = {
		["Balkans"] = "the",
		["Russian Far East"] = "the",
		["Caribbean"] = "the",
		["Caucasus"] = "the",
		["Middle East"] = "the",
		["New Territories"] = "the",
		["North Caucasus"] = "the",
		["South Caucasus"] = "the",
		["West Bank"] = "the",
		["Gaza Strip"] = "the",
	},
	["valley"] = {
		["San Fernando Valley"] = "the",
	},
}

export.placename_the_re = {
	-- We don't need entries for peninsulas, seas, oceans, gulfs or rivers
	-- because they have holonym_use_the = true.
	["*"] = {"^Isle of ", " Islands$", " Mountains$", " Empire$", " Country$", " Region$", " District$", "^City of "},
	["bay"] = {"^Bay of "},
	["lake"] = {"^Lake of "},
	["country"] = {"^Republic of ", " Republic$"},
	["republic"] = {"^Republic of ", " Republic$"},
	["region"] = {" [Rr]egion$"},
	["river"] = {" River$"},
	["local government area"] = {"^Shire of "},
	["county"] = {"^Shire of "},
	["Indian reservation"] = {" Reservation", " Nation"},
	["tribal jurisdictional area"] = {" Reservation", " Nation"},
}

export.cat_implications = {
	["region"] = {
		["Eastern Europe"] = {"continent/Europe"},
		["Central Europe"] = {"continent/Europe"},
		["Western Europe"] = {"continent/Europe"},
		["South Europe"] = {"continent/Europe"},
		["Southern Europe"] = {"continent/Europe"},
		["Northern Europe"] = {"continent/Europe"},
		["Northeast Europe"] = {"continent/Europe"},
		["Northeastern Europe"] = {"continent/Europe"},
		["Southeast Europe"] = {"continent/Europe"},
		["Southeastern Europe"] = {"continent/Europe"},
		["North Caucasus"] = {"continent/Europe"},
		["South Caucasus"] = {"continent/Asia"},
		["South Asia"] = {"continent/Asia"},
		["Southern Asia"] = {"continent/Asia"},
		["East Asia"] = {"continent/Asia"},
		["Eastern Asia"] = {"continent/Asia"},
		["Central Asia"] = {"continent/Asia"},
		["West Asia"] = {"continent/Asia"},
		["Western Asia"] = {"continent/Asia"},
		["Southeast Asia"] = {"continent/Asia"},
		["North Asia"] = {"continent/Asia"},
		["Northern Asia"] = {"continent/Asia"},
		["Anatolia"] = {"continent/Asia"},
		["Asia Minor"] = {"continent/Asia"},
		["Mesopotamia"] = {"continent/Asia"},
		["North Africa"] = {"continent/Africa"},
		["Central Africa"] = {"continent/Africa"},
		["West Africa"] = {"continent/Africa"},
		["East Africa"] = {"continent/Africa"},
		["Southern Africa"] = {"continent/Africa"},
		["Central America"] = {"continent/Central America"},
		["Caribbean"] = {"continent/North America"},
		["Polynesia"] = {"continent/Oceania"},
		["Micronesia"] = {"continent/Oceania"},
		["Melanesia"] = {"continent/Oceania"},
		["Siberia"] = {"country/Russia", "continent/Asia"},
		["Russian Far East"] = {"country/Russia", "continent/Asia"},
		["South Wales"] = {"constituent country/Wales", "continent/Europe"},
		["Balkans"] = {"continent/Europe"},
		["West Bank"] = {"country/Palestine", "continent/Asia"},
		["Gaza"] = {"country/Palestine", "continent/Asia"},
		["Gaza Strip"] = {"country/Palestine", "continent/Asia"},
	}
}

local function city_type_cat_handler(data)
	local entry_placetype = data.entry_placetype
	local generic_before_non_cities = export.get_placetype_prop(entry_placetype, "generic_before_non_cities")
	local plural_entry_placetype = export.pluralize_placetype(entry_placetype)
	local group, key, spec, container_trail = export.find_matching_holonym_location(data)
	if group and not spec.is_former_place and not spec.is_city then
		-- Categorize both in key, and in the larger polity that the key is part of, e.g. [[Hirakata]] goes in both
		-- "Cities in Osaka Prefecture" and "Cities in Japan". (But don't do the latter if no_container_cat is set.)
		local cap_plural_entry_placetype = ucfirst(plural_entry_placetype)
		local retcats = {("%s %s %s"):format(cap_plural_entry_placetype, generic_before_non_cities,
			export.get_prefixed_key(key, spec))}
		if container_trail[1] and not spec.no_container_cat then
			for _, container in ipairs(container_trail[1]) do
				insert(retcats, ("%s %s %s"):format(cap_plural_entry_placetype, generic_before_non_cities,
					export.get_prefixed_key(container.key, container.spec)))
			end
		end
		return retcats
	end
end


local function capital_city_cat_handler(data, non_city)
	local holonym_placetype, holonym_placename, holonym_index, place_desc =
		data.holonym_placetype, data.holonym_placename, data.holonym_index, data.place_desc
	-- The first time we're called we want to return something; otherwise we will be called for later-mentioned
	-- holonyms, which can result in wrongly classifying into e.g. `National capitals`. Simulate the loop in
	-- find_placetype_cat_specs() over holonyms so we get the proper `Cities in ...` categories as well as the capital
	-- category/categories we add below.
	local retcats
	if not non_city and place_desc.holonyms then
		for h_index, holonym in export.get_holonyms_to_check(place_desc, holonym_index) do
			local h_placetype, h_placename = holonym.placetype, holonym.unlinked_placename
			retcats = city_type_cat_handler {
				entry_placetype = "city",
				holonym_placetype = h_placetype,
				holonym_placename = h_placename,
				holonym_index = h_index,
				place_desc = place_desc,
			}
			if retcats then
				break
			end
		end
	end
	if not retcats then
		retcats = {}
	end

	-- Now find the appropriate capital-type category for the placetype of the holonym, e.g. 'State capitals'. If we
	-- recognize the holonym among the known holonyms in [[Module:place/locations]], also add a category like 'State
	-- capitals of the United States'.  Truncate e.g. 'autonomous region' to 'region', 'union territory' to 'territory'
	-- when looking up the type of capital category, if we can't find an entry for the holonym placetype itself (there's
	-- an entry for 'autonomous community').
	local capital_cat = export.placetype_to_capital_cat[holonym_placetype]
	if not capital_cat then
		capital_cat = export.placetype_to_capital_cat[holonym_placetype:gsub("^.* ", "")]
	end
	if capital_cat then
		capital_cat = ucfirst(capital_cat)
		local inserted_specific_variant_cat = false
		if holonym_index then
			-- Now find the first recognized holonym location. We don't stop when :also is seen because of the common pattern
			-- where we use :also to specify that a given city is the capital at multiple surrounding levels.
			local matching_group, matching_key, matching_spec, matching_container_trail, matching_holonym_index
			for h_index = holonym_index, #place_desc.holonyms do
				if place_desc.holonyms[h_index].placetype then
					matching_group, matching_key, matching_spec, matching_container_trail = export.find_matching_holonym_location {
						holonym_placetype = place_desc.holonyms[h_index].placetype,
						holonym_placename = place_desc.holonyms[h_index].unlinked_placename,
						holonym_index = h_index,
						place_desc = place_desc,
					}
					if matching_group then
						matching_holonym_index = h_index
						break
					end
				end
			end
			if matching_holonym_index == holonym_index then
				if matching_container_trail[1] and not matching_spec.no_container_cat then
					for _, container in ipairs(matching_container_trail[1]) do
						insert(retcats, ("%s of %s"):format(capital_cat, export.get_prefixed_key(container.key,
							container.spec)))
						inserted_specific_variant_cat = true
					end
				end
			elseif matching_holonym_index then
				-- Check to make sure that the holonym placetype we were called on is listed among the
				-- divtypes of the location we found.
				local function insert_specific_variant_if_possible(key, spec)
					return export.get_equiv_placetype_prop(holonym_placetype, function(pt)
						local plural_holonym_placetype = export.pluralize_placetype(pt)
						local saw_matching_div
						if spec.divs then
							local divs = spec.divs
							if type(divs) ~= "table" then
								divs = {divs}
							end
							for _, div in ipairs(divs) do
								if type(div) ~= "table" then
									div = {type = div}
								end
								if plural_holonym_placetype == div.type then
									saw_matching_div = true
									break
								end
							end
						end
						if saw_matching_div then
							insert(retcats, ("%s of %s"):format(capital_cat, export.get_prefixed_key(key, spec)))
							return true
						end
						return false
					end)
				end
				if insert_specific_variant_if_possible(matching_key, matching_spec) then
					inserted_specific_variant_cat = true
				elseif not matching_spec.no_container_cat then
					for _, containers in ipairs(matching_container_trail) do
						local saw_no_container_cat = false
						for _, container in ipairs(containers) do
							if insert_specific_variant_if_possible(container.key, container.spec) then
								inserted_specific_variant_cat = true
								break
							end
							saw_no_container_cat = saw_no_container_cat or container.spec.no_container_cat
						end
						if inserted_specific_variant_cat or saw_no_container_cat then
							break
						end
					end
				end
			end
		else
			-- This happens when in an invocation like {{place|en|capital city|s/Haryana,Punjab}} for
			-- [[Chandigarh]]. We fall back to older code that doesn't depend on the holonym index existing.
			-- FIXME: This may not be necessary. In the example just given, when processing Haryana we add to
			-- [[:Category:en:State capitals of India]], and nothing extra gets added when processing Punjab.
			-- Possibly we can just skip this case entirely.
			local group, key, spec, container_trail = export.find_matching_holonym_location(data)
			if group and container_trail[1] and not spec.no_container_cat then
				for _, container in ipairs(container_trail[1]) do
					insert(retcats, ("%s of %s"):format(capital_cat, export.get_prefixed_key(container.key,
						container.spec)))
					inserted_specific_variant_cat = true
				end
			end
		end
		if not inserted_specific_variant_cat then
			insert(retcats, capital_cat)
		end
	else
		-- We didn't recognize the holonym placetype; just put in 'Capital cities'.
		insert(retcats, "Capital cities")
	end
	return retcats
end

local function generic_place_cat_handler(data)
	local from_demonym = data.from_demonym

	local retcats = {}
	local function insert_retkey(key, spec)
		if from_demonym then
			insert(retcats, key)
		else
			insert(retcats, ("Places in %s"):format(export.get_prefixed_key(key, spec)))
		end
	end

	local group, key, spec, container_trail = export.find_matching_holonym_location(data)
	if group then
		if not spec.no_generic_place_cat then
			-- This applies to continents and continental regions.
			insert_retkey(key, spec)
		end
		-- Categorize both in key, and in the larger location(s) that the key is part of, e.g. [[Hirakata]] goes in
		-- both [[Category:Places in Osaka Prefecture, Japan]] and [[Category:Places in Japan]]. But not when
		-- no_container_cat is set (e.g. for 'United Kingdom').
		if not spec.no_container_cat then
			for _, container_set in ipairs(container_trail) do
				local stop_adding_containers = false
				for _, container in ipairs(container_set) do
					if not container.spec.no_generic_place_cat then
						insert_retkey(container.key, container.spec)
					end
					if container.spec.no_container_cat then
						stop_adding_containers = true
					end
				end
				if stop_adding_containers then
					break
				end
			end
		end
		return retcats
	end
end

function export.political_division_cat_handler(data)
	if data.from_demonym then
		return
	end
	local group, key, spec, container_trail = export.find_matching_holonym_location(data)
	if group then
		local divlists = {}
		if spec.divs then
			insert(divlists, spec.divs)
		end
		if spec.addl_divs then
			insert(divlists, spec.addl_divs)
		end
		for _, divlist in ipairs(divlists) do
			if type(divlist) ~= "table" then
				divlist = {divlist}
			end
			for _, div in ipairs(divlist) do
				if type(div) == "string" then
					div = {type = div}
				end
				local sgdiv = export.maybe_singularize_placetype(div.type) or div.type
				local prep = div.prep or "of"
				local cat_as = div.cat_as or div.type
				if type(cat_as) ~= "table" then
					cat_as = {cat_as}
				end
				if sgdiv == data.entry_placetype then
					local retcats = {}
					for _, pt_cat in ipairs(cat_as) do
						if type(pt_cat) == "string" then
							pt_cat = {type = pt_cat}
						end
						local pt_prep = pt_cat.prep or prep
						insert(retcats, ucfirst(pt_cat.type) .. " " .. pt_prep .. " " ..
							export.get_prefixed_key(key, spec))
					end
					return retcats
				end
			end
		end
	end
end

function export.get_bare_categories(args, overall_place_spec)
	local bare_cats = {}
	local place_descs = overall_place_spec.descs

	local possible_placetypes_by_place_desc = {}
	for i, place_desc in ipairs(place_descs) do
		possible_placetypes_by_place_desc[i] = {}
		for _, placetype in ipairs(place_desc.placetypes) do
			if not export.placetype_is_ignorable(placetype) then
				local equivs = export.get_placetype_equivs(placetype, {register_former_as_non_former = true})
				for _, equiv in ipairs(equivs) do
					insert(possible_placetypes_by_place_desc[i], equiv.placetype)
				end
			end
		end
	end

	local function check_term(term)
		-- Treat Wikipedia links like local ones.
		term = term:gsub("%[%[w:", "[["):gsub("%[%[wikipedia:", "[[")
		term = export.remove_links_and_html(term)
		term = term:gsub("^the ", "")
		for i, place_desc in ipairs(place_descs) do
			-- Iterate over all matching locations in case there are multiple, as with Delhi defined as
			-- {{place|en|megacity/and/union territory|c/India|containing the national capital [[New Delhi]]}}.
			for group, key, spec, container_trail in export.iterate_matching_holonym_location {
				holonym_placetype = possible_placetypes_by_place_desc[i],
				holonym_placename = term,
				place_desc = place_desc,
			} do
				insert(bare_cats, key)
			end
		end
	end

	-- FIXME: Should we only do the following if the language is English (requires that the lang is passed in)?
	-- We should always do it if `pagename` is given (as it is with {{tcl}}) but maybe not otherwise unless 1=en. There
	-- are cases like [[Ankara]] = English name for capital of Turkey, but also the name in various languages for the
	-- capital of Ghana (= English [[Accra]]). But this should get caught by mismatching the containing country. The
	-- advantage of checking when the language isn't English is we catch those places that fail to give an English
	-- translation but where the translation happens to be the same as the other-language spelling. However, I don't
	-- know how often this situation occurs.
	check_term(args.pagename or mw.title.getCurrentTitle().subpageText)
	for _, t in ipairs(args.t) do
		check_term(t)
	end
	local function check_termobj_list(terms)
		for _, term in ipairs(terms) do
			if term.eq then
				check_term(term.eq)
			end
			if term.alt or term.term then
				check_term(term.alt or term.term)
			end
		end
	end

	for _, extra_info_terms in ipairs(overall_place_spec.extra_info) do
		local arg = extra_info_terms.arg
		if arg == "modern" or arg == "now" or arg == "full" or arg == "short" then
			check_termobj_list(extra_info_terms.terms)
		end
	end
	for _, directive in ipairs(overall_place_spec.directives) do
		check_termobj_list(directive.terms)
	end

	return bare_cats
end


function export.augment_holonyms_with_container(place_descs)
	for _, place_desc in ipairs(place_descs) do
		if place_desc.holonyms then
			-- This ends up containing a copy of the original holonyms, with the augmented holonyms inserted in their
			-- appropriate position. We don't just put them at the end because some holonyms have use the `:also`
			-- modifier, which causes category processing to restart at that point after generating categories for a
			-- preceding holonym, and we don't want the preceding holonym's augmented holonyms interfering with
			-- categorization of a later holonym. We proceed from right to left, and each time we augment, we copy
			-- the holonyms with the augmented holonym(s) inserted appropriately and replace the place description's
			-- holonyms with the augmented ones before the next iteration. The reason for this is so that e.g.
			-- {{place|neighborhood|city/Birmingham|co/West Midlands|cc/England}} doesn't throw an error during the
			-- augmentation process due to 'Birmingham' referring to two known locations (in England and Alabama). If
			-- we go left to right, we will throw an ambiguity error on `city/Birmingham` because code to exclude
			-- Birmingham, Alabama needs `c/United Kingdom` present (to cause a mismatch with `c/United States`),
			-- which isn't yet present as the augmentation code hasn't gotten to `cc/England` yet. For similar
			-- reasons, we need to include the augmented holonyms in the holonyms considered in the next iteration
			-- rather than modifying the place description once at athe end.
			for i = #place_desc.holonyms, 1, -1 do
				local holonym = place_desc.holonyms[i]
				if holonym.placetype and not export.placetype_is_ignorable(holonym.placetype) then
					local group, key, spec, container_trail = export.find_matching_holonym_location {
						holonym_placetype = holonym.placetype,
						holonym_placename = holonym.unlinked_placename,
						holonym_index = i,
						place_desc = place_desc,
					}
					if group and container_trail[1] and not spec.no_auto_augment_container then
						local augmented_holonyms = {}
						for j = 1, i do
							insert(augmented_holonyms, place_desc.holonyms[j])
						end
						for _, containers in ipairs(container_trail) do
							local any_no_auto_augment_container = false
							for _, container in ipairs(containers) do
								any_no_auto_augment_container = any_no_auto_augment_container or
									container.spec.no_auto_augment_container
								local containing_type = container.spec.placetype
								if type(containing_type) == "table" then
									-- If the containing type is a list, use the first element as the canonical variant.
									containing_type = containing_type[1]
								end
								local full_container_placename, elliptical_container_placename =
									m_locations.key_to_placename(container.group, container.key)
								-- Don't side-effect holonyms while processing them.
								local new_holonym = {
									-- By the time we run, the display has already been generated so we don't need to
									-- set display_placename.
									placetype = containing_type,
									-- placename_to_key() for the group should correctly handle both full and elliptical
									-- placenames, but the full placename seems less likely to be ambiguous. FIXME: We
									-- should just store the key directly and use it when available to avoid having to
									-- convert key to placename and back to key.
									unlinked_placename = full_container_placename,
									-- Indicate that this is an augmented holonym, and was derived from the specified
									-- holonym. In iterate_matching_holonym_location(), we ignore augmented holonyms
									-- derived from holonyms that are different from the holonym we're searching for but
									-- of the same placetype. This is to correctly handle a situation like
									-- {{place|river|dept/Ardèche,Gard,Vaucluse,Bouches-du-Rhône|c/France}}. Here,
									-- `Ardèche` is in `r/Auvergne-Rhône-Alpes`, while `Gard` is in `r/Occitania` and
									-- the other two are in `r/Provence-Alpes-Côte d'Azur`. Augmenting proceeds from
									-- right to left, so after it adds `r/Provence-Alpes-Côte d'Azur` to
									-- `Bouches-du-Rhône`, Vaucluse gets augmented correctly but `Gard` fails to match
									-- in find_matching_holonym_location() because of the mismatch between augmented
									-- `r/Provence-Alpes-Côte d'Azur` and actual `r/Occitania`. Similarly, all later
									-- calls to find_matching_holonym_location() fail to match `Gard` (and likewise
									-- `Ardèche`) against any known location. To deal with this, we mark augmented
									-- holoynms as being augmented due to a source holonym, and when processing a given
									-- holonym, ignore augmented holonyms from other holonyms of the same placetype.
									-- The restriction to the same placetype is so that `Birmingham` still gets
									-- correctly disambiguated to Birmingham, England in the example given above near
									-- the top of this function, using the augmented holonym `c/United Kingdom` added by
									-- the specified `cc/England` (whose placetype `constituent country` differs from
									-- the placetype `city` of Birmingham).
									augmented_from_holonym = holonym,
								}
								insert(augmented_holonyms, new_holonym)
								-- But it is safe to modify other parts of the place_desc.
								export.key_holonym_into_place_desc(place_desc, new_holonym)
							end
							if any_no_auto_augment_container then
								break
							end
						end
						for j = i + 1, #place_desc.holonyms do
							insert(augmented_holonyms, place_desc.holonyms[j])
						end
						place_desc.holonyms = augmented_holonyms
					end
				end
			end
		end
	end
end


local function district_neighborhood_cat_handler(data)
	local function get_plural_entry_placetype(location_spec, container_trail)
		if data.entry_placetype == "suburb" then
			return "Suburbs"
		else
			-- Check for `british_spelling` setting on the spec itself or any container.
			local uses_british_spelling = location_spec.british_spelling
			if uses_british_spelling == nil and container_trail then
				for _, container_set in ipairs(container_trail) do
					local must_outer_break = false
					for _, container in ipairs(container_set) do
						if container.spec.british_spelling ~= nil then
							uses_british_spelling = container.spec.british_spelling
							must_outer_break = true
							break
						end
					end
					if must_outer_break then
						break
					end
				end
			end

			return uses_british_spelling and "Neighbourhoods" or "Neighborhoods"
		end
	end

	-- First check the immediate holonym to see if it's a city or a city-like top-level entity (Hong Kong, Bonaire,
	-- etc.)
	local group, key, spec, container_trail = export.find_matching_holonym_location(data)
	if group and not spec.is_former_place and spec.is_city then
		return {get_plural_entry_placetype(spec, container_trail) .. " of " .. export.get_prefixed_key(key, spec)}
	end

	-- If the entry placetype is neighbo(u)rhood, assume it is a neighborhood even if there isn't a city-like
	-- entity father up the chain. (E.g. due to a mistaken use of m/ instead of mun/ for municipality.)
	local has_neighborhoods
	local entry_placetype = data.entry_placetype
	if entry_placetype == "neighborhood" or entry_placetype == "neighbourhood" or entry_placetype == "suburb" then
		has_neighborhoods = true
	else
		-- Otherwise, make sure the current holonym is city-like.
		has_neighborhoods = export.get_equiv_placetype_prop(data.holonym_placetype, function(pt)
			return export.get_placetype_prop(pt, "has_neighborhoods")
		end, {continue_on_nil_only = true})
	end
	if has_neighborhoods then
		-- Loop up the holonyms, looking for city and city-like entities in case of e.g. [[Sepulveda]] written
		-- {{place|en|neighborhood|valley/San Fernando Valley|city/Los Angeles|s/California|c/USA}}
		-- but also look for a recognizable poldiv, and if so categorize as "Neighborhoods in POLDIV". We need
		-- to start with the current holonym, which is especially important for neighborhoods and suburbs that
		-- may have the first holonym be a recognizable province, etc. but can't hurt otherwise. (Previously
		-- we skipped the first/current holonym.)
		for other_holonym_index, other_holonym in export.get_holonyms_to_check(data.place_desc,
			data.holonym_index) do
			local other_holonym_data = {
				holonym_placetype = other_holonym.placetype,
				holonym_placename = other_holonym.unlinked_placename,
				holonym_index = other_holonym_index,
				place_desc = data.place_desc,
			}
			local group, key, spec, container_trail = export.find_matching_holonym_location(other_holonym_data)
			if group and not spec.is_former_place then
				return {get_plural_entry_placetype(spec, container_trail) .. (spec.is_city and " of " or " in ") ..
					export.get_prefixed_key(key, spec)}
			end
		end
	end
end


function export.check_already_seen_string(holonym_placename, already_seen_strings)
	local canon_placename = ulower(m_links.remove_links(holonym_placename))
	if type(already_seen_strings) ~= "table" then
		already_seen_strings = {already_seen_strings}
	end
	for _, already_seen_string in ipairs(already_seen_strings) do
		if canon_placename:find(already_seen_string) then
			return true
		end
	end
	return false
end


local function prefix_display_handler(prefix, holonym_placename, already_seen_strings)
	if export.check_already_seen_string(holonym_placename, already_seen_strings or ulower(prefix)) then
		return holonym_placename
	end
	if holonym_placename:find("%[%[") then
		return prefix .. " " .. holonym_placename
	end
	return prefix .. " [[" .. holonym_placename .. "]]"
end


local function suffix_display_handler(suffix, holonym_placename, already_seen_strings, include_suffix_in_link)
	if export.check_already_seen_string(holonym_placename, already_seen_strings or ulower(suffix)) then
		return holonym_placename
	end
	if holonym_placename:find("%[%[") then
		return holonym_placename .. " " .. suffix
	end
	if include_suffix_in_link then
		return "[[" .. holonym_placename .. " " .. suffix .. "]]"
	else
		return "[[" .. holonym_placename .. "]] " .. suffix
	end
end

local function borough_display_handler(holonym_placetype, holonym_placename)
	local unlinked_placename = m_links.remove_links(holonym_placename)
	if m_locations.new_york_boroughs[unlinked_placename] then
		-- Hack: don't display "borough" after the names of NYC boroughs
		return holonym_placename
	end
	return suffix_display_handler("borough", holonym_placename)
end

local function county_display_handler(holonym_placetype, holonym_placename)
	local unlinked_placename = m_links.remove_links(holonym_placename)
	-- Display handler for Irish counties. Irish counties are displayed as e.g. "County [[Cork]]".
	if m_locations.ireland_counties["County " .. unlinked_placename .. ", Ireland"] or
		m_locations.northern_ireland_counties["County " .. unlinked_placename .. ", Northern Ireland"] then
		return prefix_display_handler("County", holonym_placename)
	end
	-- Display handler for Taiwanese counties. Taiwanese counties are displayed as e.g. "[[Chiayi]] County".
	if m_locations.taiwan_counties[unlinked_placename .. " County, Taiwan"] then
		return suffix_display_handler("County", holonym_placename)
	end
	-- Display handler for Romanian counties. Romanian counties are displayed as e.g. "[[Cluj]] County".
	if m_locations.romania_counties[unlinked_placename .. " County, Romania"] then
		return suffix_display_handler("County", holonym_placename)
	end
	-- FIXME, we need the same for US counties but need to key off the country, not the specific county.
	-- Others are displayed as-is.
	return holonym_placename
end


local function prefecture_display_handler(holonym_placetype, holonym_placename)
	local unlinked_placename = m_links.remove_links(holonym_placename)
	local suffix = m_locations.japan_prefectures[unlinked_placename .. " Prefecture, Japan"] and "Prefecture" or "prefecture"
	return suffix_display_handler(suffix, holonym_placename)
end

local function province_display_handler(holonym_placetype, holonym_placename)
	local unlinked_placename = m_links.remove_links(holonym_placename)
	if
		m_locations.iran_provinces[unlinked_placename .. " Province, Iran"] or
		m_locations.laos_provinces[unlinked_placename .. " Province, Laos"] or
		m_locations.north_korea_provinces[unlinked_placename .. " Province, North Korea"] or
		m_locations.south_korea_provinces[unlinked_placename .. " Province, South Korea"] or
		m_locations.thailand_provinces[unlinked_placename .. " Province, Thailand"] or
		m_locations.turkey_provinces[unlinked_placename .. " Province, Turkey"] or
		m_locations.vietnam_provinces[unlinked_placename .. " Province, Vietnam"] then
		return suffix_display_handler("Province", holonym_placename)
	end
	return holonym_placename
end

local function state_display_handler(holonym_placetype, holonym_placename)
	local unlinked_placename = m_links.remove_links(holonym_placename)
	if m_locations.nigeria_states[unlinked_placename .. " State, Nigeria"] then
		return suffix_display_handler("State", holonym_placename)
	end
	return holonym_placename
end

local function voivodesip_display_handler(holonym_placetype, holonym_placename)
	return suffix_display_handler("Voivodeship", holonym_placename, nil, "include_suffix_in_link")
end

export.placetype_data = {
	["*"] = {
		link = false,
		cat_handler = generic_place_cat_handler,
	},
	["administrative atoll"] = {
		-- Maldives
		link = "+w:administrative divisions of the Maldives",
		preposition = "of",
		class = "subpolity",
	},
	["administrative capital"] = {
		link = "w",
		fallback = "capital city",
	},
	["administrative center"] = {
		link = "w",
		fallback = "non-city capital",
	},
	["administrative centre"] = {
		link = "w",
		fallback = "administrative center",
	},
	["administrative county"] = {
		link = "w",
		fallback = "county",
	},
	["administrative district"] = {
		link = "w",
		fallback = "district",
	},
	["administrative headquarters"] = {
		link = "separately",
		fallback = "administrative centre",
	},
	["administrative region"] = {
		link = true,
		preposition = "of",
		suffix = "region", -- but prefix is still "administrative region (of)"
		fallback = "region",
		class = "subpolity",
	},
	["administrative seat"] = {
		link = "w",
		fallback = "administrative centre",
	},
	["administrative territory"] = {
		link = "separately",
		preposition = "of",
		suffix = "territory", -- but prefix is still "administrative territory (of)"
		fallback = "territory",
		class = "subpolity",
	},
	["administrative unit"] = {
		-- Grrr, it's difficult to generalize about "administrative units". In Albania, "administrative unit" is an
		-- official term for a city-level division of municipalities; Wikipedia renders it using the more practical term
		-- "commune". In Pakistan, "administrative unit" is a collective term used to refer to all the different types
		-- of first-level divisions (four provinces, one federal territory, and two "disputed territories", i.e. Azad
		-- Kashmir and Gilgit-Balistan, that are variously described). For this reason, we set no fallback, but we need
		-- to include this so that it can be used as a placetype for Albania, categorizing as communes.
		link = "w",
		class = "subpolity",
	},
	["administrative village"] = {
		link = "w",
		preposition = "of",
		has_neighborhoods = true,
		class = "settlement",
	},
	["aimag"] = {
		-- used in Mongolia, Russia and China (Inner Mongolia); in Mongolia, equivalent to a province;
		-- in China, equivalent to a prefecture (below a province); in Russia, equivalent to a municipal district.
		link = "w",
		fallback = "prefecture",
	},
	["airport"] = {
		link = true,
		class = "man-made structure",
		default = {true},
	},
	["alliance"] = {
		link = true,
		fallback = "confederation",
	},
	["archipelago"] = {
		link = true,
		fallback = "island",
	},
	["area"] = {
		link = true,
		preposition = "of",
		fallback = "geographic and cultural area",
		-- Areas can either be administrative divisions (specifically of Kuwait) or geographic areas. Assume the former
		-- when categorizing 'Areas' but the latter when handling e.g. 'historical area'.
		class = "subpolity",
		former_type = "geographic region",
		cat_handler = district_neighborhood_cat_handler,
	},
	["arm"] = {
		link = true,
		preposition = "of",
		class = "natural feature",
		default = {"Seas"},
	},
	["arrondissement"] = {
		link = true,
		preposition = "of",
		-- FIXME!!! Grrrrr!!! In some countries, arrondissements are divisions of cities; in others, they are divisions
		-- of departments or provinces. Need to conditionalize on the country for both of the following.
		class = "subpolity",
		has_neighborhoods = true,
	},
	["associated province"] = {
		link = "separately",
		fallback = "province",
	},
	["atoll"] = {
		-- FIXME! Atolls are administrative divisions of the Maldives but natural features elsewhere. Need to
		-- conditionalize `class` on the country. See also `administrative atoll`.
		link = true,
		class = "natural feature",
		bare_category_parent = "islands",
		default = {true},
	},
	["autonomous city"] = {
		link = "w",
		preposition = "of",
		fallback = "city",
		has_neighborhoods = true,
	},
	["autonomous community"] = {
		-- Spain; refers to regional entities, not village-like entities, as might be expected from "community"
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["autonomous island"] = {
		-- Comoros; seems like an administrative atoll of the Maldives.
		link = "+w:autonomous islands of Comoros",
		preposition = "of",
		class = "subpolity",
	},
	["autonomous oblast"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		no_affix_strings = "oblast",
		class = "subpolity",
	},
	["autonomous okrug"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		no_affix_strings = "okrug",
		class = "subpolity",
	},
	["autonomous prefecture"] = {
		link = true,
		fallback = "prefecture",
	},
	["autonomous province"] = {
		link = "w",
		fallback = "province",
	},
	["autonomous region"] = {
		link = "w",
		preposition = "of",
		fallback = "administrative region",
		-- "administrative region" sets an affix of "region" but we want to display as "Tibet Autonomous Region"
		-- if the user writes 'ar:Suf/Tibet'.
		affix = "autonomous region",
	},
	["autonomous republic"] = {
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["autonomous territorial unit"] = {
		-- Moldova; only two of them, one for Gagauzia and one for Transnistria.
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["autonomous territory"] = {
		link = "w",
		fallback = "dependent territory",
	},
	["bailiwick"] = {
		-- Jersey, etc.
		link = true,
		fallback = "polity",
	},
	["barangay"] = {
		-- Philippines
		link = true,
		class = "settlement",
		-- Barangays are formal administrative divisions of a city rather than informal neighborhoods, but can use
		-- some of the properties of a neighborhood.
		fallback = "neighborhood",
	},
	["barrio"] = {
		-- Spanish-speaking countries; Philippines
		link = true,
		-- FIXME: Not completely correct, in some countries barrios are formal administrative divisions of a city.
		-- `class` will need to conditionalize on the country to be completely correct.
		fallback = "neighborhood",
	},
	["basin"] = {
		link = true,
		fallback = "lake",
	},
	["bay"] = {
		link = true,
		preposition = "of",
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["beach"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"water"},
		default = {true},
	},
	["beach resort"] = {
		link = "w",
		fallback = "resort town",
	},
	["bishopric"] = {
		link = true,
		fallback = "polity",
	},
	["bodies of water!"] = {
		-- FIXME: This is (maybe?) a type category not a name category. There should be an option for this. We need to
		-- straighten out the type vs. name vs. related-to issue.
		category_link = "[[body of water|bodies of water]]",
		class = "natural feature",
		addl_bare_category_parents = {"landforms", "ecosystems", "water"},
	},
	["borough"] = {
		link = true,
		preposition = "of",
		display_handler = borough_display_handler,
		has_neighborhoods = true,
		-- "former borough" could be a former settlement or a former part of a city but seems more likely to
		-- be a former subpolity, particularly in England. FIXME, we really need a handler to take care of this
		-- properly.
		class = "subpolity",
		-- Grr, some boroughs are city-like but some (e.g. in Britain) may be larger.
	},
	["borough seat"] = {
		link = true,
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
	},
	["branch"] = {
		link = true,
		preposition = "of",
		fallback = "river",
	},
	["bridge"] = {
		link = true,
		class = "man-made structure",
		default = {"Named bridges"},
	},
	["building"] = {
		link = true,
		class = "man-made structure",
		default = {"Named buildings"},
	},
	["built-up area"] = {
		link = "w",
		fallback = "area",
	},
	["burgh"] = {
		link = true,
		fallback = "borough",
	},
	["caliphate"] = {
		link = true,
		fallback = "polity",
	},
	["canton"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["cape"] = {
		link = true,
		fallback = "headland",
	},
	["capital"] = {
		link = true,
		fallback = "capital city",
	},
	["capital city"] = {
		link = true,
		category_link = "[[capital city|capital cities]]: the [[seat of government|seats of government]] for a country or [[political]] [[division]] of a country",
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
		bare_category_parent = "cities",
		cat_handler = capital_city_cat_handler,
		default = {true},
		-- The following is necessary so that e.g. [[Melbourne]] defined as {{place|en|capital city|s/Victoria|c/Australia}}
		-- gets categorized in the bare category [[Category:en:Melbourne]]; otherwise placetype 'capital city' wouldn't
		-- match against the placetype 'city' of Melbourne.
		fallback = "city",
	},
	["caplc"] = {
		link = "[[capital]] and [[large]]st [[city]]",
		plural_link = false,
		fallback = "capital city",
	},
	["captaincy"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
		inherently_former = {"FORMER"},
	},
	["caravan city"] = {
		link = "w",
		fallback = "city",
		class = "settlement",
		inherently_former = {"ANCIENT", "FORMER"},
	},
	["castle"] = {
		link = true,
		fallback = "building",
	},
	["cathedral city"] = {
		link = true,
		fallback = "city",
	},
	["cattle station"] = {
		-- Australia
		link = true,
		fallback = "farm",
	},
	["census area"] = {
		link = true,
		affix_type = "Suf",
		has_neighborhoods = true,
		class = "non-admin settlement",
	},
	["census-designated place"] = {
		-- United States
		link = true,
		class = "non-admin settlement",
	},
	["census division"] = {
		-- Canada
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["census town"] = {
		link = "w",
		fallback = "town",
	},
	["central business district"] = {
		link = true,
		fallback = "neighborhood",
	},
	["cercle"] = {
		-- Mali
		link = "+w:cercles of Mali",
		preposition = "of",
		class = "subpolity",
	},
	["ceremonial county"] = {
		link = true,
		fallback = "county",
	},
	["chain of islands"] = {
		link = "[[chain]] of [[island]]s",
		plural = "chains of islands",
		plural_link = "[[chain]]s of [[island]]s",
		fallback = "island",
	},
	["channel"] = {
		link = true,
		fallback = "strait",
	},
	["charter community"] = {
		-- Northwest Territories, Canada
		link = "w",
		fallback = "village",
	},
	["city"] = {
		link = true,
		generic_before_non_cities = "in",
		has_neighborhoods = true,
		class = "settlement",
		cat_handler = city_type_cat_handler,
		default = {true},
	},
	["city-state"] = {
		link = true,
		category_link = "[[sovereign]] [[microstate]]s consisting of a single [[city]] and [[w:dependent territory|dependent territories]]",
		has_neighborhoods = true,
		class = "settlement",
		["continent/*"] = {"City-states", "Cities in +++", "Countries in +++", "National capitals"},
		default = {"City-states", "Cities", "Countries", "National capitals"},
	},
	["civil parish"] = {
		-- Mostly England; similar to municipalities
		link = true,
		preposition = "of",
		affix_type = "suf",
		has_neighborhoods = true,
		class = "subpolity",
	},
	["claimed political division"] = {
		link = "[[claim]]ed [[political]] [[division]]",
		class = "subpolity",
		default = {true},
	},
	["co-capital"] = {
		link = "[[co-]][[capital]]",
		fallback = "capital city",
	},
	["coal city"] = {
		link = "+w:coal town",
		fallback = "city",
	},
	["coal town"] = {
		link = "w",
		fallback = "town",
	},
	["collectivity"] = {
		link = "w",
		preposition = "of",
		-- No default; these are weird one-off governmental divisions in France (esp. for overseas collectivities)
		class = "subpolity",
	},
	["colony"] = {
		link = true,
		fallback = "dependent territory",
	},
	["comarca"] = {
		-- per Wikipedia: traditional region or local administrative division found in Portugal, Spain, and some of
		-- their former colonies, like Brazil, Nicaragua, and Panama. In the Valencian Community, for example, it
		-- sits between municipalities and provinces, something like a county or district.
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["commandery"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
		inherently_former = {"ANCIENT", "FORMER"},
	},
	["commonwealth"] = {
		link = true,
		preposition = "of",
		-- No default; applies specifically to Puerto Rico
		class = "subpolity",
	},
	["commune"] = {
		link = true,
		fallback = "municipality",
	},
	["community"] = {
		link = true,
		category_link = "[[community|communities]] of all sizes",
		fallback = "village",
	},
	["community development block"] = {
		-- in India; appears to be similar to a rural municipality; groups several villages, unclear if there will be
		-- neighborhoods so I'm not setting `has_neighborhoods` for now
		link = "w",
		affix_type = "suf",
		no_affix_strings = "block",
		class = "subpolity",
	},
	["comune"] = {
		-- Italy, Switzerland
		link = true,
		fallback = "municipality",
	},
	["condominium"] = {
		link = true,
		fallback = "polity",
	},
	["confederacy"] = {
		link = true,
		fallback = "confederation",
	},
	["confederation"] = {
		link = true,
		fallback = "polity",
	},
	["constituency"] = {
		-- currently we have them as political divisions of Namibia but many countries have them
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["constituent country"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["constituent part"] = {
		link = "separately",
		preposition = "of",
		class = "subpolity",
	},
	["constituent republic"] = {
		-- Of Russia, Yugoslavia, etc.
		link = "separately",
		preposition = "of",
		class = "subpolity",
	},
	["counties and county-level cities!"] = {
		-- This is used when grouping counties and county-level cities under prefecture-level cities in China.
		category_link = "[[county|counties]] and [[county-level city|county-level cities]]",
		class = "subpolity",
	},
	["continent"] = {
		link = true,
		category_link = false, -- can't occur as a bare category
		class = "natural feature",
		default = {"Continents and continental regions"},
	},
	["continental region"] = {
		link = "separately",
		category_link = false, -- can't occur as a bare category
		class = "geographic region",
		fallback = "continent",
	},
	["continents and continental regions!"] = {
		category_link = "[[continent]]s and [[continent]]-[[level]] [[region]]s (e.g. [[Polynesia]])",
		class = "geographic region",
	},
	["council area"] = {
		link = true,
		-- in Scotland; similar to a county
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["country"] = {
		link = true,
		class = "polity",
		["continent/*"] = {true, "Countries"},
		default = {true},
	},
	["country-like entities!"] = {
		category_link = "[[polity|polities]] not normally considered [[country|countries]] but treated similarly for categorization purposes; typically, [[unrecognized]] [[de-facto]] countries or [[w:dependent territory|dependent territories]]",
		class = "polity",
	},
	["county"] = {
		link = true,
		preposition = "of",
		display_handler = county_display_handler,
		class = "subpolity",
	},
	["county borough"] = {
		link = true,
		-- in Wales; similar to a county
		preposition = "of",
		affix_type = "suf",
		fallback = "borough",
		class = "subpolity",
	},
	["county seat"] = {
		link = true,
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
	},
	["county town"] = {
		link = true,
		entry_placetype_use_the = true,
		preposition = "of",
		fallback = "town",
		has_neighborhoods = true,
		class = "capital",
	},
	["county-administered city"] = {
		-- In Taiwan, per Wikipedia similar to a Taiwanese township or district, which is a small city.
		-- NOT anything like a "county-level city" in PR China, which is a county masquerading as a city.
		link = "w",
		fallback = "city",
		has_neighborhoods = true,
		class = "settlement",
	},
	["county-controlled city"] = {
		-- Taiwan
		link = "w",
		fallback = "county-administered city",
	},
	["county-level city"] = {
		-- PR China
		link = "w",
		fallback = "prefecture-level city",
	},
	["crater lake"] = {
		link = true,
		fallback = "lake",
	},
	["creek"] = {
		link = true,
		fallback = "stream",
	},
	["Crown colony"] = {
		link = "+crown colony",
		fallback = "crown colony",
	},
	["crown colony"] = {
		link = true,
		fallback = "colony",
	},
	["Crown dependency"] = {
		link = true,
		fallback = "dependent territory",
	},
	["crown dependency"] = {
		link = true,
		fallback = "dependent territory",
	},
	["cultural area"] = {
		link = "w",
		fallback = "geographic and cultural area",
	},
	["cultural region"] = {
		link = "w",
		fallback = "geographic and cultural area",
	},
	["delegation"] = {
		-- Tunisia
		link = "+w:delegations of Tunisia",
		preposition = "of",
		class = "subpolity",
	},
	["department"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["departmental capital"] = {
		link = "separately",
		fallback = "capital city",
	},
	["dependency"] = {
		link = true,
		fallback = "dependent territory",
	},
	["dependent territory"] = {
		link = "w",
		preposition = "of",
		class = "subpolity",
		former_type = "dependent territory",
		bare_category_parent = "political divisions",
		["country/*"] = {true},
		default = {true},
	},
	["desert"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"ecosystems"},
		default = {true},
	},
	["deserted mediaeval village"] = {
		link = "w",
		fallback = "deserted medieval village",
	},
	["deserted medieval village"] = {
		link = "w",
		fallback = "ANCIENT settlement",
	},
	["direct-administered municipality"] = {
		-- China
		link = "+w:direct-administered municipalities of China",
		fallback = "municipality",
	},
	["direct-controlled municipality"] = {
		-- several countries
		link = "w",
		fallback = "municipality",
	},
	["distributary"] = {
		link = true,
		preposition = "of",
		fallback = "river",
	},
	["district"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		-- Grrr! FIXME! Here is where we need handlers for `class`. Using similar logic to
		-- district_neighborhood_cat_handler, we need to check if we're below or above a city to determine if the class
		-- is "settlement" or "subpolity".
		class = "subpolity",
		cat_handler = district_neighborhood_cat_handler,

		-- No default. Countries for which districts are political divisions will get entries.
	},
	["districts and autonomous regions!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case Portugal.
		category_link = "[[district]]s and [[autonomous region]]s",
		class = "subpolity",
	},
	["districts and autonomous territorial units!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case Moldova.
		category_link = "[[district]]s and [[w:autonomous territorial unit|autonomous territorial unit]]s",
		class = "subpolity",
	},
	["district capital"] = {
		link = "separately",
		fallback = "capital city",
	},
	["district headquarters"] = {
		link = "separately",
		fallback = "administrative centre",
	},
	["district municipality"] = {
		-- In Canada, a district municipality is equivalent to a rural municipality and won't have neighborhoods; in
		-- South Africa, district municipalities group local municipalities and hence won't have neighborhoods.
		link = "w",
		preposition = "of",
		affix_type = "suf",
		no_affix_strings = {"district", "municipality"},
		fallback = "municipality",
		class = "subpolity",
	},
	["division"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["division capital"] = {
		link = "separately",
		fallback = "capital city",
	},
	["dome"] = {
		link = true,
		fallback = "mountain",
	},
	["dormant volcano"] = {
		link = true,
		fallback = "volcano",
	},
	["duchy"] = {
		link = true,
		fallback = "polity",
	},
	["emirate"] = {
		link = true,
		preposition = "of",
		-- FIXME: Can be subpolities (of the United Arab Emirates).
		fallback = "polity",
	},
	["empire"] = {
		link = true,
		fallback = "polity",
	},
	["enclave"] = {
		link = true,
		preposition = "of",
		-- Enclaves can theoretically be any size but assume a subpolity.
		class = "subpolity",
	},
	["entity"] = {
		-- Bosnia and Herzegovina
		link = "+w:entities of Bosnia and Herzegovina",
		preposition = "of",
		class = "subpolity",
	},
	["escarpment"] = {
		link = true,
		fallback = "mountain",
	},
	["ethnographic region"] = {
		-- used in Lithuania
		link = "+w:ethnographic regions of Lithuania",
		fallback = "geographic and cultural area",
	},
	["exclave"] = {
		link = true,
		preposition = "of",
		-- exclaves can theoretically be any size but assume a subpolity.
		class = "subpolity",
	},
	["external territory"] = {
		link = "separately",
		fallback = "dependent territory",
	},
	["farm"] = {
		link = true,
		class = "non-admin settlement",
		default = {"Farms and ranches"},
	},
	["farms and ranches!"] = {
		category_link = "[[farm]]s and [[ranch]]es",
		class = "non-admin settlement",
	},
	["federal city"] = {
		link = "w",
		preposition = "of",
		fallback = "city",
	},
	["federal district"] = {
		link = true,
		preposition = "of",
		-- Might have neighborhoods as federal districts are often cities (e.g. Mexico City)
		has_neighborhoods = true,
		class = "settlement",
	},
	["federal subject"] = {
		-- In Russia; a generic term for first-level administrative divisions (republics, oblasts, okrugs, krais,
		-- autonomous okrugs and autonomous oblasts).
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["federal territory"] = {
		link = "w",
		fallback = "territory",
	},
	["fictional location"] = {
		link = "separately",
		former_type = "!",
		class = "hypothetical location",
		bare_category_parent = "places",
		default = {true},
	},
	["First Nations reserve"] = {
		-- Canada
		link = "[[First Nations]] [[w:Indian reserve|reserve]]",
		-- Wikipedia uses "Indian reserve"; presumably that is the legal term
		fallback = "Indian reserve",
		class = "subpolity",
	},
	["fjord"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["footpath"] = {
		link = true,
		fallback = "road",
	},
	["forest"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"ecosystems", "forestry"},
		default = {true},
	},
	["fort"] = {
		link = true,
		fallback = "building",
	},
	["fortress"] = {
		link = true,
		-- The default plural algorithm gets this right but the singularization algorithm incorrectly converts
		-- fortresses -> fortresse, so put an entry here to ensure we singularize correctly.
		plural = "fortresses",
		fallback = "building",
	},
	["frazione"] = {
		link = "w",
		fallback = "hamlet",
	},
	["freeway"] = {
		link = true,
		fallback = "road",
	},
	["French prefecture"] = {
		link = "[[w:prefectures in France|prefecture]]",
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
	},
	["geographic and cultural area"] = {
		link = "+w:cultural area",
		-- `generic_before_non_cities` is used when generating the category description of categories of the format
		-- `Geographic and cultural areas of PLACE`. `preposition` is used when generating {{place}} description and
		-- categories for any placetype that falls back to `geographic and cultural area`.
		generic_before_non_cities = "of",
		preposition = "of",
		class = "geographic region",
		bare_category_parent = "places",
		["country/*"] = {true},
		["constituent country/*"] = {true},
		["continent/*"] = {true},
		default = {true},
	},
	["geographic area"] = {
		link = "+w:geographic region",
		fallback = "geographic and cultural area",
	},
	["geographic region"] = {
		link = "w",
		fallback = "geographic and cultural area",
	},
	["geographical area"] = {
		link = "w",
		fallback = "geographic and cultural area",
	},
	["geographical region"] = {
		link = "w",
		fallback = "geographic and cultural area",
	},
	["geopolitical zone"] = {
		-- Nigeria
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["gewog"] = {
		-- Bhutan
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["ghost town"] = {
		link = true,
		generic_before_non_cities = "in",
		class = "non-admin settlement",
		bare_category_parent = "former settlements",
		cat_handler = city_type_cat_handler,
		default = {true},
	},
	["glen"] = {
		link = true,
		fallback = "valley",
	},
	["governorate"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["greater administrative region"] = {
		-- China (former division)
		link = "w",
		preposition = "of",
		class = "subpolity",
		inherently_former = {"FORMER"},
	},
	["gromada"] = {
		-- Poland (former division)
		link = "w",
		preposition = "of",
		affix_type = "Pref",
		class = "subpolity",
		inherently_former = {"FORMER"},
	},
	["group of islands"] = {
		link = "[[group]] of [[island]]s",
		plural = "groups of islands",
		plural_link = "[[group]]s of [[island]]s",
		fallback = "island group",
	},
	["gulf"] = {
		link = true,
		preposition = "of",
		holonym_use_the = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["hamlet"] = {
		link = true,
		fallback = "village",
	},
	["harbor city"] = {
		link = "separately",
		fallback = "city",
	},
	["harbor town"] = {
		link = "separately",
		fallback = "town",
	},
	["harbour city"] = {
		link = "separately",
		fallback = "city",
	},
	["harbour town"] = {
		link = "separately",
		fallback = "town",
	},
	["headland"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
	},
	["headquarters"] = {
		link = "w",
		fallback = "administrative centre",
	},
	["heath"] = {
		link = true,
		fallback = "moor",
	},
	["hemisphere"] = {
		link = true,
		entry_placetype_use_the = true,
		fallback = "continental region",
	},
	["highway"] = {
		link = true,
		fallback = "road",
	},
	["hill"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
	},
	["hill station"] = {
		link = "w",
		fallback = "town",
	},
	["hill town"] = {
		link = "w",
		fallback = "town",
	},
	["historic region"] = {
		-- provided only for the link
		link = "+w:historical region",
		fallback = "FORMER geographic region",
	},
	["historical county"] = {
		-- needed for historical counties of England/etc.
		link = "+w:historic county",
		fallback = "FORMER subpolity",
	},
	["historical region"] = {
		-- provided only for the link
		link = "w",
		fallback = "FORMER geographic region",
	},
	["home rule city"] = {
		link = "w",
		fallback = "city",
	},
	["home rule municipality"] = {
		link = "w",
		fallback = "municipality",
	},
	["hot spring"] = {
		link = true,
		fallback = "spring",
	},
	["house"] = {
		link = true,
		fallback = "building",
	},
	["housing estate"] = {
		-- not the same as a housing project (i.e. public housing)
		link = true,
		-- not exactly the case but approximately
		fallback = "neighborhood",
	},
	["hromada"] = {
		-- Ukraine
		link = "w",
		disallow_in_entries = "Use placetype 'urban hromada', 'rural hromada' or 'settlement hromada' in place of bare 'hromada'",
		disallow_in_holonyms = "Use placetype 'urban hromada'/'uhrom', 'rural hromada'/'rhrom' or 'settlement hromada'/'shrom' in place of bare 'hromada'",
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["inactive volcano"] = {
		link = "w",
		fallback = "dormant volcano",
	},
	["independent city"] = {
		link = true,
		fallback = "city",
	},
	["independent town"] = {
		link = "+independent city",
		fallback = "town",
	},
	["Indian reservation"] = {
		link = "w",
		-- In the US. Also known as "Native American reservation" or "domestic dependent nation", and the reservations
		-- themselves often use the term "nation" in their official name (e.g. the "Navajo Nation"). But Wikipedia puts
		-- the article at [[w:Indian reservation]] and uses that term when describing e.g. what the Navajo Nation is,
		-- so this must still be the legal term.
		preposition = "of",
		class = "subpolity",
		default = {true},
	},
	["Indian reserve"] = {
		link = "w",
		-- In Canada. "First Nations reserve" sounds more modern/PC but Wikipedia uses "Indian reserve"; presumably that
		-- is still the legal term.
		preposition = "of",
		class = "subpolity",
		default = {true},
	},
	["inland sea"] = {
		-- note, we also have 'inland' as a qualifier
		link = true,
		fallback = "sea",
	},
	["inner city area"] = {
		link = "[[inner city]] [[area]]",
		fallback = "neighborhood",
	},
	["island"] = {
		link = true,
		preposition = "of",
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
	},
	["island country"] = {
		-- FIXME: The following should map to both 'island' and 'country'.
		link = "w",
		fallback = "country",
	},
	["island group"] = {
		link = "separately",
		fallback = "island",
	},
	["island municipality"] = {
		link = "w",
		fallback = "municipality",
	},
	["islet"] = {
		link = "w",
		fallback = "island",
	},
	["Israeli settlement"] = {
		link = "w",
		class = "settlement",
		default = {true},
	},
	["judicial capital"] = {
		link = "w",
		fallback = "capital city",
	},
	["khanate"] = {
		link = true,
		fallback = "polity",
	},
	["kibbutz"] = {
		link = true,
		plural = "kibbutzim",
		class = "non-admin settlement",
		default = {true},
	},
	["kingdom"] = {
		link = true,
		fallback = "monarchy",
	},
	["krai"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		class = "subpolity",
	},
	["lake"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["landforms!"] = {
		category_link = "[[landform]]s",
		bare_category_parent = "places",
		addl_bare_category_parents = {"Earth"},
	},
	["largest city"] = {
		link = "[[large]]st [[city]]",
		entry_placetype_use_the = true,
		fallback = "city",
		has_neighborhoods = true,
	},
	["league"] = {
		link = true,
		fallback = "confederation",
	},
	["legislative capital"] = {
		link = "separately",
		fallback = "capital city",
	},
	["library"] = {
		link = true,
		fallback = "building",
	},
	["lieutenancy area"] = {
		-- used in the United Kingdom; per Wikipedia:
		-- In England, lieutenancy areas are colloquially known as the ceremonial counties, although this phrase does
		-- not appear in any legislation referring to them. The lieutenancy areas of Scotland are subdivisions of
		-- Scotland that are more or less based on the counties of Scotland, making use of the major cities as separate
		-- entities.[2] In Wales, the lieutenancy areas are known as the preserved counties of Wales and are based on
		-- those used for lieutenancy and local government between 1974 and 1996. The lieutenancy areas of Northern
		-- Ireland correspond to the six counties and two former county boroughs.[3]
		link = "w",
		fallback = "ceremonial county",
	},
	["local authority district"] = {
		link = "w",
		fallback = "local government district",
	},
	["local government area"] = {
		-- Australia
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["local council"] = {
		-- Malta; similar to municipalities
		link = "+w:local councils of Malta",
		preposition = "of",
		fallback = "municipality",
	},
	["local government district"] = {
		link = "w",
		preposition = "of",
		affix_type = "suf",
		affix = "district",
		class = "subpolity",
	},
	["local government district with borough status"] = {
		link = "[[w:local government district|local government district]] with [[w:borough status|borough status]]",
		plural = "local government districts with borough status",
		plural_link = "[[w:local government district|local government districts]] with [[w:borough status|borough status]]",
		preposition = "of",
		affix_type = "suf",
		affix = "district",
		class = "subpolity",
	},
	["local urban district"] = {
		link = "w",
		fallback = "unincorporated community",
	},
	["locality"] = {
		link = "+w:locality (settlement)",
		-- not necessarily true, but usually is the case
		fallback = "village",
	},
	["London borough"] = {
		link = "w",
		preposition = "of",
		affix_type = "pref",
		affix = "borough",
		fallback = "local government district with borough status",
		has_neighborhoods = true,
	},
	["macroregion"] = {
		link = true,
		fallback = "region",
	},
	["man-made structures!"] = {
		category_link = "[[w:geographical feature#Engineered constructs|man-made structures]] such as [[airport]]s, [[university|universities]] and [[metro station]]s",
		bare_category_parent = "places",
	},
	["manor"] = {
		-- FIXME: or is this more like a farm?
		link = true,
		fallback = "building",
	},
	["marginal sea"] = {
		link = true,
		preposition = "of",
		fallback = "sea",
	},
	["market city"] = {
		link = "+market town",
		fallback = "city",
	},
	["market town"] = {
		link = true,
		fallback = "town",
	},
	["massif"] = {
		link = true,
		fallback = "mountain",
	},
	["megacity"] = {
		link = true,
		fallback = "city",
	},
	["metro station"] = {
		link = true,
		class = "man-made structure",
	},
	["metropolitan borough"] = {
		link = true,
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = {"borough", "city"},
		fallback = "local government district",
		has_neighborhoods = true,
	},
	["metropolitan city"] = {
		-- These exist e.g. in Italy and are more like municipalities or even provinces than cities.
		link = true,
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = {"metropolitan", "city"},
		class = "subpolity",
	},
	["metropolitan county"] = {
		link = true,
		fallback = "county",
	},
	["metropolitan municipality"] = {
		-- In South Africa, metropolitan municipalities group local municipalities and are like districts, between
		-- provinces and municipalities.
		-- In Turkey, metropolitan municipalities are provinces-level.
		link = "w",
		preposition = "of",
		affix_type = "Suf",
		no_affix_strings = {"metropolitan", "municipality"},
		fallback = "municipality",
		class = "subpolity",
	},
	["microdistrict"] = {
		-- residential complex in post-Soviet states
		link = true,
		fallback = "neighborhood",
	},
	["micronations!"] = {
		-- FIXME, merge with microstate
		category_link = "[[micronation]]s",
		bare_category_parent = "countries",
	},
	["microstate"] = {
		link = true,
		fallback = "country",
	},
	["military base"] = {
		link = "w",
		class = "settlement", -- or "man-made structure"?
		default = {true},
	},
	["minster town"] = {
		-- England
		link = "separately",
		fallback = "town",
	},
	["monarchy"] = {
		link = true,
		fallback = "polity",
	},
	["moor"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms", "ecosystems"},
		default = {true},
	},
	["moorland"] = {
		link = true,
		fallback = "moor",
	},
	["motorway"] = {
		link = true,
		fallback = "road",
	},
	["mountain"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
	},
	["mountain indigenous district"] = {
		-- Taiwan
		link = "+w:district (Taiwan)",
		fallback = "district",
	},
	["mountain indigenous township"] = {
		-- Taiwan
		link = "+w:township (Taiwan)",
		fallback = "township",
	},
	["mountain pass"] = {
		link = true,
		-- The default plural algorithm gets this right but the singularization algorithm incorrectly converts
		-- passes -> passe, so put an entry here to ensure we singularize correctly.
		plural = "mountain passes",
		class = "natural feature",
		addl_bare_category_parents = {"mountains"},
		default = {true},
	},
	["mountain range"] = {
		link = true,
		fallback = "mountain",
	},
	["mountainous region"] = {
		link = "separately",
		fallback = "region",
	},
	["mukim"] = {
		-- Malaysia, Brunei, Indonesia, Singapore
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["municipal district"] = {
		link = "w",
		-- meaning varies depending on the country; for now, assume no neighborhoods.
		-- FIXME: has_neighborhoods might have to be a function that looks at the containing holonyms.
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = "district",
		fallback = "municipality",
	},
	["municipality"] = {
		link = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "subpolity",
	},
	["municipality with city status"] = {
		link = "[[municipality]] with [[w:city status|city status]]",
		plural = "municipalities with city status",
		plural_link = "[[municipality|municipalities]] with [[w:city status|city status]]",
		fallback = "municipality",
	},
	["museum"] = {
		link = true,
		fallback = "building",
	},
	["mythological location"] = {
		link = "separately",
		former_type = "!",
		class = "hypothetical location",
		bare_category_parent = "places",
		default = {true},
	},
	["named bridges!"] = {
		category_link = "notable [[bridge]]s",
		bare_category_parent = "man-made structures",
		addl_bare_category_parents = {"bridges"},
	},
	["named buildings!"] = {
		category_link = "notable [[house]]s, [[library|libraries]] and other [[building]]s",
		bare_category_parent = "man-made structures",
		addl_bare_category_parents = {"buildings"},
	},
	["named roads!"] = {
		category_link = "notable [[road]]s, [[highway]]s, [[trail]]s and similar linear structures",
		bare_category_parent = "man-made structures",
		addl_bare_category_parents = {"roads"},
	},
	["national capital"] = {
		link = "w",
		fallback = "capital city",
	},
	["national park"] = {
		link = true,
		fallback = "park",
	},
	["natural features!"] = {
		category_link = "[[w:geographical feature#Natural features|natural features]] such as [[lake]]s, [[mountain]]s, [[island]]s and [[ocean]]s",
		bare_category_parent = "places",
	},
	["neighborhood"] = {
		-- The majority of the properties here apply to both `neighborhoods` and `neighbourhoods`; the choice of which
		-- one to use is made by district_neighborhood_cat_handler() based on the value of `british_spelling` for the
		-- location (city, political division, etc.) of the holonym that follows the word "neighbo(u)hoods" in the
		-- category name. It does *NOT* depend on whether the {{place}} call uses "neighborhoods" or "neighbourhoods".
		-- (In general it can't, because other things like "urban areas", "districts", "subdivisions" and the like also
		-- categorize as neighbo(u)rhoods.)
		link = true,
		-- See below. These are used by category handlers in [[Module:category tree/topic cat/data/Places]].
		generic_before_non_cities = "in",
		generic_before_cities = "of",
		-- The following text is suitable for the top-level description of a neighborhood as well as categories of the
		-- form `Neighborhoods in POLDIV` e.g. `Neighborhoods in Illinois, USA` but not for categories of the form
		-- `Neighborhoods of Chicago`, where we'd get "... and other subportions of [[city|cities]] of [[Chicago]]".
		category_link = "[[neighborhood]]s, [[district]]s and other subportions of [[city|cities]]",
		category_link_before_city = "[[neighborhood]]s, [[district]]s and other subportions",
		-- NOTE: This setting is needed for administrative divisions like barangays that fall back to `neighborhood`,
		-- when set in [[Module:place/locations]] for a specific country (e.g. the Philippines). The above settings
		-- for `generic_before_non_cities` and `generic_before_cities` are used by category handlers in
		-- [[Module:category tree/topic cat/data/Places]] for `Neighborhoods in POLDIV` and `Neighborhoods of CITY`
		-- categories. In fact, district_neighborhood_cat_handler() does not currently pay attention to them, but
		-- generates "of" before cities and "in" before non-cities regardless. (FIXME: We should change that.)
		preposition = "of",
		class = "non-admin settlement",
		cat_handler = district_neighborhood_cat_handler,
	},
	["neighbourhood"] = {
		link = true,
		category_link = "[[neighbourhood]]s, [[district]]s and other subportions of [[city|cities]]",
		category_link_before_city = "[[neighbourhood]]s, [[district]]s and other subportions",
		fallback = "neighborhood",
	},
	["new area"] = {
		-- China (type of economic development zone, varying greatly in size)
		link = "w",
		preposition = "in",
		class = "subpolity", --?
	},
	["new town"] = {
		link = true,
		fallback = "town",
	},
	["non-city capital"] = {
		link = "[[capital]]",
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
		cat_handler = function(data)
			return capital_city_cat_handler(data, "non-city")
		end,
		-- FIXME, do we need the following?
		default = {true},
	},
	["non-metropolitan county"] = {
		link = "w",
		fallback = "county",
	},
	["non-metropolitan district"] = {
		link = "w",
		fallback = "local government district",
	},
	["non-sovereign kingdom"] = {
		-- especially in Africa and Asia
		link = "+w:non-sovereign monarchy",
		generic_before_non_cities = "in",
		class = "subpolity",
		["country/*"] = {true},
		["continent/*"] = {true},
		default = {true},
	},
	["non-sovereign monarchy"] = {
		link = "w",
		fallback = "non-sovereign kingdom",
	},
	["oblast"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		class = "subpolity",
	},
	["oblasts and autonomous republics!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case Ukraine.
		category_link = "[[oblast]]s and [[w:autonomous republic|autonomous republic]]s",
		class = "subpolity",
	},
	["ocean"] = {
		link = true,
		holonym_use_the = true,
		class = "natural feature",
		addl_bare_category_parents = {"seas", "bodies of water"},
		default = {true},
	},
	["okrug"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		class = "subpolity",
	},
	["overseas collectivity"] = {
		link = "w",
		fallback = "collectivity",
	},
	["overseas department"] = {
		link = "w",
		fallback = "department",
	},
	["overseas territory"] = {
		link = "w",
		fallback = "dependent territory",
	},
	["parish"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["parish municipality"] = {
		-- in Quebec, often similar to a rural village; the famous [[Saint-Louis-du-Ha! Ha!]] is one of them.
		link = "+w:parish municipality (Quebec)",
		preposition = "of",
		fallback = "municipality",
		has_neighborhoods = true,
	},
	["parish seat"] = {
		link = true,
		entry_placetype_use_the = true,
		preposition = "of",
		class = "capital",
		has_neighborhoods = true,
	},
	["park"] = {
		link = true,
		class = "man-made structure",
		default = {true},
	},
	["pass"] = {
		link = "+mountain pass",
		-- The default plural algorithm gets this right but the singularization algorithm incorrectly converts
		-- passes -> passe, so put an entry here to ensure we singularize correctly.
		plural = "passes",
		fallback = "mountain pass",
	},
	["path"] = {
		link = true,
		fallback = "road",
	},
	["peak"] = {
		link = true,
		fallback = "mountain",
	},
	["peninsula"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
	},
	["periphery"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["places!"] = {
		generic_before_non_cities = "in",
		generic_before_cities = "in",
		class = "generic place",
		category_link = "[[place]]s of all sorts",
		-- `category_link_top_level` control the description used in the top-level [[Category:Places]] and
		-- language-specific variants such as [[Category:en:Places]]. The actual text for a language-spefic variant is
		-- "{{{langname}}} names of [[geographical]] [[place]]s of all sorts; [[toponym]]s." where the "names of"
		-- portion is automatically generated by the appropriate handler in
		-- [[Module:category tree/topic cat/data/Places]].
		category_link_top_level = "[[geographical]] [[place]]s of all sorts; [[toponym]]s",
		bare_category_parent = "names",
	},
	["planned community"] = {
		-- Include this so we don't categorize 'planned community' into villages, as 'community' does.
		link = true,
		class = "settlement",
		has_neighborhoods = true,
	},
	["plateau"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true},
		-- FIXME: Should generate both "Plateaus" and the appropriate 'geographic and cultural area' category
	},
	["Polish colony"] = {
		link = "[[w:colony (Poland)|colony]]",
		affix_type = "suf",
		affix = "colony",
		fallback = "village",
		has_neighborhoods = true,
	},
	["political divisions!"] = {
		category_link = "[[political]] [[division]]s and [[subdivision]]s, such as [[state]]s, [[province]]s, [[county|counties]] or [[district]]s",
		bare_category_parent = "places",
	},
	["polity"] = {
		link = true,
		category_link = "[[independent]] or [[semi-]][[independent]] [[polity|polities]]",
		class = "polity",
		bare_category_parent = "places",
		default = {true},
	},
	["populated place"] = {
		link = "+w:populated place",
		-- not necessarily true, but usually is the case
		fallback = "village",
	},
	["port"] = {
		link = true,
		class = "man-made structure",
		default = {true},
	},
	["port city"] = {
		-- FIXME: should categorize into "Ports" as well as "Cities"
		link = true,
		fallback = "city",
	},
	["port town"] = {
		-- FIXME: should categorize into "Ports" as well as "Towns"
		link = "w",
		fallback = "town",
	},
	["prefecture"] = {
		-- FIXME! `prefecture` is like a county in Japan and elsewhere but a department capital city in France.
		-- May need `has_neighborhoods` to be a function.
		link = true,
		preposition = "of",
		display_handler = prefecture_display_handler,
		class = "subpolity",
	},
	["prefecture-level city"] = {
		-- China; they are huge entities with a central city; not cities themselves.
		link = "w",
		preposition = "of",
		class = "subpolity",
	},
	["preserved county"] = {
		-- In Wales; they are former counties enshrined in law; there are 8 of them and each consists of one or more
		-- "principal areas" (styled as "counties" or "county boroughs"), of which there are 22.
		link = "w",
		preposition = "of",
		class = "subpolity",
		inherently_former = {"FORMER"},
	},
	["primary area"] = {
		-- a grouping of "districts" (neighborhoods) in Gothenburg, Sweden
		link = "+w:sv:primärområde",
		fallback = "neighborhood",
	},
	["principality"] = {
		link = true,
		fallback = "monarchy",
	},
	["promontory"] = {
		link = true,
		fallback = "headland",
	},
	["protectorate"] = {
		link = true,
		fallback = "dependent territory",
	},
	["province"] = {
		link = true,
		preposition = "of",
		display_handler = province_display_handler,
		class = "subpolity",
	},
	["provinces and autonomous regions!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case China.
		category_link = "[[province]]s and [[autonomous region]]s",
		class = "subpolity",
	},
	["provinces and territories!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case Canada and Pakistan.
		category_link = "[[province]]s and [[territory|territories]]",
		class = "subpolity",
	},
	["provincial capital"] = {
		link = true,
		fallback = "capital city",
	},
	["raion"] = {
		link = true,
		preposition = "of",
		affix_type = "Suf",
		class = "subpolity",
	},
	["ranch"] = {
		link = true,
		fallback = "farm",
	},
	["range"] = {
		-- FIXME: Where is this used? Is it a mountain range?
		link = true,
		holonym_use_the = true,
		class = "natural feature",
	},
	["regency"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["region"] = {
		link = true,
		preposition = "of",
		-- If 'region' isn't a specific administrative division, fall back to 'geographic and cultural area'
		fallback = "geographic and cultural area",
		-- "former region" is a subpolity but traditional/historic(al)/ancient/medieval/etc. is a geographic region
		class = "geographic region",
	},
	["regional capital"] = {
		link = "separately",
		fallback = "capital city",
	},
	["regional county municipality"] = {
		-- Quebec
		link = "w",
		preposition = "of",
		affix_type = "Suf",
		no_affix_strings = {"municipality", "county"},
		fallback = "municipality",
	},
	["regional district"] = {
		link = "w",
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = "district",
		fallback = "district",
	},
	["regional municipality"] = {
		link = "w",
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = "municipality",
		fallback = "municipality",
	},
	["regional unit"] = {
		link = "w",
		preposition = "of",
		affix_type = "suf",
		class = "subpolity",
	},
	["registration county"] = {
		-- Used in Scotland for land registration purposes; formerly used in England, Wales and Ireland for statistical
		-- purposes (registration of births, deaths and marriages, and for the output of census information).
		link = "w",
		fallback = "county",
	},
	["republic"] = {
		-- Of Russia, Yugoslavia, etc. "Republics" in general are sovereign but we use "country" in that case.
		link = true,
		fallback = "constituent republic",
	},
	["research base"] = {
		link = "+w:research station",
		fallback = "research station",
	},
	["research station"] = {
		link = "w",
		class = "non-admin settlement", -- or "man-made structure"?
		default = {true},
	},
	["reservoir"] = {
		link = true,
		fallback = "lake",
	},
	["residential area"] = {
		link = "separately",
		fallback = "neighborhood",
	},
	["resort city"] = {
		link = "w",
		fallback = "city",
	},
	["resort town"] = {
		link = "w",
		fallback = "town",
	},
	["river"] = {
		link = true,
		generic_before_non_cities = "in",
		holonym_use_the = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		cat_handler = city_type_cat_handler,
		["continent/*"] = {true},
		default = {true},
	},
	["river island"] = {
		link = "w",
		fallback = "island",
	},
	["road"] = {
		link = true,
		class = "man-made structure",
		default = {"Named roads"},
	},
	["Roman province"] = {
		-- FIXME! Eliminate this in favor of 'former province|emp/Roman Empire'
		link = "w",
		default = {"Provinces of the Roman Empire"},
		class = "subpolity",
	},
	["royal borough"] = {
		link = "w",
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = {"royal", "borough"},
		fallback = "local government district with borough status",
		has_neighborhoods = true,
	},
	["royal burgh"] = {
		link = true,
		fallback = "borough",
	},
	["royal capital"] = {
		link = "w",
		fallback = "capital city",
	},
	["rural committee"] = {
		-- Hong Kong; a group of villages
		link = "w",
		affix_type = "Suf",
		has_neighborhoods = true,
		class = "settlement",
	},
	["rural community"] = {
		-- New Brunswick
		link = "+w:list of municipalities in New_Brunswick#Rural communities",
		fallback = "municipality",
	},
	["rural hromada"] = {
		link = "[[rural]] [[w:hromada|hromada]]",
		affix_type = "suf",
		fallback = "hromada",
	},
	["rural municipality"] = {
		link = "w",
		preposition = "of",
		affix_type = "Pref",
		no_affix_strings = "municipality",
		fallback = "municipality",
		has_neighborhoods = true, --?
	},
	["rural township"] = {
		-- Taiwan
		link = "+w:rural township (Taiwan)",
		fallback = "township",
	},
	["sanctuary"] = {
		link = true,
		fallback = "temple",
	},
	["satrapy"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
		inherently_former = {"ANCIENT", "FORMER"},
	},
	["sea"] = {
		link = true,
		holonym_use_the = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["seaport"] = {
		link = true,
		fallback = "port",
	},
	["seat"] = {
		link = true,
		fallback = "administrative centre",
	},
	["self-administered area"] = {
		-- Myanmar (groups self-administered divisions and zones)
		link = "+w:self-administered zone",
		preposition = "of",
		class = "subpolity",
	},
	["self-administered division"] = {
		-- Myanmar (only one of them: Wa Self-Administered Division)
		link = "w",
		fallback = "self-administered area",
	},
	["self-administered zone"] = {
		-- Myanmar (five of them)
		link = "w",
		fallback = "self-administered area",
	},
	["separatist state"] = {
		link = "separately",
		fallback = "unrecognized country",
	},
	["settlement"] = {
		link = true,
		category_link = "[[settlement]]s such as [[city|cities]], [[village]]s and [[farm]]s",
		bare_category_parent = "places",
		-- not necessarily true, but usually is the case
		fallback = "village",
	},
	["settlement hromada"] = {
		link = "[[w:Populated places in Ukraine#Rural settlements|settlement]] [[w:hromada|hromada]]",
		affix_type = "suf",
		fallback = "hromada",
	},
	["sheading"] = {
		-- Isle of Man
		link = true,
		fallback = "district",
	},
	["sheep station"] = {
		-- Australia
		link = true,
		fallback = "farm",
	},
	["shire"] = {
		link = true,
		fallback = "county",
	},
	["shire county"] = {
		link = "w",
		fallback = "county",
	},
	["shire town"] = {
		link = true,
		fallback = "county seat",
	},
	["ski resort city"] = {
		link = "[[ski resort]] [[city]]",
		fallback = "city",
	},
	["ski resort town"] = {
		link = "[[ski resort]] [[town]]",
		fallback = "town",
	},
	["spa city"] = {
		link = "+w:spa town",
		fallback = "city",
	},
	["spa town"] = {
		link = "w",
		fallback = "town",
	},
	["space station"] = {
		link = true,
		fallback = "research station",
	},
	["special administrative region"] = {
		-- in China; in practice they are city-like (Hong Kong, Macau); also [[Oecusse]] in East Timor is formally a
		-- "special administrative region"; North Korea had one such region planned (Sinuiju) but abandoned; Indonesia
		-- has similar "special regions" of Jakarta, Yogyakarta and Aceh; and South Sudan has three "special
		-- administrative areas"
		link = "+w:special administrative regions of China",
		preposition = "of",
		class = "subpolity",
		has_neighborhoods = true, --?
		-- no suffix since places in Hong Kong or Macau are listed without China, except Hong Kong and Macau themselves
		-- they also contain regions (or areas), e.g. [[Kowloon]], so it would be confusing
		suffix = "",
	},
	["special collectivity"] = {
		link = "w",
		fallback = "collectivity",
	},
	["special municipality"] = {
		-- formerly linked to the Taiwan article but there are also special municipalities of the Netherlands
		link = "w",
		fallback = "municipality",
	},
	["special ward"] = {
		-- Tokyo
		link = true,
		fallback = "municipality",
	},
	["spit"] = {
		link = true,
		fallback = "peninsula",
	},
	["spring"] = {
		link = true,
		class = "natural feature",
		default = {true},
	},
	["star"] = {
		link = true,
		class = "natural feature",
		default = {true},
	},
	["state"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
		-- 'former/historical state' could refer either to a state of a country (a division) or a state = sovereign
		-- entity. The latter appears more common (e.g. in various "ancient states" of East Asia).
		former_type = "polity",
	},
	["states and territories!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case Australia.
		category_link = "[[state]]s and [[territory|territories]]",
		class = "subpolity",
	},
	["states and union territories!"] = {
		-- This and other similar "combined placetypes" are for use in the plural when grouping first-level
		-- administrative regions of certain countries, in this case India.
		category_link = "[[state]]s and [[union territory|union territories]]",
		class = "subpolity",
	},
	["state capital"] = {
		link = true,
		fallback = "capital city",
	},
	["state park"] = {
		link = true,
		fallback = "park",
	},
	["state-level new area"] = {
		-- China (type of economic development zone, varying greatly in size)
		link = "w",
		fallback = "new area",
	},
	["statistical region"] = {
		-- Slovenia
		link = true,
		fallback = "administrative region",
	},
	["statutory city"] = {
		link = "w",
		fallback = "city",
	},
	["statutory town"] = {
		link = "w",
		fallback = "town",
	},
	["strait"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"bodies of water"},
		default = {true},
	},
	["stream"] = {
		link = true,
		fallback = "river",
	},
	["street"] = {
		link = true,
		fallback = "road",
	},
	["strip"] = {
		link = true,
		fallback = "geographic region",
	},
	["strip of land"] = {
		link = "[[strip]] of [[land]]",
		plural = "strips of land",
		plural_link = "[[strip]]s of [[land]]",
		fallback = "geographic region",
	},
	["sub-metropolitan city"] = {
		link = "+w:List of cities in Nepal#Sub-metropolitan cities",
		fallback = "city",
	},
	["sub-prefectural city"] = {
		link = "w",
		fallback = "subprovincial city",
	},
	["subdistrict"] = {
		link = true,
		preposition = "of",
		has_neighborhoods = true, --?
		-- FIXME: subdistricts can be neighborhood-like (of Jakarta) or larger (in China); need a handler
		class = "subpolity",
		default = {true},
	},
	["subdivision"] = {
		link = true,
		preposition = "of",
		affix_type = "suf",
		-- FIXME: subdivisions can be neighborhood-like or larger; need a handler
		class = "subpolity",
		cat_handler = district_neighborhood_cat_handler,
	},
	["submerged ghost town"] = {
		-- FIXME: Consider just having "submerged" as a qualifier.
		link = "[[submerged]] [[ghost town]]",
		fallback = "ghost town",
	},
	["subnational kingdom"] = {
		link = "+w:subnational monarchy",
		fallback = "non-sovereign kingdom",
	},
	["subnational monarchy"] = {
		link = "w",
		fallback = "non-sovereign kingdom",
	},
	["subprefecture"] = {
		link = true,
		affix_type = "suf",
		preposition = "of",
		class = "subpolity",
	},
	["subprovince"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["subprovincial city"] = {
		link = "w",
		-- China; special status given to certain prefecture-level cities
		fallback = "prefecture-level city",
	},
	["subprovincial district"] = {
		link = "w",
		-- China; special status given to Binhai New Area and Pudong New Area, which are county-level districts
		preposition = "of",
		class = "subpolity",
	},
	["subregion"] = {
		link = true,
		fallback = "geographic region",
	},
	["suburb"] = {
		link = true,
		-- The following text is suitable for the top-level description of a suburb as well as categories of the form
		-- 'Suburbs in POLDIV' e.g. 'Suburbs in Illinois, USA' but not for categories of the form 'Suburbs of Chicago',
		-- where we'd get "[[suburb]]s of [[city|cities]] of [[Chicago]]".
		category_link = "[[suburb]]s of [[city|cities]]",
		category_link_before_city = "[[suburb]]s",
		-- See comments under "neighborhood" for the following three settings. They are used by
		-- [[Module:category tree/topic cat/data/Places]] for generating the text of 'Suburbs in/of PLACE' categories
		-- but currently ignored by district_neighborhood_cat_handler (which actually generates the categories for a
		-- given page), which hardcodes "in" for non-cities and "of" for cities. (FIXME: Change this.)
		generic_before_non_cities = "in",
		generic_before_cities = "of",
		preposition = "of",
		has_neighborhoods = true, --?
		class = "non-admin settlement", --?
		cat_handler = district_neighborhood_cat_handler,
	},
	["suburban area"] = {
		link = "w",
		fallback = "suburb",
	},
	["subway station"] = {
		link = "w",
		fallback = "metro station",
	},
	["sum"] = {
		-- In China, Mongolia, Russia; something like a county in Mongolia but a township in China (Inner Mongolia),
		-- and equivalent to a [[selsoviet]] in the parts of Russia where it's in use (a rural council, below a raion).
		link = "+w:sum (administrative division)",
		-- This fallback is somewha arbitrary. We could use "county" but that has a display handler
		-- which we don't want to be active (FIXME: If the display handler would be active, that's a bug).
		fallback = "division",
	},
	["supercontinent"] = {
		link = true,
		fallback = "continent",
	},
	["tehsil"] = {
		link = true,
		affix_type = "suf",
		no_affix_strings = {"tehsil", "tahsil"},
		class = "subpolity",
	},
	["temple"] = {
		link = true,
		fallback = "building",
	},
	["territorial authority"] = {
		link = "w",
		fallback = "district",
	},
	["territory"] = {
		link = true,
		preposition = "of",
		class = "subpolity",
	},
	["theme"] = {
		link = "+w:theme (Byzantine district)",
		preposition = "of",
		class = "subpolity",
	},
	["town"] = {
		link = true,
		generic_before_non_cities = "in",
		has_neighborhoods = true,
		class = "settlement",
		cat_handler = city_type_cat_handler,
		default = {true},
	},
	["town with bystatus"] = {
		-- can't use templates in links currently
		link = "[[town]] with [[bystatus#Norwegian Bokmål|bystatus]]",
		plural = "towns with bystatus",
		plural_link = "[[town]]s with [[bystatus#Norwegian Bokmål|bystatus]]",
		fallback = "town",
	},
	["township"] = {
		link = true,
		has_neighborhoods = true,
		class = "settlement", --?
		default = {true},
	},
	["township municipality"] = {
		-- Quebec
		link = "+w:township municipality (Quebec)",
		preposition = "of",
		fallback = "municipality",
		has_neighborhoods = true, --?
	},
	["traditional county"] = {
		link = true,
		fallback = "county",
	},
	["traditional region"] = {
		-- FIXME: Verify this works. Same for 'historic(al) region'.
		-- provided only for the link
		link = "w",
		fallback = "FORMER geographic region",
	},
	["trail"] = {
		link = true,
		fallback = "road",
	},
	["treaty port"] = {
		link = "w",
		fallback = "city",
		class = "settlement",
		inherently_former = {"FORMER"},
	},
	["tributary"] = {
		link = true,
		preposition = "of",
		fallback = "river",
	},
	["underground station"] = {
		link = "w",
		fallback = "metro station",
	},
	["unincorporated area"] = {
		link = "w",
		-- I don't know if this fallback makes sense everywhere.
		fallback = "unincorporated community",
	},
	["unincorporated community"] = {
		link = true,
		generic_before_non_cities = "in",
		class = "non-admin settlement",
	},
	["unincorporated territory"] = {
		link = "w",
		fallback = "territory",
	},
	["union territory"] = {
		-- India
		link = true,
		preposition = "of",
		entry_placetype_indefinite_article = "a",
		class = "subpolity",
	},
	["unitary authority"] = {
		-- UK, New Zealand
		link = true,
		entry_placetype_indefinite_article = "a",
		fallback = "local government district",
	},
	["unitary district"] = {
		link = "w",
		entry_placetype_indefinite_article = "a",
		fallback = "local government district",
	},
	["united township municipality"] = {
		-- Quebec
		link = "+w:united township municipality (Quebec)",
		entry_placetype_indefinite_article = "a",
		fallback = "township municipality",
		has_neighborhoods = true, --?
	},
	["university"] = {
		link = true,
		entry_placetype_indefinite_article = "a",
		class = "man-made structure",
		default = {true},
	},
	["unrecognised country"] = {
		link = "w",
		fallback = "unrecognized country",
	},
	["unrecognized and nearly unrecognized countries!"] = {
		category_link = "[[de facto]] [[independent]] [[state]]s with little or no {{w|international recognition}}",
		bare_category_parent = "country-like entities",
	},
	["unrecognized country"] = {
		link = "w",
		class = "polity",
		default = {"Unrecognized and nearly unrecognized countries"},
	},
	["unrecognised state"] = {
		link = "w",
		fallback = "unrecognized country",
	},
	["unrecognized state"] = {
		link = "w",
		fallback = "unrecognized country",
	},
	["urban area"] = {
		link = "separately",
		fallback = "neighborhood",
	},
	["urban hromada"] = {
		link = "[[urban]] [[w:hromada|hromada]]",
		affix_type = "suf",
		fallback = "hromada",
	},
	["urban service area"] = {
		-- A strange beast existing in Alberta; technically a type of hamlet but in practice used for much larger
		-- cities and treated equivalent to a city. (There are only two of them, [[Fort McMurray]] and [[Sherwood Park]]).
		link = "w",
		fallback = "city",
	},
	["urban township"] = {
		link = "w",
		fallback = "township",
	},
	["urban-type settlement"] = {
		-- appears to be a particular type of small urban settlement in post-Soviet states,
		-- had an administrative function.
		link = "w",
		fallback = "town",
	},
	["valley"] = {
		link = true,
		class = "natural feature",
		addl_bare_category_parents = {"landforms", "water"},
		default = {true},
	},
	["viceroyalty"] = {
		-- in essence, a type of colony
		link = true,
		fallback = "dependent territory",
	},
	["village"] = {
		link = true,
		generic_before_non_cities = "in",
		category_link = "[[village]]s, [[hamlet]]s, and other small [[community|communities]] and [[settlement]]s",
		class = "settlement",
		cat_handler = city_type_cat_handler,
		default = {true},
	},
	["village development committee"] = {
		-- former administrative structure in Nepal; also exists in India but not as a formal unit
		link = "+w:village development committee (Nepal)",
		inherently_former = {"FORMER"},
		fallback = "village",
	},
	["village municipality"] = {
		-- Quebec
		link = "+w:village municipality (Quebec)",
		preposition = "of",
		fallback = "municipality",
		has_neighborhoods = true, --?
	},
	["voivodeship"] = {
		-- Poland
		link = true,
		display_handler = voivodeship_display_handler,
		preposition = "of",
		class = "subpolity",
	},
	["volcano"] = {
		link = true,
		plural = "volcanoes",
		class = "natural feature",
		addl_bare_category_parents = {"landforms"},
		default = {true, "Mountains"},
	},
	["ward"] = {
		link = true,
		class = "settlement",
		-- Wards are formal administrative divisions of a city but have some properties of neighborhoods.
		fallback = "neighborhood",
	},
	["watercourse"] = {
		link = true,
		fallback = "channel",
	},
	["Welsh community"] = {
		-- Wales
		link = "[[w:community (Wales)|community]]",
		preposition = "of",
		affix_type = "suf",
		affix = "community",
		has_neighborhoods = true,
		class = "settlement",
	},
	["zone"] = {
		-- administrative division of Ethiopia, Qatar, Nepal, India
		link = "+w:zone#Place names",
		preposition = "of",
		class = "subpolity",
	},

	----------------------------------------------------------------------------------------------
	--                               Categories for former places                               --
	----------------------------------------------------------------------------------------------

	["ANCIENT capital"] = {
		link = false,
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
		-- FIXME: Consider removing 'ancient settlements' here. Ancient capitals, like former capitals, often still
		-- exist but just aren't the capital any more. Maybe we should have an 'Ancient capitals' category.
		default = {"Ancient settlements", "Former capitals"},
	},
	["ANCIENT non-admin settlement"] = {
		link = false,
		class = "non-admin settlement",
		fallback = "ANCIENT settlement",
	},
	["ANCIENT settlement"] = {
		link = false,
		has_neighborhoods = true,
		class = "settlement",
		default = {"Ancient settlements"},
	},
	["ancient settlements!"] = {
		category_link = "former [[city|cities]], [[town]]s and [[village]]s that existed in [[antiquity]]",
		bare_category_parent = "former settlements",
	},

	["FORMER capital"] = {
		link = false,
		entry_placetype_use_the = true,
		preposition = "of",
		has_neighborhoods = true,
		class = "capital",
		default = {"Former capitals"},
	},
	["former capitals!"] = {
		category_link = "former [[capital]] [[city|cities]] and [[town]]s",
		bare_category_parent = "settlements",
	},
	["former counties and county-level cities!"] = {
		-- For categorizing former counties and county-level cities of China
		category_link = "no-longer existing [[county|counties]] and [[county-level city|county-level cities]]",
		bare_category_breadcrumb = "counties and county-level cities",
		bare_category_parent = "former political divisions",
	},
	["FORMER county"] = {
		-- For categorizing former counties and county-level cities of China
		link = false,
		fallback = "FORMER subpolity",
	},
	["FORMER county-level city"] = {
		-- For categorizing former counties and county-level cities of China
		link = false,
		fallback = "FORMER subpolity",
	},
	["former countries and country-like entities!"] = {
		category_link = "[[country|countries]] and similar [[polity|polities]] that no longer exist",
		bare_category_breadcrumb = "countries and country-like entities",
		bare_category_parent = "former polities",
	},
	["FORMER country"] = {
		link = false,
		class = "polity",
		default = {"Former countries and country-like entities"},
	},
	["former dependent territories!"] = {
		category_link = "[[w:dependent territory|dependent territories]] (colonies, dependencies, protectorates, etc.) that no longer exist",
		bare_category_breadcrumb = "dependent territories",
		bare_category_parent = "former political divisions",
	},
	["FORMER dependent territory"] = {
		link = false,
		preposition = "of",
		class = "subpolity",
		default = {"Former dependent territories"},
	},
	["former districts!"] = {
		-- For categorizing former districts of China
		category_link = "no-longer-existing [[district]]s",
		bare_category_breadcrumb = "districts",
		bare_category_parent = "former political divisions",
	},
	["FORMER district"] = {
		-- For categorizing former districts of China
		link = false,
		fallback = "FORMER subpolity",
	},
	["FORMER geographic region"] = {
		link = false,
		fallback = "geographic and cultural area",
	},
	["FORMER man-made structure"] = {
		link = false,
		class = "man-made structure",
		default = {"Former man-made structures"},
	},
	["former man-made structures!"] = {
		category_link = "man-made structures such as [[airport]]s and [[park]]s that no longer exist",
		bare_category_breadcrumb = "man-made structures",
		bare_category_parent = "former places",
	},
	["former municipalities!"] = {
		-- For categorizing former municipalities of the Netherlands
		category_link = "no-longer-existing [[municipality|municipalities]]",
		bare_category_breadcrumb = "municipalities",
		bare_category_parent = "former political divisions",
	},
	["FORMER municipality"] = {
		-- For categorizing former municipalities of the Netherlands
		link = false,
		fallback = "FORMER subpolity",
	},
	["FORMER natural feature"] = {
		link = false,
		class = "natural feature",
		default = {"Former natural features"},
	},
	["former natural features!"] = {
		category_link = "natural features such as [[lake]]s, [[river]]s and [[island]]s that no longer exist",
		bare_category_breadcrumb = "natural features",
		bare_category_parent = "former places",
	},
	["FORMER non-admin settlement"] = {
		link = false,
		class = "non-admin settlement",
		fallback = "FORMER settlement",
	},
	["former places!"] = {
		category_link = "[[place]]s of all sorts that no longer exist",
		bare_category_breadcrumb = "former",
		bare_category_parent = "places",
	},
	["former political divisions!"] = {
		category_link = "[[political]] [[division]]s (states, provinces, counties, etc.) that no longer exist",
		bare_category_breadcrumb = "political divisions",
		bare_category_parent = "former places",
	},
	["former polities!"] = {
		category_link = "[[polity|polities]] (countries, kingdoms, empires, etc.) that no longer exist",
		bare_category_breadcrumb = "polities",
		bare_category_parent = "former places",
	},
	["FORMER polity"] = {
		link = false,
		class = "polity",
		default = {"Former polities"},
	},
	["former prefectures!"] = {
		-- For categorizing former prefectures of China
		category_link = "no-longer-existing [[prefecture]]s",
		bare_category_breadcrumb = "prefectures",
		bare_category_parent = "former political divisions",
	},
	["FORMER prefecture"] = {
		-- For categorizing former prefectures of China
		link = false,
		fallback = "FORMER subpolity",
	},
	["former provinces!"] = {
		-- For categorizing former provinces of China, etc.
		category_link = "no-longer-existing [[province]]s",
		bare_category_breadcrumb = "provinces",
		bare_category_parent = "former political divisions",
	},
	["FORMER province"] = {
		-- For categorizing ancient/historical/former provinces of the Roman Empire
		link = false,
		fallback = "FORMER subpolity",
	},
	["former region"] = {
		-- A former region is considered a former political division, but not a 'historical/traditional/etc.' region.
		link = "separately",
		preposition = "of",
		inherently_former = {"FORMER"},
		class = "subpolity",
	},
	["FORMER settlement"] = {
		link = false,
		has_neighborhoods = true,
		class = "settlement",
		default = {"Former settlements"},
	},
	["former settlements!"] = {
		category_link = "[[city|cities]], [[town]]s and [[village]]s that no longer exist or have been merged or reclassified",
		bare_category_breadcrumb = "settlements",
		bare_category_parent = "former political divisions",
	},
	["FORMER subpolity"] = {
		link = false,
		preposition = "of",
		class = "subpolity",
		default = {"Former political divisions"},
	},

	----------------------------------------------------------------------------------------------
	--                                      form-of categories                                  --
	----------------------------------------------------------------------------------------------

	---------- Abbreviations ----------

	["abbreviations of counties!"] = {
		-- For categorizing abbreviations of counties of e.g. England
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[county|counties]]",
		bare_category_breadcrumb = "counties",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of countries!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "abbreviations of places",
	},
	["abbreviations of departments!"] = {
		-- For categorizing abbreviations of departments of e.g. France
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[department]]s",
		bare_category_breadcrumb = "departments",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of districts!"] = {
		-- For categorizing abbreviations of districts of e.g. ???
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[district]]s",
		bare_category_breadcrumb = "districts",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of divisions!"] = {
		-- For categorizing abbreviations of divisions of e.g. Bangladesh
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[division]]s",
		bare_category_breadcrumb = "divisions",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of former countries!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[country|countries]] that no longer [[exist]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "abbreviations of former places",
	},
	["abbreviations of former places!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[place]]s that no longer [[exist]]",
		bare_category_breadcrumb = "abbreviations",
		bare_category_parent = "former places",
		addl_bare_category_parents = {{name = "abbreviations of places", sort = "former"}},
	},
	["abbreviations of places!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "abbreviations",
		bare_category_parent = "places",
	},
	["abbreviations of political divisions!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[political]] [[division]]s",
		bare_category_breadcrumb = "political divisions",
		bare_category_parent = "abbreviations of places",
	},
	["abbreviations of prefectures!"] = {
		-- For categorizing abbreviations of prefectures of e.g. Japan
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[prefecture]]s",
		bare_category_breadcrumb = "prefectures",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of provinces!"] = {
		-- For categorizing abbreviations of provinces of e.g. Canada
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[province]]s",
		bare_category_breadcrumb = "provinces",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of provinces and territories!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[province]]s and [[territory|territories]]",
		bare_category_breadcrumb = "provinces and territories",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of regions!"] = {
		-- For categorizing abbreviations of regions of e.g. Italy
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[administrative region]]s",
		bare_category_breadcrumb = "regions",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of states!"] = {
		-- For categorizing abbreviations of states of e.g. the United States
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[state]]s",
		bare_category_breadcrumb = "states",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of states and territories!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[state]]s and [[territory|territories]]",
		bare_category_breadcrumb = "states and territories",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of states and union territories!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[state]]s and [[union territory|union territories]]",
		bare_category_breadcrumb = "states and union territories",
		bare_category_parent = "abbreviations of political divisions",
	},
	["abbreviations of territories!"] = {
		full_category_link = "{{glossary|abbreviation}}s of [[name]]s of [[territory|territories]]",
		bare_category_breadcrumb = "territories",
		bare_category_parent = "abbreviations of political divisions",
	},
	["ABBREVIATION_OF country"] = {
		link = false,
		default = {"Abbreviations of countries"},
	},
	["ABBREVIATION_OF county"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF department"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF district"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF division"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF FORMER country"] = {
		link = false,
		default = {"Abbreviations of former countries"},
	},
	["ABBREVIATION_OF FORMER place"] = {
		link = false,
		default = {"Abbreviations of former places"},
	},
	["ABBREVIATION_OF place"] = {
		link = false,
		default = {"Abbreviations of places"},
	},
	["ABBREVIATION_OF prefecture"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF province"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF region"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF state"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF subpolity"] = {
		link = false,
		default = {"Abbreviations of political divisions"},
	},
	["ABBREVIATION_OF territory"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},
	["ABBREVIATION_OF union territory"] = {
		link = false,
		fallback = "ABBREVIATION_OF subpolity",
	},

	---------- Archaic forms ----------

	["archaic forms of places!"] = {
		full_category_link = "{{glossary|archaic}} [[form]]s of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "archaic forms",
		bare_category_parent = "places",
	},
	["ARCHAIC_FORM_OF place"] = {
		link = false,
		default = {"Archaic forms of places"},
	},

	---------- Clippings ----------

	["clippings of places!"] = {
		full_category_link = "{{glossary|clipping}}s of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "clippings",
		bare_category_parent = "places",
	},
	["CLIPPING_OF place"] = {
		link = false,
		default = {"Clippings of places"},
	},

	---------- Dated forms ----------

	["dated forms of places!"] = {
		full_category_link = "{{glossary|dated}} [[form]]s of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "dated forms",
		bare_category_parent = "places",
	},
	["DATED_FORM_OF place"] = {
		link = false,
		default = {"Dated forms of places"},
	},

	---------- Derogatory names ----------

	["derogatory names for cities!"] = {
		full_category_link = "{{glossary|derogatory}} [[name]]s for [[city|cities]]",
		bare_category_breadcrumb = "cities",
		bare_category_parent = "derogatory names for places",
		addl_bare_category_parents = {"nicknames for cities"},
	},
	["derogatory names for continents!"] = {
		full_category_link = "{{glossary|derogatory}} [[name]]s for [[continent]]s",
		bare_category_breadcrumb = "continents",
		bare_category_parent = "derogatory names for places",
		addl_bare_category_parents = {"nicknames for continents"},
	},
	["derogatory names for countries!"] = {
		full_category_link = "{{glossary|derogatory}} [[name]]s for [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "derogatory names for places",
		addl_bare_category_parents = {"nicknames for countries"},
	},
	["derogatory names for places!"] = {
		full_category_link = "{{glossary|derogatory}} [[name]]s for [[place]]s",
		bare_category_breadcrumb = "derogatory names",
		bare_category_parent = "nicknames for places",
	},
	["derogatory names for states!"] = {
		full_category_link = "{{glossary|derogatory}} [[name]]s for [[state]]s",
		bare_category_breadcrumb = "states",
		bare_category_parent = "derogatory names for places",
		addl_bare_category_parents = {"nicknames for states"},
	},
	["DEROGATORY_NAME_FOR capital"] = {
		link = false,
		default = {"Derogatory names for cities"},
	},
	["DEROGATORY_NAME_FOR city"] = {
		link = false,
		default = {"Derogatory names for cities"},
	},
	["DEROGATORY_NAME_FOR continent"] = {
		link = false,
		default = {"Derogatory names for continents"},
	},
	["DEROGATORY_NAME_FOR country"] = {
		link = false,
		default = {"Derogatory names for countries"},
	},
	["DEROGATORY_NAME_FOR metropolitan city"] = {
		-- "metropolitan city" doesn't fall back to "city"
		link = false,
		default = {"Derogatory names for cities"},
	},
	["DEROGATORY_NAME_FOR place"] = {
		link = false,
		default = {"Derogatory names for places"},
	},
	["DEROGATORY_NAME_FOR prefecture-level city"] = {
		-- "prefecture-level city" doesn't fall back to "city" but things like "county-level city" and
		-- "subprovincial city" fall back to "prefecture-level city"
		link = false,
		default = {"Derogatory names for cities"},
	},
	["DEROGATORY_NAME_FOR state"] = {
		link = false,
		default = {"Derogatory names for states"},
	},
	["DEROGATORY_NAME_FOR town"] = {
		link = false,
		default = {"Derogatory names for cities"},
	},

	---------- Ellipses ----------

	["ellipses of places!"] = {
		full_category_link = "{{glossary|ellipsis|ellipses}} of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "ellipses",
		bare_category_parent = "places",
	},
	["ELLIPSIS_OF place"] = {
		link = false,
		default = {"Ellipses of places"},
	},

	---------- Former long-form names ----------

	["former long-form names of countries!"] = {
		full_category_link = "no-longer-[[use]]d [[long]]-[[form]] (but typically [[unofficial]]) [[name]]s of [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "former long-form names of places",
		addl_bare_category_parents = {{name = "former names of countries", sort = "long-form"}},
	},
	["former long-form names of places!"] = {
		full_category_link = "no-longer-[[use]]d [[long]]-[[form]] (but typically [[unofficial]]) [[name]]s of [[place]]s",
		bare_category_breadcrumb = "long-form",
		bare_category_parent = "former names of places",
	},
	["FORMER_LONG_FORM_OF country"] = {
		link = false,
		default = {"Former long-form names of countries"},
	},
	["FORMER_LONG_FORM_OF place"] = {
		link = false,
		default = {"Former long-form names of places"},
	},

	---------- Former names ----------

	["former names of capitals!"] = {
		full_category_link = "[[former]] [[name]]s of [[capital city|capital cities]] that generally still exist but under a different name",
		bare_category_breadcrumb = "capitals",
		bare_category_parent = "former names of settlements",
	},
	["former names of countries!"] = {
		full_category_link = "[[former]] [[name]]s of [[country|countries]] that generally still exist but under a different name",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "former names of places",
	},
	["former names of places!"] = {
		full_category_link = "[[former]] [[name]]s of [[place]]s that generally still exist but under a different name",
		bare_category_breadcrumb = "former names",
		bare_category_parent = "places",
	},
	["former names of political divisions!"] = {
		full_category_link = "[[former]] [[name]]s of [[political]] [[division]]s (states, provinces, counties, etc.) that generally still exist but under a different name",
		bare_category_breadcrumb = "political divisions",
		bare_category_parent = "former names of places",
	},
	["former names of polities!"] = {
		full_category_link = "[[former]] [[name]]s of [[polity|polities]] (e.g. [[country|countries]]) that generally still exist but under a different name",
		bare_category_breadcrumb = "polities",
		bare_category_parent = "former names of places",
	},
	["former names of settlements!"] = {
		full_category_link = "[[former]] [[name]]s of [[city|cities]], [[town]]s, [[village]]s, etc. that generally still exist but under a different name",
		bare_category_breadcrumb = "settlements",
		bare_category_parent = "former names of political divisions",
	},
	["FORMER_NAME_OF capital"] = {
		link = false,
		default = {"Former names of capitals"},
	},
	["FORMER_NAME_OF country"] = {
		link = false,
		default = {"Former names of countries"},
	},
	["FORMER_NAME_OF place"] = {
		link = false,
		default = {"Former names of places"},
	},
	["FORMER_NAME_OF polity"] = {
		link = false,
		default = {"Former names of polities"},
	},
	["FORMER_NAME_OF region"] = {
		link = false,
		fallback = "FORMER_NAME_OF subpolity",
	},
	["FORMER_NAME_OF settlement"] = {
		link = false,
		default = {"Former names of settlements"},
	},
	["FORMER_NAME_OF subpolity"] = {
		link = false,
		default = {"Former names of political divisions"},
	},

	---------- Former nicknames ----------

	["former nicknames for cities!"] = {
		full_category_link = "no-longer-used [[nickname]]s for [[city|cities]], e.g. the [[Eternal City]] for [[Kyoto]] during the {{w|Heian period}} ({{circa2|800–1100|short=yes}} {{AD}})",
		bare_category_breadcrumb = "cities",
		bare_category_parent = "former nicknames for places",
		addl_bare_category_parents = {"nicknames for cities"},
	},
	["former nicknames for places!"] = {
		full_category_link = "no-longer-used [[nickname]]s for [[place]]s",
		bare_category_breadcrumb = "former",
		bare_category_parent = "nicknames for places",
		addl_bare_category_parents = {{name = "former names of places", sort = "nicknames"}},
	},
	["FORMER_NICKNAME_FOR capital"] = {
		link = false,
		default = {"Former nicknames for cities"},
	},
	["FORMER_NICKNAME_FOR city"] = {
		link = false,
		default = {"Former nicknames for cities"},
	},
	["FORMER_NICKNAME_FOR metropolitan city"] = {
		-- "metropolitan city" doesn't fall back to "city"
		link = false,
		default = {"Former nicknames for cities"},
	},
	["FORMER_NICKNAME_FOR place"] = {
		link = false,
		default = {"Former nicknames for places"},
	},
	["FORMER_NICKNAME_FOR prefecture-level city"] = {
		-- "prefecture-level city" doesn't fall back to "city" but things like "county-level city" and
		-- "subprovincial city" fall back to "prefecture-level city"
		link = false,
		default = {"Former nicknames for cities"},
	},
	["FORMER_NICKNAME_FOR town"] = {
		link = false,
		default = {"Former nicknames for cities"},
	},

	---------- Former official names ----------

	["former official names of countries!"] = {
		full_category_link = "no-longer-[[use]]d [[official]] [[name]]s of [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "former official names of places",
		addl_bare_category_parents = {{name = "former names of countries", sort = "official"}},
	},
	["former official names of places!"] = {
		full_category_link = "no-longer-[[use]]d [[official]] [[name]]s of [[place]]s",
		bare_category_breadcrumb = "official",
		bare_category_parent = "former names of places",
	},
	["FORMER_OFFICIAL_NAME_OF country"] = {
		link = false,
		default = {"Former official names of countries"},
	},
	["FORMER_OFFICIAL_NAME_OF place"] = {
		link = false,
		default = {"Former official names of places"},
	},

	---------- Long-form names ----------

	["long-form names of countries!"] = {
		full_category_link = "[[long]]-[[form]] (but typically [[unofficial]]) [[name]]s of [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "long-form names of places",
	},
	["long-form names of places!"] = {
		full_category_link = "[[long]]-[[form]] (but typically [[unofficial]]) [[name]]s of [[place]]s",
		bare_category_breadcrumb = "long-form names",
		bare_category_parent = "places",
	},
	["LONG_FORM_OF country"] = {
		link = false,
		default = {"Long-form names of countries"},
	},
	["LONG_FORM_OF place"] = {
		link = false,
		default = {"Long-form names of places"},
	},

	---------- Nicknames ----------

	["nicknames for cities!"] = {
		full_category_link = "[[nickname]]s for [[city|cities]], e.g. the [[Big Apple]] for [[New York City]]",
		bare_category_breadcrumb = "cities",
		bare_category_parent = "nicknames for places",
		addl_bare_category_parents = {"cities"},
	},
	["nicknames for continents!"] = {
		full_category_link = "[[nickname]]s for [[continent]]s",
		bare_category_breadcrumb = "continents",
		bare_category_parent = "nicknames for places",
		addl_bare_category_parents = {"continents"},
	},
	["nicknames for countries!"] = {
		full_category_link = "[[nickname]]s for [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "nicknames for places",
		addl_bare_category_parents = {"countries"},
	},
	["nicknames for places!"] = {
		full_category_link = "[[nickname]]s for [[place]]s",
		bare_category_breadcrumb = "places",
		bare_category_parent = "nicknames",
		addl_bare_category_parents = {"places"},
	},
	["nicknames for states!"] = {
		-- For categorizing nicknames for states of e.g. the United States
		full_category_link = "[[nicknames]] for [[state]]s",
		bare_category_breadcrumb = "states",
		bare_category_parent = "nicknames for places",
		addl_bare_category_parents = {"states"},
	},
	["NICKNAME_FOR capital"] = {
		link = false,
		default = {"Nicknames for cities"},
	},
	["NICKNAME_FOR city"] = {
		link = false,
		default = {"Nicknames for cities"},
	},
	["NICKNAME_FOR continent"] = {
		link = false,
		default = {"Nicknames for continents"},
	},
	["NICKNAME_FOR country"] = {
		link = false,
		default = {"Nicknames for countries"},
	},
	["NICKNAME_FOR metropolitan city"] = {
		-- "metropolitan city" doesn't fall back to "city"
		link = false,
		default = {"Nicknames for cities"},
	},
	["NICKNAME_FOR place"] = {
		link = false,
		default = {"Nicknames for places"},
	},
	["NICKNAME_FOR prefecture-level city"] = {
		-- "prefecture-level city" doesn't fall back to "city" but things like "county-level city" and
		-- "subprovincial city" fall back to "prefecture-level city"
		link = false,
		default = {"Nicknames for cities"},
	},
	["NICKNAME_FOR state"] = {
		link = false,
		default = {"Nicknames for states"},
	},
	["NICKNAME_FOR town"] = {
		link = false,
		default = {"Nicknames for cities"},
	},

	---------- Obsolete forms ----------

	["obsolete forms of places!"] = {
		full_category_link = "{{glossary|obsolete}} [[form]]s of [[name]]s of [[place]]s",
		bare_category_breadcrumb = "obsolete forms",
		bare_category_parent = "places",
	},
	["OBSOLETE_FORM_OF place"] = {
		link = false,
		default = {"Obsolete forms of places"},
	},

	---------- Official names ----------

	["official names of countries!"] = {
		full_category_link = "[[official]] [[name]]s of [[country|countries]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "official names of places",
	},
	["official names of former countries!"] = {
		full_category_link = "[[official]] [[name]]s of [[country|countries]] that no longer [[exist]]",
		bare_category_breadcrumb = "countries",
		bare_category_parent = "official names of former places",
	},
	["official names of former places!"] = {
		full_category_link = "[[official]] [[name]]s of [[place]]s that no longer [[exist]]",
		bare_category_breadcrumb = "official names",
		bare_category_parent = "former places",
		addl_bare_category_parents = {{name = "official names of places", sort = "former"}},
	},
	["official names of places!"] = {
		full_category_link = "[[official]] [[name]]s of [[place]]s",
		bare_category_breadcrumb = "official names",
		bare_category_parent = "places",
	},
	["OFFICIAL_NAME_OF country"] = {
		link = false,
		default = {"Official names of countries"},
	},
	["OFFICIAL_NAME_OF FORMER country"] = {
		link = false,
		default = {"Official names of former countries"},
	},
	["OFFICIAL_NAME_OF FORMER place"] = {
		link = false,
		default = {"Official names of former places"},
	},
	["OFFICIAL_NAME_OF place"] = {
		link = false,
		default = {"Official names of places"},
	},

	---------- Official nicknames ----------

	["official nicknames for places!"] = {
		full_category_link = "[[official]] [[nickname]]s for [[place]]s",
		bare_category_breadcrumb = "official",
		bare_category_parent = "nicknames for places",
	},
	["official nicknames for states!"] = {
		-- For categorizing official nicknames for states of e.g. the United States
		full_category_link = "[[official]] [[nicknames]] for [[state]]s",
		bare_category_breadcrumb = "official",
		bare_category_parent = "nicknames for states",
		addl_bare_category_parents = {"states"},
	},
	["OFFICIAL_NICKNAME_FOR place"] = {
		link = false,
		default = {"Official nicknames for places"},
	},
	["OFFICIAL_NICKNAME_FOR state"] = {
		link = false,
		default = {"Official nicknames for states"},
	},
}

export.plural_placetype_to_singular = {}
for sg_placetype, spec in pairs(export.placetype_data) do
	if spec.plural then
		export.plural_placetype_to_singular[spec.plural] = sg_placetype
	end
end

return export