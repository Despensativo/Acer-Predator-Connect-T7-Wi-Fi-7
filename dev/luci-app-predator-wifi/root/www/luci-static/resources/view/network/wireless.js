'use strict';
'require view';
'require dom';
'require poll';
'require fs';
'require ui';
'require rpc';
'require uci';
'require form';
'require network';
'require firewall';
'require tools.widgets as widgets';

var callPredatorWifiAction = rpc.declare({
	object: 'predator',
	method: 'luci_wifi_action',
	params: ['action', 'device', 'mac'],
	expect: { '': {} }
});

function radio_to_ath(section_id) {
	if (section_id == 'wifi0') return 'ath0';
	if (section_id == 'wifi1') return 'ath1';
	if (section_id == 'wifi2') return 'ath2';
	return section_id;
}

function count_changes(section_id) {
	var changes = ui.changes.changes, n = 0;
	if (!L.isObject(changes))
		return n;
	if (Array.isArray(changes.wireless))
		for (var i = 0; i < changes.wireless.length; i++)
			n += (changes.wireless[i][1] == section_id);
	return n;
}

function render_radio_badge(radioDev) {
	return E('span', { 'class': 'ifacebadge' }, [
		E('img', { 'src': L.resource('icons/wifi%s.png').format(radioDev.isUp() ? '' : '_disabled') }),
		' ',
		radioDev.getName()
	]);
}

function render_signal_badge(signalPercent, signalValue, noiseValue, wrap, mode) {
	var icon, title, value;
	if (signalPercent < 0)
		icon = L.resource('icons/signal-none.png');
	else if (signalPercent == 0)
		icon = L.resource('icons/signal-0.png');
	else if (signalPercent < 25)
		icon = L.resource('icons/signal-0-25.png');
	else if (signalPercent < 50)
		icon = L.resource('icons/signal-25-50.png');
	else if (signalPercent < 75)
		icon = L.resource('icons/signal-50-75.png');
	else
		icon = L.resource('icons/signal-75-100.png');

	if (signalValue != null && signalValue != 0) {
		if (noiseValue != null && noiseValue != 0) {
			value = '%d/%d\xa0%s'.format(signalValue, noiseValue, _('dBm'));
			title = '%s: %d %s / %s: %d %s / %s %d'.format(_('Signal'), signalValue, _('dBm'), _('Noise'), noiseValue, _('dBm'), _('SNR'), signalValue - noiseValue);
		}
		else {
			value = '%d\xa0%s'.format(signalValue, _('dBm'));
			title = '%s: %d %s'.format(_('Signal'), signalValue, _('dBm'));
		}
	}
	else if (signalPercent > -1) {
		switch (mode) {
			case 'ap': title = _('No client associated'); break;
			case 'sta': case 'adhoc': case 'mesh': title = _('Not associated'); break;
			default: title = _('No RX signal');
		}
		if (noiseValue != null && noiseValue != 0) {
			value = '---/%d\xa0%s'.format(noiseValue, _('dBm'));
			title = '%s / %s: %d %s'.format(title, _('Noise'), noiseValue, _('dBm'));
		}
		else {
			value = '---\xa0%s'.format(_('dBm'));
		}
	}
	else {
		value = E('em', {}, E('small', {}, [_('disabled')]));
		title = _('Interface is disabled');
	}

	return E('div', { 'class': wrap ? 'center' : 'ifacebadge', 'title': title, 'data-signal': signalValue, 'data-noise': noiseValue }, [
		E('img', { 'src': icon }),
		E('span', {}, [wrap ? E('br') : ' ', value])
	]);
}

function render_network_badge(radioNet) {
	return render_signal_badge(radioNet.isUp() ? radioNet.getSignalPercent() : -1, radioNet.getSignal(), radioNet.getNoise(), false, radioNet.getMode());
}

function render_radio_status(radioDev, wifiNets) {
	var name = radioDev.getI18n().replace(/ Wireless Controller .+$/, ''),
	    node = E('div', [E('big', {}, E('strong', {}, name)), E('div')]),
	    channel = radioDev.ubus('dev', 'iwinfo', 'channel'),
	    frequency = radioDev.ubus('dev', 'iwinfo', 'frequency') ? '%.03f'.format(radioDev.ubus('dev', 'iwinfo', 'frequency') / 1000) : null,
	    width = radioDev.ubus('dev', 'iwinfo', 'width'),
	    txpower = radioDev.ubus('dev', 'iwinfo', 'txpower'),
	    noise = radioDev.ubus('dev', 'iwinfo', 'noise'),
	    bitrate = radioDev.ubus('dev', 'iwinfo', 'bitrate') ? (radioDev.ubus('dev', 'iwinfo', 'bitrate') / 1000) : null;

	for (var i = 0; i < wifiNets.length; i++) {
		channel = channel || wifiNets[i].getChannel();
		frequency = frequency || wifiNets[i].getFrequency();
		bitrate = bitrate || wifiNets[i].getBitRate();
		if (!width && wifiNets[i].getChannelWidth)
			width = wifiNets[i].getChannelWidth();
		if (txpower == null)
			txpower = wifiNets[i].getTXPower();
		if (noise == null || noise == 0)
			noise = wifiNets[i].getNoise();
	}

	if (radioDev.isUp()) {
		var items = [
			_('Channel'), '%s (%s %s)'.format(channel || '?', frequency || '?', _('GHz'))
		];
		if (width) {
			items.push(_('Width'), '%d %s'.format(width, _('MHz')));
		}
		if (txpower != null) {
			items.push(_('Tx-Power'), '%d %s'.format(txpower, _('dBm')));
		}
		items.push(_('Bitrate'), '%s %s'.format(bitrate || '?', _('Mbit/s')));
		if (noise != null && noise != 0) {
			items.push(_('Noise'), '%d %s'.format(noise, _('dBm')));
		}
		L.itemlist(node.lastElementChild, items, ' | ');
	}
	else {
		node.lastElementChild.appendChild(E('em', _('Device is not active')));
	}
	return node;
}

function render_network_status(radioNet) {
	var mode = radioNet.getActiveMode(),
	    bssid = radioNet.getActiveBSSID(),
	    channel = radioNet.getChannel(),
	    width = radioNet.getChannelWidth ? radioNet.getChannelWidth() : null,
	    disabled = (radioNet.get('disabled') == '1' || uci.get('wireless', radioNet.getWifiDeviceName(), 'disabled') == '1'),
	    is_assoc = (bssid && bssid != '00:00:00:00:00:00' && channel && mode != 'Unknown' && !disabled),
	    is_mesh = (radioNet.getMode() == 'mesh'),
	    changecount = count_changes(radioNet.getName()),
	    status_text = null;

	if (changecount)
		status_text = E('a', { href: '#', click: L.bind(ui.changes.displayChanges, ui.changes) }, _('Interface has %d pending changes').format(changecount));
	else if (!is_assoc)
		status_text = E('em', disabled ? _('Wireless is disabled') : _('Wireless is not associated'));

	return L.itemlist(E('div'), [
		is_mesh ? _('Mesh ID') : _('SSID'), (is_mesh ? radioNet.getMeshID() : radioNet.getSSID()) || '?',
		_('Mode'), mode,
		_('BSSID'), (!changecount && is_assoc) ? bssid : null,
		_('Encryption'), (!changecount && is_assoc) ? radioNet.getActiveEncryption() || _('None') : null,
		_('Width'), (!changecount && is_assoc && width) ? '%d MHz'.format(width) : null,
		null, status_text
	], [' | ', E('br')]);
}

function render_modal_status(node, radioNet) {
	var mode = radioNet.getActiveMode(),
	    noise = radioNet.getNoise(),
	    bssid = radioNet.getActiveBSSID(),
	    channel = radioNet.getChannel(),
	    width = radioNet.getChannelWidth ? radioNet.getChannelWidth() : null,
	    disabled = (radioNet.get('disabled') == '1'),
	    is_assoc = (bssid && bssid != '00:00:00:00:00:00' && channel && mode != 'Unknown' && !disabled);

	if (node == null)
		node = E('span', { 'class': 'ifacebadge large', 'data-network': radioNet.getName() }, [E('small'), E('span')]);

	dom.content(node.firstElementChild, render_signal_badge(disabled ? -1 : radioNet.getSignalPercent(), radioNet.getSignal(), noise, true, radioNet.getMode()));

	L.itemlist(node.lastElementChild, [
		_('Mode'), mode,
		_('SSID'), radioNet.getSSID() || '?',
		_('BSSID'), is_assoc ? bssid : null,
		_('Encryption'), is_assoc ? radioNet.getActiveEncryption() || _('None') : null,
		_('Channel'), is_assoc ? '%d (%.3f %s%s)'.format(radioNet.getChannel(), radioNet.getFrequency() || 0, _('GHz'), width ? ' • %d MHz'.format(width) : '') : null,
		_('Tx-Power'), is_assoc ? '%d %s'.format(radioNet.getTXPower(), _('dBm')) : null,
		_('Signal'), (is_assoc && radioNet.getSignal()) ? '%d %s'.format(radioNet.getSignal(), _('dBm')) : null,
		_('Noise'), (is_assoc && noise != null) ? '%d %s'.format(noise, _('dBm')) : null,
		_('Bitrate'), is_assoc ? '%.1f %s'.format(radioNet.getBitRate() || 0, _('Mbit/s')) : null,
		_('Country'), is_assoc ? radioNet.getCountryCode() : null
	], [' | ', E('br'), E('br'), E('br'), E('br'), E('br'), ' | ', E('br'), ' | ']);

	if (!is_assoc)
		dom.append(node.lastElementChild, E('em', disabled ? _('Wireless is disabled') : _('Wireless is not associated')));

	return node;
}

function format_wifirate(rate) {
	var s = '%.1f\xa0%s, %d\xa0%s'.format(rate.rate / 1000, _('Mbit/s'), rate.mhz, _('MHz')),
	    ht = rate.ht, vht = rate.vht, he = rate.he, eht = rate.eht,
	    mhz = rate.mhz, nss = rate.nss, mcs = rate.mcs, sgi = rate.short_gi;

	if (eht) {
		if (mcs != null) s += ', EHT-MCS\xa0%d'.format(mcs);
		if (nss) s += ', EHT-NSS\xa0%d'.format(nss);
	}
	else if (he) {
		if (mcs != null) s += ', HE-MCS\xa0%d'.format(mcs);
		if (nss) s += ', HE-NSS\xa0%d'.format(nss);
	}
	else if (ht || vht) {
		if (vht) s += ', VHT-MCS\xa0%d'.format(mcs);
		if (nss) s += ', VHT-NSS\xa0%d'.format(nss);
		if (ht) s += ', MCS\xa0%s'.format(mcs);
		if (sgi) s += ', ' + _('Short GI').replace(/ /g, '\xa0');
	}
	return s;
}

function radio_restart(id, ev) {
	var row = document.querySelector('.cbi-section-table-row[data-sid="%s"]'.format(id)),
	    dsc = row.querySelector('[data-name="_stat"] > div'),
	    btn = row.querySelector('.cbi-section-actions button');
	btn.blur();
	btn.classList.add('spinning');
	btn.disabled = true;
	dsc.setAttribute('restart', '');
	dom.content(dsc, E('em', _('Device is restarting…')));
}

function network_updown(id, map, ev) {
	var radio = uci.get('wireless', id, 'device'),
	    disabled = (uci.get('wireless', id, 'disabled') == '1') || (uci.get('wireless', radio, 'disabled') == '1');
	if (disabled) {
		uci.unset('wireless', id, 'disabled');
		uci.unset('wireless', radio, 'disabled');
	}
	else {
		uci.set('wireless', id, 'disabled', '1');
		var all_networks_disabled = true,
		    wifi_ifaces = uci.sections('wireless', 'wifi-iface');
		for (var i = 0; i < wifi_ifaces.length; i++) {
			if (wifi_ifaces[i].device == radio && wifi_ifaces[i].disabled != '1') {
				all_networks_disabled = false;
				break;
			}
		}
		if (all_networks_disabled)
			uci.set('wireless', radio, 'disabled', '1');
	}
	return map.save().then(function() {
		return ui.changes.apply();
	}).then(function() {
		return callPredatorWifiAction('reload', '', '');
	});
}

function next_free_sid(offset) {
	var sid = 'wifinet' + offset;
	while (uci.get('wireless', sid))
		sid = 'wifinet' + (++offset);
	return sid;
}

function add_dependency_permutations(o, deps) {
	var res = null;
	for (var key in deps) {
		if (!deps.hasOwnProperty(key) || !Array.isArray(deps[key]))
			continue;
		var list = deps[key], tmp = [];
		for (var j = 0; j < list.length; j++) {
			for (var k = 0; k < (res ? res.length : 1); k++) {
				var item = (res ? Object.assign({}, res[k]) : {});
				item[key] = list[j];
				tmp.push(item);
			}
		}
		res = tmp;
	}
	for (var i = 0; i < (res ? res.length : 0); i++)
		o.depends(res[i]);
}

var CBIWifiFrequencyValue = form.Value.extend({
	callFrequencyList: rpc.declare({
		object: 'iwinfo',
		method: 'freqlist',
		params: ['device'],
		expect: { results: [] }
	}),

	load: function(section_id) {
		var ath = radio_to_ath(section_id);
		return Promise.all([
			network.getWifiDevice(section_id),
			L.resolveDefault(this.callFrequencyList(ath), [])
		]).then(L.bind(function(data) {
			this.radioName = section_id;
			this.channels = {
				'11g': ['auto', 'auto', true],
				'11a': ['auto', 'auto', true],
				'11a_6g': ['auto', 'auto', true]
			};

			var freqlist = Array.isArray(data[1]) ? data[1] : [];
			if (freqlist.length > 0) {
				for (var i = 0; i < freqlist.length; i++) {
					var f = freqlist[i];
					if (f.mhz <= 2484)
						this.channels['11g'].push(f.channel, '%d (%d MHz)'.format(f.channel, f.mhz), !f.restricted);
					else if (f.mhz >= 5925)
						this.channels['11a_6g'].push(f.channel, '%d (%d MHz%s)'.format(f.channel, f.mhz, ((f.channel - 5) % 16 === 0) ? ' • PSC' : ''), !f.restricted);
					else
						this.channels['11a'].push(f.channel, '%d (%d MHz%s)'.format(f.channel, f.mhz, (f.channel >= 100 && f.channel <= 144) ? ' • 240MHz/DFS' : ''), !f.restricted);
				}
			}

			if (this.channels['11g'].length <= 3) {
				var ch2g = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];
				for (var i = 0; i < ch2g.length; i++)
					this.channels['11g'].push(ch2g[i], '%d (%d MHz)'.format(ch2g[i], 2407 + ch2g[i] * 5), true);
			}
			if (this.channels['11a'].length <= 3) {
				var ch5g = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165];
				for (var i = 0; i < ch5g.length; i++)
					this.channels['11a'].push(ch5g[i], '%d (%d MHz%s)'.format(ch5g[i], 5000 + ch5g[i] * 5, (ch5g[i] >= 100 && ch5g[i] <= 144) ? ' • 240MHz/DFS' : ''), true);
			}
			if (this.channels['11a_6g'].length <= 3) {
				var ch6g = [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129, 133, 137, 141, 145, 149, 153, 157, 161, 165, 169, 173, 177, 181, 185, 189, 193, 197, 201, 205, 209, 213, 217, 221, 225, 229, 233];
				for (var i = 0; i < ch6g.length; i++)
					this.channels['11a_6g'].push(ch6g[i], '%d (%d MHz%s)'.format(ch6g[i], 5950 + ch6g[i] * 5, ((ch6g[i] - 5) % 16 === 0) ? ' • PSC' : ''), true);
			}

			if (section_id == 'wifi0') {
				this.modes = [
					'be', 'Wi-Fi 7 (802.11be EHT)', true,
					'ax', 'Wi-Fi 6 (802.11ax HE)', true,
					'n', 'Wi-Fi 4 (802.11n HT)', true,
					'', 'Legacy (802.11b/g)', true
				];
				this.htmodes = {
					'': ['HT20', '20 MHz', true],
					'n': ['HT20', '20 MHz', true, 'HT40', 'Auto (20/40 MHz)', true, 'HT40_FORCE', '40 MHz (Forced)', true],
					'ax': ['HT20', '20 MHz', true, 'HT40', 'Auto (20/40 MHz)', true, 'HT40_FORCE', '40 MHz (Forced)', true],
					'be': ['HT20', '20 MHz', true, 'HT40', 'Auto (20/40 MHz)', true, 'HT40_FORCE', '40 MHz (Forced)', true]
				};
				this.bands = {
					'': ['11g', '2.4 GHz', true],
					'n': ['11g', '2.4 GHz', true],
					'ax': ['11g', '2.4 GHz', true],
					'be': ['11g', '2.4 GHz', true]
				};
			}
			else if (section_id == 'wifi2') {
				this.modes = [
					'be', 'Wi-Fi 7 (802.11be EHT)', true,
					'ax', 'Wi-Fi 6E (802.11ax HE)', true
				];
				this.htmodes = {
					'ax': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true, 'HT80', '80 MHz', true, 'HT160', '160 MHz', true],
					'be': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true, 'HT80', '80 MHz', true, 'HT160', '160 MHz', true, 'HT240', '240 MHz (Punctured)', true, 'HT320', '320 MHz (Ultra)', true]
				};
				this.bands = {
					'ax': ['11a_6g', '6 GHz', true],
					'be': ['11a_6g', '6 GHz', true]
				};
			}
			else {
				this.modes = [
					'be', 'Wi-Fi 7 (802.11be EHT)', true,
					'ax', 'Wi-Fi 6 (802.11ax HE)', true,
					'ac', 'Wi-Fi 5 (802.11ac VHT)', true,
					'n', 'Wi-Fi 4 (802.11n HT)', true,
					'', 'Legacy (802.11a)', true
				];
				this.htmodes = {
					'': ['HT20', '20 MHz', true],
					'n': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true],
					'ac': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true, 'HT80', '80 MHz', true, 'HT160', '160 MHz', true],
					'ax': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true, 'HT80', '80 MHz', true, 'HT160', '160 MHz', true],
					'be': ['HT20', '20 MHz', true, 'HT40', '40 MHz', true, 'HT80', '80 MHz', true, 'HT160', '160 MHz', true, 'HT240', '240 MHz (Wi-Fi 7 Punctured)', true]
				};
				this.bands = {
					'': ['11a', '5 GHz', true],
					'n': ['11a', '5 GHz', true],
					'ac': ['11a', '5 GHz', true],
					'ax': ['11a', '5 GHz', true],
					'be': ['11a', '5 GHz', true]
				};
			}
		}, this));
	},

	setValues: function(sel, vals) {
		if (sel.vals)
			sel.vals.selected = sel.selectedIndex;
		while (sel.options[0])
			sel.remove(0);
		for (var i = 0; vals && i < vals.length; i += 3)
			if (vals[i + 2])
				sel.add(E('option', { value: vals[i + 0] }, [vals[i + 1]]));
		if (vals && !isNaN(vals.selected))
			sel.selectedIndex = vals.selected;
		sel.parentNode.style.display = (sel.options.length <= 1) ? 'none' : '';
		sel.vals = vals;
	},

	toggleWifiMode: function(elem) {
		this.toggleWifiHTMode(elem);
		this.toggleWifiBand(elem);
	},

	toggleWifiHTMode: function(elem) {
		var mode = elem.querySelector('.mode');
		var bwdt = elem.querySelector('.htmode');
		this.setValues(bwdt, this.htmodes[mode.value]);
	},

	toggleWifiBand: function(elem) {
		var mode = elem.querySelector('.mode');
		var band = elem.querySelector('.band');
		this.setValues(band, this.bands[mode.value]);
		this.toggleWifiChannel(elem);
	},

	toggleWifiChannel: function(elem) {
		var band = elem.querySelector('.band');
		var chan = elem.querySelector('.channel');
		this.setValues(chan, this.channels[band.value]);
	},

	setInitialValues: function(section_id, elem) {
		var mode = elem.querySelector('.mode'),
		    band = elem.querySelector('.band'),
		    chan = elem.querySelector('.channel'),
		    bwdt = elem.querySelector('.htmode'),
		    htval = uci.get('wireless', section_id, 'htmode') || 'HT80',
		    hwval = uci.get('wireless', section_id, 'hwmode') || '11bea',
		    chval = uci.get('wireless', section_id, 'channel') || 'auto',
		    coex = uci.get('wireless', section_id, 'chan_coex_disable') || uci.get('wireless', section_id + '_ap', 'disablecoext') || '0';

		if (section_id == 'wifi0' && htval == 'HT40' && coex == '1')
			htval = 'HT40_FORCE';
		htval = htval.replace(/^(VHT|HE|EHT)/, 'HT');

		this.setValues(mode, this.modes);
		if (/be/.test(hwval) || /HT240|HT320/.test(htval))
			mode.value = 'be';
		else if (/ax/.test(hwval))
			mode.value = 'ax';
		else if (/ac/.test(hwval) || /HT80|HT160/.test(htval))
			mode.value = 'ac';
		else if (/n/.test(hwval) || /HT20|HT40/.test(htval))
			mode.value = 'n';
		else
			mode.value = '';

		this.toggleWifiMode(elem);

		if (section_id == 'wifi2')
			band.value = '11a_6g';
		else if (section_id == 'wifi1' || /a/.test(hwval))
			band.value = '11a';
		else
			band.value = '11g';

		this.toggleWifiBand(elem);
		bwdt.value = htval;
		chan.value = chval;
		return elem;
	},

	renderWidget: function(section_id, option_index, cfgvalue) {
		var elem = E('div');
		dom.content(elem, [
			E('label', { 'style': 'float:left; margin-right:3px' }, [
				_('Mode'), E('br'),
				E('select', { 'class': 'mode', 'style': 'width:auto', 'change': L.bind(this.toggleWifiMode, this, elem) })
			]),
			E('label', { 'style': 'float:left; margin-right:3px' }, [
				_('Band'), E('br'),
				E('select', { 'class': 'band', 'style': 'width:auto', 'change': L.bind(this.toggleWifiBand, this, elem) })
			]),
			E('label', { 'style': 'float:left; margin-right:3px' }, [
				_('Channel'), E('br'),
				E('select', { 'class': 'channel', 'style': 'width:auto' })
			]),
			E('label', { 'style': 'float:left; margin-right:3px' }, [
				_('Width'), E('br'),
				E('select', { 'class': 'htmode', 'style': 'width:auto' })
			]),
			E('br', { 'style': 'clear:left' })
		]);
		return this.setInitialValues(section_id, elem);
	},

	cfgvalue: function(section_id) {
		return [
			uci.get('wireless', section_id, 'htmode'),
			uci.get('wireless', section_id, 'hwmode'),
			uci.get('wireless', section_id, 'channel'),
			uci.get('wireless', section_id, 'chan_coex_disable')
		];
	},

	formvalue: function(section_id) {
		var node = this.map.findElement('data-field', this.cbid(section_id));
		return [
			node.querySelector('.htmode').value,
			node.querySelector('.band').value,
			node.querySelector('.channel').value,
			node.querySelector('.mode').value
		];
	},

	write: function(section_id, value) {
		var ht = value[0] || 'HT80',
		    band = value[1],
		    chan = value[2] || 'auto',
		    mode = value[3] || 'be',
		    hwmode = '11bea';

		if (section_id == 'wifi0' || band == '11g') {
			if (mode == 'be') hwmode = '11beg';
			else if (mode == 'ax') hwmode = '11axg';
			else if (mode == 'n') hwmode = '11ng';
			else hwmode = '11g';

			if (ht == 'HT40_FORCE') {
				uci.set('wireless', section_id, 'htmode', 'HT40');
				uci.set('wireless', section_id, 'chan_coex_disable', '1');
				if (uci.get('wireless', 'wifi0_ap'))
					uci.set('wireless', 'wifi0_ap', 'disablecoext', '1');
				if (chan == 'auto')
					chan = '6';
			}
			else {
				uci.set('wireless', section_id, 'htmode', ht);
				uci.set('wireless', section_id, 'chan_coex_disable', '0');
				if (uci.get('wireless', 'wifi0_ap'))
					uci.set('wireless', 'wifi0_ap', 'disablecoext', '0');
			}
		}
		else if (section_id == 'wifi2' || band == '11a_6g') {
			hwmode = (mode == 'ax') ? '11axa' : '11bea';
			uci.set('wireless', section_id, 'band', '3');
			uci.set('wireless', section_id, 'htmode', ht);
			if (ht == 'HT240')
				uci.set('wireless', section_id, 'puncture_bitmap', '61440');
			else
				uci.set('wireless', section_id, 'puncture_bitmap', '0');
		}
		else {
			if (mode == 'be') hwmode = '11bea';
			else if (mode == 'ax') hwmode = '11axa';
			else if (mode == 'ac') hwmode = '11ac';
			else if (mode == 'n') hwmode = '11na';
			else hwmode = '11a';

			uci.set('wireless', section_id, 'htmode', ht);
			if (ht == 'HT240') {
				var chNum = parseInt(chan, 10);
				if (isNaN(chNum) || chNum < 100 || chNum > 144)
					chan = '100';
				uci.set('wireless', section_id, 'ccfs', '130');
				uci.set('wireless', section_id, 'puncture_bitmap', '61440');
				uci.set('wireless', section_id, 'puncture_strict', '0');
				uci.set('wireless', section_id, 'dfs_punctureEn', '1');
				if (uci.get('wireless', 'wifi1_ap'))
					uci.set('wireless', 'wifi1_ap', 'cactimeout', '1');
			}
			else {
				uci.set('wireless', section_id, 'ccfs', '0');
				uci.set('wireless', section_id, 'puncture_bitmap', '0');
			}
		}

		uci.set('wireless', section_id, 'hwmode', hwmode);
		uci.set('wireless', section_id, 'channel', chan);
	}
});

var CBIWifiTxPowerValue = form.ListValue.extend({
	callTxPowerList: rpc.declare({
		object: 'iwinfo',
		method: 'txpowerlist',
		params: ['device'],
		expect: { results: [] }
	}),

	load: function(section_id) {
		var ath = radio_to_ath(section_id);
		return L.resolveDefault(this.callTxPowerList(ath), []).then(L.bind(function(pwrlist) {
			this.powerval = this.wifiNetwork ? this.wifiNetwork.getTXPower() : null;
			this.poweroff = this.wifiNetwork ? this.wifiNetwork.getTXPowerOffset() : null;
			this.value('', _('driver default'));
			if (Array.isArray(pwrlist) && pwrlist.length > 0) {
				for (var i = 0; i < pwrlist.length; i++)
					this.value(pwrlist[i].dbm, '%d dBm (%d mW)'.format(pwrlist[i].dbm, pwrlist[i].mw));
			}
			else {
				var fallbackDbm = [10, 12, 14, 16, 18, 20, 21, 22, 23, 24, 25, 26, 28, 30];
				for (var i = 0; i < fallbackDbm.length; i++) {
					var d = fallbackDbm[i], mw = Math.round(Math.pow(10, d / 10));
					this.value(d, '%d dBm (%d mW)'.format(d, mw));
				}
			}
			return form.ListValue.prototype.load.apply(this, [section_id]);
		}, this));
	},

	renderWidget: function(section_id, option_index, cfgvalue) {
		var widget = form.ListValue.prototype.renderWidget.apply(this, [section_id, option_index, cfgvalue]);
		widget.firstElementChild.style.width = 'auto';
		dom.append(widget, E('span', [
			' - ', _('Current power'), ': ',
			E('span', [this.powerval != null ? '%d dBm'.format(this.powerval) : E('em', _('unknown'))]),
			this.poweroff ? ' + %d dB offset = %s dBm'.format(this.poweroff, this.powerval != null ? this.powerval + this.poweroff : '?') : ''
		]));
		return widget;
	}
});

var CBIWifiCountryValue = form.Value.extend({
	callCountryList: rpc.declare({
		object: 'iwinfo',
		method: 'countrylist',
		params: ['device'],
		expect: { results: [] }
	}),

	load: function(section_id) {
		var ath = radio_to_ath(section_id);
		return L.resolveDefault(this.callCountryList(ath), []).then(L.bind(function(countrylist) {
			this.value('', _('driver default'));
			if (Array.isArray(countrylist) && countrylist.length > 0) {
				for (var i = 0; i < countrylist.length; i++)
					this.value(countrylist[i].iso3166, '%s - %s'.format(countrylist[i].iso3166, countrylist[i].country));
			}
			else {
				var defaults = [
					['BR', 'Brazil'],
					['US', 'United States'],
					['00', 'World / Global'],
					['PT', 'Portugal'],
					['ES', 'Spain'],
					['DE', 'Germany'],
					['GB', 'United Kingdom'],
					['FR', 'France'],
					['CA', 'Canada'],
					['AU', 'Australia'],
					['JP', 'Japan'],
					['TW', 'Taiwan'],
					['CN', 'China']
				];
				for (var i = 0; i < defaults.length; i++)
					this.value(defaults[i][0], '%s - %s'.format(defaults[i][0], defaults[i][1]));
			}
			return form.Value.prototype.load.apply(this, [section_id]);
		}, this));
	},

	validate: function(section_id, formvalue) {
		if (formvalue != null && formvalue != '' && !/^[A-Z0-9][A-Z0-9]$/.test(formvalue))
			return _('Use ISO/IEC 3166 alpha2 country codes.');
		return true;
	},

	renderWidget: function(section_id, option_index, cfgvalue) {
		var typeClass = (this.keylist && this.keylist.length) ? form.ListValue : form.Value;
		return typeClass.prototype.renderWidget.apply(this, [section_id, option_index, cfgvalue]);
	}
});

return view.extend({
	poll_status: function(map, data) {
		var rows = map.querySelectorAll('.cbi-section-table-row[data-sid]');
		for (var i = 0; i < rows.length; i++) {
			var section_id = rows[i].getAttribute('data-sid'),
			    radioDev = data[1].filter(function(d) { return d.getName() == section_id; })[0],
			    radioNet = data[2].filter(function(n) { return n.getName() == section_id; })[0],
			    badge = rows[i].querySelector('[data-name="_badge"] > div'),
			    stat = rows[i].querySelector('[data-name="_stat"]'),
			    btns = rows[i].querySelectorAll('.cbi-section-actions button'),
			    busy = btns[0].classList.contains('spinning') || btns[1].classList.contains('spinning') || btns[2].classList.contains('spinning');

			if (radioDev) {
				dom.content(badge, render_radio_badge(radioDev));
				dom.content(stat, render_radio_status(radioDev, data[2].filter(function(n) { return n.getWifiDeviceName() == radioDev.getName(); })));
			}
			else if (radioNet) {
				dom.content(badge, render_network_badge(radioNet));
				dom.content(stat, render_network_status(radioNet));
			}

			if (stat.hasAttribute('restart'))
				dom.content(stat, E('em', _('Device is restarting…')));

			btns[0].disabled = busy;
			btns[1].disabled = busy;
			btns[2].disabled = busy;
		}

		var table = document.querySelector('#wifi_assoclist_table'),
		    hosts = data[0],
		    trows = [];

		for (var i = 0; i < data[3].length; i++) {
			var bss = data[3][i],
			    name = hosts.getHostnameByMACAddr(bss.mac),
			    ipv4 = hosts.getIPAddrByMACAddr(bss.mac),
			    ipv6 = hosts.getIP6AddrByMACAddr(bss.mac);
			var hint;
			if (name && ipv4 && ipv6)
				hint = '%s <span class="hide-xs">(%s, %s)</span>'.format(name, ipv4, ipv6);
			else if (name && (ipv4 || ipv6))
				hint = '%s <span class="hide-xs">(%s)</span>'.format(name, ipv4 || ipv6);
			else
				hint = name || ipv4 || ipv6 || '?';

			var row = [
				E('span', { 'class': 'ifacebadge', 'data-ifname': bss.network.getIfname(), 'data-ssid': bss.network.getSSID() }, [
					E('img', { 'src': L.resource('icons/wifi%s.png').format(bss.network.isUp() ? '' : '_disabled'), 'title': bss.radio.getI18n() }),
					E('span', [' %s '.format(bss.network.getShortName()), E('small', '(%s)'.format(bss.network.getIfname()))])
				]),
				bss.mac,
				hint,
				render_signal_badge(Math.min((bss.signal + 110) / 70 * 100, 100), bss.signal, bss.noise),
				E('span', {}, [
					E('span', format_wifirate(bss.rx)),
					E('br'),
					E('span', format_wifirate(bss.tx))
				])
			];

			if (bss.network.isClientDisconnectSupported()) {
				if (table.firstElementChild.childNodes.length < 6)
					table.firstElementChild.appendChild(E('div', { 'class': 'th cbi-section-actions' }));
				row.push(E('button', {
					'class': 'cbi-button cbi-button-remove',
					'click': L.bind(function(net, mac, ev) {
						dom.parent(ev.currentTarget, '.tr').style.opacity = 0.5;
						ev.currentTarget.classList.add('spinning');
						ev.currentTarget.disabled = true;
						ev.currentTarget.blur();
						net.disconnectClient(mac, true, 5, 60000);
					}, this, bss.network, bss.mac)
				}, [_('Disconnect')]));
			}
			else {
				row.push('-');
			}
			trows.push(row);
		}

		cbi_update_table(table, trows, E('em', _('No information available')));

		var stat = document.querySelector('.cbi-modal [data-name="_wifistat_modal"] .ifacebadge.large');
		if (stat)
			render_modal_status(stat, data[2].filter(function(n) { return n.getName() == stat.getAttribute('data-network'); })[0]);

		return network.flushCache();
	},

	load: function() {
		return Promise.all([
			uci.changes(),
			uci.load('wireless')
		]);
	},

	checkAnonymousSections: function() {
		var wifiIfaces = uci.sections('wireless', 'wifi-iface');
		for (var i = 0; i < wifiIfaces.length; i++)
			if (wifiIfaces[i]['.anonymous'])
				return true;
		return false;
	},

	callUciRename: rpc.declare({
		object: 'uci',
		method: 'rename',
		params: ['config', 'section', 'name']
	}),

	render: function() {
		if (this.checkAnonymousSections())
			return this.renderMigration();
		else
			return this.renderOverview();
	},

	handleMigration: function(ev) {
		var wifiIfaces = uci.sections('wireless', 'wifi-iface'),
		    id_offset = 0,
		    tasks = [];
		for (var i = 0; i < wifiIfaces.length; i++) {
			if (!wifiIfaces[i]['.anonymous'])
				continue;
			var new_name = next_free_sid(id_offset);
			tasks.push(this.callUciRename('wireless', wifiIfaces[i]['.name'], new_name));
			id_offset = +new_name.substring(7) + 1;
		}
		return Promise.all(tasks)
			.then(L.bind(ui.changes.init, ui.changes))
			.then(L.bind(ui.changes.apply, ui.changes));
	},

	renderMigration: function() {
		ui.showModal(_('Wireless configuration migration'), [
			E('p', _('The existing wireless configuration needs to be changed for LuCI to function properly.')),
			E('p', _('Upon pressing "Continue", anonymous "wifi-iface" sections will be assigned with a name in the form <em>wifinet#</em> and the network will be restarted to apply the updated configuration.')),
			E('div', { 'class': 'right' }, E('button', {
				'class': 'btn cbi-button-action important',
				'click': ui.createHandlerFn(this, 'handleMigration')
			}, _('Continue')))
		]);
	},

	handleSaveApply: function(ev, mode) {
		return this.handleSave(ev).then(function() {
			return ui.changes.apply(mode == '0');
		}).then(function() {
			return callPredatorWifiAction('reload', '', '');
		});
	},

	renderOverview: function() {
		var m, s, o;
		m = new form.Map('wireless');
		m.chain('network');
		m.chain('firewall');

		s = m.section(form.GridSection, 'wifi-device', _('Wireless Overview'));
		s.anonymous = true;
		s.addremove = false;

		s.load = function() {
			return network.getWifiDevices().then(L.bind(function(radios) {
				this.radios = radios.sort(function(a, b) { return a.getName() > b.getName(); });
				var tasks = [];
				for (var i = 0; i < radios.length; i++)
					tasks.push(radios[i].getWifiNetworks());
				return Promise.all(tasks);
			}, this)).then(L.bind(function(data) {
				this.wifis = [];
				for (var i = 0; i < data.length; i++)
					this.wifis.push.apply(this.wifis, data[i]);
			}, this));
		};

		s.cfgsections = function() {
			var rv = [];
			for (var i = 0; i < this.radios.length; i++) {
				rv.push(this.radios[i].getName());
				for (var j = 0; j < this.wifis.length; j++)
					if (this.wifis[j].getWifiDeviceName() == this.radios[i].getName())
						rv.push(this.wifis[j].getName());
			}
			return rv;
		};

		s.modaltitle = function(section_id) {
			var radioNet = this.wifis.filter(function(w) { return w.getName() == section_id; })[0];
			return radioNet ? radioNet.getI18n() : _('Edit wireless network');
		};

		s.lookupRadioOrNetwork = function(section_id) {
			var radioDev = this.radios.filter(function(r) { return r.getName() == section_id; })[0];
			if (radioDev)
				return radioDev;
			var radioNet = this.wifis.filter(function(w) { return w.getName() == section_id; })[0];
			if (radioNet)
				return radioNet;
			return null;
		};

		s.renderRowActions = function(section_id) {
			var inst = this.lookupRadioOrNetwork(section_id), btns;
			if (inst.getWifiNetworks) {
				btns = [
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'title': _('Restart radio interface'),
						'click': ui.createHandlerFn(this, radio_restart, section_id)
					}, _('Restart')),
					E('button', {
						'class': 'cbi-button cbi-button-action important',
						'title': _('Find and join network'),
						'click': ui.createHandlerFn(this, 'handleScan', inst)
					}, _('Scan')),
					E('button', {
						'class': 'cbi-button cbi-button-add',
						'title': _('Provide new network'),
						'click': ui.createHandlerFn(this, 'handleAdd', inst)
					}, _('Add'))
				];
			}
			else {
				var isDisabled = (inst.get('disabled') == '1' || uci.get('wireless', inst.getWifiDeviceName(), 'disabled') == '1');
				btns = [
					E('button', {
						'class': 'cbi-button cbi-button-neutral enable-disable',
						'title': isDisabled ? _('Enable this network') : _('Disable this network'),
						'click': ui.createHandlerFn(this, network_updown, section_id, this.map)
					}, isDisabled ? _('Enable') : _('Disable')),
					E('button', {
						'class': 'cbi-button cbi-button-action important',
						'title': _('Edit this network'),
						'click': ui.createHandlerFn(this, 'renderMoreOptionsModal', section_id)
					}, _('Edit')),
					E('button', {
						'class': 'cbi-button cbi-button-negative remove',
						'title': _('Delete this network'),
						'click': ui.createHandlerFn(this, 'handleRemove', section_id)
					}, _('Remove'))
				];
			}
			return E('div', { 'class': 'td middle cbi-section-actions' }, E('div', btns));
		};

		s.addModalOptions = function(s) {
			return network.getWifiNetwork(s.section).then(function(radioNet) {
				var hwtype = uci.get('wireless', radioNet.getWifiDeviceName(), 'type');
				var is_qca_or_mac = (hwtype == 'mac80211' || hwtype == 'qcawificfg80211');
				var o, ss;

				o = s.option(form.SectionValue, '_device', form.NamedSection, radioNet.getWifiDeviceName(), 'wifi-device', _('Device Configuration'));
				o.modalonly = true;
				ss = o.subsection;
				ss.tab('general', _('General Setup'));
				ss.tab('advanced', _('Advanced Settings'));

				var isDisabled = (radioNet.get('disabled') == '1' || uci.get('wireless', radioNet.getWifiDeviceName(), 'disabled') == 1);

				o = ss.taboption('general', form.DummyValue, '_wifistat_modal', _('Status'));
				o.cfgvalue = L.bind(function(radioNet) {
					return render_modal_status(null, radioNet);
				}, this, radioNet);
				o.write = function() {};

				o = ss.taboption('general', form.Button, '_toggle', isDisabled ? _('Wireless network is disabled') : _('Wireless network is enabled'));
				o.inputstyle = isDisabled ? 'apply' : 'reset';
				o.inputtitle = isDisabled ? _('Enable') : _('Disable');
				o.onclick = ui.createHandlerFn(s, network_updown, s.section, s.map);

				o = ss.taboption('general', CBIWifiFrequencyValue, '_freq', '<br />' + _('Operating frequency'));
				o.ucisection = s.section;

				if (is_qca_or_mac) {
					o = ss.taboption('general', CBIWifiTxPowerValue, 'txpower', _('Maximum transmit power'), _('Specifies the maximum transmit power the wireless radio may use. Depending on regulatory requirements and wireless usage, the actual transmit power may be reduced by the driver.'));
					o.wifiNetwork = radioNet;

					o = ss.taboption('advanced', CBIWifiCountryValue, 'country', _('Country Code'));
					o.wifiNetwork = radioNet;

					o = ss.taboption('advanced', form.Flag, 'chan_coex_disable', _('Force 40MHz mode (Disable 20/40 Coexistence)'), _('Always use 40MHz channels on 2.4 GHz even if overlapping networks or 40MHz-intolerant clients are present.'));
					o.rmempty = true;

					o = ss.taboption('advanced', form.Value, 'frag', _('Fragmentation Threshold'));
					o.datatype = 'min(256)';
					o.placeholder = _('off');

					o = ss.taboption('advanced', form.Value, 'rts', _('RTS/CTS Threshold'));
					o.datatype = 'uinteger';
					o.placeholder = _('off');

					o = ss.taboption('advanced', form.Value, 'beacon_int', _('Beacon Interval'));
					o.datatype = 'range(15,65535)';
					o.placeholder = 100;
					o.rmempty = true;
				}

				o = s.option(form.SectionValue, '_iface', form.NamedSection, radioNet.getName(), 'wifi-iface', _('Interface Configuration'));
				o.modalonly = true;
				ss = o.subsection;
				ss.tab('general', _('General Setup'));
				ss.tab('encryption', _('Wireless Security'));
				ss.tab('macfilter', _('MAC-Filter'));
				ss.tab('advanced', _('Advanced Settings'));

				o = ss.taboption('general', form.ListValue, 'mode', _('Mode'));
				o.value('ap', _('Access Point'));
				o.value('sta', _('Client'));
				o.value('adhoc', _('Ad-Hoc'));

				o = ss.taboption('general', form.Value, 'mesh_id', _('Mesh Id'));
				o.depends('mode', 'mesh');

				o = ss.taboption('advanced', form.Flag, 'mesh_fwding', _('Forward mesh peer traffic'));
				o.rmempty = false;
				o.default = '1';
				o.depends('mode', 'mesh');

				o = ss.taboption('advanced', form.Value, 'mesh_rssi_threshold', _('RSSI threshold for joining'), _('0 = not using RSSI threshold, 1 = do not change driver default'));
				o.rmempty = false;
				o.default = '0';
				o.datatype = 'range(-255,1)';
				o.depends('mode', 'mesh');

				o = ss.taboption('general', form.Value, 'ssid', _('<abbr title="Extended Service Set Identifier">ESSID</abbr>'));
				o.datatype = 'maxlength(32)';
				o.depends('mode', 'ap');
				o.depends('mode', 'sta');
				o.depends('mode', 'adhoc');
				o.depends('mode', 'ahdemo');
				o.depends('mode', 'monitor');
				o.depends('mode', 'ap-wds');
				o.depends('mode', 'sta-wds');
				o.depends('mode', 'wds');

				o = ss.taboption('general', form.Value, 'bssid', _('<abbr title="Basic Service Set Identifier">BSSID</abbr>'));
				o.datatype = 'macaddr';

				o = ss.taboption('general', widgets.NetworkSelect, 'network', _('Network'), _('Choose the network(s) you want to attach to this wireless interface or fill out the <em>custom</em> field to define a new network.'));
				o.rmempty = true;
				o.multiple = true;
				o.novirtual = true;
				o.write = function(section_id, value) {
					return network.getDevice(section_id).then(L.bind(function(dev) {
						var old_networks = dev.getNetworks().reduce(function(o, v) { o[v.getName()] = v; return o; }, {}),
						    new_networks = {},
						    values = L.toArray(value),
						    tasks = [];

						for (var i = 0; i < values.length; i++) {
							new_networks[values[i]] = true;
							if (old_networks[values[i]])
								continue;
							tasks.push(network.getNetwork(values[i]).then(L.bind(function(name, net) {
								return net || network.addNetwork(name, { proto: 'none' });
							}, this, values[i])).then(L.bind(function(dev, net) {
								if (net) {
									if (!net.isEmpty())
										net.set('type', 'bridge');
									net.addDevice(dev);
								}
							}, this, dev)));
						}

						for (var name in old_networks)
							if (!new_networks[name])
								tasks.push(network.getNetwork(name).then(L.bind(function(dev, net) {
									if (net)
										net.deleteDevice(dev);
								}, this, dev)));

						return Promise.all(tasks);
					}, this));
				};

				if (is_qca_or_mac) {
					var mode = ss.children[0],
					    bssid = ss.children[5],
					    encr;

					mode.value('mesh', '802.11s');
					mode.value('ahdemo', _('Pseudo Ad-Hoc (ahdemo)'));
					mode.value('monitor', _('Monitor'));
					bssid.depends('mode', 'adhoc');
					bssid.depends('mode', 'sta');
					bssid.depends('mode', 'sta-wds');

					o = ss.taboption('macfilter', form.ListValue, 'macfilter', _('MAC-Address Filter'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');
					o.value('', _('disable'));
					o.value('allow', _('Allow listed only'));
					o.value('deny', _('Allow all except listed'));

					o = ss.taboption('macfilter', form.DynamicList, 'maclist', _('MAC-List'));
					o.datatype = 'macaddr';
					o.depends('macfilter', 'allow');
					o.depends('macfilter', 'deny');
					o.load = function(section_id) {
						return network.getHostHints().then(L.bind(function(hints) {
							hints.getMACHints().map(L.bind(function(hint) {
								this.value(hint[0], hint[1] ? '%s (%s)'.format(hint[0], hint[1]) : hint[0]);
							}, this));
							return form.DynamicList.prototype.load.apply(this, [section_id]);
						}, this));
					};

					mode.value('ap-wds', '%s (%s)'.format(_('Access Point'), _('WDS')));
					mode.value('sta-wds', '%s (%s)'.format(_('Client'), _('WDS')));
					mode.write = function(section_id, value) {
						switch (value) {
							case 'ap-wds':
								uci.set('wireless', section_id, 'mode', 'ap');
								uci.set('wireless', section_id, 'wds', '1');
								break;
							case 'sta-wds':
								uci.set('wireless', section_id, 'mode', 'sta');
								uci.set('wireless', section_id, 'wds', '1');
								break;
							default:
								uci.set('wireless', section_id, 'mode', value);
								uci.unset('wireless', section_id, 'wds');
								break;
						}
					};
					mode.cfgvalue = function(section_id) {
						var mode = uci.get('wireless', section_id, 'mode'),
						    wds = uci.get('wireless', section_id, 'wds');
						if (mode == 'ap' && wds)
							return 'ap-wds';
						else if (mode == 'sta' && wds)
							return 'sta-wds';
						return mode;
					};

					o = ss.taboption('general', form.Flag, 'hidden', _('Hide <abbr title="Extended Service Set Identifier">ESSID</abbr>'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');

					o = ss.taboption('general', form.Flag, 'wmm', _('WMM Mode'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');
					o.default = o.enabled;

					o = ss.taboption('advanced', form.Flag, 'isolate', _('Isolate Clients'), _('Prevents client-to-client communication'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');

					o = ss.taboption('advanced', form.Flag, 'rrm', _('802.11k Radio Resource Measurement (RRM)'), _('Enables neighbor reports and beacon measurements for seamless client roaming.'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');
					o.default = o.enabled;

					o = ss.taboption('advanced', form.Flag, 'bss_transition', _('802.11v BSS Transition Management'), _('Allows the router to steer clients to the optimal band (2.4 / 5 / 6 GHz).'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');
					o.default = o.enabled;

					o = ss.taboption('advanced', form.Value, 'maxsta', _('Maximum Associated Stations'));
					o.depends('mode', 'ap');
					o.depends('mode', 'ap-wds');
					o.datatype = 'range(1,512)';
					o.placeholder = '64';
					o.optional = true;

					o = ss.taboption('advanced', form.Value, 'ifname', _('Interface name'), _('Override default interface name'));
					o.optional = true;
					o.placeholder = radioNet.getIfname();
					if (/^(wifi|radio)\d+\.network/.test(o.placeholder))
						o.placeholder = '';

					o = ss.taboption('advanced', form.Flag, 'shortgi', _('Short GI (Guard Interval)'));
					o.default = o.enabled;

					o = ss.taboption('advanced', form.Value, 'dtim_period', _('DTIM Interval'), _('Delivery Traffic Indication Message Interval'));
					o.optional = true;
					o.placeholder = 2;
					o.datatype = 'range(1,255)';
				}

				encr = o = ss.taboption('encryption', form.ListValue, 'encryption', _('Encryption'));
				o.depends('mode', 'ap');
				o.depends('mode', 'sta');
				o.depends('mode', 'adhoc');
				o.depends('mode', 'ahdemo');
				o.depends('mode', 'ap-wds');
				o.depends('mode', 'sta-wds');
				o.depends('mode', 'mesh');
				o.cfgvalue = function(section_id) {
					var v = String(uci.get('wireless', section_id, 'encryption'));
					if (v == 'wep')
						return 'wep-open';
					else if (v.match(/\+/))
						return v.replace(/\+.+$/, '');
					return v;
				};
				o.write = function(section_id, value) {
					var e = this.section.children.filter(function(o) { return o.option == 'encryption'; })[0].formvalue(section_id),
					    co = this.section.children.filter(function(o) { return o.option == 'cipher'; })[0],
					    c = co.formvalue(section_id);

					if (value == 'wpa' || value == 'wpa2' || value == 'wpa3' || value == 'wpa3-mixed')
						uci.unset('wireless', section_id, 'key');

					if (co.isActive(section_id) && e && (c == 'tkip' || c == 'ccmp' || c == 'tkip+ccmp')) {
						if (e == 'psk2' && c == 'ccmp' && hwtype == 'qcawificfg80211')
							e = 'psk2+aes';
						else
							e += '+' + c;
					}
					else if (e == 'psk2' && hwtype == 'qcawificfg80211') {
						e = 'psk2+aes';
					}

					uci.set('wireless', section_id, 'encryption', e);
					if (e == 'sae') {
						uci.set('wireless', section_id, 'sae', '1');
						uci.set('wireless', section_id, 'ieee80211w', '2');
					}
					else if (e == 'sae-mixed') {
						uci.set('wireless', section_id, 'sae', '1');
						uci.set('wireless', section_id, 'ieee80211w', '1');
					}
					else if (e.indexOf('psk') === 0) {
						uci.set('wireless', section_id, 'sae', '0');
					}
				};

				o = ss.taboption('encryption', form.ListValue, 'cipher', _('Cipher'));
				o.depends('encryption', 'wpa');
				o.depends('encryption', 'wpa2');
				o.depends('encryption', 'wpa3');
				o.depends('encryption', 'wpa3-mixed');
				o.depends('encryption', 'psk');
				o.depends('encryption', 'psk2');
				o.depends('encryption', 'wpa-mixed');
				o.depends('encryption', 'psk-mixed');
				o.value('auto', _('auto'));
				o.value('ccmp', _('Force CCMP (AES)'));
				o.value('tkip', _('Force TKIP'));
				o.value('tkip+ccmp', _('Force TKIP and CCMP (AES)'));
				o.write = ss.children.filter(function(o) { return o.option == 'encryption'; })[0].write;
				o.cfgvalue = function(section_id) {
					var v = String(uci.get('wireless', section_id, 'encryption'));
					if (v.match(/\+/)) {
						v = v.replace(/^[^+]+\+/, '');
						if (v == 'aes')
							v = 'ccmp';
						else if (v == 'tkip+aes' || v == 'aes+tkip' || v == 'ccmp+tkip')
							v = 'tkip+ccmp';
					}
					return v;
				};

				var crypto_modes = [];
				if (is_qca_or_mac) {
					crypto_modes.push(['psk2', 'WPA2-PSK', 35]);
					crypto_modes.push(['sae', 'WPA3-SAE', 31]);
					crypto_modes.push(['sae-mixed', 'WPA2-PSK/WPA3-SAE Mixed Mode', 30]);
					crypto_modes.push(['psk-mixed', 'WPA-PSK/WPA2-PSK Mixed Mode', 22]);
					crypto_modes.push(['psk', 'WPA-PSK', 21]);
					crypto_modes.push(['wpa3', 'WPA3-EAP', 33]);
					crypto_modes.push(['wpa3-mixed', 'WPA2-EAP/WPA3-EAP Mixed Mode', 32]);
					crypto_modes.push(['wpa2', 'WPA2-EAP', 34]);
					crypto_modes.push(['wpa', 'WPA-EAP', 20]);
					crypto_modes.push(['owe', 'OWE (Opportunistic Wireless Encryption)', 1]);

					encr.crypto_support = {
						'ap': { 'wep-open': true, 'wep-shared': true, 'psk': true, 'psk2': true, 'psk-mixed': true, 'sae': true, 'sae-mixed': true, 'wpa': true, 'wpa2': true, 'wpa3': true, 'wpa3-mixed': true, 'owe': true },
						'sta': { 'wep-open': true, 'wep-shared': true, 'psk': true, 'psk2': true, 'psk-mixed': true, 'sae': true, 'sae-mixed': true, 'wpa': true, 'wpa2': true, 'wpa3': true, 'wpa3-mixed': true, 'owe': true },
						'adhoc': { 'wep-open': true, 'wep-shared': true, 'psk': true, 'psk2': true, 'psk-mixed': true },
						'mesh': { 'sae': true },
						'ahdemo': { 'wep-open': true, 'wep-shared': true },
						'wds': { 'wep-open': true, 'wep-shared': true }
					};
					encr.crypto_support['ap-wds'] = encr.crypto_support['ap'];
					encr.crypto_support['sta-wds'] = encr.crypto_support['sta'];

					encr.validate = function(section_id, value) {
						var modeopt = this.section.children.filter(function(o) { return o.option == 'mode'; })[0],
						    modeval = modeopt.formvalue(section_id),
						    modetitle = modeopt.vallist[modeopt.keylist.indexOf(modeval)],
						    enctitle = this.vallist[this.keylist.indexOf(value)];
						if (value == 'none')
							return true;
						if (!L.isObject(this.crypto_support[modeval]) || !this.crypto_support[modeval].hasOwnProperty(value))
							return _('The selected %s mode is incompatible with %s encryption').format(modetitle, enctitle);
						return this.crypto_support[modeval][value];
					};
				}
				else if (hwtype == 'broadcom') {
					crypto_modes.push(['psk2', 'WPA2-PSK', 33]);
					crypto_modes.push(['psk+psk2', 'WPA-PSK/WPA2-PSK Mixed Mode', 22]);
					crypto_modes.push(['psk', 'WPA-PSK', 21]);
				}

				crypto_modes.push(['wep-open', _('WEP Open System'), 11]);
				crypto_modes.push(['wep-shared', _('WEP Shared Key'), 10]);
				crypto_modes.push(['none', _('No Encryption'), 0]);
				crypto_modes.sort(function(a, b) { return b[2] - a[2]; });

				for (var i = 0; i < crypto_modes.length; i++) {
					var security_level = (crypto_modes[i][2] >= 30) ? _('strong security')
						: (crypto_modes[i][2] >= 20) ? _('medium security')
							: (crypto_modes[i][2] >= 10) ? _('weak security') : _('open network');
					encr.value(crypto_modes[i][0], '%s (%s)'.format(crypto_modes[i][1], security_level));
				}

				o = ss.taboption('encryption', form.Value, 'auth_server', _('Radius-Authentication-Server'));
				add_dependency_permutations(o, { mode: ['ap', 'ap-wds'], encryption: ['wpa', 'wpa2', 'wpa3', 'wpa3-mixed'] });
				o.rmempty = true;
				o.datatype = 'host(0)';

				o = ss.taboption('encryption', form.Value, 'auth_port', _('Radius-Authentication-Port'), _('Default %d').format(1812));
				add_dependency_permutations(o, { mode: ['ap', 'ap-wds'], encryption: ['wpa', 'wpa2', 'wpa3', 'wpa3-mixed'] });
				o.rmempty = true;
				o.datatype = 'port';

				o = ss.taboption('encryption', form.Value, 'auth_secret', _('Radius-Authentication-Secret'));
				add_dependency_permutations(o, { mode: ['ap', 'ap-wds'], encryption: ['wpa', 'wpa2', 'wpa3', 'wpa3-mixed'] });
				o.rmempty = true;
				o.password = true;

				o = ss.taboption('encryption', form.Value, '_wpa_key', _('Key'));
				o.depends('encryption', 'psk');
				o.depends('encryption', 'psk2');
				o.depends('encryption', 'psk+psk2');
				o.depends('encryption', 'psk-mixed');
				o.depends('encryption', 'sae');
				o.depends('encryption', 'sae-mixed');
				o.datatype = 'wpakey';
				o.rmempty = true;
				o.password = true;
				o.cfgvalue = function(section_id) {
					var key = uci.get('wireless', section_id, 'key') || uci.get('wireless', section_id, 'sae_password');
					return /^[1234]$/.test(key) ? null : key;
				};
				o.write = function(section_id, value) {
					uci.set('wireless', section_id, 'key', value);
					uci.set('wireless', section_id, 'sae_password', value);
					uci.unset('wireless', section_id, 'key1');
					uci.unset('wireless', section_id, 'key2');
					uci.unset('wireless', section_id, 'key3');
					uci.unset('wireless', section_id, 'key4');
				};

				o = ss.taboption('encryption', form.ListValue, '_wep_key', _('Used Key Slot'));
				o.depends('encryption', 'wep-open');
				o.depends('encryption', 'wep-shared');
				o.value('1', _('Key #%d').format(1));
				o.value('2', _('Key #%d').format(2));
				o.value('3', _('Key #%d').format(3));
				o.value('4', _('Key #%d').format(4));
				o.cfgvalue = function(section_id) {
					var slot = +uci.get('wireless', section_id, 'key');
					return (slot >= 1 && slot <= 4) ? String(slot) : '';
				};
				o.write = function(section_id, value) {
					uci.set('wireless', section_id, 'key', value);
				};

				for (var slot = 1; slot <= 4; slot++) {
					o = ss.taboption('encryption', form.Value, 'key%d'.format(slot), _('Key #%d').format(slot));
					o.depends('encryption', 'wep-open');
					o.depends('encryption', 'wep-shared');
					o.datatype = 'wepkey';
					o.rmempty = true;
					o.password = true;
					o.write = function(section_id, value) {
						if (value != null && (value.length == 5 || value.length == 13))
							value = 's:%s'.format(value);
						uci.set('wireless', section_id, this.option, value);
					};
				}

				if (is_qca_or_mac) {
					o = ss.taboption('encryption', form.Flag, 'ieee80211r', _('802.11r Fast Transition'), _('Enables fast roaming among access points that belong to the same Mobility Domain'));
					add_dependency_permutations(o, { mode: ['ap', 'ap-wds'], encryption: ['wpa', 'wpa2', 'wpa3', 'wpa3-mixed', 'psk', 'psk2', 'psk-mixed', 'sae', 'sae-mixed'] });
					o.rmempty = true;

					o = ss.taboption('encryption', form.Value, 'mobility_domain', _('Mobility Domain'), _('4-character hexadecimal ID'));
					o.depends({ ieee80211r: '1' });
					o.placeholder = '4f57';
					o.datatype = 'and(hexstring,length(4))';
					o.rmempty = true;

					o = ss.taboption('encryption', form.ListValue, 'ieee80211w', _('802.11w Management Frame Protection'), _('Protects management frames against spoofing and deauthentication attacks.'));
					o.value('0', _('Disabled'));
					o.value('1', _('Optional'));
					o.value('2', _('Required'));
					add_dependency_permutations(o, { mode: ['ap', 'ap-wds', 'sta', 'sta-wds'], encryption: ['owe', 'psk2', 'psk-mixed', 'sae', 'sae-mixed', 'wpa2', 'wpa3', 'wpa3-mixed'] });
					o.defaults = {
						'2': [{ encryption: 'sae' }, { encryption: 'owe' }, { encryption: 'wpa3' }, { encryption: 'wpa3-mixed' }],
						'1': [{ encryption: 'sae-mixed' }],
						'0': []
					};
				}
			});
		};

		s.handleRemove = function(section_id, ev) {
			document.querySelector('.cbi-section-table-row[data-sid="%s"]'.format(section_id)).style.opacity = 0.5;
			return form.TypedSection.prototype.handleRemove.apply(this, [section_id, ev]);
		};

		s.handleScan = function(radioDev, ev) {
			var table = E('div', { 'class': 'table' }, [
				E('div', { 'class': 'tr table-titles' }, [
					E('div', { 'class': 'th col-2 middle center' }, _('Signal')),
					E('div', { 'class': 'th col-4 middle left' }, _('SSID')),
					E('div', { 'class': 'th col-2 middle center hide-xs' }, _('Channel / Width')),
					E('div', { 'class': 'th col-2 middle left hide-xs' }, _('Mode')),
					E('div', { 'class': 'th col-3 middle left hide-xs' }, _('BSSID')),
					E('div', { 'class': 'th col-3 middle left' }, _('Encryption')),
					E('div', { 'class': 'th cbi-section-actions right' }, ' ')
				])
			]);

			var stop = E('button', {
				'class': 'btn',
				'click': L.bind(this.handleScanStartStop, this),
				'style': 'display:none',
				'data-state': 'stop'
			}, _('Stop refresh'));

			cbi_update_table(table, [], E('em', { class: 'spinning' }, _('Starting wireless scan...')));

			var md = ui.showModal(_('Join Network: Wireless Scan'), [
				table,
				E('div', { 'class': 'right' }, [
					stop,
					' ',
					E('button', {
						'class': 'btn',
						'click': L.bind(this.handleScanAbort, this)
					}, _('Dismiss'))
				])
			]);

			md.style.maxWidth = '90%';
			md.style.maxHeight = 'none';

			this.pollFn = L.bind(this.handleScanRefresh, this, radioDev, {}, table, stop);
			poll.add(this.pollFn);
			poll.start();
		};

		s.handleScanRefresh = function(radioDev, scanCache, table, stop) {
			return radioDev.getScanList().then(L.bind(function(results) {
				var rows = [];
				for (var i = 0; i < results.length; i++)
					scanCache[results[i].bssid] = results[i];

				for (var k in scanCache)
					if (scanCache[k].stale)
						results.push(scanCache[k]);

				results.sort(function(a, b) {
					var diff = (b.quality - a.quality) || (a.channel - b.channel);
					if (diff)
						return diff;
					if (a.ssid < b.ssid)
						return -1;
					else if (a.ssid > b.ssid)
						return 1;
					if (a.bssid < b.bssid)
						return -1;
					else if (a.bssid > b.bssid)
						return 1;
				});

				for (var i = 0; i < results.length; i++) {
					var res = results[i],
					    qv = res.quality || 0,
					    qm = res.quality_max || 0,
					    q = (qv > 0 && qm > 0) ? Math.floor((100 / qm) * qv) : 0,
					    s = res.stale ? 'opacity:0.5' : '',
					    chInfo = res.bw ? '%d (%s%s)'.format(res.channel, res.bw, res.gen ? ' • ' + res.gen : '') : '%d'.format(res.channel);

					rows.push([
						E('span', { 'style': s }, render_signal_badge(q, res.signal, res.noise)),
						E('span', { 'style': s }, (res.ssid != null) ? '%h'.format(res.ssid) : E('em', _('hidden'))),
						E('span', { 'style': s }, chInfo),
						E('span', { 'style': s }, '%h'.format(res.mode)),
						E('span', { 'style': s }, '%h'.format(res.bssid)),
						E('span', { 'style': s }, '%h'.format(network.formatWifiEncryption(res.encryption))),
						E('div', { 'class': 'right' }, E('button', {
							'class': 'cbi-button cbi-button-action important',
							'click': L.bind(this.handleJoin, this, radioDev, res)
						}, _('Join Network')))
					]);
					res.stale = true;
				}

				cbi_update_table(table, rows, E('em', _('No wireless networks found on this band')));
				stop.disabled = false;
				stop.style.display = '';
				stop.classList.remove('spinning');
			}, this));
		};

		s.handleScanStartStop = function(ev) {
			var btn = ev.currentTarget;
			if (btn.getAttribute('data-state') == 'stop') {
				poll.remove(this.pollFn);
				btn.firstChild.data = _('Start refresh');
				btn.setAttribute('data-state', 'start');
			}
			else {
				poll.add(this.pollFn);
				btn.firstChild.data = _('Stop refresh');
				btn.setAttribute('data-state', 'stop');
				btn.classList.add('spinning');
				btn.disabled = true;
			}
		};

		s.handleScanAbort = function(ev) {
			var md = dom.parent(ev.target, 'div[aria-modal="true"]');
			if (md) {
				md.style.maxWidth = '';
				md.style.maxHeight = '';
			}
			ui.hideModal();
			poll.remove(this.pollFn);
			this.pollFn = null;
		};

		s.handleJoinConfirm = function(radioDev, bss, form, ev) {
			var nameopt = L.toArray(form.lookupOption('name', '_new_'))[0],
			    passopt = L.toArray(form.lookupOption('password', '_new_'))[0],
			    bssidopt = L.toArray(form.lookupOption('bssid', '_new_'))[0],
			    zoneopt = L.toArray(form.lookupOption('zone', '_new_'))[0],
			    replopt = L.toArray(form.lookupOption('replace', '_new_'))[0],
			    nameval = (nameopt && nameopt.isValid('_new_')) ? nameopt.formvalue('_new_') : null,
			    passval = (passopt && passopt.isValid('_new_')) ? passopt.formvalue('_new_') : null,
			    bssidval = (bssidopt && bssidopt.isValid('_new_')) ? bssidopt.formvalue('_new_') : null,
			    zoneval = zoneopt ? zoneopt.formvalue('_new_') : null,
			    enc = L.isObject(bss.encryption) ? bss.encryption : null,
			    is_wep = (enc && Array.isArray(enc.wep)),
			    is_psk = (enc && Array.isArray(enc.wpa) && L.toArray(enc.authentication).filter(function(a) { return a == 'psk'; }).length > 0),
			    is_sae = (enc && Array.isArray(enc.wpa) && L.toArray(enc.authentication).filter(function(a) { return a == 'sae'; }).length > 0);

			if (nameval == null || (passopt && passval == null))
				return;

			var section_id = null;
			return this.map.save(function() {
				var wifi_sections = uci.sections('wireless', 'wifi-iface');
				if (replopt.formvalue('_new_') == '1') {
					for (var i = 0; i < wifi_sections.length; i++)
						if (wifi_sections[i].device == radioDev.getName())
							uci.remove('wireless', wifi_sections[i]['.name']);
				}
				if (uci.get('wireless', radioDev.getName(), 'disabled') == '1') {
					for (var i = 0; i < wifi_sections.length; i++)
						if (wifi_sections[i].device == radioDev.getName())
							uci.set('wireless', wifi_sections[i]['.name'], 'disabled', '1');
					uci.unset('wireless', radioDev.getName(), 'disabled');
				}
				uci.set('wireless', radioDev.getName(), 'vap_diff_mode', '1');

				section_id = next_free_sid(wifi_sections.length);
				uci.add('wireless', 'wifi-iface', section_id);
				uci.set('wireless', section_id, 'device', radioDev.getName());
				uci.set('wireless', section_id, 'mode', (bss.mode == 'Ad-Hoc') ? 'adhoc' : 'sta');
				uci.set('wireless', section_id, 'wds', '1');
				uci.set('wireless', section_id, 'network', nameval);

				if (bss.ssid != null) {
					uci.set('wireless', section_id, 'ssid', bss.ssid);
					if (bssidval == '1')
						uci.set('wireless', section_id, 'bssid', bss.bssid);
				}
				else if (bss.bssid != null) {
					uci.set('wireless', section_id, 'bssid', bss.bssid);
				}

				if (is_sae) {
					uci.set('wireless', section_id, 'encryption', 'sae');
					uci.set('wireless', section_id, 'sae', '1');
					uci.set('wireless', section_id, 'ieee80211w', '2');
					uci.set('wireless', section_id, 'key', passval);
					uci.set('wireless', section_id, 'sae_password', passval);
				}
				else if (is_psk) {
					for (var i = enc.wpa.length - 1; i >= 0; i--) {
						if (enc.wpa[i] == 2) {
							uci.set('wireless', section_id, 'encryption', 'psk2+aes');
							break;
						}
						else if (enc.wpa[i] == 1) {
							uci.set('wireless', section_id, 'encryption', 'psk');
							break;
						}
					}
					uci.set('wireless', section_id, 'key', passval);
					uci.set('wireless', section_id, 'sae_password', passval);
				}
				else if (is_wep) {
					uci.set('wireless', section_id, 'encryption', 'wep-open');
					uci.set('wireless', section_id, 'key', '1');
					uci.set('wireless', section_id, 'key1', passval);
				}
				else {
					uci.set('wireless', section_id, 'encryption', 'none');
				}

				return network.addNetwork(nameval, { proto: 'dhcp' }).then(function(net) {
					firewall.deleteNetwork(net.getName());
					var zonePromise = zoneval
						? firewall.getZone(zoneval).then(function(zone) { return zone || firewall.addZone(zoneval); })
						: Promise.resolve();
					return zonePromise.then(function(zone) {
						if (zone)
							zone.addNetwork(net.getName());
					});
				});
			}).then(L.bind(function() {
				return this.renderMoreOptionsModal(section_id);
			}, this));
		};

		s.handleJoin = function(radioDev, bss, ev) {
			this.handleScanAbort(ev);
			var m2 = new form.Map('wireless'),
			    s2 = m2.section(form.NamedSection, '_new_'),
			    enc = L.isObject(bss.encryption) ? bss.encryption : null,
			    is_wep = (enc && Array.isArray(enc.wep)),
			    is_psk = (enc && Array.isArray(enc.wpa) && L.toArray(enc.authentication).filter(function(a) { return a == 'psk' || a == 'sae'; }).length > 0),
			    replace, passphrase, name, bssid, zone;

			var nameUsed = function(name) {
				var s = uci.get('network', name);
				if (s != null && s['.type'] != 'interface')
					return true;
				var net = (s != null) ? network.instantiateNetwork(name) : null;
				return (net != null && !net.isEmpty());
			};

			s2.render = function() {
				return Promise.all([{}, this.renderUCISection('_new_')]).then(this.renderContents.bind(this));
			};

			replace = s2.option(form.Flag, 'replace', _('Replace wireless configuration'), _('Check this option to delete the existing networks from this radio.'));

			name = s2.option(form.Value, 'name', _('Name of the new network'), _('The allowed characters are: <code>A-Z</code>, <code>a-z</code>, <code>0-9</code> and <code>_</code>'));
			name.datatype = 'uciname';
			name.default = 'wwan';
			name.rmempty = false;
			name.validate = function(section_id, value) {
				if (nameUsed(value))
					return _('The network name is already used');
				return true;
			};
			for (var i = 2; nameUsed(name.default); i++)
				name.default = 'wwan%d'.format(i);

			if (is_wep || is_psk) {
				passphrase = s2.option(form.Value, 'password', is_wep ? _('WEP passphrase') : _('WPA passphrase'), _('Specify the secret encryption key here.'));
				passphrase.datatype = is_wep ? 'wepkey' : 'wpakey';
				passphrase.password = true;
				passphrase.rmempty = false;
			}

			if (bss.ssid != null) {
				bssid = s2.option(form.Flag, 'bssid', _('Lock to BSSID'), _('Instead of joining any network with a matching SSID, only connect to the BSSID <code>%h</code>.').format(bss.bssid));
				bssid.default = '0';
			}

			zone = s2.option(widgets.ZoneSelect, 'zone', _('Create / Assign firewall-zone'), _('Choose the firewall zone you want to assign to this interface. Select <em>unspecified</em> to remove the interface from the associated zone or fill out the <em>custom</em> field to define a new zone and attach the interface to it.'));
			zone.default = 'wan';

			return m2.render().then(L.bind(function(nodes) {
				ui.showModal(_('Joining Network: %q').replace(/%q/, '"%h"'.format(bss.ssid)), [
					nodes,
					E('div', { 'class': 'right' }, [
						E('button', { 'class': 'btn', 'click': ui.hideModal }, _('Cancel')),
						' ',
						E('button', {
							'class': 'cbi-button cbi-button-positive important',
							'click': ui.createHandlerFn(this, 'handleJoinConfirm', radioDev, bss, m2)
						}, _('Submit'))
					])
				], 'cbi-modal').querySelector('[id="%s"] input[class][type]'.format((passphrase || name).cbid('_new_'))).focus();
			}, this));
		};

		s.handleAdd = function(radioDev, ev) {
			var rname = radioDev.getName(),
			    section_id = next_free_sid(uci.sections('wireless', 'wifi-iface').length);
			uci.unset('wireless', rname, 'disabled');
			uci.add('wireless', 'wifi-iface', section_id);
			uci.set('wireless', section_id, 'device', rname);
			uci.set('wireless', section_id, 'mode', 'ap');
			uci.set('wireless', section_id, 'wds', '1');
			uci.set('wireless', section_id, 'network', 'lan');
			uci.set('wireless', section_id, 'ssid', 'Predator_7G_Extra');
			if (rname == 'wifi2') {
				uci.set('wireless', section_id, 'encryption', 'sae');
				uci.set('wireless', section_id, 'sae', '1');
				uci.set('wireless', section_id, 'ieee80211w', '2');
			}
			else {
				uci.set('wireless', section_id, 'encryption', 'psk2+aes');
			}
			this.addedSection = section_id;
			return this.renderMoreOptionsModal(section_id);
		};

		o = s.option(form.DummyValue, '_badge');
		o.modalonly = false;
		o.textvalue = function(section_id) {
			var inst = this.section.lookupRadioOrNetwork(section_id),
			    node = E('div', { 'class': 'center' });
			if (inst.getWifiNetworks)
				node.appendChild(render_radio_badge(inst));
			else
				node.appendChild(render_network_badge(inst));
			return node;
		};

		o = s.option(form.DummyValue, '_stat');
		o.modalonly = false;
		o.textvalue = function(section_id) {
			var inst = this.section.lookupRadioOrNetwork(section_id);
			if (inst.getWifiNetworks)
				return render_radio_status(inst, this.section.wifis.filter(function(e) { return (e.getWifiDeviceName() == inst.getName()); }));
			else
				return render_network_status(inst);
		};

		return m.render().then(L.bind(function(m, nodes) {
			poll.add(L.bind(function() {
				var section_ids = m.children[0].cfgsections(),
				    tasks = [network.getHostHints(), network.getWifiDevices()];

				for (var i = 0; i < section_ids.length; i++) {
					var row = nodes.querySelector('.cbi-section-table-row[data-sid="%s"]'.format(section_ids[i]));
					if (!row) continue;
					var dsc = row.querySelector('[data-name="_stat"] > div'),
					    btns = row.querySelectorAll('.cbi-section-actions button');
					if (dsc && dsc.getAttribute('restart') == '') {
						dsc.setAttribute('restart', '1');
						tasks.push(callPredatorWifiAction('restart_radio', section_ids[i], '').catch(function(e) {
							ui.addNotification(null, E('p', e.message));
						}));
					}
					else if (dsc && dsc.getAttribute('restart') == '1') {
						dsc.removeAttribute('restart');
						btns[0].classList.remove('spinning');
						btns[0].disabled = false;
					}
				}

				return Promise.all(tasks).then(L.bind(function(hosts_radios) {
					var tasks = [];
					for (var i = 0; i < hosts_radios[1].length; i++)
						tasks.push(hosts_radios[1][i].getWifiNetworks());
					return Promise.all(tasks).then(function(data) {
						hosts_radios[2] = [];
						for (var i = 0; i < data.length; i++)
							hosts_radios[2].push.apply(hosts_radios[2], data[i]);
						return hosts_radios;
					});
				}, network)).then(L.bind(function(hosts_radios_wifis) {
					var tasks = [];
					for (var i = 0; i < hosts_radios_wifis[2].length; i++)
						tasks.push(hosts_radios_wifis[2][i].getAssocList());
					return Promise.all(tasks).then(function(data) {
						hosts_radios_wifis[3] = [];
						for (var i = 0; i < data.length; i++) {
							var wifiNetwork = hosts_radios_wifis[2][i],
							    radioDev = hosts_radios_wifis[1].filter(function(d) { return d.getName() == wifiNetwork.getWifiDeviceName(); })[0];
							for (var j = 0; j < data[i].length; j++)
								hosts_radios_wifis[3].push(Object.assign({ radio: radioDev, network: wifiNetwork }, data[i][j]));
						}
						return hosts_radios_wifis;
					});
				}, network)).then(L.bind(this.poll_status, this, nodes));
			}, this), 5);

			var table = E('div', { 'class': 'table assoclist', 'id': 'wifi_assoclist_table' }, [
				E('div', { 'class': 'tr table-titles' }, [
					E('div', { 'class': 'th nowrap' }, _('Network')),
					E('div', { 'class': 'th hide-xs' }, _('MAC-Address')),
					E('div', { 'class': 'th' }, _('Host')),
					E('div', { 'class': 'th' }, _('Signal / Noise')),
					E('div', { 'class': 'th' }, _('RX Rate / TX Rate'))
				])
			]);

			cbi_update_table(table, [], E('em', { 'class': 'spinning' }, _('Collecting data...')));
			return E([nodes, E('h3', _('Associated Stations')), table]);
		}, this, m));
	}
});