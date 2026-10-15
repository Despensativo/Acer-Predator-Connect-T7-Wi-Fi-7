'use strict';
'require view';
'require fs';
'require ui';
'require poll';

function getLang() {
	var l = (typeof L !== 'undefined' && L.env && L.env.lang) ? L.env.lang.toLowerCase() : '';
	if (!l && typeof document !== 'undefined' && document.documentElement && document.documentElement.lang)
		l = document.documentElement.lang.toLowerCase();
	if (!l && typeof navigator !== 'undefined' && navigator.language)
		l = navigator.language.toLowerCase();
	if (l.indexOf('pt') === 0) return 'pt';
	if (l.indexOf('es') === 0) return 'es';
	return 'en';
}

function tr3(pt, en, es) {
	var lang = getLang();
	if (lang === 'pt') return pt;
	if (lang === 'es') return es || en;
	return en;
}

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

function parseBwNum(bwStr) {
	var m = String(bwStr || '').match(/(\d+)/);
	return m ? parseInt(m[1], 10) : 20;
}

function getBwBadgeStyle(bwStr) {
	var n = parseBwNum(bwStr);
	if (n >= 160) return 'background:#8e44ad; color:#fff; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; margin-left:6px;';
	if (n >= 80)  return 'background:#2980b9; color:#fff; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; margin-left:6px;';
	if (n >= 40)  return 'background:#16a085; color:#fff; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; margin-left:6px;';
	return 'background:#7f8c8d; color:#fff; padding:2px 7px; border-radius:4px; font-weight:bold; font-size:11px; margin-left:6px;';
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
	pollingPaused: false,

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
		m.appendChild(E('h2', {}, tr3(
			'Wi-Fi como WAN / Repetidor Inteligente (WISP)',
			'Wi-Fi as WAN / Smart Repeater (WISP)',
			'Wi-Fi como WAN / Repetidor Inteligente (WISP)'
		)));
		m.appendChild(E('div', { 'class': 'cbi-map-descr' }, tr3(
			'Conecte o seu Acer Predator T7 a qualquer rede Wi-Fi externa (roteador da operadora, hotspot 4G/5G do celular ou rede de eventos) para usá-la como link de Internet. A sua rede local (Predator_7G), o DHCP interno, o compartilhamento KSMBD e o Firewall continuam 100% protegidos e operacionais sem risco de colapso.',
			'Connect your Acer Predator T7 to any external Wi-Fi network (ISP router, 4G/5G mobile hotspot, or event network) to use it as your Internet uplink. Your local network (Predator_7G), internal DHCP, KSMBD file sharing, and Firewall remain 100% protected and operational without risk of collapse.',
			'Conecte su Acer Predator T7 a cualquier red Wi-Fi externa (router del operador, hotspot móvil 4G/5G o red de eventos) para usarla como enlace de Internet. Su red local (Predator_7G), DHCP interno, uso compartido KSMBD y Firewall permanecen 100% protegidos y operativos sin riesgo de colapso.'
		)));

		// Card de Status Ativo
		this.statusCardNode = E('div', { 'class': 'cbi-section', 'id': 'wisp-status-card' });
		this.renderStatusCard(this.statusCardNode, statusData);
		m.appendChild(this.statusCardNode);

		// Botão de Pausar/Retomar telemetria em tempo real
		var btnPausePoll = E('button', {
			'class': 'cbi-button',
			'id': 'btn-pause-poll',
			'style': 'margin-right:10px;',
			'click': function() {
				self.pollingPaused = !self.pollingPaused;
				this.innerText = self.pollingPaused
					? tr3('▶️ Retomar Telemetria da Tela', '▶️ Resume Screen Telemetry', '▶️ Reanudar Telemetría de Pantalla')
					: tr3('⏸️ Pausar Telemetria (3s)', '⏸️ Pause Telemetry (3s)', '⏸️ Pausar Telemetría (3s)');
			}
		}, tr3('⏸️ Pausar Telemetria (3s)', '⏸️ Pause Telemetry (3s)', '⏸️ Pausar Telemetría (3s)'));

		// Seção de Redes Disponíveis
		var scanSection = E('div', { 'class': 'cbi-section' });
		var scanHeader = E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:15px;' }, [
			E('h3', { 'style': 'margin:0;' }, tr3('Redes Wi-Fi no Espectro', 'Wi-Fi Networks in Spectrum', 'Redes Wi-Fi en el Espectro')),
			E('div', {}, [
				btnPausePoll,
				E('button', {
					'class': 'cbi-button cbi-button-neutral',
					'style': 'margin-right:10px;',
					'click': ui.createHandlerFn(this, 'openHiddenNetworkModal')
				}, tr3('➕ Conectar a Rede Oculta (Manual)', '➕ Connect to Hidden Network (Manual)', '➕ Conectar a Red Oculta (Manual)')),
				E('button', {
					'class': 'cbi-button cbi-button-action',
					'id': 'btn-rescan',
					'click': ui.createHandlerFn(this, 'handleRescan')
				}, tr3('🔍 Atualizar / Escanear Novamente', '🔍 Refresh / Rescan Spectrum', '🔍 Actualizar / Escanear Nuevamente'))
			])
		]);
		scanSection.appendChild(scanHeader);

		// Barra de Filtro e Ordenação Avançada
		var inputFilter = E('input', {
			'type': 'text',
			'class': 'cbi-input-text',
			'placeholder': tr3('🔍 Filtrar por nome, BSSID ou MHz...', '🔍 Filter by name, BSSID or MHz...', '🔍 Filtrar por nombre, BSSID o MHz...'),
			'style': 'width:250px; font-size:13px; padding:6px 10px;'
		});

		var selectSort = E('select', {
			'class': 'cbi-input-select',
			'style': 'font-size:13px; padding:6px 10px;'
		}, [
			E('option', { 'value': 'signal' }, tr3('📶 Melhor Sinal (Padrão)', '📶 Best Signal (Default)', '📶 Mejor Señal (Predeterminado)')),
			E('option', { 'value': 'bw' }, tr3('⚡ Maior Largura MHz (320 / 160 / 80 MHz Primeiro)', '⚡ Widest Channel MHz (320 / 160 / 80 MHz First)', '⚡ Mayor Ancho MHz (320 / 160 / 80 MHz Primero)')),
			E('option', { 'value': 'alpha' }, tr3('🔤 Ordem Alfabética (A-Z)', '🔤 Alphabetical Order (A-Z)', '🔤 Orden Alfabético (A-Z)')),
			E('option', { 'value': 'grouped' }, tr3('🔗 Agrupar Redes Iguais (Mesmo Nome / Vários Canais)', '🔗 Group Identical SSIDs (Multi-Channel)', '🔗 Agrupar Redes Iguales (Mismo Nombre)')),
			E('option', { 'value': 'band' }, tr3('📡 5 GHz / 6 GHz Primeiro', '📡 5 GHz / 6 GHz First', '📡 5 GHz / 6 GHz Primero'))
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
				E('strong', { 'style': 'font-size:13px; color:#495057;' }, tr3('Filtro:', 'Filter:', 'Filtro:')),
				inputFilter,
				this.networkCounterNode
			]),
			E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
				E('strong', { 'style': 'font-size:13px; color:#495057;' }, tr3('Ordenar por:', 'Sort by:', 'Ordenar por:')),
				selectSort
			])
		]);
		scanSection.appendChild(toolbar);

		// Container da Tabela
		this.scanTableContainer = E('div', { 'id': 'wisp-scan-table' });
		scanSection.appendChild(this.scanTableContainer);
		m.appendChild(scanSection);

		this.updateScanTable();

		// Polling dinâmico do status a cada 3 segundos (NÃO realiza scan de rádio, apenas lê contadores locais)
		poll.add(function() {
			if (document.hidden || self.pollingPaused)
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
				       (n.bw && n.bw.toLowerCase().indexOf(filter) !== -1) ||
				       (n.gen && n.gen.toLowerCase().indexOf(filter) !== -1) ||
				       (n.channel && String(n.channel) === filter);
			});
		}

		var sort = this.currentSort || 'signal';

		if (sort === 'bw') {
			list.sort(function(a, b) {
				var bwDiff = parseBwNum(b.bw) - parseBwNum(a.bw);
				if (bwDiff !== 0) return bwDiff;
				return (b.quality || 0) - (a.quality || 0);
			});
		} else if (sort === 'alpha') {
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
			this.networkCounterNode.innerText = tr3('(%d de %d redes)', '(%d of %d networks)', '(%d de %d redes)').format(networks.length, this.rawNetworks.length);
		}

		this.renderScanTable(this.scanTableContainer, networks);
	},

	renderStatusCard: function(container, s) {
		container.innerHTML = '';
		var self = this;

		var isConnected = (s.connected === true);
		var isConnecting = (!isConnected && s.state === 'connecting');
		var statusText = isConnected ? tr3('CONECTADO (Link de Internet Ativo via Wi-Fi)', 'CONNECTED (Active Wi-Fi Internet Uplink)', 'CONECTADO (Enlace de Internet Activo vía Wi-Fi)') : 
		                 (isConnecting ? tr3('INICIALIZANDO / CALIBRANDO RÁDIO WI-FI (%s)...', 'INITIALIZING / CALIBRATING WI-FI RADIO (%s)...', 'INICIALIZANDO / CALIBRANDO RADIO WI-FI (%s)...').format(s.ssid || 'Hotspot') : 
		                 tr3('DESCONECTADO (Internet via Cabo Ethernet ou Offline)', 'DISCONNECTED (Internet via Ethernet Cable or Offline)', 'DESCONECTADO (Internet vía Cable Ethernet u Offline)'));

		var badgeBg = '#7f8c8d';
		var badgeText = tr3('DESCONECTADO', 'DISCONNECTED', 'DESCONECTADO');

		if (isConnected) {
			if (s.internet_online) {
				badgeBg = '#27ae60';
				badgeText = tr3('INTERNET ONLINE', 'INTERNET ONLINE', 'INTERNET EN LÍNEA');
			} else if (s.captive_portal) {
				badgeBg = '#f39c12';
				badgeText = tr3('PORTAL DE ACESSO', 'CAPTIVE PORTAL', 'PORTAL CAUTIVO');
			} else {
				badgeBg = '#2980b9';
				badgeText = tr3('LINK ATIVO', 'LINK ACTIVE', 'ENLACE ACTIVO');
			}
		} else if (isConnecting) {
			badgeBg = '#e67e22';
			badgeText = tr3('⏳ CALIBRANDO', '⏳ CALIBRATING', '⏳ CALIBRANDO');
		}

		var box = E('div', {
			'style': 'border:2px solid ' + (isConnected ? '#27ae60' : (isConnecting ? '#f39c12' : '#bdc3c7')) + '; border-radius:8px; padding:18px; background:' + (isConnected ? 'rgba(46, 204, 113, 0.04)' : (isConnecting ? 'rgba(243, 156, 18, 0.04)' : '#fff')) + ';'
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
				}, tr3('🔌 Desconectar e Reverter para Cabo', '🔌 Disconnect & Revert to Ethernet', '🔌 Desconectar y Revertir a Cable')) : ''
			])
		]);

		if (isConnected) {
			var details = E('div', {
				'style': 'display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-top:16px; padding-top:16px; border-top:1px dashed #ccc;'
			}, [
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Rede Conectada (SSID): ', 'Connected Network (SSID): ', 'Red Conectada (SSID): ')), E('br'), E('strong', { 'style': 'font-size:14px;' }, s.ssid) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Ponto de Acesso (BSSID): ', 'Access Point (BSSID): ', 'Punto de Acceso (BSSID): ')), E('br'), E('strong', { 'style': 'font-family:monospace; font-size:13px;' }, s.bssid || '-') ]),
				E('div', {}, [
					E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Banda / Canal / Largura (MHz): ', 'Band / Channel / Width (MHz): ', 'Banda / Canal / Ancho (MHz): ')),
					E('br'),
					E('strong', {}, (s.band || '-') + (s.channel ? ' (CH ' + s.channel + ' · ' + s.freq + ' MHz)' : '')),
					s.bw ? E('span', { 'style': getBwBadgeStyle(s.bw) }, '⚡ ' + s.bw) : '',
					s.gen ? E('span', { 'style': 'background:#34495e; color:#fff; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:4px;' }, s.gen) : ''
				]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('IP da WAN Recebido: ', 'WAN IP Received: ', 'IP de WAN Recibida: ')), E('br'), E('strong', { 'style': 'color:#2980b9; font-size:14px;' }, s.ip + (s.netmask ? ' /' + s.netmask : '')) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Gateway Padrão: ', 'Default Gateway: ', 'Puerta de Enlace: ')), E('br'), E('strong', {}, s.gateway || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Servidores DNS: ', 'DNS Servers: ', 'Servidores DNS: ')), E('br'), E('strong', {}, s.dns || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Sinal do Link: ', 'Link Signal: ', 'Señal del Enlace: ')), E('br'), E('strong', { 'style': 'color:#27ae60;' }, s.signal + ' (' + s.quality + '%)') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Latência na Internet: ', 'Internet Latency: ', 'Latencia en Internet: ')), E('br'), E('strong', { 'style': 'color:#16a085;' }, (s.ping || '-') + ' (Ping 1.1.1.1)') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Velocidade TX (PHY Rate): ', 'TX Speed (PHY Rate): ', 'Velocidad TX (PHY Rate): ')), E('br'), E('strong', { 'style': 'color:#8e44ad;' }, s.tx_rate || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Velocidade RX (PHY Rate): ', 'RX Speed (PHY Rate): ', 'Velocidad RX (PHY Rate): ')), E('br'), E('strong', { 'style': 'color:#2980b9;' }, s.rx_rate || '-') ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Tráfego Transferido: ', 'Transferred Traffic: ', 'Tráfico Transferido: ')), E('br'), E('strong', { 'style': 'font-size:12px;' }, '⬇️ ' + formatBytes(s.rx_bytes) + ' | ⬆️ ' + formatBytes(s.tx_bytes)) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Tempo Conectado: ', 'Connected Uptime: ', 'Tiempo Conectado: ')), E('br'), E('strong', {}, formatUptime(s.uptime)) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Rádio Físico / Interface: ', 'Physical Radio / Interface: ', 'Radio Físico / Interfaz: ')), E('br'), E('strong', {}, (s.device || '-') + (s.sta_iface ? ' (' + s.sta_iface + ')' : '')) ]),
				E('div', {}, [ E('span', { 'style': 'color:#7f8c8d; font-size:12px;' }, tr3('Prioridade de Rota: ', 'Route Priority: ', 'Prioridad de Ruta: ')), E('br'), E('span', { 'style': 'font-size:12px; color:#555;' }, tr3('Métrica 20 (Failover Nativo: Cabo Métrica 10 prevalece se plugado)', 'Metric 20 (Native Failover: Cable Metric 10 prevails if plugged)', 'Métrica 20 (Failover Nativo: Cable Métrica 10 prevalece si se conecta)')) ])
			]);
			box.appendChild(details);

			// Nota técnica sobre largura de canal (PLL) e escaneamento
			box.appendChild(E('div', {
				'style': 'margin-top:14px; padding:10px 14px; background:#ebf5fb; border-left:4px solid #2980b9; border-radius:4px; font-size:12px; color:#2c3e50; line-height:1.5;'
			}, [
				E('strong', {}, tr3('💡 Nota de Engenharia sobre Largura de Canal (MHz) e Escaneamento: ', '💡 Engineering Note on Channel Width (MHz) & Scanning: ', '💡 Nota de Ingeniería sobre Ancho de Canal (MHz) y Escaneo: ')),
				tr3(
					'1) A conexão WISP NÃO realiza varredura em segundo plano! O escaneamento de espectro ocorre exclusivamente quando você abre esta página ou clica em "Escanear Novamente", portanto manter a conexão ativa não consome ar nem reduz seus MHz. 2) A largura exibida acima (' + (s.bw || '40 MHz') + ') é ditada fisicamente pelo roteador externo ("' + (s.ssid || 'Hotspot') + '"): como o rádio 5 GHz (wifi1) possui um único oscilador PLL compartilhado entre o cliente WAN (ath11) e o AP local (ath1), o rádio 5 GHz acompanha a largura do roteador provedor enquanto conectado, enquanto a banda de 6 GHz (wifi2) segue livre em 320 MHz / 240 MHz na velocidade máxima!',
					'1) The WISP connection does NOT run background scans! Spectrum scanning only happens once when opening this page or clicking "Rescan", so it never throttles your MHz. 2) The channel width shown above (' + (s.bw || '40 MHz') + ') is physically dictated by the upstream router ("' + (s.ssid || 'Hotspot') + '"): because the 5 GHz radio (wifi1) shares a single hardware PLL oscillator between the WAN client (ath11) and local AP (ath1), 5 GHz locks to the upstream AP\'s channel width while connected, while 6 GHz (wifi2) runs independently at full 320 MHz / 240 MHz speed!',
					'1) ¡La conexión WISP NO realiza escaneos en segundo plano! El escaneo de espectro solo ocurre al abrir esta página o hacer clic en "Escanear Nuevamente", por lo que nunca reduce sus MHz. 2) El ancho mostrado arriba (' + (s.bw || '40 MHz') + ') lo dicta físicamente el router externo ("' + (s.ssid || 'Hotspot') + '"): como el radio de 5 GHz (wifi1) comparte un único oscilador PLL entre el cliente WAN (ath11) y el AP local (ath1), 5 GHz sigue el ancho del proveedor mientras está conectado, mientras que 6 GHz (wifi2) opera libremente a 320 MHz / 240 MHz.'
				)
			]));

			// Alerta de Captive Portal
			if (s.captive_portal) {
				box.appendChild(E('div', { 'class': 'alert-message warning', 'style': 'margin-top:15px;' }, [
					E('strong', {}, tr3('Atenção - Portal de Autenticação Detectado: ', 'Warning - Captive Portal Detected: ', 'Atención - Portal Cautivo Detectado: ')),
					tr3('O roteador está associado ao Wi-Fi externo, mas a rede requer aceite de termos ou login. Abra o navegador em qualquer celular ou computador conectado ao T7 para completar a liberação.', 'The router is associated with the external Wi-Fi, but the network requires terms acceptance or login. Open a browser on any phone or PC connected to the T7 to complete authentication.', 'El router está asociado al Wi-Fi externo, pero la red requiere inicio de sesión. Abra el navegador en cualquier dispositivo conectado al T7 para autenticarse.')
				]));
			}

			// Alerta e Resolução de Conflito de Sub-rede
			if (s.conflict_detected) {
				var conflictBox = E('div', { 'class': 'alert-message error', 'style': 'margin-top:15px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;' }, [
					E('div', {}, [
						E('strong', {}, tr3('CONFLITO DE SUB-REDE DETECTADO: ', 'SUBNET CONFLICT DETECTED: ', 'CONFLICTO DE SUBRED DETECTADO: ')),
						E('p', { 'style': 'margin:4px 0 0 0;' }, tr3('A rede Wi-Fi externa forneceu um IP na mesma faixa da sua rede local (192.168.76.x). Clique ao lado para mover a sua rede local para 192.168.77.1 automaticamente.', 'The external Wi-Fi network assigned an IP in the same subnet as your LAN (192.168.76.x). Click beside to move your LAN to 192.168.77.1 automatically.', 'La red Wi-Fi externa asignó una IP en el mismo rango que su LAN (192.168.76.x). Haga clic al lado para cambiar su LAN a 192.168.77.1 automáticamente.'))
					]),
					E('button', {
						'class': 'cbi-button cbi-button-action',
						'click': ui.createHandlerFn(self, 'handleFixConflict')
					}, tr3('🛠️ Corrigir Conflito Agora (Mudar LAN para 192.168.77.1)', '🛠️ Fix Conflict Now (Move LAN to 192.168.77.1)', '🛠️ Corregir Conflicto Ahora (Cambiar LAN a 192.168.77.1)'))
				]);
				box.appendChild(conflictBox);
			}
		} else if (isConnecting) {
			var calibBox = E('div', {
				'style': 'margin-top:14px; padding:14px; background:#fef9e7; border:1px solid #f9e79f; border-radius:6px;'
			}, [
				E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;' }, [
					E('strong', { 'style': 'color:#7d6608; font-size:14px;' }, [
						E('span', { 'class': 'spinning', 'style': 'margin-right:8px;' }, ''),
						tr3('Hardware Qualcomm IPQ5332 / QCN9224 em calibração e sintonia...', 'Qualcomm IPQ5332 / QCN9224 hardware calibrating and tuning...', 'Hardware Qualcomm IPQ5332 / QCN9224 en calibración y sintonía...')
					]),
					s.device ? E('span', { 'style': 'background:#fcf3cf; color:#7d6608; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:12px;' }, tr3('Rádio: ', 'Radio: ', 'Radio: ') + s.device) : ''
				]),
				E('p', { 'style': 'margin:4px 0 10px 0; font-size:13px; color:#7d6608;' }, s.message || tr3('Sincronizando frequências de rádio e negociando concessão de IP via DHCP...', 'Synchronizing radio frequencies and negotiating DHCP lease...', 'Sincronizando frecuencias de radio y negociando concesión DHCP...')),
				E('div', { 'style': 'font-size:12px; color:#9a7d0a; line-height:1.6; border-top:1px dashed #f9e79f; padding-top:10px;' }, [
					E('div', { 'style': 'font-weight:bold; margin-bottom:4px;' }, tr3('⏱️ Tempo médio de calibração por cenário:', '⏱️ Average calibration time by scenario:', '⏱️ Tiempo medio de calibración por escenario:')),
					E('div', {}, tr3('• 📶 2.4 GHz (wifi0): ~12s a 15s (resposta rápida)', '• 📶 2.4 GHz (wifi0): ~12s to 15s (fast response)', '• 📶 2.4 GHz (wifi0): ~12s a 15s (respuesta rápida)')),
					E('div', {}, tr3('• ⚡ 5 GHz 80 MHz (wifi1): ~15s a 18s (padrão otimizado sem radar)', '• ⚡ 5 GHz 80 MHz (wifi1): ~15s to 18s (optimized non-DFS)', '• ⚡ 5 GHz 80 MHz (wifi1): ~15s a 18s (estándar sin radar)')),
					E('div', {}, tr3('• 📡 5 GHz 160 MHz / Canais DFS: ~60s (escuta mandatória de radar CAC)', '• 📡 5 GHz 160 MHz / DFS Channels: ~60s (mandatory radar CAC listen)', '• 📡 5 GHz 160 MHz / Canales DFS: ~60s (escucha de radar CAC)')),
					E('div', {}, tr3('• 🚀 6 GHz (wifi2): ~18s a 22s (handshake WPA3-SAE obrigatório)', '• 🚀 6 GHz (wifi2): ~18s to 22s (mandatory WPA3-SAE handshake)', '• 🚀 6 GHz (wifi2): ~18s a 22s (handshake WPA3-SAE obligatorio)')),
					E('div', { 'style': 'color:#b9770e; margin-top:4px;' }, tr3('• 🛡️ Trava de Rollback: 15s (reversão automática para cabo se a senha falhar)', '• 🛡️ Rollback Guard: 15s (automatic revert to Ethernet if password fails)', '• 🛡️ Guardia de Rollback: 15s (reversión automática a cable si falla la clave)'))
				])
			]);
			box.appendChild(calibBox);
		} else {
			box.appendChild(E('p', { 'style': 'margin:12px 0 0 0; color:#666;' }, 
				s.message || tr3('Nenhuma rede Wi-Fi externa conectada. Escolha uma das redes abaixo ou clique em "Conectar a Rede Oculta" para usar um hotspot como saída de internet.', 'No external Wi-Fi network connected. Select one of the networks below or click "Connect to Hidden Network" to use a hotspot as your internet uplink.', 'Ninguna red Wi-Fi externa conectada. Elija una red abajo o haga clic en "Conectar a Red Oculta" para usar un hotspot como salida a internet.')
			));
		}

		container.appendChild(box);
	},

	renderScanTable: function(container, networks) {
		container.innerHTML = '';

		if (!networks || networks.length === 0) {
			container.appendChild(E('div', { 'class': 'alert-message notice' }, 
				tr3('Nenhuma rede Wi-Fi corresponde aos critérios no momento. Clique em "Atualizar / Escanear Novamente" para varrer o espectro.', 'No Wi-Fi networks match the criteria right now. Click "Refresh / Rescan Spectrum" to scan the air.', 'Ninguna red Wi-Fi coincide con los criterios. Haga clic en "Actualizar / Escanear Nuevamente" para escanear el espectro.')
			));
			return;
		}

		var table = E('table', { 'class': 'table' }, [
			E('tr', { 'class': 'tr table-titles' }, [
				E('th', { 'class': 'th', 'style': 'width:90px;' }, tr3('Sinal', 'Signal', 'Señal')),
				E('th', { 'class': 'th' }, tr3('Nome da Rede (SSID)', 'Network Name (SSID)', 'Nombre de Red (SSID)')),
				E('th', { 'class': 'th' }, tr3('Banda / Canal / Largura (MHz)', 'Band / Channel / Width (MHz)', 'Banda / Canal / Ancho (MHz)')),
				E('th', { 'class': 'th' }, tr3('Segurança', 'Security', 'Seguridad')),
				E('th', { 'class': 'th', 'style': 'width:180px; text-align:right;' }, tr3('Ação', 'Action', 'Acción'))
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
				}, tr3('⚠️ Própria Rede (Loop Bloqueado)', '⚠️ Own Network (Loop Blocked)', '⚠️ Red Propia (Bucle Bloqueado)'));
			} else {
				actionBtn = E('button', {
					'class': 'cbi-button cbi-button-apply',
					'click': ui.createHandlerFn(self, 'openConnectModal', net)
				}, tr3('Conectar', 'Connect', 'Conectar'));
			}

			var bwLabel = net.bw || '20 MHz';
			var genLabel = net.gen || '';

			var row = E('tr', { 'class': 'tr', 'style': isDuplicateName ? 'background: rgba(41, 128, 185, 0.03);' : '' }, [
				E('td', { 'class': 'td' }, [
					E('div', { 'style': 'display:flex; align-items:center;' }, [
						E('div', {
							'style': 'width:12px; height:12px; border-radius:50%; background:' + sigColor + '; margin-right:8px;'
						}),
						E('div', {}, [
							E('strong', {}, net.quality + '%'),
							net.signal ? E('div', { 'style': 'font-size:10px; color:#7f8c8d;' }, net.signal + ' dBm') : ''
						])
					])
				]),
				E('td', { 'class': 'td' }, [
					E('strong', {}, net.ssid),
					isDuplicateName ? E('span', {
						'class': 'badge',
						'style': 'background:#2980b9; color:#fff; font-size:10px; margin-left:8px;'
					}, tr3('🔗 Mesmo Wi-Fi (Canal Diferente)', '🔗 Same Wi-Fi (Different Channel)', '🔗 Mismo Wi-Fi (Canal Diferente)')) : '',
					net.bssid ? E('div', { 'style': 'font-size:11px; color:#7f8c8d; font-family:monospace; margin-top:2px;' }, 'BSSID: ' + net.bssid) : '',
					isSelf ? E('span', { 'style': 'color:#e74c3c; font-size:12px; margin-left:8px;' }, tr3('(Rede interna do seu T7)', '(Your T7 internal network)', '(Red interna de su T7)')) : ''
				]),
				E('td', { 'class': 'td' }, [
					E('div', { 'style': 'display:flex; align-items:center; flex-wrap:wrap; gap:4px;' }, [
						E('span', { 'class': 'badge' }, net.band),
						E('span', { 'style': 'color:#555; font-size:12px;' }, tr3('Canal ', 'Ch ', 'Canal ') + net.channel),
						E('span', { 'style': getBwBadgeStyle(bwLabel) }, '⚡ ' + bwLabel),
						genLabel ? E('span', { 'style': 'background:#ecf0f1; color:#2c3e50; border:1px solid #bdc3c7; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:bold;' }, genLabel) : ''
					])
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
			E('option', { 'value': 'WPA2-PSK' }, tr3('WPA2-PSK (Padrão mais comum)', 'WPA2-PSK (Most common standard)', 'WPA2-PSK (Estándar más común)')),
			E('option', { 'value': 'WPA3-SAE' }, tr3('WPA3-SAE (Wi-Fi 6E / Wi-Fi 7)', 'WPA3-SAE (Wi-Fi 6E / Wi-Fi 7)', 'WPA3-SAE (Wi-Fi 6E / Wi-Fi 7)')),
			E('option', { 'value': 'WPA2/WPA3' }, tr3('WPA2/WPA3 Misto', 'WPA2/WPA3 Mixed', 'WPA2/WPA3 Mixto')),
			E('option', { 'value': 'Aberta' }, tr3('Aberta (Sem Senha)', 'Open (No Password)', 'Abierta (Sin Contraseña)'))
		]);

		if (net.encryption === 'WPA3-SAE' || net.encryption === 'sae') selectEnc.value = 'WPA3-SAE';
		else if (net.encryption === 'Aberta' || net.encryption === 'none') selectEnc.value = 'Aberta';
		else if (net.encryption === 'WPA2/WPA3') selectEnc.value = 'WPA2/WPA3';
		else selectEnc.value = 'WPA2-PSK';

		var isInitiallyOpen = (selectEnc.value === 'Aberta');

		var inputKey = E('input', {
			'type': 'password',
			'class': 'cbi-input-text',
			'placeholder': isInitiallyOpen ? tr3('Rede aberta (sem senha)', 'Open network (no password)', 'Red abierta (sin contraseña)') : tr3('Digite a senha da rede (mínimo 8 caracteres)', 'Enter network password (min 8 chars)', 'Ingrese la contraseña de red (mín 8 caracteres)'),
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
			inputKey.placeholder = isNowOpen ? tr3('Rede aberta (sem senha)', 'Open network (no password)', 'Red abierta (sin contraseña)') : tr3('Digite a senha da rede (mínimo 8 caracteres)', 'Enter network password (min 8 chars)', 'Ingrese la contraseña de red (mín 8 caracteres)');
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
					errBox.innerText = tr3('Trava de Segurança: A senha do Wi-Fi deve ter no mínimo 8 caracteres.', 'Security Guard: Wi-Fi password must be at least 8 characters.', 'Guardia de Seguridad: La contraseña debe tener al menos 8 caracteres.');
					errBox.style.display = 'block';
					inputKey.focus();
					return;
				}

				var bssidArg = (checkLockBssid.checked && net.bssid) ? net.bssid : '';

				self.startConnectionProgress(net.ssid, key, chosenEnc, net.band, bssidArg);
			}
		}, tr3('Conectar e Testar Link', 'Connect & Test Uplink', 'Conectar y Probar Enlace'));

		var modalContent = E('div', {}, [
			E('div', { 'style': 'background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px; padding:12px; margin-bottom:15px;' }, [
				E('div', { 'style': 'font-size:15px; margin-bottom:4px;' }, [
					tr3('Rede Alvo: ', 'Target Network: ', 'Red Objetivo: '),
					E('strong', { 'style': 'font-size:16px; color:#2980b9;' }, net.ssid)
				]),
				E('div', { 'style': 'font-size:12px; color:#666; display:flex; gap:15px; flex-wrap:wrap;' }, [
					E('span', {}, '📡 ' + net.band + ' (Canal ' + net.channel + ')'),
					E('span', { 'style': 'font-weight:bold; color:#8e44ad;' }, '⚡ ' + (net.bw || '20 MHz') + (net.gen ? ' · ' + net.gen : '')),
					net.bssid ? E('span', { 'style': 'font-family:monospace;' }, '📍 BSSID: ' + net.bssid) : '',
					E('span', {}, '📶 ' + net.quality + '% (' + net.signal + ' dBm)')
				])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Tipo de Segurança:', 'Security Type:', 'Tipo de Seguridad:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectEnc ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Senha do Wi-Fi:', 'Wi-Fi Password:', 'Contraseña de Wi-Fi:')),
				E('div', { 'class': 'cbi-value-field' }, [
					inputKey,
					E('div', { 'style': 'margin-top:6px;' }, [
						E('label', {}, [ checkShowPass, tr3('Mostrar senha digitada', 'Show typed password', 'Mostrar contraseña escrita') ])
					]),
					errBox
				])
			]),
			net.bssid ? E('div', { 'class': 'cbi-value', 'style': 'margin-top:12px; padding:10px; background:#fdfefe; border:1px dashed #bdc3c7; border-radius:6px;' }, [
				E('label', { 'style': 'cursor:pointer; display:flex; align-items:flex-start;' }, [
					checkLockBssid,
					E('div', {}, [
						E('strong', {}, tr3('Fixar conexão neste ponto de acesso específico (BSSID)', 'Lock connection to this specific access point (BSSID)', 'Fijar conexión en este punto de acceso específico (BSSID)')),
						E('div', { 'style': 'font-size:11px; color:#7f8c8d; margin-top:2px;' }, 
							tr3('Marcado (Recomendado): Fixa o roteador neste rádio exato para garantir que ele permaneça na frequência e canal escolhidos. Desmarque se esta rede possuir repetidores/mesh e você preferir que o T7 faça roaming livre pelo melhor sinal.', 'Checked (Recommended): Locks the router to this exact radio so it stays on the chosen frequency and channel. Uncheck if this network uses mesh/repeaters and you want free roaming.', 'Marcado (Recomendado): Fija el router en este radio exacto. Desmarque si la red tiene repetidores/mesh y prefiere roaming libre.')
						)
					])
				])
			]) : '',
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, tr3('Cancelar', 'Cancel', 'Cancelar')),
				btnSubmit
			])
		]);

		ui.showModal(tr3('Conectar a Rede Wi-Fi Externa (WISP)', 'Connect to External Wi-Fi Network (WISP)', 'Conectar a Red Wi-Fi Externa (WISP)'), modalContent);

		setTimeout(function() {
			if (!inputKey.disabled) {
				inputKey.focus();
			}
		}, 150);
	},

	startConnectionProgress: function(ssid, key, enc, band, bssid) {
		var self = this;

		var scenarioName = '5 GHz 80 MHz (wifi1 - QCN9224)';
		var estSeconds = 18;
		var bStr = (band || '').toLowerCase();
		if (bStr.indexOf('2.4') !== -1 || bStr.indexOf('2g') !== -1) {
			scenarioName = '2.4 GHz (wifi0 - IPQ5332)';
			estSeconds = 14;
		} else if (bStr.indexOf('6') !== -1) {
			scenarioName = '6 GHz (wifi2 - QCN9224 Wi-Fi 7)';
			estSeconds = 20;
		} else {
			scenarioName = '5 GHz 80 MHz (wifi1 - QCN9224)';
			estSeconds = 18;
		}

		var timerEl = E('span', { 'style': 'font-weight:bold; font-size:14px; color:#2980b9;' }, '0s / ~' + estSeconds + 's');
		var barEl = E('div', {
			'style': 'background:#2980b9; height:100%; width:4%; border-radius:4px; transition:width 0.4s ease;'
		});

		var timerBox = E('div', {
			'style': 'background:#f4f6f7; border:1px solid #d5dbdb; border-radius:6px; padding:12px; margin:14px 0;'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;' }, [
				E('strong', { 'style': 'font-size:13px; color:#2c3e50;' }, [
					tr3('⏱️ Cenário: ', '⏱️ Scenario: ', '⏱️ Escenario: '), scenarioName
				]),
				timerEl
			]),
			E('div', { 'style': 'background:#eaeded; border-radius:4px; height:8px; overflow:hidden;' }, [
				barEl
			]),
			E('div', { 'style': 'margin-top:10px; font-size:11px; color:#7f8c8d; line-height:1.4;' }, [
				E('div', { 'style': 'font-weight:bold; margin-bottom:2px;' }, tr3('Tempo médio de calibração por cenário:', 'Average calibration time by scenario:', 'Tiempo medio de calibración por escenario:')),
				E('div', {}, tr3('• 📶 2.4 GHz: ~12s a 15s | • ⚡ 5 GHz 80 MHz: ~15s a 18s', '• 📶 2.4 GHz: ~12s to 15s | • ⚡ 5 GHz 80 MHz: ~15s to 18s', '• 📶 2.4 GHz: ~12s a 15s | • ⚡ 5 GHz 80 MHz: ~15s a 18s')),
				E('div', {}, tr3('• 📡 5 GHz 160 MHz / DFS: ~60s | • 🚀 6 GHz: ~18s a 22s', '• 📡 5 GHz 160 MHz / DFS: ~60s | • 🚀 6 GHz: ~18s to 22s', '• 📡 5 GHz 160 MHz / DFS: ~60s | • 🚀 6 GHz: ~18s a 22s')),
				E('div', { 'style': 'color:#d35400;' }, tr3('• 🛡️ Trava de Rollback: 15s (reversão automática para cabo se a senha falhar)', '• 🛡️ Rollback Guard: 15s (automatic revert to Ethernet if password fails)', '• 🛡️ Guardia de Rollback: 15s (reversión automática a cable si falla la clave)'))
			])
		]);

		var step1Node = E('li', { 'style': 'margin-bottom:10px;' }, [
			E('span', { 'style': 'color:#27ae60; font-weight:bold; margin-right:8px;' }, '✔️'),
			tr3('Passo 1/4: Perfil de rádio, segurança e firewall configurados', 'Step 1/4: Radio, security and firewall profile configured', 'Paso 1/4: Perfil de radio, seguridad y firewall configurados')
		]);

		var step2Node = E('li', { 'style': 'margin-bottom:10px;' }, [
			E('span', { 'class': 'spinning', 'style': 'margin-right:8px;' }, ''),
			tr3('Passo 2/4: Sincronizando rádios e associando ao ponto Wi-Fi...', 'Step 2/4: Synchronizing radios and associating with Wi-Fi AP...', 'Paso 2/4: Sincronizando radios y asociando al punto Wi-Fi...')
		]);

		var step3Node = E('li', { 'style': 'margin-bottom:10px; opacity:0.5;' }, [
			E('span', { 'style': 'margin-right:8px;' }, '⏳'),
			tr3('Passo 3/4: Aguardando concessão de endereço IP via DHCP', 'Step 3/4: Waiting for DHCP IP address lease', 'Paso 3/4: Esperando concesión de dirección IP vía DHCP')
		]);

		var step4Node = E('li', { 'style': 'margin-bottom:10px; opacity:0.5;' }, [
			E('span', { 'style': 'margin-right:8px;' }, '⏳'),
			tr3('Passo 4/4: Validando rota e conectividade com a Internet', 'Step 4/4: Validating route and Internet connectivity', 'Paso 4/4: Validando ruta y conectividad a Internet')
		]);

		var progressList = E('ul', { 'style': 'list-style:none; padding-left:0; font-size:14px; margin:18px 0;' }, [
			step1Node, step2Node, step3Node, step4Node
		]);

		var statusMsgNode = E('p', { 'style': 'color:#7f8c8d; font-size:12px; margin-top:12px; line-height:1.5;' }, 
			tr3('Blindagem Ativa: Se o seu computador estiver conectado ao Wi-Fi do T7 (Predator_7G), a rede reconecta automaticamente em segundos sem interromper a configuração.', 'Active Shield: If your PC is connected to the T7 Wi-Fi (Predator_7G), the network reconnects automatically in seconds without interrupting setup.', 'Blindaje Activo: Si su PC está conectada al Wi-Fi del T7 (Predator_7G), la red se reconecta automáticamente en segundos sin interrumpir la configuración.')
		);

		var modalBody = E('div', {}, [
			E('div', { 'style': 'font-size:15px; margin-bottom:5px;' }, [
				tr3('Estabelecendo conexão com a rede: ', 'Establishing connection to network: ', 'Estableciendo conexión con la red: '),
				E('strong', { 'style': 'font-size:16px; color:#2980b9;' }, ssid)
			]),
			timerBox,
			progressList,
			statusMsgNode
		]);

		ui.showModal(tr3('Conectando ao Wi-Fi...', 'Connecting to Wi-Fi...', 'Conectando al Wi-Fi...'), modalBody);

		var elapsedSec = 0;
		var timerTicker = setInterval(function() {
			elapsedSec++;
			timerEl.innerText = elapsedSec + 's / ~' + estSeconds + 's';
			var pct = Math.min(94, Math.round((elapsedSec / estSeconds) * 90));
			barEl.style.width = Math.max(4, pct) + '%';
		}, 1000);

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
							step2Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + tr3('Passo 2/4: Rádio associado com sucesso!', 'Step 2/4: Radio associated successfully!', '¡Paso 2/4: Radio asociado con éxito!');
						} else {
							step2Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + (p.message || tr3('Passo 2/4: Sincronizando rádios...', 'Step 2/4: Synchronizing radios...', 'Paso 2/4: Sincronizando radios...'));
						}
					}

					if (p.step >= 3) {
						step3Node.style.opacity = 1;
						if (p.step > 3 || p.state === 'verifying' || p.state === 'success') {
							step3Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + tr3('Passo 3/4: IP obtido via DHCP: ', 'Step 3/4: DHCP IP obtained: ', 'Paso 3/4: IP obtenida vía DHCP: ') + '<strong>' + (p.ip || '') + '</strong>';
						} else {
							step3Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + tr3('Passo 3/4: Aguardando concessão de IP via DHCP...', 'Step 3/4: Waiting for DHCP IP lease...', 'Paso 3/4: Esperando concesión de IP vía DHCP...');
						}
					}

					if (p.step >= 4) {
						step4Node.style.opacity = 1;
						if (p.state === 'success') {
							step4Node.innerHTML = '<span style="color:#27ae60; font-weight:bold; margin-right:8px;">✔️</span> ' + tr3('Passo 4/4: Internet Online e Rota Ativa!', 'Step 4/4: Internet Online and Route Active!', '¡Paso 4/4: Internet en Línea y Ruta Activa!');
						} else if (p.state === 'verifying') {
							step4Node.innerHTML = '<span class="spinning" style="margin-right:8px;"></span> ' + tr3('Passo 4/4: Validando teste de internet e latência...', 'Step 4/4: Validating internet test and latency...', 'Paso 4/4: Validando prueba de internet y latencia...');
						}
					}

					if (p.state === 'success') {
						clearInterval(pollTimer);
						clearInterval(timerTicker);
						barEl.style.width = '100%';
						barEl.style.background = '#27ae60';
						ui.showModal(tr3('🎉 Conexão Estabelecida com Sucesso!', '🎉 Connection Established Successfully!', '🎉 ¡Conexión Establecida con Éxito!'), [
							E('p', { 'style': 'font-size:15px; color:#27ae60;' }, tr3('O seu Acer Predator T7 está oficialmente conectado à Internet via Wi-Fi!', 'Your Acer Predator T7 is officially connected to the Internet via Wi-Fi!', '¡Su Acer Predator T7 está oficialmente conectado a Internet vía Wi-Fi!')),
							E('div', { 'style': 'background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px; padding:12px; margin:15px 0;' }, [
								E('p', { 'style': 'margin:4px 0;' }, [ tr3('Rede: ', 'Network: ', 'Red: '), E('strong', {}, ssid) ]),
								E('p', { 'style': 'margin:4px 0;' }, [ tr3('IP WAN Recebido: ', 'WAN IP Received: ', 'IP WAN Recibida: '), E('strong', { 'style': 'color:#2980b9;' }, p.ip || '-') ]),
								p.gateway ? E('p', { 'style': 'margin:4px 0;' }, [ tr3('Gateway Padrão: ', 'Default Gateway: ', 'Puerta de Enlace: '), E('strong', {}, p.gateway) ]) : ''
							]),
							E('div', { 'class': 'right' }, [
								E('button', {
									'class': 'cbi-button cbi-button-apply',
									'click': function() { ui.hideModal(); window.location.reload(); }
								}, tr3('Concluir', 'Finish', 'Concluir'))
							])
						]);
					} else if (p.state === 'error') {
						clearInterval(pollTimer);
						clearInterval(timerTicker);
						ui.showModal(tr3('Falha na Conexão', 'Connection Failed', 'Fallo en la Conexión'), [
							E('div', { 'class': 'alert-message error' }, p.message || tr3('Não foi possível conectar. Verifique a senha.', 'Could not connect. Check the password.', 'No se pudo conectar. Verifique la contraseña.')),
							E('div', { 'class': 'right' }, [
								E('button', { 'class': 'cbi-button', 'click': ui.hideModal }, tr3('Fechar', 'Close', 'Cerrar'))
							])
						]);
					} else if (pollCount >= maxPolls) {
						clearInterval(pollTimer);
						clearInterval(timerTicker);
						ui.showModal(tr3('Tempo Limite Atingido', 'Timeout Reached', 'Tiempo Límite Alcanzado'), [
							E('div', { 'class': 'alert-message warning' }, tr3('O processo demorou mais que o esperado. A página será recarregada para verificar o estado atual.', 'The process took longer than expected. The page will reload to verify the current state.', 'El proceso tardó más de lo esperado. La página se recargará para verificar el estado actual.')),
							E('div', { 'class': 'right' }, [
								E('button', { 'class': 'cbi-button cbi-button-apply', 'click': function() { window.location.reload(); } }, tr3('Verificar Estado', 'Check Status', 'Verificar Estado'))
							])
						]);
					}
				}).catch(function(err) {
					statusMsgNode.innerHTML = '<span class="spinning"></span> ' + tr3('Sincronizando rádios do T7... Reconectando automaticamente ao roteador...', 'Synchronizing T7 radios... Automatically reconnecting to router...', 'Sincronizando radios del T7... Reconectando automáticamente al router...');
				});
			}, 1200);
		}).catch(function(err) {
			clearInterval(timerTicker);
			ui.hideModal();
			ui.addNotification(null, E('p', {}, tr3('Erro ao disparar conexão: ', 'Error triggering connection: ', 'Error al iniciar conexión: ') + err.message), 'error');
		});
	},

	openHiddenNetworkModal: function() {
		var self = this;

		var inputSsid = E('input', {
			'type': 'text',
			'class': 'cbi-input-text',
			'placeholder': tr3('Digite o nome exato da rede (SSID)', 'Enter exact network name (SSID)', 'Ingrese el nombre exacto de la red (SSID)'),
			'style': 'width:100%; font-size:14px; padding:8px;'
		});

		var selectBand = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%; font-size:14px; padding:6px;' }, [
			E('option', { 'value': '5 GHz' }, tr3('5 GHz (Recomendado - Mais Rápida e Estável)', '5 GHz (Recommended - Faster & Stable)', '5 GHz (Recomendado - Más Rápida y Estable)')),
			E('option', { 'value': '2.4 GHz' }, tr3('2.4 GHz (Maior Alcance através de Barreiras)', '2.4 GHz (Longer Range through Walls)', '2.4 GHz (Mayor Alcance a través de Paredes)')),
			E('option', { 'value': '6 GHz' }, tr3('6 GHz (Wi-Fi 6E/7 - Requer WPA3-SAE)', '6 GHz (Wi-Fi 6E/7 - Requires WPA3-SAE)', '6 GHz (Wi-Fi 6E/7 - Requiere WPA3-SAE)'))
		]);

		var selectEnc = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%; font-size:14px; padding:6px;' }, [
			E('option', { 'value': 'psk2' }, tr3('WPA2/WPA3 Pessoal (Padrão mais comum)', 'WPA2/WPA3 Personal (Most common)', 'WPA2/WPA3 Personal (Más común)')),
			E('option', { 'value': 'sae' }, tr3('WPA3-SAE (Exclusivo WPA3)', 'WPA3-SAE (WPA3 Only)', 'WPA3-SAE (Exclusivo WPA3)')),
			E('option', { 'value': 'none' }, tr3('Aberta (Sem Senha)', 'Open (No Password)', 'Abierta (Sin Contraseña)'))
		]);

		var inputKey = E('input', {
			'type': 'password',
			'class': 'cbi-input-text',
			'placeholder': tr3('Digite a senha da rede (mínimo 8 caracteres)', 'Enter network password (min 8 chars)', 'Ingrese la contraseña de red (mín 8 caracteres)'),
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
			inputKey.placeholder = isNowOpen ? tr3('Rede aberta (sem senha)', 'Open network (no password)', 'Red abierta (sin contraseña)') : tr3('Digite a senha da rede (mínimo 8 caracteres)', 'Enter network password (min 8 chars)', 'Ingrese la contraseña de red (mín 8 caracteres)');
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
					errBox.innerText = tr3('O nome da rede (SSID) é obrigatório.', 'Network name (SSID) is required.', 'El nombre de la red (SSID) es obligatorio.');
					errBox.style.display = 'block';
					inputSsid.focus();
					return;
				}

				if (enc !== 'none' && (!key || key.length < 8)) {
					errBox.innerText = tr3('Trava de Segurança: A senha do Wi-Fi deve ter no mínimo 8 caracteres.', 'Security Guard: Wi-Fi password must be at least 8 characters.', 'Guardia de Seguridad: La contraseña debe tener al menos 8 caracteres.');
					errBox.style.display = 'block';
					inputKey.focus();
					return;
				}

				self.startConnectionProgress(ssid, key, enc, band, '');
			}
		}, tr3('Conectar à Rede Oculta', 'Connect to Hidden Network', 'Conectar a Red Oculta'));

		var modalContent = E('div', {}, [
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Nome da Rede (SSID):', 'Network Name (SSID):', 'Nombre de Red (SSID):')),
				E('div', { 'class': 'cbi-value-field' }, [ inputSsid ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Frequência / Banda:', 'Frequency / Band:', 'Frecuencia / Banda:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectBand ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Segurança:', 'Security:', 'Seguridad:')),
				E('div', { 'class': 'cbi-value-field' }, [ selectEnc ])
			]),
			E('div', { 'class': 'cbi-value' }, [
				E('label', { 'class': 'cbi-value-title' }, tr3('Senha do Wi-Fi:', 'Wi-Fi Password:', 'Contraseña de Wi-Fi:')),
				E('div', { 'class': 'cbi-value-field' }, [
					inputKey,
					E('div', { 'style': 'margin-top:6px;' }, [ E('label', {}, [ checkShowPass, tr3('Mostrar senha digitada', 'Show typed password', 'Mostrar contraseña escrita') ]) ]),
					errBox
				])
			]),
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, tr3('Cancelar', 'Cancel', 'Cancelar')),
				btnSubmit
			])
		]);

		ui.showModal(tr3('Conectar a Rede Oculta (Manual)', 'Connect to Hidden Network (Manual)', 'Conectar a Red Oculta (Manual)'), modalContent);

		setTimeout(function() {
			inputSsid.focus();
		}, 150);
	},

	handleRescan: function() {
		var btn = document.getElementById('btn-rescan');
		if (btn) {
			btn.disabled = true;
			btn.innerText = tr3('Varrendo todo o espectro... Aguarde ~3s...', 'Scanning full spectrum... Wait ~3s...', 'Escaneando todo el espectro... Espere ~3s...');
		}

		if (this.scanTableContainer) {
			this.scanTableContainer.innerHTML = '<p class="spinning" style="margin:20px 0;">' + tr3('Varrendo o espectro ativamente em 2.4 GHz, 5 GHz e 6 GHz...', 'Actively scanning spectrum across 2.4 GHz, 5 GHz and 6 GHz...', 'Escaneando activamente el espectro en 2.4 GHz, 5 GHz y 6 GHz...') + '</p>';
		}

		var self = this;
		fs.exec('/usr/sbin/wifi-wisp-tool', ['scan', 'force']).then(function(res) {
			if (btn) {
				btn.disabled = false;
				btn.innerText = tr3('🔍 Atualizar / Escanear Novamente', '🔍 Refresh / Rescan Spectrum', '🔍 Actualizar / Escanear Nuevamente');
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
				btn.innerText = tr3('🔍 Atualizar / Escanear Novamente', '🔍 Refresh / Rescan Spectrum', '🔍 Actualizar / Escanear Nuevamente');
			}
			ui.addNotification(null, E('p', {}, tr3('Erro ao escanear redes: ', 'Error scanning networks: ', 'Error al escanear redes: ') + err.message), 'error');
		});
	},

	handleDisconnect: function() {
		ui.showModal(tr3('Confirmar Desconexão', 'Confirm Disconnection', 'Confirmar Desconexión'), [
			E('p', {}, tr3('Deseja realmente desconectar o Wi-Fi WAN e retornar a saída da internet exclusivamente para o cabo Ethernet?', 'Do you really want to disconnect Wi-Fi WAN and return internet uplink exclusively to the Ethernet cable?', '¿Desea desconectar el Wi-Fi WAN y volver la salida de internet exclusivamente al cable Ethernet?')),
			E('div', { 'class': 'right' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, tr3('Cancelar', 'Cancel', 'Cancelar')),
				E('button', {
					'class': 'cbi-button cbi-button-remove',
					'click': function() {
						ui.showModal(tr3('Desconectando...', 'Disconnecting...', 'Desconectando...'), E('p', { 'class': 'spinning' }, tr3('Removendo interface Wi-Fi WAN e recarregando rádios...', 'Removing Wi-Fi WAN interface and reloading radios...', 'Eliminando interfaz Wi-Fi WAN y recargando radios...')));
						fs.exec('/usr/sbin/wifi-wisp-tool', ['disconnect']).then(function() {
							ui.hideModal();
							window.location.reload();
						}).catch(function(err) {
							ui.hideModal();
							ui.addNotification(null, E('p', {}, tr3('Erro ao desconectar: ', 'Error disconnecting: ', 'Error al desconectar: ') + err.message), 'error');
						});
					}
				}, tr3('Confirmar Desconexão', 'Confirm Disconnection', 'Confirmar Desconexión'))
			])
		]);
	},

	handleFixConflict: function() {
		ui.showModal(tr3('Corrigir Conflito de Sub-rede', 'Fix Subnet Conflict', 'Corregir Conflicto de Subred'), [
			E('p', {}, tr3('Esta ação irá alterar o IP interno do roteador para 192.168.77.1 para resolver a colisão com a rede externa.', 'This action will change the router internal IP to 192.168.77.1 to resolve the collision with the external network.', 'Esta acción cambiará la IP interna del router a 192.168.77.1 para resolver la colisión con la red externa.')),
			E('p', { 'style': 'color:#e67e22;' }, tr3('Seus dispositivos receberão um novo IP e você deverá acessar o roteador pelo endereço http://192.168.77.1 após a mudança.', 'Your devices will receive a new IP and you must access the router at http://192.168.77.1 after the change.', 'Sus dispositivos recibirán una nueva IP y deberá acceder al router en http://192.168.77.1 después del cambio.')),
			E('div', { 'class': 'right' }, [
				E('button', { 'class': 'cbi-button', 'click': ui.hideModal, 'style': 'margin-right:10px;' }, tr3('Cancelar', 'Cancel', 'Cancelar')),
				E('button', {
					'class': 'cbi-button cbi-button-action',
					'click': function() {
						ui.showModal(tr3('Aplicando novo IP...', 'Applying new IP...', 'Aplicando nueva IP...'), E('p', { 'class': 'spinning' }, tr3('Alterando rede local para 192.168.77.1... Aguarde 10 segundos.', 'Changing local network to 192.168.77.1... Wait 10 seconds.', 'Cambiando red local a 192.168.77.1... Espere 10 segundos.')));
						fs.exec('/usr/sbin/wifi-wisp-tool', ['fix_lan_conflict']).then(function() {
							setTimeout(function() {
								window.location.href = 'http://192.168.77.1/cgi-bin/luci/admin/network/wifi_wisp';
							}, 8000);
						}).catch(function(err) {
							ui.hideModal();
							ui.addNotification(null, E('p', {}, tr3('Erro ao alterar IP: ', 'Error changing IP: ', 'Error al cambiar IP: ') + err.message), 'error');
						});
					}
				}, tr3('Confirmar e Mudar para 192.168.77.1', 'Confirm & Move to 192.168.77.1', 'Confirmar y Cambiar a 192.168.77.1'))
			])
		]);
	}
});
