_addon.author = 'Jyouya'
_addon.command = 'em'
_addon.name = 'ExtraMacros'
_addon.version = '1.0'

config = require('config')

settings = config.load()

current_display = nil

keys_pressed = {
	[219] = false,
	[220] = false,
	[56] = false,
	[29] = false,
	[221] = false,
}

kb_modifiers = {
	[219] = 'win',
	[220] = 'win',
	[56] = 'alt',
	[29] = 'ctrl',
	[221] = 'apps'
}

display_book = {
	win = false,
	alt = false,
	ctrl = false,
	apps = false,
}

function display_macros(dik)
	if dik == 219 or dik == 220 then -- win was pressed
		current_display = 'win'
		windower.prim.set_visibility('win_book', true)
		for k, v in pairs(win_text) do
			windower.text.set_visibility(v.bind, true)
			windower.text.set_visibility(v.text, true)
		end
	elseif dik == 56 then -- alt
		current_display = 'alt'
		windower.prim.set_visibility('alt_book', true)
		for k, v in pairs(alt_text) do
			windower.text.set_visibility(v.bind, true)
			windower.text.set_visibility(v.text, true)
		end
	elseif dik == 29 then -- ctrl
		current_display = 'ctrl'
		windower.prim.set_visibility('ctrl_book', true)
		for k, v in pairs(ctrl_text) do
			windower.text.set_visibility(v.bind, true)
			windower.text.set_visibility(v.text, true)
		end
	elseif dik == 221 then -- apps
		current_display = 'apps'
		windower.prim.set_visibility('apps_book', true)
		for k, v in pairs(apps_text) do
			windower.text.set_visibility(v.bind, true)
			windower.text.set_visibility(v.text, true)
		end
	end
end

function hide_macros(dik)
	current_display = nil
	if dik == 219 or dik == 220 then -- win was pressed
		windower.prim.set_visibility('win_book', false)
		for k, v in pairs(win_text) do
			windower.text.set_visibility(v.bind, false)
			windower.text.set_visibility(v.text, false)
		end
	elseif dik == 56 then -- alt
		windower.prim.set_visibility('alt_book', false)
		for k, v in pairs(alt_text) do
			windower.text.set_visibility(v.bind, false)
			windower.text.set_visibility(v.text, false)
		end
	elseif dik == 29 then -- ctrl
		windower.prim.set_visibility('ctrl_book', false)
		for k, v in pairs(ctrl_text) do
			windower.text.set_visibility(v.bind, false)
			windower.text.set_visibility(v.text, false)
		end
	elseif dik == 221 then -- apps
		windower.prim.set_visibility('apps_book', false)
		for k, v in pairs(apps_text) do
			windower.text.set_visibility(v.bind, false)
			windower.text.set_visibility(v.text, false)
		end
	end			
end

windower.register_event('keyboard', function(dik, pressed, flags, blocked)
	if display_book[kb_modifiers[dik]] then
		keys_pressed[dik] = pressed
		if pressed and not current_display then	-- we need to pull up a new macrobar
			display_macros(dik)
		elseif not pressed and kb_modifiers[dik] then -- one of our modifier keys was released
			if current_display == kb_modifiers[dik] then -- the key for the window macrobook we're displaying was released
				hide_macros(dik)
				for k,v in pairs(keys_pressed) do
					if v then
						display_macros(k)
						break
					end
				end
			end
		end
	end
end)

windower.register_event('addon command', function(...)
	
end)

windower.register_event('job change', function(main_job_id, main_job_level, sub_job_id, sub_job_level)
	windower.send_command('lua r ExtraMacros')
end)

keynames = {
	backtick='`',
	minus='-',
	equals='=',
	backslash='\\',
	period='.',
	comma=',',
	lbracket='[',
	rbracket=']',
	semicolon=';',
	slash='/',
	}

function resolve_keyname(str)
	return keynames[str] or str
end

function bind_win(k,v)
	k = resolve_keyname(k)
	windower.send_command('bind @%s %s':format(k,v.command))
	local bind = 'Win %s':format(k:upper())
	win_text[bind] = {text=bind..'1', bind=bind..'2'}
	
	-- Create the text object for the description
	windower.text.create(win_text[bind].text)
	windower.text.set_text(win_text[bind].text, v.text)
	windower.text.set_location(win_text[bind].text, settings.posx + 5 + (v.x - 1) * 68, settings.posy + 1 + (v.y - 1) * 56)
	windower.text.set_color(win_text[bind].text, 255, 255, 255, 255)
	windower.text.set_bold(win_text[bind].text, true)
	windower.text.set_font(win_text[bind].text, 'Helvetica')
	windower.text.set_font_size(win_text[bind].text, 10)
	windower.text.set_visibility(win_text[bind].text, false)
	
	-- Create the text object for the keybind info
	windower.text.create(win_text[bind].bind)
	windower.text.set_text(win_text[bind].bind, bind)
	windower.text.set_location(win_text[bind].bind, settings.posx - 6 + v.x * 68, settings.posy + 36 + (v.y - 1) * 56)
	windower.text.set_right_justified(win_text[bind].bind, true)
	windower.text.set_color(win_text[bind].bind, 255, 255, 255, 255)
	windower.text.set_bold(win_text[bind].bind, true)
	windower.text.set_font(win_text[bind].bind, 'Helvetica')
	windower.text.set_font_size(win_text[bind].bind, 10)
	windower.text.set_visibility(win_text[bind].bind, false)
	
	display_book.win = true
end

function bind_alt(k,v)
	k = resolve_keyname(k)
	windower.send_command('bind !%s %s':format(k, v.command))
	local bind = 'Alt %s':format(k:upper())
	alt_text[bind] = {text=bind..'1', bind=bind..'2'}
	
	-- Create the text object for the description
	windower.text.create(alt_text[bind].text)
	windower.text.set_text(alt_text[bind].text, v.text)
	windower.text.set_location(alt_text[bind].text, settings.posx + 5 + (v.x - 1) * 68, settings.posy + 1 + (v.y - 1) * 56)
	windower.text.set_color(alt_text[bind].text, 255, 255, 255, 255)
	windower.text.set_bold(alt_text[bind].text, true)
	windower.text.set_font(alt_text[bind].text, 'Helvetica')
	windower.text.set_font_size(alt_text[bind].text, 10)
	windower.text.set_visibility(alt_text[bind].text, false)
	
	-- Create the text object for the keybind info
	windower.text.create(alt_text[bind].bind)
	windower.text.set_text(alt_text[bind].bind, bind)
	windower.text.set_location(alt_text[bind].bind, settings.posx - 6 + v.x * 68, settings.posy + 36 + (v.y - 1) * 56)
	windower.text.set_right_justified(alt_text[bind].bind, true)
	windower.text.set_color(alt_text[bind].bind, 255, 255, 255, 255)
	windower.text.set_bold(alt_text[bind].bind, true)
	windower.text.set_font(alt_text[bind].bind, 'Helvetica')
	windower.text.set_font_size(alt_text[bind].bind, 10)
	windower.text.set_visibility(alt_text[bind].bind, false)
	
	display_book.alt = true
end

function bind_ctrl(k,v)
	k = resolve_keyname(k)
	windower.send_command('bind ^%s %s':format(k, v.command))
	local bind = 'Ctrl %s':format(k:upper())
	ctrl_text[bind] = {text=bind..'1', bind=bind..'2'}
	
	-- Create the text object for the description
	windower.text.create(ctrl_text[bind].text)
	windower.text.set_text(ctrl_text[bind].text, v.text)
	windower.text.set_location(ctrl_text[bind].text, settings.posx + 5 + (v.x - 1) * 68, settings.posy + 1 + (v.y - 1) * 56)
	windower.text.set_color(ctrl_text[bind].text, 255, 255, 255, 255)
	windower.text.set_bold(ctrl_text[bind].text, true)
	windower.text.set_font(ctrl_text[bind].text, 'Helvetica')
	windower.text.set_font_size(ctrl_text[bind].text, 10)
	windower.text.set_visibility(ctrl_text[bind].text, false)
	
	-- Create the text object for the keybind info
	windower.text.create(ctrl_text[bind].bind)
	windower.text.set_text(ctrl_text[bind].bind, bind)
	windower.text.set_location(ctrl_text[bind].bind, settings.posx - 6 + v.x * 68, settings.posy + 36 + (v.y - 1) * 56)
	windower.text.set_right_justified(ctrl_text[bind].bind, true)
	windower.text.set_color(ctrl_text[bind].bind, 255, 255, 255, 255)
	windower.text.set_bold(ctrl_text[bind].bind, true)
	windower.text.set_font(ctrl_text[bind].bind, 'Helvetica')
	windower.text.set_font_size(ctrl_text[bind].bind, 10)
	windower.text.set_visibility(ctrl_text[bind].bind, false)
	
	display_book.ctrl = true
end

function bind_apps(k,v)
	k = resolve_keyname(k)
	windower.send_command('bind ^%s %s':format(k, v.command))
	local bind = 'Apps %s':format(k:upper())
	apps_text[bind] = {text=bind..'1', bind=bind..'2'}
	
	-- Create the text object for the description
	windower.text.create(apps_text[bind].text)
	windower.text.set_text(apps_text[bind].text, v.text)
	windower.text.set_location(apps_text[bind].text, settings.posx + 5 + (v.x - 1) * 68, settings.posy + 1 + (v.y - 1) * 56)
	windower.text.set_color(apps_text[bind].text, 255, 255, 255, 255)
	windower.text.set_bold(apps_text[bind].text, true)
	windower.text.set_font(apps_text[bind].text, 'Helvetica')
	windower.text.set_font_size(apps_text[bind].text, 10)
	windower.text.set_visibility(apps_text[bind].text, false)
	
	-- Create the text object for the keybind info
	windower.text.create(apps_text[bind].bind)
	windower.text.set_text(apps_text[bind].bind, bind)
	windower.text.set_location(apps_text[bind].bind, settings.posx - 6 + v.x * 68, settings.posy + 36 + (v.y - 1) * 56)
	windower.text.set_right_justified(apps_text[bind].bind, true)
	windower.text.set_color(apps_text[bind].bind, 255, 255, 255, 255)
	windower.text.set_bold(apps_text[bind].bind, true)
	windower.text.set_font(apps_text[bind].bind, 'Helvetica')
	windower.text.set_font_size(apps_text[bind].bind, 10)
	windower.text.set_visibility(apps_text[bind].bind, false)
	
	display_book.apps = true
end

-- Create the three macrobars
windower.prim.create('win_book')
windower.prim.create('alt_book')
windower.prim.create('ctrl_book')
windower.prim.create('apps_book')

windower.prim.set_visibility('win_book', false)
windower.prim.set_visibility('alt_book', false)
windower.prim.set_visibility('ctrl_book', false)
windower.prim.set_visibility('apps_book', false)

windower.prim.set_position('win_book', settings.posx, settings.posy)
windower.prim.set_position('alt_book', settings.posx, settings.posy)
windower.prim.set_position('ctrl_book', settings.posx, settings.posy)
windower.prim.set_position('apps_book', settings.posx, settings.posy)

windower.prim.set_texture('win_book', windower.addon_path..'data/blank_macrobar.png')
windower.prim.set_texture('alt_book', windower.addon_path..'data/blank_macrobar.png')
windower.prim.set_texture('ctrl_book', windower.addon_path..'data/blank_macrobar.png')
windower.prim.set_texture('apps_book', windower.addon_path..'data/blank_macrobar.png')

windower.prim.set_fit_to_texture('win_book', true)
windower.prim.set_fit_to_texture('alt_book', true)
windower.prim.set_fit_to_texture('ctrl_book', true)
windower.prim.set_fit_to_texture('apps_book', true)

win_text = {}
alt_text = {}
ctrl_text = {}
apps_text = {}

	-- Add text to the macrobars
	-- Add description text on top
	-- Add keybind text on bottom

-- Bind the keys


if settings.win then
	for k, v in pairs(settings.win) do
		bind_win(k,v)
		print(k,v)
	end
end
if settings.alt then
	for k, v in pairs(settings.alt) do
		bind_alt(k,v)
	end
end
if settings.ctrl then
	for k, v in pairs(settings.ctrl) do
		bind_ctrl(k,v)
	end
end
if settings.apps then
	for k, v in pairs(settings.apps) do
		bind_apps(k,v)
	end
end

me = windower.ffxi.get_player()

if settings.jobspecific and settings.jobspecific[me.main_job:lower()] then
	--print('job specific binds detected')
	for k, v in pairs(settings.jobspecific[me.main_job:lower()].win) do
		bind_win(k,v)
	end

	for k, v in pairs(settings.jobspecific[me.main_job:lower()].alt) do
		bind_alt(k,v)
	end

	for k, v in pairs(settings.jobspecific[me.main_job:lower()].ctrl) do
		bind_ctrl(k,v)
	end	
	
	for k, v in pairs(settings.jobspecific[me.main_job:lower()].apps) do
		bind_apps(k,v)
	end
	
	if settings.jobspecific[me.main_job:lower()][me.sub_job:lower()] then
		for k, v in pairs(settings.jobspecific[me.main_job:lower()][me.sub_job:lower()].win) do
			bind_win(k,v)
		end

		for k, v in pairs(settings.jobspecific[me.main_job:lower()][me.sub_job:lower()].alt) do
			bind_alt(k,v)
		end

		for k, v in pairs(settings.jobspecific[me.main_job:lower()][me.sub_job:lower()].ctrl) do
			bind_ctrl(k,v)
		end	
		
		for k, v in pairs(settings.jobspecific[me.main_job:lower()][me.sub_job:lower()].apps) do
			bind_apps(k,v)
		end
		
	end
end

function format_text(str)
	
end