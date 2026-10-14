'use strict';
'require view';
'require fs';
'require ui';
'require poll';

function formatBytes(bytes) {
	var b = parseInt(bytes) || 0;
	if (b >= 1073741824) return (b / 1073741824).toFixed(2) + ' GB';
	if (b >= 1048576) return (b / 1048576).toFixed(1) + ' MB';
	if (b >= 1024) return (b / 1024).toFixed(0) + ' KB';
	return b + ' B';
}

function formatUptime(seconds) {
	var sec = parseInt(seconds) || 0;
	if (sec < 60) return sec + 's';
	var min = Math.floor(sec / 60);
	var h = Math.floor(min / 60);
	if (h > 0) return h + 'h ' + (min % 60) + 'm';
	return min + 'm ' + (sec % 60) + 's';
}

return view.extend({
	// Suprime a barra confusa e redundante de "Salvar e Aplicar"
	handleSaveApply: null,
	handleSave: null,
	handleReset: null,

	statusCardNode: null,
	scanTableContainer: null,
	networkCounterNode: null,
	rawNetworks: [],
	currentFilter: '',
	currentSort: 'signal',

	load: function() {
		return Promise.all([
			fs.exec('/usr/sbin/wifi-wisp-tool', ['status']),
			fs.exec('/usr/sbin/wifi-wisp-tool', ['scan'])
		]).catch(function(err) {
			return [{ stdout: '{"connected":false,"state":"error"}' }, { stdout: '{"networks":[]}' }];
		});
	},

	render: function(data) {
		var self = this;
		var statusData = {};
		var scanData = { networks: [] };

		try {
			var txt0 = (data[0].stdout || '').trim();
			var idx0 = txt0.indexOf('{');
			if (idx0 !== -1) statusData = JSON.parse(txt0.substring(idx0));
		} catch(e) {}
		try {
			var txt1 = (data[1].stdout || '').trim();
			var idx1 = txt1.indexOf('{');
			if (idx1 !== -1) scanData = JSON.parse(txt1.substring(idx1));
		} catch(e) {}

		this.rawNetworks = scanData.networks || [];

		var m = E('div', { 'class': 'cbi-map' });

		// Título e Introdução
		m.appendChild(E('h2', {}, _('Wi-Fi como WAN / Repetidor Inteligente (WISP)')));
		m.appendChild(E('div', { 'class': 'cbi-map-descr' }, 
			_('Conecte o seu Acer Predator T7 a qualquer rede Wi-Fi externa (roteador da operadora, hotspot 4G/5G do celular ou rede de eventos) para usá-la como link de Internet. A sua rede local (GAMER_7G), o DHCP interno, o compartilhamento KSMBD e o Firewall continuam 100% protegidos e operacionais sem risco de colapso.')
		));

		// Card de Status Ativo
		this.statusCardNode = E('div', { 'class': 'cbi-section', 'id': 'wisp-status-card' });
		this.renderStatusCard(this.statusCardNode, statusData);
		m.appendChild(this.statusCardNode);

		// Seção de Redes Disponíveis
		var scanSection = E('div', { 'class': 'cbi-section' });
		var scanHeader = E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:15px;' }, [
			E('h3', { 'style': 'margin:0;' }, _('Redes Wi-Fi no Espectro')),
			E('div', {}, [
				E('button', {
					'class': 'cbi-button cbi-button-neutral',
					'style': 'margin-right:10px;',
					'click': ui.createHandlerFn(this, 'openHiddenNetworkModal')
				}, _('➕ Conectar a Rede Oculta (Manual)')),
				E('button', {
					'class': 'cbi-button cbi-button-action',
					'id': 'btn-rescan',
					'click': ui.createHandlerFn(this, 'handleRescan')
				}, _('🔍 Atualizar / Escanear Novamente'))
			])
		]);
		scanSection.appendChild(scanHeader);

		// Barra de Filtro e Ordenação Avançada
		var inputFilter = E('input', {
			'type': 'text',
			'class': 'cbi-input-text',
			'placeholder': _('🔍 Filtrar rede por nome ou BSSID...'),
			'style': 'width:240px; font-size:13px; padding:6px 10px;'
		});

		var selectSort = E('select', {
			'class': 'cbi-input-select',
			'style': 'font-size:13px; padding:6px 10px;'
		}, [
			E('option', { 'value': 'signal' }, _('📶 Melhor Sinal (Padrão)')),
			E('option', { 'value': 'alpha' }, _('🔤 Ordem Alfabética (A-Z)')),
			E('option', { 'value': 'grouped' }, _('🔗 Agrupar Redes Iguais (Mesmo Nome / Vários Canais)')),
			E('option', { 'value': 'band' }, _('📡 5 GHz / 6 GHz Primeiro'))
		]);

		this.networkCounterNode = E('span', {
			'style': 'font-size:12px; color:#7f8c8d; margin-left:8px;'
		});

		inputFilter.addEventListener('input', function() {
			self.currentFilter = this.value;
			self.updateScanTable();
		});

		selectSort.addEventListener('change', function() {
			self.currentSort = this.value;
			self.updateScanTable();
		});

		var toolbar = E('div', {
			'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:15px; padding:10px 14px; background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px;'
		}, [
			E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
				E('strong', { 'style': 'font-size:13px; color:#495057;' }, _('Filtro:')),
				inputFilter,
				this.networkCounterNode
			]),
			E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
				E('strong', { 'style': 'font-size:13px; color:#495057;' }, _('Ordenar por:')),
				selectSort
			])
		]);
		scanSection.appendChild(toolbar);

		// Container da Tabela
		this.scanTableContainer = E('div', { 'id': 'wisp-scan-table' });
		scanSection.appendChild(this.scanTableContainer);
		m.appendChild(scanSection);

		this.updateScanTable();

		// Polling dinâmico do status a cada 3 segundos
		poll.add(function() {
			if (document.hidden)
				return Promise.resolve();

			return fs.exec('/usr/sbin/wifi-wisp-tool', ['status']).then(function(res) {
				var s = {};
				try {
					var txt = (res.stdout || '').trim();
					var idx = txt.indexOf('{');
					if (idx !== -1) s = JSON.parse(txt.substring(idx));
				} catch(e) {}
				if (self.statusCardNode) {
					self.renderStatusCard(self.statusCardNode, s);
				}
			}).catch(function() {});
		}, 3);

		return m;
	},

	getProcessedNetworks: function() {
		var list = (this.rawNetworks || []).slice();
		var filter = (this.currentFilter || '').toLowerCase().trim();

		if (filter) {
			list = list.filter(function(n) {
				return (n.ssid && n.ssid.toLowerCase().indexOf(filter) !== -1) ||
				       (n.bssid && n.bssid.toLowerCase().indexOf(filter) !== -1) ||
				       (n.channel && String(n.channel) === filter);
			});
		}

		var sort = this.currentSort || 'signal';

		if (sort === 'alpha') {
			list.sort(function(a, b) {
				var cmp = (a.ssid || '').localeCompare(b.ssid || '', undefined, { sensitivity: 'base' });
				if (cmp !== 0) return cmp;
				return (b.quality || 0) - (a.quality || 0);
			});
		} else if (sort === 'grouped') {
			list.sort(function(a, b) {
				var nameA = (a.ssid || '').toLowerCase();
				var nameB = (b.ssid || '').toLowerCase();
				if (nameA < nameB) return -1;
				if (nameA > nameB) return 1;
				if ((b.freq || 0) !== (a.freq || 0)) return (b.freq || 0) - (a.freq || 0);
				if ((a.channel || 0) !== (b.channel || 0)) return (a.channel || 0) - (b.channel || 0);
				return (b.quality || 0) - (a.quality || 0);
			});
		} else if (sort === 'band') {
			list.sort(function(a, b) {
				if ((b.freq || 0) !== (a.freq || 0)) return (b.freq || 0) - (a.freq || 0);
				return (b.quality || 0) - (a.quality || 0);
			});
		} else {
			list.sort(function(a, b) {
				return (b.quality || 0) - (a.quality || 0);
			});
		}

		return list;
	},

	updateScanTable: function() {
		if (!this.scanTableContainer) return;

		var networks = this.getProcessedNetworks();

		if (this.networkCounterNode) {
			this.networkCounterNode.innerText = _('(%d de %d redes)').format(networks.length, this.rawNetworks.length);
		}

		this.renderScanTable(this.scanTableContainer, networks);
	},

	renderStatusCard: function(container, s) {
		container.innerHTML = '';
		var self = this;

		var isConnected = (s.connected === true);
		var headerColor = isConnected ? '#2ecc71' : '#7f8c8d';
		var statusText = isConnected ? _('CONECTADO (Link de Internet Ativo via Wi-Fi)') : _('DESCONECTADO (Internet via Cabo Ethernet ou Offline)');

		var badgeBg = '#7f8c8d';
		var badgeText = 'OFFLINE';

		if (isConnected) {
			if (s.internet_online) {
				badgeBg = '#27ae60';
				badgeText = 'INTERNET ONLINE';
			} else if (s.captive_portal) {
				badgeBg = '#f39c12';
				badgeText = 'PORTAL DE ACESSO';
			} else {
				badgeBg = '#2980b9';
				badgeText = 'LINK ATIVO';
			}
		}

		var box = E('div', {
			'style': 'border:2px solid ' + (isConnected ? '#27ae60' : '#bdc3c7') + '; border-radius:8px; padding:18px; background: rgba(46, 204, 113, 0.04);'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;' }, [
				E('div', {}, [
					E('span', {
						'style': 'background:' + badgeBg + '; color:#fff; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:12px; margin-right:10px;'
					}, badgeText),
					E('strong', { 'style': 'font-size:16px;' }, statusText)
				]),
				isConnected ? E('button', {
					'class': 'cbi-button cbi-button-remove',
					'click': ui.createHandlerFn(this, 'handleDisconnect')
				}, _('🔌 Desconectar e Reverter para Cabo')) : ''
			])
		]);

		if (isConnected) {
			var details = E('div', {
				'style': 'display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-top:16px; padding-top:16px; border-top:1px dashed #ccc;'
			}, [
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Rede Conectada (SSID): ')), E('br'), E('strong', { 'style': 'font-size:14px;' }, s.ssid) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Ponto de Acesso (BSSID): ')), E('br'), E('strong', { 'style': 'font-family:monospace; font-size:13px;' }, s.bssid || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Banda / Frequência: ')), E('br'), E('strong', {}, (s.band || '-') + (s.channel ? ' (Canal ' + s.channel + ' - ' + s.freq + ' MHz)' : '')) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('IP da WAN Recebido: ')), E('br'), E('strong', { 'style': 'color:#2980b9; font-size:14px;' }, s.ip + (s.netmask ? ' /' + s.netmask : '')) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Gateway Padrão: ')), E('br'), E('strong', {}, s.gateway || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Servidores DNS: ')), E('br'), E('strong', {}, s.dns || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Sinal do Link: ')), E('br'), E('strong', { 'style': 'color:#27ae60;' }, s.signal + ' (' + s.quality + '%)') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Latência na Internet: ')), E('br'), E('strong', { 'style': 'color:#16a085;' }, (s.ping || '-') + ' (Ping 1.1.1.1)') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Velocidade TX (PHY Rate): ')), E('br'), E('strong', { 'style': 'color:#8e44ad;' }, s.tx_rate || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Velocidade RX (PHY Rate): ')), E('br'), E('strong', { 'style': 'color:#2980b9;' }, s.rx_rate || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Tráfego Transferido: ')), E('br'), E('strong', { 'style': 'font-size:12px;' }, '⬇️ ' + formatBytes(s.rx_bytes) + ' | ⬆️ ' + formatBytes(s.tx_bytes)) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Tempo Conectado: ')), E('br'), E('strong', {}, formatUptime(s.uptime)) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Rádio Físico / Interface: ')), E('br'), E('strong', {}, (s.device || '-') + (s.sta_iface ? ' (' + s.sta_iface + ')' : '')) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, _('Prioridade de Rota: ')), E('br'), E('span', { 'style': 'font-size:12px; color:#555;' }, _('Métrica 20 (Cabo prevalece automaticamente se plugado)')) ])
			]);
			box.appendChild(details);

			// Alerta de Captive Portal
			if (s.captive_portal) {
				box.appendChild(E('div', { 'class': 'alert-message warning', 'style': 'margin-top:15px;' }, [
					E('strong', {}, _('Atenção - Portal de Autenticação Detectado: ')),
					_('O roteador está associado ao Wi-Fi externo, mas a rede requer aceite de termos ou login. Abra o navegador em qualquer celular ou computador conectado ao T7 para completar a liberação.')
				]));
			}

			// Alerta e Resolução de Conflito de Sub-rede
			if (s.conflict_detected) {
				var conflictBox = E('div', { 'class': 'alert-message error', 'style': 'margin-top:15px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;' }, [
					E('div', {}, [
						E('strong', {}, _('CONFLITO DE SUB-REDE DETECTADO: ')),
						E('p', { 'style': 'margin:4px 0 0 0;' }, _('A rede Wi-Fi externa forneceu um IP na mesma faixa da sua rede local (192.168.76.x). Isso pode travar a navegação. Clique ao lado para mover a sua rede local para 192.168.77.1 automaticamente.'))
					]),
					E('button', {
						'class': 'cbi-button cbi-button-action',
						'click': ui.createHandlerFn(self, 'handleFixConflict')
					}, _('🛠️ Corrigir Conflito Agora (Mudar LAN para 192.168.77.1)'))
				]);
				box.appendChild(conflictBox);
			}
		} else {
			box.appendChild(E('p', { 'style': 'margin:12px 0 0 0; color:#666;' }, 
				s.message || _('Nenhuma rede Wi-Fi externa conectada. Escolha uma das redes abaixo ou clique em "Conectar a Rede Oculta" para usar um hotspot como saída de internet.')
			));
		}

		container.appendChild(box);
	},

	renderScanTable: function(container, networks) {
		container.innerHTML = '';

		if (!networks || networks.length === 0) {
			container.appendChild(E('div', { 'class': 'alert-message notice' }, 
				_('Nenhuma rede Wi-Fi corresponde aos critérios no momento. Clique em "Atualizar / Escanear Novamente" para varrer o espectro.')
			));
			return;
		}

		var table = E('table', { 'class': 'table' }, [
			E('tr', { 'class': 'tr table-titles' }, [
				E('th', { 'class': 'th', 'style': 'width:80px;' }, _('Sinal')),
				E('th', { 'class': 'th' }, _('Nome da Rede (SSID)')),
				E('th', { 'class': 'th' }, _('Banda / Canal')),
				E('th', { 'class': 'th' }, _('Segurança')),
				E('th', { 'class': 'th', 'style': 'width:180px; text-align:right;' }, _('Ação'))
			])
		]);

		var self = this;
		var lastSsid = null;

		networks.forEach(function(net) {
			var sigColor = '#27ae60';
			if (net.quality < 35) sigColor = '#e74c3c';
			else if (net.quality < 65) sigColor = '#f39c12';

			var isSelf = (net.is_self === true);
			var isDuplicateName = (lastSsid && lastSsid.toLowerCase() === (net.ssid || '').toLowerCase());
			lastSsid = net.ssid;

			var actionBtn;
			if (isSelf) {
				actionBtn = E('span', {
					'class': 'label',
					'style': 'background:#e74c3c; color:#fff; padding:5px 8px; border-radius:4px; font-size:11px; white-space:nowrap;'
				}, _('⚠️ Própria Rede (Loop Bloqueado)'));
			} else {
				actionBtn = E('button', {
					'class': 'cbi-button cbi-button-apply',
					'click': ui.createHandlerFn(self, 'openConnectModal', net)
				}, _('Conectar'));
			}

			var row = E('tr', { 'class': 'tr', 'style': isDuplicateName ? 'background: rgba(41, 128, 185, 0.03);' : '' }, [
				E('td', { 'class': 'td' }, [
					E('div', { 'style': 'display:flex; align-items:center;' }, [
						E('div', {
							'style': 'width:12px; height:12px; border-radius:50%; background:' + sigColor + '; margin-right:8px;'
						}),
						E('span', {}, net.quality + '%')
					])
				]),
				E('td', { 'class': 'td' }, [
					E('strong', {}, net.ssid),
					isDuplicateName ? E('span', {
						'class': 'badge',
						'style': 'background:#2980b9; color:#fff; font-size:10px; margin-left:8px;'
					}, _('🔗 Mesmo Wi-Fi (Canal Diferente)')) : '',
					net.bssid ? E('div', { 'style': 'font-size:11px; color:#7f8c8d; font-family:monospace; margin-top:2px;' }, 'BSSID: ' + net.bssid) : '',
					isSelf ? E('span', { 'style': 'color:#e74c3c; font-size:12px; margin-left:8px;' }, _('(Rede interna do seu T7)')) : ''
				]),
				E('td', { 'class': 'td' }, [
					E('span', { 'class': 'badge' }, net.band),
					E('span', { 'style': 'margin-left:6px; color:#666;' }, '(Canal ' + net.channel + ')')
				]),
				E('td', { 'class': 'td' }, net.encryption),
				E('td', { 'class': 'td', 'style': 'text-align:right;' }, actionBtn)
			]);

			table.appendChild(row);
		});

		container.appendChild(table);
	},

	openConnectModal: function(net) {
		var self = this;

		var selectEnc = E('select', {
			'class': 'cbi-input-select',
			'style': 'width:100%; font-size:14px; padding:6px;'
		}, [
			E('option', { 'value': 'WPA2-PSK' }, _('WPA2-PSK (Padrão mais comum)')),
			E('option', { 'value': 'WPA3-SAE' }, _('WPA3-SAE (Wi-Fi 6E / Wi-Fi 7)')),
			E('option', { 'value': 'WPA2/WPA3' }, _('WPA2/WPA3 Misto')),
			E('option', { 'value': 'Aberta' }, _('Aberta (Sem Senha)'))
		]);

		if (net.encryption === 'WPA3-SAE' || net.encryption === 'sae') selectEnc.value = 'WPA3-SAE';
		else if (net.encryption === 'Aberta' || net.encryption === 'none') selectEnc.value = 'Aberta';
		else if (net.encryption === 'WPA2/WPA3') selectEnc.value = 'WPA2/WPA3';
		else selectEnc.value = 'WPA2-PSK';

		var isInitiallyOpen = (selectEnc.value === 'Aberta');

		var inputKey = E('input', {
			'type': 'password',
			'class': 'cbi-input-text',
			'placeholder': isInitiallyOpen ? _('Rede aberta (sem senha)') : _('Digite a senha da rede (mínimo 8 caracteres)'),
			'autocomplete': 'new-password',
			'style': 'width:100%; font-size:14px; padding:8px;'
		});

		if (isInitiallyOpen) {
			inputKey.disabled = true;
		}

		var checkShowPass = E('input', {
			'type': 'checkbox',
			'style': 'margin-right:6px;',
			'change': function() {
				inputKey.type = this.checked ? 'text' : 'password';
			}
		});

		var checkLockBssid = E('input', {
			'type': 'checkbox',
			'checked': true,
			'style': 'margin-right:8px;'
		});

		var errBox = E('div', {
			'style': 'color:#e74c3c; font-weight:bold; margin-top:8px; display:none;'
		});

		selectEnc.addEventListener('change', function() {
			var isNowOpen = (this.value === 'Aberta');
			inputKey.disabled = isNowOpen;
			inputKey.placeholder = isNowOpen ? _('Rede aberta (sem senha)') : _('Digite a senha da rede (mínimo 8 caracteres)');
			if (isNowOpen) {
				inputKey.value = '';
				errBox.style.display = 'none';
			} else {
				inputKey.focus();
			}
		});

		var btnSubmit = E('button', {
			'class': 'cbi-button cbi-button-apply',
			'click': function() {
				var key = inputKey.value;
				var chosenEnc = selectEnc.value;
				var isChosenOpen = (chosenEnc === 'Aberta');

				if (!isChosenOpen && (!key || key.length < 8)) {
					errBox.innerText = _('Trava de Segurança: A senha do Wi-Fi deve ter no mínimo 8 caracteres.');
					errBox.style.display = 'block';
					inputKey.focus();
					return;
				}

				var bssidArg = (checkLockBssid.checked && net.bssid) ? net.bssid : '';

				self.startConnectionProgress(net.ssid, key, chosenEnc, net.band, bssidArg);
			}
		}, _('Conectar e Testar Link'));

		var modalContent = E('div', {}, [
			E('div', { 'style': 'background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px; padding:12px; margin-bottom:15px;' }, [
				E('div', { 'style': 'font-size:15px; margin-bottom:4px;' }, [
					_('Rede Alvo: '),
					E('strong', { 'style': 'font-size:16px; color:#2980b9;' }, net.ssid)
				]),
				E('div', { 'style': 'font-size:12px; color:#666; display:flex; gap:15px; flex-wrap:wrap;' }, [
					E('span', {}, '📡 ' + net.band + ' (Canal ' + net.channel + ')'),
					net.bssid ? E('span', { 'style': 'font-family:monospace;' }, '📍 BSSID: ' + net.bssid) : '',
					E('span', {}, '📶 Sinal: ' + net.quality + '% (' + net.signal + ' dBm)')
				])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Tipo de Segurança:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectEnc ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Senha do Wi-Fi:')),
				E('div', { 'class': 'cbi-value-field' }, [
					inputKey,
					E('div', { 'style': 'margin-top:6px;' }, [
						E('label', {}, [ checkShowPass, _('Mostrar senha digitada') ])
					]),
					errBox
				])
			]),
			net.bssid ? E('div', { 'class': 'cbi-value', 'style': 'margin-top:12px; padding:10px; background:#fdfefe; border:1px dashed #bdc3c7; border-radius:6px;' }, [
				E('label', { 'style': 'cursor:pointer; display:flex; align-items:flex-start;' }, [
					checkLockBssid,
					E('div', {}, [
						E('strong', {}, _('Fixar conexão neste ponto de acesso específico (BSSID)')),
						E('div', { 'style': 'font-size:11px; color:#7f8c8d; margin-top:2px;' }, 
							_('Marcado (Recomendado): Fixa o roteador neste rádio exato para garantir que ele permaneça na frequência e canal escolhidos. Desmarque se esta rede possuir repetidores/mesh e você preferir que o T7 faça roaming livre pelo melhor sinal.')
						)
					])
				])
			]) : '',
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, _('Cancelar')),
				btnSubmit
			])
		]);

		ui.showModal(_('Conectar a Rede Wi-Fi Externa (WISP)'), modalContent);

		setTimeout(function() {
			if (!inputKey.disabled) {
				inputKey.focus();
			}
		}, 150);
	},

	startConnectionProgress: function(ssid, key, enc, band, bssid) {
		var self = this;

		var step1Node = E('li', { 'style': 'margin-bottom:10px;' }, [
			E('span', { 'style': 'color:#27ae60; font-weight:bold; margin-right:8px;' }, '✔️'),
			_('Passo 1/4: Perfil de rádio, segurança e firewall configurados')
		]);

		var step2Node = E('li', { 'style': 'margin-bottom:10px;' }, [
			E('span', { 'class': 'spinning', 'style': 'margin-right:8px;' }, ''),
			_('Passo 2/4: Sincronizando rádios e associando ao ponto Wi-Fi...')
		]);

		var step3Node = E('li', { 'style': 'margin-bottom:10px; opacity:0.5;' }, [
			E('span', { 'style': 'margin-right:8px;' }, '⏳'),
			_('Passo 3/4: Aguardando concessão de endereço IP via DHCP')
		]);

		var step4Node = E('li', { 'style': 'margin-bottom:10px; opacity:0.5;' }, [
			E('span', { 'style': 'margin-right:8px;' }, '⏳'),
			_('Passo 4/4: Validando rota e conectividade com a Internet')
		]);

		var progressList = E('ul', { 'style': 'list-style:none; padding-left:0; font-size:14px; margin:18px 0;' }, [
			step1Node, step2Node, step3Node, step4Node
		]);

		var statusMsgNode = E('p', { 'style': 'color:#7f8c8d; font-size:12px; margin-top:12px; line-height:1.5;' }, 
			_('Blindagem Ativa: Se o seu computador estiver conectado ao Wi-Fi do T7 (GAMER_7G), a rede reconecta automaticamente em segundos sem interromper a configuração.')
		);

		var modalBody = E('div', {}, [
			E('div', { 'style': 'font-size:15px; margin-bottom:5px;' }, [
				_('Estabelecendo conexão com a rede: '),
				E('strong', { 'style': 'font-size:16px; color:#2980b9;' }, ssid)
			]),
			progressList,
			statusMsgNode
		]);

		ui.showModal(_('Conectando ao Wi-Fi...'), modalBody);

		// Disparo assíncrono imediato (retorna em 20ms, nunca dropa socket HTTP)
		fs.exec('/usr/sbin/wifi-wisp-tool', ['connect_bg', ssid, key, enc, band, bssid]).then(function() {
			var pollCount = 0;
			var maxPolls = 25; // Até ~30 segundos

			var pollTimer = setInterval(function() {
				pollCount++;

				fs.exec('/usr/sbin/wifi-wisp-tool', ['progress']).then(function(res) {
					var p = {};
					try {
						var txt = (res.stdout || '').trim();
						var idx = txt.indexOf('{');
						if (idx !== -1) p = JSON.parse(txt.substring(idx));
					} catch(e) {}

					if (p.step >= 2) {
						step2Node.style.opacity = 1;
						if (p.step > 2 || p.state === 'dhcp' || p.state === 'verifying' || p.state === 'success') {
							step2Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + _('Passo 2/4: Rádio associado com sucesso!');
						} else {
							step2Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + (p.message || _('Passo 2/4: Sincronizando rádios...'));
						}
					}

					if (p.step >= 3) {
						step3Node.style.opacity = 1;
						if (p.step > 3 || p.state === 'verifying' || p.state === 'success') {
							step3Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + _('Passo 3/4: IP obtido via DHCP: ') + '<strong>' + (p.ip || '') + '</strong>';
						} else {
							step3Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + _('Passo 3/4: Aguardando concessão de IP via DHCP...');
						}
					}

					if (p.step >= 4) {
						step4Node.style.opacity = 1;
						if (p.state === 'success') {
							step4Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + _('Passo 4/4: Internet Online e Rota Ativa!');
						} else if (p.state === 'verifying') {
							step4Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + _('Passo 4/4: Validando teste de internet e latência...');
						}
					}

					if (p.state === 'success') {
						clearInterval(pollTimer);
						ui.showModal(_('🎉 Conexão Estabelecida com Sucesso!'), [
							E('p', { 'style': 'font-size:15px; color:#27ae60;' }, _('O seu Acer Predator T7 está oficialmente conectado à Internet via Wi-Fi!')),
							E('div', { 'style': 'background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px; padding:12px; margin:15px 0;' }, [
								E('p', { 'style': 'margin:4px 0;' }, [ _('Rede: '), E('strong', {}, ssid) ]),
								E('p', { 'style': 'margin:4px 0;' }, [ _('IP WAN Recebido: '), E('strong', { 'style': 'color:#2980b9;' }, p.ip || '-') ]),
								p.gateway ? E('p', { 'style': 'margin:4px 0;' }, [ _('Gateway Padrão: '), E('strong', {}, p.gateway) ]) : ''
							]),
							E('div', { 'class': 'right' }, [
								E('button', {
									'class': 'cbi-button cbi-button-apply',
									'click': function() { ui.hideModal(); window.location.reload(); }
								}, _('Concluir'))
							])
						]);
					} else if (p.state === 'error') {
						clearInterval(pollTimer);
						ui.showModal(_('Falha na Conexão'), [
							E('div', { 'class': 'alert-message error' }, p.message || _('Não foi possível conectar. Verifique a senha.')),
							E('div', { 'class': 'right' }, [
								E('button', { 'class': 'cbi-button', 'click': ui.hideModal }, _('Fechar'))
							])
						]);
					} else if (pollCount >= maxPolls) {
						clearInterval(pollTimer);
						ui.showModal(_('Tempo Limite Atingido'), [
							E('div', { 'class': 'alert-message warning' }, _('O processo demorou mais que o esperado. A página será recarregada para verificar o estado atual.')),
							E('div', { 'class': 'right' }, [
								E('button', { 'class': 'cbi-button cbi-button-apply', 'click': function() { window.location.reload(); } }, _('Verificar Estado'))
							])
						]);
					}
				}).catch(function(err) {
					// SILÊNCIO RESILIENTE: Se a rede Wi-Fi cair momentaneamente durante o reload do rádio,
					// NÃO exibe erro XHR na tela! Segue tentando reconectar graciosamente.
					statusMsgNode.innerHTML = '<span class="spinning"></span> ' + _('Sincronizando rádios do T7... Reconectando automaticamente ao roteador...');
				});
			}, 1200);
		}).catch(function(err) {
			ui.hideModal();
			ui.addNotification(null, E('p', {}, _('Erro ao disparar conexão: ') + err.message), 'error');
		});
	},

	openHiddenNetworkModal: function() {
		var self = this;

		var inputSsid = E('input', {
			'type': 'text',
			'class': 'cbi-input-text',
			'placeholder': _('Digite o nome exato da rede (SSID)'),
			'style': 'width:100%; font-size:14px; padding:8px;'
		});

		var selectBand = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%; font-size:14px; padding:6px;' }, [
			E('option', { 'value': '5 GHz' }, _('5 GHz (Recomendado - Mais Rápida e Estável)')),
			E('option', { 'value': '2.4 GHz' }, _('2.4 GHz (Maior Alcance através de Barreiras)')),
			E('option', { 'value': '6 GHz' }, _('6 GHz (Wi-Fi 6E/7 - Requer WPA3-SAE)'))
		]);

		var selectEnc = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%; font-size:14px; padding:6px;' }, [
			E('option', { 'value': 'psk2' }, _('WPA2/WPA3 Pessoal (Padrão mais comum)')),
			E('option', { 'value': 'sae' }, _('WPA3-SAE (Exclusivo WPA3)')),
			E('option', { 'value': 'none' }, _('Aberta (Sem Senha)'))
		]);

		var inputKey = E('input', {
			'type': 'password',
			'class': 'cbi-input-text',
			'placeholder': _('Digite a senha da rede (mínimo 8 caracteres)'),
			'autocomplete': 'new-password',
			'style': 'width:100%; font-size:14px; padding:8px;'
		});

		var checkShowPass = E('input', {
			'type': 'checkbox',
			'style': 'margin-right:6px;',
			'change': function() { inputKey.type = this.checked ? 'text' : 'password'; }
		});

		var errBox = E('div', { 'style': 'color:#e74c3c; font-weight:bold; margin-top:8px; display:none;' });

		selectEnc.addEventListener('change', function() {
			var isNowOpen = (this.value === 'none');
			inputKey.disabled = isNowOpen;
			inputKey.placeholder = isNowOpen ? _('Rede aberta (sem senha)') : _('Digite a senha da rede (mínimo 8 caracteres)');
			if (isNowOpen) {
				inputKey.value = '';
				errBox.style.display = 'none';
			} else {
				inputKey.focus();
			}
		});

		var btnSubmit = E('button', {
			'class': 'cbi-button cbi-button-apply',
			'click': function() {
				var ssid = inputSsid.value.trim();
				var band = selectBand.value;
				var enc = selectEnc.value;
				var key = inputKey.value;

				if (!ssid) {
					errBox.innerText = _('O nome da rede (SSID) é obrigatório.');
					errBox.style.display = 'block';
					inputSsid.focus();
					return;
				}

				if (enc !== 'none' && (!key || key.length < 8)) {
					errBox.innerText = _('Trava de Segurança: A senha do Wi-Fi deve ter no mínimo 8 caracteres.');
					errBox.style.display = 'block';
					inputKey.focus();
					return;
				}

				self.startConnectionProgress(ssid, key, enc, band, '');
			}
		}, _('Conectar à Rede Oculta'));

		var modalContent = E('div', {}, [
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Nome da Rede (SSID):')),
				E('div', { 'class': 'cbi-value-field' }, [ inputSsid ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Frequência / Banda:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectBand ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Segurança:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectEnc ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, _('Senha do Wi-Fi:')),
				E('div', { 'class': 'cbi-value-field' }, [
					inputKey,
					E('div', { 'style': 'margin-top:6px;' }, [ E('label', {}, [ checkShowPass, _('Mostrar senha digitada') ]) ]),
					errBox
				])
			]),
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, _('Cancelar')),
				btnSubmit
			])
		]);

		ui.showModal(_('Conectar a Rede Oculta (Manual)'), modalContent);

		setTimeout(function() {
			inputSsid.focus();
		}, 150);
	},

	handleRescan: function() {
		var btn = document.getElementById('btn-rescan');
		if (btn) {
			btn.disabled = true;
			btn.innerText = _('Varrendo todo o espectro... Aguarde ~3s...');
		}

		if (this.scanTableContainer) {
			this.scanTableContainer.innerHTML = '<p class="spinning" style="margin:20px 0;">' + _('Varrendo o espectro ativamente em 2.4 GHz, 5 GHz e 6 GHz...') + '</p>';
		}

		var self = this;
		fs.exec('/usr/sbin/wifi-wisp-tool', ['scan', 'force']).then(function(res) {
			if (btn) {
				btn.disabled = false;
				btn.innerText = _('🔍 Atualizar / Escanear Novamente');
			}
			var scanData = { networks: [] };
			try {
				var txt = (res.stdout || '').trim();
				var idx = txt.indexOf('{');
				if (idx !== -1) {
					scanData = JSON.parse(txt.substring(idx));
				}
			} catch(e) {}
			self.rawNetworks = scanData.networks || [];
			self.updateScanTable();
		}).catch(function(err) {
			if (btn) {
				btn.disabled = false;
				btn.innerText = _('🔍 Atualizar / Escanear Novamente');
			}
			ui.addNotification(null, E('p', {}, _('Erro ao escanear redes: ') + err.message), 'error');
		});
	},

	handleDisconnect: function() {
		ui.showModal(_('Confirmar Desconexão'), [
			E('p', {}, _('Deseja realmente desconectar o Wi-Fi WAN e retornar a saída da internet exclusivamente para o cabo Ethernet?')),
			E('div', { 'class': 'right' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, _('Cancelar')),
				E('button', {
					'class': 'cbi-button cbi-button-remove',
					'click': function() {
						ui.showModal(_('Desconectando...'), E('p', { 'class': 'spinning' }, _('Removendo interface Wi-Fi WAN e recarregando rádios...')));
						fs.exec('/usr/sbin/wifi-wisp-tool', ['disconnect']).then(function() {
							ui.hideModal();
							window.location.reload();
						}).catch(function(err) {
							ui.hideModal();
							ui.addNotification(null, E('p', {}, _('Erro ao desconectar: ') + err.message), 'error');
						});
					}
				}, _('Confirmar Desconexão'))
			])
		]);
	},

	handleFixConflict: function() {
		ui.showModal(_('Corrigir Conflito de Sub-rede'), [
			E('p', {}, _('Esta ação irá alterar o IP interno do roteador para 192.168.77.1 para resolver a colisão com a rede externa.')),
			E('p', { 'style': 'color:#e67e22;' }, _('Seus dispositivos receberão um novo IP e você deverá acessar o roteador pelo endereço http://192.168.77.1 após a mudança.')),
			E('div', { 'class': 'right' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, _('Cancelar')),
				E('button', {
					'class': 'cbi-button cbi-button-action',
					'click': function() {
						ui.showModal(_('Aplicando novo IP...'), E('p', { 'class': 'spinning' }, _('Alterando rede local para 192.168.77.1... Aguarde 10 segundos.')));
						fs.exec('/usr/sbin/wifi-wisp-tool', ['fix_lan_conflict']).then(function() {
							setTimeout(function() {
								window.location.href = 'http://192.168.77.1/cgi-bin/luci/admin/network/wifi_wisp';
							}, 8000);
						}).catch(function(err) {
							ui.hideModal();
							ui.addNotification(null, E('p', {}, _('Erro ao alterar IP: ') + err.message), 'error');
						});
					}
				}, _('Confirmar e Mudar para 192.168.77.1'))
			])
		]);
	}
});
