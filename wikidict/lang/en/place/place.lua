local export = {}

local m_placetypes = require("Module:place/placetypes")
local m_links = require("Module:links")
local memoize = require("Module:memoize")
local m_strutils = require("Module:string utilities")
local m_table = require("Module:table")

local en_utilities_module = "Module:en-utilities"
local form_of_module = "Module:form of"
local languages_module = "Module:languages"
local parse_interface_module = "Module:parse interface"
local parse_utilities_module = "Module:parse utilities"
local parameter_utilities_module = "Module:parameter utilities"
local utilities_module = "Module:utilities"

local enlang = require(languages_module).getByCode("en")

local rmatch = m_strutils.match
local rfind = m_strutils.find
local ulen = m_strutils.len
local split = m_strutils.split
local dump = mw.dumpObject
local insert = table.insert
local concat = table.concat
local pluralize = require(en_utilities_module).pluralize
local extend = m_table.extend
local unpack = unpack or table.unpack -- Lua 5.2 compatibility

local placetype_data = m_placetypes.placetype_data

export.all_form_of_directives = {
	["former name of"] = {text = "+", type_prefix = "FORMER_NAME_OF"},
	["fmr of"] = {alias_of = "former name of"},
	["ancient name of"] = {text = "+", type_prefix = "FORMER_NAME_OF"},
	["official name of"] = {text = "+", type_prefix = "OFFICIAL_NAME_OF"},
	["former official name of"] = {text = "+", type_prefix = "FORMER_OFFICIAL_NAME_OF"},
	["long form of"] = {text = "+", type_prefix = "LONG_FORM_OF"},
	["former long form of"] = {text = "+", type_prefix = "FORMER_LONG_FORM_OF"},
	["nickname for"] = {text = "+", type_prefix = "NICKNAME_FOR"},
	["official nickname for"] = {text = "+", type_prefix = "OFFICIAL_NICKNAME_FOR"},
	["former nickname for"] = {text = "+", type_prefix = "FORMER_NICKNAME_FOR"},
	["derogatory name for"] = {text = "[[Appendix:Glossary#derogatory|derogatory]] name for", type_prefix = "DEROGATORY_NAME_FOR"},
	["synonym of"] = {text = "+"},
	["syn of"] = {alias_of = "synonym of"},
	["abbreviation of"] = {text = "[[Appendix:Glossary#abbreviation|abbreviation]] of", type_prefix = "ABBREVIATION_OF",
		default_foreign = true},
	["abbr of"] = {alias_of = "abbreviation of"},
	["abbrev of"] = {alias_of = "abbreviation of"},
	["initialism of"] = {text = "[[Appendix:Glossary#initialism|initialism]] of", type_prefix = "ABBREVIATION_OF",
		default_foreign = true},
	["init of"] = {alias_of = "initialism of"},
	["acronym of"] = {text = "[[Appendix:Glossary#acronym|acronym]] of", type_prefix = "ABBREVIATION_OF",
		default_foreign = true},
	["syllabic abbreviation of"] = {text = "[[Appendix:Glossary#syllabic abbreviation|syllabic abbreviation]] of", type_prefix = "ABBREVIATION_OF",
		default_foreign = true},
	["sylabbr of"] = {alias_of = "syllabic abbreviation of"},
	["sylabbrev of"] = {alias_of = "syllabic abbreviation of"},
	["ellipsis of"] = {text = "[[Appendix:Glossary#ellipsis|ellipsis]] of", type_prefix = "ELLIPSIS_OF",
		default_foreign = true},
	["ellip of"] = {alias_of = "ellipsis of"},
	["clipping of"] = {text = "[[Appendix:Glossary#clipping|clipping]] of", type_prefix = "CLIPPING_OF",
		default_foreign = true},
	["clip of"] = {alias_of = "clipping of"},
	["alternative form of"] = {text = "+", default_foreign = true},
	["alt form"] = {alias_of = "alternative form of"},
	["alternative spelling of"] = {text = "+", default_foreign = true},
	["alt spell"] = {alias_of = "alternative spelling of"},
	["alt sp"] = {alias_of = "alternative spelling of"},
	["dated form of"] = {text = "[[Appendix:Glossary#dated|dated]] form of", type_prefix = "DATED_FORM_OF",
		default_foreign = true},
	["dated form"] = {alias_of = "dated form of"},
	["dated spelling of"] = {text = "[[Appendix:Glossary#dated|dated]] spelling of", type_prefix = "DATED_FORM_OF",
		default_foreign = true},
	["dated spell"] = {alias_of = "dated spelling of"},
	["dated sp"] = {alias_of = "dated spelling of"},
	["archaic form of"] = {text = "[[Appendix:Glossary#archaic|archaic]] form of", type_prefix = "ARCHAIC_FORM_OF",
		default_foreign = true},
	["arch form"] = {alias_of = "archaic form of"},
	["archaic spelling of"] = {text = "[[Appendix:Glossary#archaic|archaic]] spelling of", type_prefix = "ARCHAIC_FORM_OF",
		default_foreign = true},
	["arch spell"] = {alias_of = "archaic spelling of"},
	["arch sp"] = {alias_of = "archaic spelling of"},
	["obsolete form of"] = {text = "[[Appendix:Glossary#obsolete|obsolete]] form of", type_prefix = "OBSOLETE_FORM_OF",
		default_foreign = true},
	["obs form"] = {alias_of = "obsolete form of"},
	["obsolete spelling of"] = {text = "[[Appendix:Glossary#obsolete|obsolete]] spelling of", type_prefix = "OBSOLETE_FORM_OF",
		default_foreign = true},
	["obs spell"] = {alias_of = "obsolete spelling of"},
	["obs sp"] = {alias_of = "obsolete spelling of"},
}

local function get_seat_text(overall_place_spec)
	local placetype = overall_place_spec.descs[1].placetypes[1]
	if placetype == "county" or placetype == "counties" then
		return "county seat"
	elseif placetype == "parish" or placetype == "parishes" then
		return "parish seat"
	elseif placetype == "borough" or placetype == "boroughs" then
		return "borough seat"
	else
		return "seat"
	end
end

export.extra_info_args = {
	{arg = "modern", text = "+", conjunction = "or", display_even_when_dropped = true},
	{arg = "now", text = "now,", conjunction = "or", display_even_when_dropped = true},
	{arg = "full", text = "in full,", conjunction = "or", display_even_when_dropped = true},
	{arg = "short", text = "short form", conjunction = "or"},
	{arg = "abbr", text = "abbreviation", conjunction = "or"},
	{arg = "former", text = "formerly,"},
	{arg = "official", text = "official name", match_sentence_style = true, auto_plural = true, with_colon = true},
	{arg = "capital", text = "+", match_sentence_style = true, auto_plural = true, with_colon = true},
	{arg = "largest city", text = "+", match_sentence_style = true, auto_plural = true, with_colon = true},
	{arg = "caplc", text = "capital and largest city", match_sentence_style = true, auto_plural = false,
		with_colon = true},
	{arg = "seat", text = get_seat_text, match_sentence_style = true, auto_plural = true, with_colon = true},
	{arg = "shire town", text = "+", match_sentence_style = true, auto_plural = true, with_colon = true},
	{arg = "headquarters", text = "+", match_sentence_style = true, auto_plural = false, with_colon = true},
	{arg = "center", text = "administrative center", match_sentence_style = true, auto_plural = false, with_colon = true},
	{arg = "centre", text = "administrative centre", match_sentence_style = true, auto_plural = false, with_colon = true},
}

export.extra_info_arg_map = {}

for _, spec in ipairs(export.extra_info_args) do
	export.extra_info_arg_map[spec.arg] = spec
end

local function link(text, langcode, id)
	if not langcode then
		return text
	end

	return m_links.full_link(
		{term = text, lang = require(languages_module).getByCode(langcode, true, "allow etym"), id = id},
		nil, "allow self link"
	)
end


local function ucfirst_all(text)
	if text:find(" ") then
		local parts = split(text, " ", true)
		for i, part in ipairs(parts) do
			parts[i] = m_strutils.ucfirst(part)
		end
		return concat(parts, " ")
	else
		return m_strutils.ucfirst(text)
	end
end


local function lc(text)
	return mw.getContentLanguage():lc(text)
end

local function split_on_comma(val)
	if val:find(",") then
		return require(parse_interface_module).split_on_comma(val)
	else
		return {val}
	end
end


local function split_on_slash(arg)
	if arg:find("<") then
		local m_parse_utilities = require(parse_utilities_module)
		-- We implement this by parsing balanced segment runs involving <...>, and splitting on slash in the remainder.
		-- The result is a list of lists, so we have to rejoin the inner lists by concatenating.
		local segments = m_parse_utilities.parse_balanced_segment_run(arg, "<", ">")
		local slash_separated_groups = m_parse_utilities.split_alternating_runs(segments, "/")
		for i, group in ipairs(slash_separated_groups) do
			slash_separated_groups[i] = concat(group)
		end
		return slash_separated_groups
	else
		return split(arg, "/", true)
	end
end


local function split_holonym(raw)
	local no_display, combined_holonym = raw:match("^(!)(.*)$")
	no_display = not not no_display
	combined_holonym = combined_holonym or raw
	local suppress_comma, combined_holonym_without_comma = combined_holonym:match("^(%*)(.*)$")
	suppress_comma = not not suppress_comma
	combined_holonym = combined_holonym_without_comma or combined_holonym
	local holonym_parts = split_on_slash(combined_holonym)
	if #holonym_parts == 1 then
		-- `unlinked_placename` should not be used.
		return {{display_placename = combined_holonym, no_display = no_display, suppress_comma = suppress_comma}}
	end

	-- Rejoin further slashes in case of slash in holonym placename, e.g. Admaston/Bromley.
	local placetype = holonym_parts[1]
	local placename = concat(holonym_parts, "/", 2)

	-- Check for modifiers after the holonym placetype.
	local split_holonym_placetype = split(placetype, ":", true)
	placetype = split_holonym_placetype[1]
	local affix_type
	local saw_also
	local saw_the
	for i = 2, #split_holonym_placetype do
		local modifier = split_holonym_placetype[i]
		if modifier == "also" then
			saw_also = true
		elseif modifier == "the" then
			saw_the = true
		elseif modifier == "pref" or modifier == "Pref" or modifier == "suf" or modifier == "Suf" or
			modifier == "noaff" then
			affix_type = modifier
		end
	end

	placetype = m_placetypes.resolve_placetype_aliases(placetype)
	local holonyms = split_on_comma(placename)
	local pluralize_affix = #holonyms > 1
	local affix_holonym_index = (affix_type == "pref" or affix_type == "Pref") and 1 or affix_type == "noaff" and 0 or
		#holonyms
	for i, placename in ipairs(holonyms) do
		-- Check for langcode before the holonym placename, but don't get tripped up by Wikipedia links, which begin
		-- "[[w:...]]" or "[[wikipedia:]]".
		local langcode, placename_without_langcode = rmatch(placename, "^([^%[%]]-):(.*)$")
		if langcode then
			placename = placename_without_langcode
		end
		placename = m_placetypes.resolve_placename_display_aliases(placetype, placename)
		holonyms[i] = {
			placetype = placetype,
			display_placename = placename,
			unlinked_placename = m_placetypes.remove_links_and_html(placename),
			langcode = langcode,
			affix_type = i == affix_holonym_index and affix_type or nil,
			pluralize_affix = i == affix_holonym_index and pluralize_affix,
			suppress_affix = i ~= affix_holonym_index,
			no_display = no_display,
			suppress_comma = suppress_comma,
			force_the = i == 1 and saw_the,
		}
	end

	return holonyms
end


local get_param_mods = memoize(function()
	local m_param_utils = require(parameter_utilities_module)
	return m_param_utils.construct_param_mods {
		{group = {"link", "q", "l", "ref"}},
		{param = "eq"},
		-- FIXME: Finish [[Module:format utilities]].
		--{param = "conj", set = require(format_utilities_module).allowed_conjs_for_join_segments, overall = true},
		{param = "conj", set = {["and"] = true, ["or"] = true, ["and/or"] = true}, overall = true},
	}
end)

local function parse_term_with_inline_modifiers(term, paramname, default_lang)
	-- FIXME: Finish changes to [[Module:parameter utilities]] and [[Module:parse utilities]] that support continuations
	-- and new-format generate_obj().
	--local function generate_obj(data)
	--	local m_param_utils = require(parameter_utilities_module)
	--	data.parse_lang_prefix = true
	--	data.special_continuations = m_param_utils.default_special_continuations
	--	data.default_lang = default_lang
	--	return m_param_utils.generate_obj_maybe_parsing_lang_prefix(data)
	--end
	local function generate_obj(raw_term, parse_err)
		local obj = require(parameter_utilities_module).generate_obj_maybe_parsing_lang_prefix {
			term = raw_term,
			parse_err = parse_err,
			parse_lang_prefix = true,
		}
		obj.lang = obj.lang or default_lang
		return obj
	end
	return require(parse_interface_module).parse_inline_modifiers(term, {
		paramname = paramname,
		param_mods = get_param_mods(),
		generate_obj = generate_obj,
		-- FIXME: See above.
		--generate_obj_new_format = true,
		splitchar = ",",
		outer_container = {},
	})
end


local function parse_form_of_directive(arg, lang, form_of_overridden_args)
	local form_of_directive, raw_terms = arg:match("^@([a-z -]+):(.*)$")
	if not export.all_form_of_directives[form_of_directive] then
		local known_directives = {}
		for k, _ in pairs(export.all_form_of_directives) do
			insert(known_directives, '"' .. k .. '"')
		end
	end
	local spec = export.all_form_of_directives[form_of_directive]
	local canonical_directive = form_of_directive
	local default_foreign = spec.default_foreign
	local directive_param = "@" .. form_of_directive
	if form_of_overridden_args and form_of_overridden_args[canonical_directive] then
		raw_terms = form_of_overridden_args[canonical_directive].new_value
		local new_directive = form_of_overridden_args[canonical_directive].new_directive
		local new_spec = export.all_form_of_directives[new_directive]
		if new_directive ~= canonical_directive then
			directive_param = directive_param .. (" (replaced with @%s)"):format(new_directive)
			canonical_directive = new_directive
			spec = new_spec
		end
		default_foreign = true
	end
	local terms = parse_term_with_inline_modifiers(raw_terms, directive_param,
		default_foreign and lang or enlang)
	return {
		directive = canonical_directive,
		terms = terms.terms,
		conj = terms.conj,
		spec = spec,
	}
end


local function parse_extra_info_arg(args, spec, default_lang)
	if not args then
		return nil
	end
	if type(args) ~= "table" then
		args = {args}
	end
	if not args[1] then
		return nil
	end

	local terms = nil

	local conj
	for i, arg in ipairs(args) do
		local this_terms = parse_term_with_inline_modifiers(arg, spec.arg .. (i == 1 and "" or i), default_lang)
		local thisconj = this_terms.conj
		if not conj then
			conj = thisconj
		end
		if not terms then
			terms = this_terms.terms
		else
			m_table.extend(terms, this_terms.terms)
		end
	end

	return {
		spec = spec,
		terms = terms,
		conj = conj,
	}
end


function export.parse_new_style_place_desc(text, lang, form_of_directives, form_of_overridden_args)
	local placetypes = {}
	local segments = split(text, "<<(.-)>>")
	local retval = {holonyms = {}, order = {}}
	local form_of_directives_already_present = form_of_directives and not not form_of_directives[1]
	for i, segment in ipairs(segments) do
		if i % 2 == 1 then
			insert(retval.order, {type = "raw", value = segment})
		elseif segment:find("@") then
            local form_of_directive = parse_form_of_directive(segment, lang, form_of_overridden_args)
            form_of_directive.pretext = retval.order[1].value
            retval.order[1] = nil
            insert(form_of_directives, form_of_directive)
		elseif segment:find("/") then
			local holonyms = split_holonym(segment)
			for j, holonym in ipairs(holonyms) do
				if j > 1 then
					if not holonym.no_display then
						if j == #holonyms then
							insert(retval.order, {type = "raw", value = " and "})
						else
							insert(retval.order, {type = "raw", value = ", "})
						end
					end
					-- All but the first in a multi-holonym need an article. For the first one, the article is
					-- specified in the raw text if needed. (Currently, needs_article is only used when displaying the
					-- holonym, so it wouldn't matter when no_display is set, but we set it anyway in case we need it
					-- for something else.)
					holonym.needs_article = true
				end
				insert(retval.holonyms, holonym)
				if not holonym.no_display then
					insert(retval.order, {type = "holonym", value = #retval.holonyms})
				end
				m_placetypes.key_holonym_into_place_desc(retval, holonym)
			end
		else
			local treat_as, display = segment:match("^(..-):(.+)$")
			if treat_as then
				segment = treat_as
			else
				display = segment
			end
			-- see if the placetype segment is just qualifiers
			local only_qualifiers = true
			local split_segments = split(segment, " ", true)
			for _, split_segment in ipairs(split_segments) do
				if m_placetypes.placetype_qualifiers[split_segment] == nil then
					only_qualifiers = false
					break
				end
			end
			insert(placetypes, {placetype = segment, only_qualifiers = only_qualifiers})
			if only_qualifiers then
				insert(retval.order, {type = "qualifier", value = display})
			else
				insert(retval.order, {type = "placetype", value = display})
			end
		end
	end

	if not form_of_directives_already_present and form_of_directives and form_of_directives[1] then
		form_of_directives[#form_of_directives].posttext = ""
	end

	local final_placetypes = {}
	for i, placetype in ipairs(placetypes) do
		if i > 1 and placetypes[i - 1].only_qualifiers then
			final_placetypes[#final_placetypes] = final_placetypes[#final_placetypes] .. " " .. placetypes[i].placetype
		else
			insert(final_placetypes, placetypes[i].placetype)
		end
	end
	retval.placetypes = final_placetypes
	return retval
end


local function parse_conjoined_new_style_place_desc(text, lang, form_of_directives, form_of_overridden_args)
	local separate_specs = split(text, ";(;[^ ]*)")
	local descs = {}
	for i = 1, #separate_specs do
		if i % 2 == 1 then
			insert(descs, export.parse_new_style_place_desc(separate_specs[i], lang, form_of_directives,
				form_of_overridden_args))
			form_of_directives = nil
		else
			descs[#descs].separator = separate_specs[i]
		end
	end
	return descs
end


local function parse_overall_place_spec(data)
	local args, from_tcl, extra_info_overridden_set, form_of_overridden_args =
		data.args, data.from_tcl, data.extra_info_overridden_set, data.form_of_overridden_args
	local descs = {}
	local this_desc
	-- Index of separate (semicolon-separated) place descriptions within `descs`.
	local desc_index = 1
	-- Index of separate holonyms within a place description. 0 means we've seen no holonyms and have yet to process
	-- the placetypes that precede the holonyms. 1 means we've seen no holonyms but have already processed the
	-- placetypes.
	local holonym_index = 0
	local in_place_desc = false

	local form_of_directives = {}

	local function set_desc_joiner(desc, separator)
		if separator == ";" then
			this_desc.joiner = "; "
			this_desc.include_following_article = true
		elseif separator == ";;" then
			this_desc.joiner = " "
		else
			local joiner = separator:sub(2)
			if rfind(joiner, "^%a") then
				this_desc.joiner = " " .. joiner .. " "
			else
				this_desc.joiner = joiner .. " "
			end
		end
	end

	for _, arg in ipairs(args[2]) do
		if arg:find("^@") then
			local form_of_directive = parse_form_of_directive(arg, args[1], form_of_overridden_args)
			if form_of_directives[1] then
				form_of_directive.pretext = ", "
			else
				form_of_directive.pretext = ""
			end
			insert(form_of_directives, form_of_directive)
		elseif arg == ";" or arg:find("^;[^ ]") then
			set_desc_joiner(this_desc, arg)
			desc_index = desc_index + 1
			holonym_index = 0
			in_place_desc = false
		else
			if arg:find("<<") then
				in_place_desc = true
				local this_descs = parse_conjoined_new_style_place_desc(arg, args[1], form_of_directives,
					form_of_overridden_args)
				for j, desc in ipairs(this_descs) do
					this_desc = desc
					if holonym_index > 0 then
						desc_index = desc_index + 1
						holonym_index = 0
					end
					if j < #this_descs then
						set_desc_joiner(this_desc, this_desc.separator)
					end
					descs[desc_index] = this_desc
					last_was_new_style = true
					holonym_index = #this_desc.holonyms + 1
				end
			else
				-- Old-style arguments can directly follow a new-style argument; they become additional holonyms
				-- tacked onto the end of the holonym list, and are displayed old-style except that there is no
				-- prefix before the first one following the new-style argument.
				in_place_desc = true
				if holonym_index == 0 then
					local entry_placetypes = split_on_slash(arg)
					this_desc = {placetypes = entry_placetypes, holonyms = {}}
					descs[desc_index] = this_desc
					holonym_index = holonym_index + 1
				else
					local holonyms = split_holonym(arg)
					for j, holonym in ipairs(holonyms) do
						if j > 1 then
							-- All but the first in a multi-holonym need an article. Not for the first one because e.g.
							-- {{place|en|city|s/Arizona|c/United States}} should not display as "a city in Arizona, the
							-- United States". The overall first holonym in the place description gets an article if 
							-- needed regardless of our setting here.
							holonym.needs_article = true
							-- Insert "and" before the last holonym.
							if j == #holonyms then
								this_desc.holonyms[holonym_index] = {
									-- Use the no_display value from the first holonym; it should be the same for all
									-- holonyms. `unlinked_placename` should not be used.
									display_placename = "and", no_display = holonyms[1].no_display
								}
								holonym_index = holonym_index + 1
							end
						end
						this_desc.holonyms[holonym_index] = holonym
						m_placetypes.key_holonym_into_place_desc(this_desc, this_desc.holonyms[holonym_index])
						holonym_index = holonym_index + 1
					end
				end
			end
		end
	end

	if form_of_directives[1] and not form_of_directives[#form_of_directives].posttext then
		form_of_directives[#form_of_directives].posttext =
			(args.def and args.def ~= "-" or not args.def and descs[1]) and ": " or ""
	end

	local extra_info = {}
	for _, extra_info_spec in ipairs(export.extra_info_args) do
		local extra_info_terms = parse_extra_info_arg(args[extra_info_spec.arg], extra_info_spec,
			-- If called from {{tcl}} and extra info argument was set by {{tcl}}, interpret the argument
			-- according to the language in 1=; otherwise interpret as English. To override this, prefix
			-- with the appropriate language.
			from_tcl and extra_info_overridden_set and extra_info_overridden_set[extra_info_spec.arg] and args[1] or
				enlang)
		if extra_info_terms then
			insert(extra_info, extra_info_terms)
		end
	end

	return {
		lang = args[1],
		args = args,
		directives = form_of_directives,
		descs = descs,
		extra_info = extra_info,
	}
end

local function get_translations(transl, ids)
	local ret = {}

	for i, t in ipairs(transl) do
		local arg_transls = split_on_comma(t)
		local arg_ids = ids[i]
		if arg_ids then
			arg_ids = split_on_comma(arg_ids)
		end
		for j, arg_transl in ipairs(arg_transls) do
			insert(ret, link(arg_transl, "en", arg_ids and arg_ids[j] or nil))
		end
	end

	return concat(ret, ", ")
end

local function get_placename_article(decorated_placename, placetypes, placename, suppress_holonym_use_the_check)
	local unlinked_decorated_placename = m_placetypes.remove_links_and_html(decorated_placename)
	if unlinked_decorated_placename:find("^the ") then
		return nil
	end
	placename = placename or unlinked_decorated_placename
	if type(placetypes) == "string" then
		placetypes = {placetypes}
	end
	for _, placetype in ipairs(placetypes) do
		local art = m_placetypes.get_equiv_placetype_prop(placetype, function(pt)
			local art = m_placetypes.placename_article[pt] and m_placetypes.placename_article[pt][placename]
			if art then
				return art
			end
		end)
		if art then
			return art
		end
	end
	-- Get equivalent placetypes of the specified placetype so that e.g.
	-- {{place|en|@official name of:Bahamas|island country|r/Caribbean}} put 'the' before Bahamas ("Bahamas" is just
	-- specified as a country but "island country" falls back to "country").
	local all_equiv_placetypes = {}
	for _, placetype in ipairs(placetypes) do
		local this_equiv_placetypes = m_placetypes.get_placetype_equivs(placetype)
		for _, this_equiv_placetype in ipairs(this_equiv_placetypes) do
			insert(all_equiv_placetypes, this_equiv_placetype.placetype)
		end
	end
	-- Look for a known location. We should be using find_matching_holonym_location() but that function doesn't
	-- currently work without alias resolution. Instead we check if any matching location has `the = true` set.
	-- In practice there aren't any cases where a given placename matches two locations, only one of which has
	-- `the = true` set.
	for group, key, spec in m_placetypes.iterate_matching_location {
		placetypes = all_equiv_placetypes,
		placename = placename,
		alias_resolution = "none",
	} do
		-- `iterate_holonym_location` doesn't initialize the spec if alias resolution is turned off, so check both
		-- the spec and group. Be careful in case `the = false` is explicitly given by the spec.
		if spec.the ~= nil then
			if spec.the then
				return "the"
			end
		elseif group.default_the then
			return "the"
		end
	end
	if not suppress_holonym_use_the_check then
		-- See if the placetype requests an article to be placed before the placename. This occurs e.g. with 'sea'. But
		-- if the user specifies e.g. "sea:pref/Cortez", we'll wrongly get "the sea of the Cortez", so in that case we
		-- need to ignore the holonym article specified along with the placetype.
		for _, placetype in ipairs(placetypes) do
			local holonym_use_the = m_placetypes.get_equiv_placetype_prop(placetype,
				function(pt) return placetype_data[pt] and placetype_data[pt].holonym_use_the end)
			if holonym_use_the then
				return "the"
			end
		end
	end
	local universal_res = m_placetypes.placename_the_re["*"]
	for _, re in ipairs(universal_res) do
		if unlinked_decorated_placename:find(re) then
			return "the"
		end
	end
	for _, placetype in ipairs(placetypes) do
		local matched = m_placetypes.get_equiv_placetype_prop(placetype, function(pt)
			local res = m_placetypes.placename_the_re[pt]
			if not res then
				return nil
			end
			for _, re in ipairs(res) do
				if unlinked_decorated_placename:find(re) then
					return true
				end
			end
			return nil
		end)
		if matched then
			return "the"
		end
	end
	return nil
end


local function get_holonym_article(decorated_placename, place_desc, holonym_index)
	local holonym = place_desc.holonyms[holonym_index]
	local holonym_placetype = holonym.placetype
	if not holonym_placetype then
		return nil
	end
	return get_placename_article(decorated_placename, holonym_placetype, holonym.unlinked_placename,
		not not holonym.affix_type)
end


local function format_holonym(place_desc, holonym_index, needs_article)
	local holonym = place_desc.holonyms[holonym_index]
	if holonym.no_display then
		return ""
	end

	local orig_needs_article = needs_article
	needs_article = needs_article or holonym.needs_article or holonym.force_the

	local output = holonym.display_placename
	local placetype = holonym.placetype
	local affix_type_pt_data, affix_type, affix_is_prefix, affix, prefix, suffix, no_affix_strings
	local pt_equiv_for_affix_type, already_seen_affix, need_affix

	-- Implement display handlers.
	local display_handler = m_placetypes.get_equiv_placetype_prop(placetype,
		function(pt) return placetype_data[pt] and placetype_data[pt].display_handler end)
	if display_handler then
		output = display_handler(placetype, output)
	end
	if not holonym.suppress_affix then
		-- Implement adding an affix (prefix or suffix) based on the holonym's placetype. The affix will be
		-- added either if the placetype's placetype_data spec says so (by setting 'affix_type'), or if the
		-- user explicitly called for this (e.g. by using 'r:suf/O'Higgins'). Before adding the affix,
		-- however, we check to see if the affix is already present (e.g. the placetype is "district"
		-- and the placename is "Mission District"). The placetype can override the affix to add (by setting
		-- `prefix`, `suffix` or `affix`) and/or override the strings used for checking if the affix is already
		-- present (by setting 'no_affix_strings', which defaults to the affix explicitly given through `prefix`,
		-- `suffix` or `affix` if any are given). `prefix` and `suffix` take precedence over `affix` if both are
		-- set, but only when the appropriate type of affix is requested.

		-- Search through equivalent placetypes for a setting of `affix_type`, `affix`, `prefix` or `suffix`. If we
		-- find any, use them. If `affix_type` is given, it is overridden by the user's explicitly specified affix
		-- type. If either an `affix_type` is found or the user explicitly specified an affix type, the affix is
		-- displayed according to the following:
		-- 1. If `prefix`, `suffix` or `affix` is given by the placetype or equivalent placetypes, use it (e.g.
		--    placetype `administrative region` requests suffix "region" but doesn't set affix type; if the user
		--    explicitly specifies `administrative region` as the placetype for a holonym and specifies a suffixal
		--    affix type, use "region"). In this search, we stop looking if we find an explicit `affix_type`
		--    setting; if this is found without an associated affix setting, the assumption is the associated
		--    placetype was intended as the affix, not some explicit affix setting associated with a fallback
		--    placetype.
		-- 2. Otherwise, if the user explicitly requested an affix type, use the actual placetype (principle of
		--    least surprise).
		-- 3. Finally, fall back to the placetype associated with an explicit `affix_type` setting (which will
		--    always exist if we get this far).
		affix_type_pt_data, pt_equiv_for_affix_type = m_placetypes.get_equiv_placetype_prop(placetype,
			function(pt)
				local cdpt = placetype_data[pt]
				return cdpt and cdpt.affix_type and cdpt or nil
			end
		)
		affix_pt_data, pt_equiv_for_affix = m_placetypes.get_equiv_placetype_prop(placetype,
			function(pt)
				local cdpt = placetype_data[pt]
				return cdpt and (cdpt.affix_type or cdpt.affix or cdpt.prefix or cdpt.suffix) and cdpt or nil
			end
		)
		if affix_type_pt_data then
			affix_type = affix_type_pt_data.affix_type
			need_affix = true
		end
		if affix_pt_data then
			prefix = affix_pt_data.prefix or affix_pt_data.affix
			suffix = affix_pt_data.suffix or affix_pt_data.affix
			need_affix = true
		end
		no_affix_strings = affix_pt_data and affix_pt_data.no_affix_strings or
			affix_type_pt_data and affix_type_pt_data.no_affix_strings
		if holonym.affix_type and placetype then
			affix_type = holonym.affix_type
			prefix = prefix or placetype
			suffix = suffix or placetype
			need_affix = true
		end
		if need_affix then
			-- At this point the affix_type has been determined and can't change any more, so we can figure out
			-- whether we need the calculated prefix or suffix.
			affix_is_prefix = affix_type == "pref" or affix_type == "Pref"
			if affix_is_prefix then
				affix = prefix
			else
				affix = suffix
			end
			no_affix_strings = no_affix_strings or lc(affix)
			if holonym.pluralize_affix then
				affix = m_placetypes.pluralize_placetype(affix)
			end
			already_seen_affix = m_placetypes.check_already_seen_string(output, no_affix_strings)
		end
	end
	output = link(output, holonym.langcode or placetype and "en" or nil)
	if need_affix and not affix_is_prefix and not already_seen_affix then
		output = output .. " " .. (affix_type == "Suf" and ucfirst_all(affix) or affix)
	end

	if needs_article then
		local article = holonym.force_the and "the" or get_holonym_article(output, place_desc, holonym_index)
		if article then
			output = article .. " " .. output
		end
	end

	if affix_is_prefix and not already_seen_affix then
		output = (affix_type == "Pref" and ucfirst_all(affix) or affix) .. " of " .. output
		if orig_needs_article then
			-- Put the article before the added affix if we're the first holonym in the place description. This is
			-- distinct from the article added above for the holonym itself; cf. "c:pref/United States,Canada" ->
			-- "the countries of the United States and Canada". We need to use the value of `needs_article` passed
			-- in from the function, which indicates whether we're processing the first holonym.
			output = "the " .. output
		end
	end
	return output
end


local function format_holonym_in_context(entry_placetype, place_desc, holonym_index, holonym_no_prefix)
	local desc = ""

	-- If holonym.placetype is nil, the holonym is just raw text, e.g. 'in southern'.

	if holonym_no_prefix then
		desc = " "
	else
		local holonym = place_desc.holonyms[holonym_index]
		if not holonym.no_display then
			-- First compute the initial delimiter.
			if holonym_index == 1 then
				if holonym.placetype then
					desc = desc .. " " .. m_placetypes.get_placetype_entry_preposition(entry_placetype) .. " "
				elseif not holonym.display_placename:find("^,") then
					desc = desc .. " "
				end
			else
				local prev_holonym = place_desc.holonyms[holonym_index - 1]
				if prev_holonym.placetype and not holonym.suppress_comma then
					local dname = holonym.display_placename
					if dname ~= "and" and dname ~= "in" and dname ~= "and the" and dname ~= "in the" then
						desc = desc .. ","
					end
				end

				if holonym.placetype or not holonym.display_placename:find("^,") then
					desc = desc .. " "
				end
			end
		end
	end

	return desc .. format_holonym(place_desc, holonym_index, not holonym_no_prefix and holonym_index == 1)
end


local function get_placetype_description(placetype)
	local splits = m_placetypes.split_qualifiers_from_placetype(placetype)
	local prefix = ""
	for _, split in ipairs(splits) do
		local prev_qualifier, this_qualifier, bare_placetype = unpack(split, 1, 3)
		if this_qualifier then
			prefix = (prev_qualifier and prev_qualifier .. " " .. this_qualifier or this_qualifier) .. " "
		else
			prefix = ""
		end
		local display_form = m_placetypes.get_placetype_display_form(bare_placetype)
		if display_form then
			return prefix .. display_form
		end
		placetype = bare_placetype
	end
	return prefix .. placetype
end


local function get_qualifier_description(qualifier)
	local splits = m_placetypes.split_qualifiers_from_placetype(qualifier .. " foo")
	local split = splits[#splits]
	local prev_qualifier, this_qualifier, bare_placetype = unpack(split, 1, 3)
	return prev_qualifier and prev_qualifier .. " " .. this_qualifier or this_qualifier
end


local function format_form_of_directive(overall_place_spec, directive_terms, ucfirst, from_tcl)
	local formatted_terms = {}

	local placetypes
	if not overall_place_spec.descs[2] then
		placetypes = overall_place_spec.descs[1].placetypes
	else
		placetypes = {}
		for _, desc in ipairs(overall_place_spec.descs) do
			m_table.extend(placetypes, desc.placetypes)
		end
	end
	for _, termobj in ipairs(directive_terms.terms) do
		local placename_article
		if not termobj.alt and termobj.term and not termobj.term:find("%[%[") then
			placename_article = get_placename_article(termobj.term, placetypes)
		end
		local linked_term = m_links.full_link(termobj, "term", nil, "show qualifiers")
		linked_term = "<span class='form-of-definition-link'>" .. linked_term .. "</span>"
		if termobj.eq then
			linked_term = linked_term .. " (= " .. m_links.full_link {term = termobj.eq, lang = enlang} .. ")"
		end
		if placename_article then
			linked_term = placename_article .. " " .. linked_term
		end
		insert(formatted_terms, linked_term)
	end

	local spec = directive_terms.spec
	local text = spec.text
	if type(text) == "function" then
		text = text(overall_place_spec)
	end
	if text == "+" then
		text = directive_terms.directive
	end
	if ucfirst then
		text = m_strutils.ucfirst(text)
	end
	return require(form_of_module).format_form_of {
		text = text,
		lemmas = m_table.serialCommaJoin(formatted_terms, {conj = directive_terms.conj or spec.conjunction or "and"}),
		lemma_classes = false,
		-- text_classes = "place-text",
	}
end


local function format_extra_info(overall_place_spec, extra_info_terms, sentence_style)
	local formatted_terms = {}

	for _, termobj in ipairs(extra_info_terms.terms) do
		insert(formatted_terms, m_links.full_link(termobj, nil, nil, "show qualifiers"))
	end

	local spec = extra_info_terms.spec
	local text = spec.text
	if type(text) == "function" then
		text = text(overall_place_spec)
	end
	if text == "+" then
		text = spec.arg
	end
	if spec.auto_plural and formatted_terms[2] then
		text = pluralize(text)
	end

	if spec.with_colon then
		text = text .. ":"
	end

	if sentence_style and spec.match_sentence_style then
		text = ". " .. m_strutils.ucfirst(text)
	else
		text = "; " .. text
	end

	-- FIME: Use joinSegments when available.
	-- return text .. " " ..
	--	m_table.joinSegments(formatted_terms, {conj = extra_info_terms.conj or spec.conjunction or "and"})
	return text .. " " ..
		m_table.serialCommaJoin(formatted_terms, {conj = extra_info_terms.conj or spec.conjunction or "and"})
end


local function format_old_style_place_desc_for_display(args, place_desc, desc_index, with_article, ucfirst)
	-- The placetype used to determine whether "in" or "of" follows is the last placetype if there are
	-- multiple slash-separated placetypes, but ignoring "and", "or" and parenthesized notes
	-- such as "(one of 254)".
	local entry_placetype = nil
	local placetypes = place_desc.placetypes
	local function is_and_or(item)
		return item == "and" or item == "or"
	end
	local parts = {}
	local function ins(txt)
		insert(parts, txt)
	end
	local function ins_space()
		if #parts > 0 then
			ins(" ")
		end
	end

	local and_or_pos
	for i, placetype in ipairs(placetypes) do
		if is_and_or(placetype) then
			and_or_pos = i
			-- no break here; we want the last in case of more than one
		end
	end

	local remaining_placetype_index
	if and_or_pos then
		local items = {}
		for i = 1, and_or_pos + 1 do
			local pt = placetypes[i]
			if is_and_or(pt) then
				-- skip
			elseif i > 1 and pt:find("^%(") then
				-- append placetypes beginning with a paren to previous item
				items[#items] = items[#items] .. " " .. pt
			else
				entry_placetype = pt
				insert(items, get_placetype_description(pt))
			end
		end
		ins(m_table.serialCommaJoin(items, {conj = placetypes[and_or_pos]}))
		remaining_placetype_index = and_or_pos + 2
	else
		remaining_placetype_index = 1
	end

	for i = remaining_placetype_index, #placetypes do
		local pt = placetypes[i]
		-- Check for and, or and placetypes beginning with a paren (so that things like
		-- "{{place|en|county/(one of 254)|s/Texas}}" work).
		if m_placetypes.placetype_is_ignorable(pt) then
			ins_space()
			ins(pt)
		else
			entry_placetype = pt
			-- Join multiple placetypes with comma unless placetypes are already
			-- joined with "and". We allow "the" to precede the second placetype
			-- if they're not joined with "and" (so we get "city and county seat of ..."
			-- but "city, the county seat of ...").
			if i > 1 then
				ins(", ")
				local article = m_placetypes.get_placetype_article(pt)
				if article then
					ins(article)
					ins(" ")
				end
			end

			ins(get_placetype_description(pt))
		end
	end

	if place_desc.holonyms then
		for holonym_index, _ in ipairs(place_desc.holonyms) do
			ins(format_holonym_in_context(entry_placetype, place_desc, holonym_index))
		end
	end

	local gloss = concat(parts)

	if with_article then
		local article
		if desc_index == 1 then
			article = args.a
		else
			if not place_desc.holonyms then
				-- there isn't a following holonym; the place type given might be raw text as well, so don't add
				-- an article.
				with_article = false
			else
				local saw_placetype_holonym = false
				for _, holonym in ipairs(place_desc.holonyms) do
					if holonym.placetype then
						saw_placetype_holonym = true
						break
					end
				end
				if not saw_placetype_holonym then
					-- following holonym(s)s is/are just raw text; the place type given might be raw text as well,
					-- so don't add an article.
					with_article = false
				end
			end
		end
		if with_article then
			article = article or m_placetypes.get_placetype_article(place_desc.placetypes[1], ucfirst)
			if article then
				gloss = article .. " " .. gloss
			elseif ucfirst then
				gloss = m_strutils.ucfirst(gloss)
			end
		end
	end

	return gloss
end


function export.format_new_style_place_desc_for_display(args, place_desc, with_article)
	local parts = {}
	local function ins(txt)
		insert(parts, txt)
	end

	if with_article and args.a then
		ins(args.a .. " ")
	end

	local max_holonym = 0
	for _, order in ipairs(place_desc.order) do
		local segment_type, segment = order.type, order.value
		if segment_type == "raw" then
			ins(segment)
		elseif segment_type == "placetype" then
			ins(get_placetype_description(segment))
		elseif segment_type == "qualifier" then
			ins(get_qualifier_description(segment))
		elseif segment_type == "holonym" then
			ins(format_holonym(place_desc, segment, false))
			if segment > max_holonym then
				max_holonym = segment
			end
		end
	end

	if place_desc.holonyms and max_holonym < #place_desc.holonyms then
		local holonym_no_prefix = true
		for holonym_index = max_holonym + 1, #place_desc.holonyms do
			ins(format_holonym_in_context(nil, place_desc, holonym_index, holonym_no_prefix))
			holonym_no_prefix = false
		end
	end

	return concat(parts)
end


local function get_display_form(data)
	local overall_place_spec, ucfirst, sentence_style, drop_extra_info, extra_info_overridden_set, from_tcl =
		data.overall_place_spec, data.ucfirst, data.sentence_style, data.drop_extra_info,
		data.extra_info_overridden_set, data.from_tcl
	local args = overall_place_spec.args
	local parts = {}
	local function ins(txt)
		table.insert(parts, txt)
	end

	if overall_place_spec.directives and overall_place_spec.directives[1] then
		for i, directive_terms in ipairs(overall_place_spec.directives) do
			ins(directive_terms.pretext)
			if directive_terms.pretext ~= "" then
				ucfirst = false
			end
			ins(format_form_of_directive(overall_place_spec, directive_terms, ucfirst, from_tcl))
			ucfirst = false
			if i == #overall_place_spec.directives and directive_terms.posttext then
				ins(directive_terms.posttext)
			end
		end
	end
	if args.def == "-" then
		return concat(parts)
	end
	if args.def then
		if args.def:find("<<") then
			local def_desc = export.parse_new_style_place_desc(args.def, args[1])
			ins(export.format_new_style_place_desc_for_display({}, def_desc, false))
		else
			ins(args.def)
		end
	else
		local include_article = true
		for n, desc in ipairs(overall_place_spec.descs) do
			if desc.order then
				ins(export.format_new_style_place_desc_for_display(args, desc, n == 1))
			else
				ins(format_old_style_place_desc_for_display(args, desc, n, include_article, ucfirst))
			end
			if desc.joiner then
				ins(desc.joiner)
			end
			include_article = desc.include_following_article
			ucfirst = false
		end
	end

	local addl = args.addl
	if addl then
		posttext = posttext or ""
		if addl:find("^[;:]") then
			ins(addl)
		elseif addl:find("^_") then
			ins(" " .. addl:sub(2))
		else
			ins(", " .. addl)
		end
	end

	for _, extra_info_terms in ipairs(overall_place_spec.extra_info) do
		-- Include a given extra info term either when
		-- (1) drop_extra_info not set (it's set by {{tcl}}), or
		-- (2) the extra info term is marked as "display even when dropped" (e.g. modern= or full=, to help understand
		--     the term's sense), or
		-- (3) the term was overridden by a `place_*=` setting in {{tcl}}.
		if not drop_extra_info or extra_info_terms.spec.display_even_when_dropped or
			extra_info_overridden_set and extra_info_overridden_set[extra_info_terms.spec.arg] then
			ins(format_extra_info(overall_place_spec, extra_info_terms, sentence_style))
		end
	end

	return concat(parts)
end

local function get_def(data)
	local overall_place_spec, from_tcl, drop_extra_info, extra_info_overridden_set, translation_follows =
		data.overall_place_spec, data.from_tcl, data.drop_extra_info, data.extra_info_overridden_set,
		data.translation_follows
	local args = overall_place_spec.args
	local sentence_style = overall_place_spec.lang:getCode() == "en"
	local ucfirst = sentence_style and not args.nocap
	if #args.t > 0 then
		local gloss = get_display_form {
			overall_place_spec = overall_place_spec,
			ucfirst = false,
			sentence_style = false,
			drop_extra_info = drop_extra_info,
			extra_info_overridden_set = extra_info_overridden_set,
			from_tcl = from_tcl,
		}
		if from_tcl and not args.tcl_nolc then
			gloss = m_strutils.lcfirst(gloss)
		end
		if translation_follows then
			return (gloss == "" and "" or gloss .. ": ") .. get_translations(args.t, args.tid)
		else
			return get_translations(args.t, args.tid) .. (gloss == "" and "" or " (" .. gloss .. ")")
		end
	else
		return get_display_form {
			overall_place_spec = overall_place_spec,
			ucfirst = ucfirst,
			sentence_style = sentence_style,
			drop_extra_info = drop_extra_info,
			extra_info_overridden_set = extra_info_overridden_set,
			from_tcl = from_tcl,
		}
	end
end

function export.format(data)
	local template_args = data.template_args
	local list_param = {list = true}
	local boolean_param = {type = "boolean"}
	local params = {
		[1] = {required = true, type = "language", default = "und"},
		[2] = {required = true, list = true},
		["t"] = list_param,
		["tid"] = {list = true, allow_holes = true},
		["nocap"] = boolean_param,
		["sort"] = true,
		["pagename"] = true, -- for testing or documentation purposes

		["a"] = true,
		["addl"] = true,
		["def"] = true,

		-- params that are only used when transcluding using {{tcl}}/{{transclude}}, to transmit information to {{tcl}}.
		["tcl"] = true,
		["tcl_t"] = list_param,
		["tcl_tid"] = list_param,
		["tcl_nolb"] = true,
		["tcl_nolc"] = boolean_param,
		["tcl_noextratext"] = boolean_param,
	}

	-- add "extra info" parameters
	for _, extra_arg_spec in ipairs(export.extra_info_args) do
		params[extra_arg_spec.arg] = list_param
	end

	local args = require("Module:parameters").process(template_args, params)
	data.args = args
	local overall_place_spec = parse_overall_place_spec(data)
	data.overall_place_spec = overall_place_spec

	return get_def(data)
end

function export.show(frame)
	return export.format {
		template_args = frame:getParent().args,
	}
end


return export
