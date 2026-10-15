'use strict';
'require view';
'require rpc';
'require ui';

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
	var b = parseInt(bytes, 10) || 0;
	if (b >= 1073741824) return (b / 1073741824).toFixed(2) + ' GB';
	if (b >= 1048576) return (b / 1048576).toFixed(1) + ' MB';
	if (b >= 1024) return (b / 1024).toFixed(0) + ' KB';
	return b + ' B';
}

var callGetStatus = rpc.declare({
	object: 'predator',
	method: 'get_status',
	expect: { '': {} }
});

var callWakeOnLan = rpc.declare({
	object: 'predator',
	method: 'wake_on_lan',
	params: [ 'mac' ],
	expect: { '': {} }
});

var callOptimizeChannels = rpc.declare({
	object: 'predator',
	method: 'optimize_channels',
	expect: { '': {} }
});

var callSetupWireguard = rpc.declare({
	object: 'predator',
	method: 'setup_wireguard',
	params: [ 'action', 'config', 'enabled', 'priv', 'pub', 'psk', 'address', 'mtu', 'endpoint_host', 'endpoint_port', 'allowed_ips', 'keepalive' ],
	expect: { '': {} }
});

var callSetSchedule = rpc.declare({
	object: 'predator',
	method: 'set_schedule',
	params: [ 'action', 'enabled', 'start', 'stop', 'days' ],
	expect: { '': {} }
});

var callSetService = rpc.declare({
	object: 'predator',
	method: 'set_service',
	params: [ 'service', 'enabled' ],
	expect: { '': {} }
});

var callRunNetDiag = rpc.declare({
	object: 'predator',
	method: 'run_net_diag',
	params: [ 'mode', 'target', 'size' ],
	expect: { '': {} }
});

var CSS = `
	.p-apps-wrap {
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
		max-width: 1200px;
		margin: 0 auto;
		color: #1e293b;
	}
	.p-apps-hero {
		background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 55%, #0f766e 100%);
		color: #fff;
		border-radius: 14px;
		padding: 24px 28px;
		margin-bottom: 22px;
		box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 16px;
	}
	.p-apps-hero h2 {
		margin: 0 0 6px 0;
		font-size: 23px;
		font-weight: 800;
		color: #fff;
		letter-spacing: -0.3px;
	}
	.p-apps-hero p {
		margin: 0;
		font-size: 13.5px;
		color: #cbd5e1;
		max-width: 780px;
		line-height: 1.5;
	}
	.p-apps-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
		gap: 20px;
		margin-bottom: 24px;
	}
	@media (max-width: 768px) {
		.p-apps-grid {
			grid-template-columns: 1fr;
		}
	}
	.p-app-card {
		background: #fff;
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		padding: 20px 22px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
	.p-app-card-full {
		grid-column: 1 / -1;
	}
	.p-app-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 10px;
		margin-bottom: 10px;
	}
	.p-app-title {
		font-size: 16px;
		font-weight: 800;
		color: #0f172a;
		margin: 0;
	}
	.p-app-sub {
		font-size: 12.5px;
		color: #64748b;
		line-height: 1.5;
		margin-bottom: 14px;
	}
	.p-badge {
		display: inline-block;
		padding: 4px 10px;
		border-radius: 999px;
		font-size: 11px;
		font-weight: 800;
		white-space: nowrap;
	}
	.p-badge-on {
		background: #dcfce7;
		color: #15803d;
		border: 1px solid #86efac;
	}
	.p-badge-warn {
		background: #fef3c7;
		color: #b45309;
		border: 1px solid #fcd34d;
	}
	.p-badge-off {
		background: #f1f5f9;
		color: #475569;
		border: 1px solid #cbd5e1;
	}
	.p-form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
		gap: 10px;
		margin-bottom: 12px;
	}
	.p-field label {
		display: block;
		font-size: 11px;
		font-weight: 700;
		color: #475569;
		margin-bottom: 4px;
		text-transform: uppercase;
	}
	.p-field input, .p-field select, .p-field textarea {
		width: 100%;
		padding: 7px 10px;
		border: 1px solid #cbd5e1;
		border-radius: 6px;
		font-size: 12.5px;
		box-sizing: border-box;
		background: #f8fafc;
		color: #0f172a;
	}
	.p-btn-row {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
		align-items: center;
		margin-top: 10px;
	}
	.p-btn {
		padding: 8px 14px;
		border-radius: 7px;
		font-size: 12.5px;
		font-weight: 700;
		border: none;
		cursor: pointer;
		transition: all 0.15s ease;
		text-decoration: none !important;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.p-btn-primary {
		background: #2563eb;
		color: #fff !important;
	}
	.p-btn-primary:hover { background: #1d4ed8; }
	.p-btn-success {
		background: #059669;
		color: #fff !important;
	}
	.p-btn-success:hover { background: #047857; }
	.p-btn-purple {
		background: #7c3aed;
		color: #fff !important;
	}
	.p-btn-purple:hover { background: #6d28d9; }
	.p-btn-danger {
		background: #dc2626;
		color: #fff !important;
	}
	.p-btn-danger:hover { background: #b91c1c; }
	.p-btn-outline {
		background: #f8fafc;
		color: #334155 !important;
		border: 1px solid #cbd5e1;
	}
	.p-btn-outline:hover { background: #e2e8f0; }
	.p-stat-strip {
		display: flex;
		gap: 14px;
		flex-wrap: wrap;
		padding: 10px 12px;
		background: #f8fafc;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 12px;
		margin-bottom: 12px;
	}
	.p-wol-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 12.5px;
		margin-top: 8px;
	}
	.p-wol-table th, .p-wol-table td {
		padding: 8px 10px;
		border-bottom: 1px solid #e2e8f0;
		text-align: left;
	}
	.p-wol-table th {
		background: #f8fafc;
		font-size: 11px;
		text-transform: uppercase;
		color: #475569;
	}
`;

return view.extend({
	handleSaveApply: null,
	handleSave: null,
	handleReset: null,

	load: function() {
		return callGetStatus().catch(function() { return {}; });
	},

	render: function(status) {
		var apps = (status && status.apps) ? status.apps : {};
		var silicon = (status && status.silicon) ? status.silicon : {};

		var root = E('div', { 'class': 'p-apps-wrap' }, [
			E('style', {}, CSS)
		]);

		// Hero Banner
		root.appendChild(E('div', { 'class': 'p-apps-hero' }, [
			E('div', {}, [
				E('div', { 'style': 'font-size:11px; font-weight:800; text-transform:uppercase; color:#38bdf8; letter-spacing:0.8px; margin-bottom:4px;' },
					'⚡ CUDY WR11000 · QSDK SPF 12.4 · OPENWRT 19.07.10 ARCHIVE'),
				E('h2', {}, tr3(
					'Predator Central de Aplicativos & Motores Nativos',
					'Predator Native Applications & Engines Center',
					'Predator Central de Aplicaciones y Motores Nativos'
				)),
				E('p', {}, tr3(
					'Gerenciamento completo dos motores nativos destravados na ROM e portados da plataforma Qualcomm IPQ5332 + QCN9224: VPN WireGuard Kernel-Space, OpenVPN completo, Wake-on-LAN com tabela ao vivo, Agendador Eco RF, IPTV Multicast, DNS Criptografado (DoH + Anti-QUIC) e Escudo de Pacotes OPKG.',
					'Full management of native engines unlocked in ROM and ported from the Qualcomm IPQ5332 + QCN9224 platform: Kernel-Space WireGuard VPN, full OpenVPN, live Wake-on-LAN table, Eco RF Scheduler, IPTV Multicast, Encrypted DNS (DoH + Anti-QUIC) and OPKG Package Shield.',
					'Gestión completa de los motores nativos desbloqueados en la ROM y portados de la plataforma Qualcomm IPQ5332 + QCN9224: VPN WireGuard Kernel-Space, OpenVPN completo, tabla Wake-on-LAN en vivo, Programador Eco RF, IPTV Multicast, DNS Cifrado (DoH + Anti-QUIC) y Escudo de Paquetes OPKG.'
				))
			]),
			E('div', { 'style': 'display:flex; gap:10px; flex-wrap:wrap;' }, [
				E('a', {
					'class': 'p-btn p-btn-outline',
					'style': 'background:rgba(255,255,255,0.12); color:#fff !important; border-color:rgba(255,255,255,0.25);',
					'href': L.url('admin', 'network', 'predator_wifi')
				}, tr3('⬅️ Voltar ao Painel Wi-Fi 7', '⬅️ Back to Wi-Fi 7 Dashboard', '⬅️ Volver al Panel Wi-Fi 7')),
				E('a', {
					'class': 'p-btn p-btn-outline',
					'style': 'background:rgba(255,255,255,0.12); color:#fff !important; border-color:rgba(255,255,255,0.25);',
					'href': L.url('admin', 'network', 'wifi_wisp')
				}, tr3('📡 Painel WISP (Wi-Fi WAN)', '📡 WISP Panel (Wi-Fi WAN)', '📡 Panel WISP (Wi-Fi WAN)'))
			])
		]));

		var grid = E('div', { 'class': 'p-apps-grid' });

		// =========================================================================
		// 1. WIREGUARD VPN KERNEL-SPACE (FULL MANUAL + .CONF IMPORTER)
		// =========================================================================
		var wgUp = apps.wg_up === '1';
		var wgEn = apps.wg_enabled === '1';
		var wgCard = E('div', { 'class': 'p-app-card p-app-card-full' });

		wgCard.appendChild(E('div', { 'class': 'p-app-head' }, [
			E('div', {}, [
				E('h3', { 'class': 'p-app-title' }, tr3(
					'🛡️ 1. Cliente VPN WireGuard Kernel-Space (wg0)',
					'🛡️ 1. Kernel-Space WireGuard VPN Client (wg0)',
					'🛡️ 1. Cliente VPN WireGuard Kernel-Space (wg0)'
				)),
				E('div', { 'class': 'p-app-sub', 'style': 'margin-bottom:6px;' }, tr3(
					'Criptografia ChaCha20-Poly1305 direto no kernel Linux 5.4.213 (wireguard.ko + netifd proto). Configure manualmente cada parâmetro abaixo ou cole um arquivo .conf pronto (ProtonVPN, Mullvad, Surfshark, NordLynx, Cloudflare WARP).',
					'ChaCha20-Poly1305 encryption directly in Linux kernel 5.4.213 (wireguard.ko + netifd proto). Configure every parameter manually below or paste a ready .conf file (ProtonVPN, Mullvad, Surfshark, NordLynx, Cloudflare WARP).',
					'Cifrado ChaCha20-Poly1305 directo en el kernel Linux 5.4.213 (wireguard.ko + netifd proto). Configure manualmente cada parámetro abajo o pegue un archivo .conf listo (ProtonVPN, Mullvad, Surfshark, NordLynx, Cloudflare WARP).'
				))
			]),
			E('span', { 'class': 'p-badge ' + (wgUp ? 'p-badge-on' : (wgEn ? 'p-badge-warn' : 'p-badge-off')) },
				wgUp ? '● TUNNEL wg0 UP' : (wgEn ? '◐ CONFIGURADO' : '○ STANDBY (KERNEL PRONTO)'))
		]));

		wgCard.appendChild(E('div', { 'class': 'p-stat-strip' }, [
			E('span', {}, [ E('strong', {}, 'Endpoint: '), apps.wg_endpoint || tr3('Não definido', 'Not set', 'No definido') ]),
			E('span', {}, [ E('strong', {}, 'IP wg0: '), apps.wg_address || '-' ]),
			E('span', {}, [ E('strong', {}, 'MTU: '), apps.wg_mtu || '1420' ]),
			E('span', {}, [ E('strong', {}, 'RX / TX: '), '⬇️ ' + formatBytes(apps.wg_rx) + ' · ⬆️ ' + formatBytes(apps.wg_tx) ]),
			E('span', {}, [ E('strong', {}, 'Firewall Zone: '), 'wan (NAT Masquerade)' ])
		]));

		var inWgPriv = E('input', { 'type': 'password', 'value': apps.wg_priv || '', 'placeholder': 'Ex: YN5...=' });
		var inWgAddr = E('input', { 'type': 'text', 'value': apps.wg_address || '10.2.0.2/32', 'placeholder': '10.2.0.2/32' });
		var inWgMtu  = E('input', { 'type': 'number', 'value': apps.wg_mtu || '1420', 'placeholder': '1420' });
		var inWgPub  = E('input', { 'type': 'text', 'value': apps.wg_pub || '', 'placeholder': 'Ex: mQ8...=' });
		var inWgPsk  = E('input', { 'type': 'password', 'value': apps.wg_psk || '', 'placeholder': tr3('Opcional', 'Optional', 'Opcional') });
		var inWgHost = E('input', { 'type': 'text', 'value': apps.wg_endpoint_host || '', 'placeholder': 'Ex: br1.vpn.com / 185.x.x.x' });
		var inWgPort = E('input', { 'type': 'number', 'value': apps.wg_endpoint_port || '51820', 'placeholder': '51820' });
		var inWgAllow = E('input', { 'type': 'text', 'value': apps.wg_allowed_ips || '0.0.0.0/0', 'placeholder': '0.0.0.0/0' });
		var inWgKeep  = E('input', { 'type': 'number', 'value': apps.wg_keepalive || '25', 'placeholder': '25' });

		var wgFormGrid = E('div', { 'class': 'p-form-grid' }, [
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Chave Privada (PrivateKey)', 'Client PrivateKey', 'Clave Privada (PrivateKey)')), inWgPriv ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Endereço IP do Túnel (Address)', 'Tunnel IP Address', 'Dirección IP del Túnel')), inWgAddr ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, 'MTU (Bytes)'), inWgMtu ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Chave Pública do Servidor (Peer PublicKey)', 'Server Peer PublicKey', 'Clave Pública del Servidor')), inWgPub ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, 'PresharedKey (PSK)'), inWgPsk ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Servidor (Endpoint Host/IP)', 'Endpoint Host / IP', 'Servidor (Endpoint Host/IP)')), inWgHost ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Porta (Endpoint Port)', 'Endpoint Port', 'Puerto (Endpoint Port)')), inWgPort ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Rotas no Túnel (AllowedIPs)', 'Tunnel Routes (AllowedIPs)', 'Rutas en el Túnel (AllowedIPs)')), inWgAllow ]),
			E('div', { 'class': 'p-field' }, [ E('label', {}, 'Persistent Keepalive (s)'), inWgKeep ])
		]);
		wgCard.appendChild(wgFormGrid);

		var wgConfArea = E('textarea', {
			'rows': '4',
			'style': 'width:100%; font-family:monospace; font-size:11.5px; padding:8px; border:1px solid #cbd5e1; border-radius:6px; background:#f8fafc; margin-top:4px;',
			'placeholder': '[Interface]\nPrivateKey = ...\nAddress = 10.2.0.2/32\n\n[Peer]\nPublicKey = ...\nEndpoint = 185.x.x.x:51820\nAllowedIPs = 0.0.0.0/0'
		});

		var wgImportDetails = E('details', { 'style': 'margin:8px 0; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:8px; padding:10px 14px;' }, [
			E('summary', { 'style': 'cursor:pointer; font-weight:700; font-size:12.5px; color:#2563eb;' },
				tr3('📋 Ou clique aqui para colar um arquivo .conf WireGuard completo', '📋 Or click here to paste a complete WireGuard .conf file', '📋 O haga clic aquí para pegar un archivo .conf WireGuard completo')),
			wgConfArea,
			E('div', { 'style': 'margin-top:8px;' }, [
				E('button', {
					'class': 'p-btn p-btn-primary',
					'click': function() {
						var val = (wgConfArea.value || '').trim();
						if (!val) return;
						callSetupWireguard('import', val, '1', '', '', '', '', '', '', '', '', '').then(function(r) {
							if (r && r.success) {
								ui.addNotification(null, E('p', {}, tr3('Arquivo .conf WireGuard importado e túnel wg0 ativado!', 'WireGuard .conf imported and wg0 tunnel activated!', '¡Archivo .conf WireGuard importado y túnel wg0 activado!')), 'info');
								setTimeout(function() { window.location.reload(); }, 1800);
							} else {
								ui.addNotification(null, E('p', {}, tr3('Arquivo .conf inválido: verifique PrivateKey e PublicKey.', 'Invalid .conf: check PrivateKey and PublicKey.', 'Archivo .conf inválido: verifique PrivateKey y PublicKey.')), 'error');
							}
						});
					}
				}, tr3('📥 Importar Arquivo .conf & Ativar', '📥 Import .conf File & Activate', '📥 Importar Archivo .conf y Activar'))
			])
		]);
		wgCard.appendChild(wgImportDetails);

		wgCard.appendChild(E('div', { 'class': 'p-btn-row' }, [
			E('button', {
				'class': 'p-btn p-btn-success',
				'click': function() {
					var priv = inWgPriv.value.trim();
					var pub = inWgPub.value.trim();
					if (!priv || !pub) {
						ui.addNotification(null, E('p', {}, tr3('Preencha pelo menos a PrivateKey e a PublicKey do servidor (ou importe um arquivo .conf).', 'Fill in at least PrivateKey and Server PublicKey (or import a .conf file).', 'Complete al menos PrivateKey y PublicKey del servidor (o importe un archivo .conf).')), 'warning');
						return;
					}
					callSetupWireguard(
						'save', '', '1',
						priv, pub, inWgPsk.value.trim(),
						inWgAddr.value.trim(), inWgMtu.value.trim(),
						inWgHost.value.trim(), inWgPort.value.trim(),
						inWgAllow.value.trim(), inWgKeep.value.trim()
					).then(function(r) {
						if (r && r.success) {
							ui.addNotification(null, E('p', {}, tr3('Configuração WireGuard salva e túnel wg0 iniciado!', 'WireGuard configuration saved and wg0 tunnel started!', '¡Configuración WireGuard guardada y túnel wg0 iniciado!')), 'info');
							setTimeout(function() { window.location.reload(); }, 1800);
						}
					});
				}
			}, tr3('💾 Salvar Parâmetros & Conectar wg0', '💾 Save Parameters & Connect wg0', '💾 Guardar Parámetros y Conectar wg0')),
			E('button', {
				'class': 'p-btn p-btn-outline',
				'click': function() {
					var show = (inWgPriv.type === 'password');
					inWgPriv.type = show ? 'text' : 'password';
					inWgPsk.type = show ? 'text' : 'password';
				}
			}, tr3('👁️ Mostrar/Ocultar Chaves', '👁️ Show/Hide Keys', '👁️ Mostrar/Ocultar Claves')),
			wgEn ? E('button', {
				'class': 'p-btn ' + (wgUp ? 'p-btn-outline' : 'p-btn-primary'),
				'click': function() {
					callSetupWireguard('toggle', '', wgUp ? '0' : '1', '', '', '', '', '', '', '', '', '').then(function() {
						setTimeout(function() { window.location.reload(); }, 1500);
					});
				}
			}, wgUp ? tr3('⏸️ Pausar Túnel wg0', '⏸️ Pause wg0 Tunnel', '⏸️ Pausar Túnel wg0') : tr3('▶️ Religar Túnel wg0', '▶️ Resume wg0 Tunnel', '▶️ Reanudar Túnel wg0')) : '',
			(wgEn || apps.wg_priv) ? E('button', {
				'class': 'p-btn p-btn-danger',
				'click': function() {
					callSetupWireguard('delete', '', '0', '', '', '', '', '', '', '', '', '').then(function() {
						setTimeout(function() { window.location.reload(); }, 1200);
					});
				}
			}, tr3('🗑️ Remover Perfil wg0', '🗑️ Delete wg0 Profile', '🗑️ Eliminar Perfil wg0')) : ''
		]));

		grid.appendChild(wgCard);

		// =========================================================================
		// 2. OPENVPN NATIVO DA ROM (CLIENT / SERVER)
		// =========================================================================
		var ovpnRun = apps.openvpn_running === '1';
		var ovpnCard = E('div', { 'class': 'p-app-card' }, [
			E('div', {}, [
				E('div', { 'class': 'p-app-head' }, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'🔑 2. OpenVPN Nativo Desbloqueado (Client & Server)',
						'🔑 2. Unlocked Native OpenVPN (Client & Server)',
						'🔑 2. OpenVPN Nativo Desbloqueado (Client & Server)'
					)),
					E('span', { 'class': 'p-badge ' + (ovpnRun ? 'p-badge-on' : 'p-badge-warn') },
						ovpnRun ? '● DAEMON ATIVO' : '● PRONTO NA ROM')
				]),
				E('div', { 'class': 'p-app-sub' }, tr3(
					'O binário /usr/sbin/openvpn e o módulo kmod-tun já vêm de fábrica na ROM da Acer, mas o menu estava oculto pela trava "hidden = true". Destravamos o painel completo do OpenVPN para importar arquivos .ovpn, gerenciar chaves TLS e criar servidores ou clientes VPN.',
					'The /usr/sbin/openvpn binary and kmod-tun module come pre-installed in the Acer ROM, but the menu was hidden by "hidden = true". We unlocked the full OpenVPN panel to import .ovpn files, manage TLS keys, and create VPN servers or clients.',
					'El binario /usr/sbin/openvpn y el módulo kmod-tun vienen de fábrica en la ROM de Acer, pero el menú estaba oculto por "hidden = true". Desbloqueamos el panel completo de OpenVPN para importar archivos .ovpn y gestionar túneles.'
				)),
				E('div', { 'class': 'p-stat-strip' }, [
					E('span', {}, [ E('strong', {}, 'Binário: '), '/usr/sbin/openvpn (SSL/TLS + TUN/TAP)' ]),
					E('span', {}, [ E('strong', {}, tr3('Perfis Configurados: ', 'Configured Profiles: ', 'Perfiles Configurados: ')), apps.openvpn_profiles || '0' ])
				])
			]),
			E('div', { 'class': 'p-btn-row' }, [
				E('a', {
					'class': 'p-btn p-btn-primary',
					'href': L.url('admin', 'vpn', 'openvpn')
				}, tr3('⚙️ Abrir Painel Completo OpenVPN (.ovpn)', '⚙️ Open Full OpenVPN Panel (.ovpn)', '⚙️ Abrir Panel Completo OpenVPN (.ovpn)')),
				E('button', {
					'class': 'p-btn ' + (ovpnRun ? 'p-btn-danger' : 'p-btn-success'),
					'click': function() {
						callSetService('openvpn', ovpnRun ? '0' : '1').then(function() {
							setTimeout(function() { window.location.reload(); }, 1200);
						});
					}
				}, ovpnRun ? tr3('⏹️ Parar Daemon OpenVPN', '⏹️ Stop OpenVPN Daemon', '⏹️ Detener Daemon OpenVPN') : tr3('▶️ Iniciar Daemon OpenVPN', '▶️ Start OpenVPN Daemon', '▶️ Iniciar Daemon OpenVPN'))
			])
		]);
		grid.appendChild(ovpnCard);

		// =========================================================================
		// 3. AGENDADOR ECO WI-FI + CHAVE RF IMEDIATA
		// =========================================================================
		var schEn = apps.sched_enabled === '1';
		var inSchOff = E('input', { 'type': 'time', 'value': apps.sched_off || '00:00' });
		var inSchOn  = E('input', { 'type': 'time', 'value': apps.sched_on || '06:00' });
		var selSchDays = E('select', {}, [
			E('option', { 'value': '*', 'selected': (apps.sched_days === '*' || !apps.sched_days) ? 'selected' : null }, tr3('📅 Todos os Dias (Seg a Dom)', '📅 Every Day (Mon-Sun)', '📅 Todos los Días (Lun a Dom)')),
			E('option', { 'value': '1-5', 'selected': (apps.sched_days === '1-5') ? 'selected' : null }, tr3('💼 Dias Úteis (Segunda a Sexta)', '💼 Weekdays (Monday to Friday)', '💼 Días Laborables (Lunes a Viernes)')),
			E('option', { 'value': '0,6', 'selected': (apps.sched_days === '0,6') ? 'selected' : null }, tr3('🌴 Fim de Semana (Sábado e Domingo)', '🌴 Weekends (Saturday & Sunday)', '🌴 Fin de Semana (Sábado y Domingo)'))
		]);
		var chkSchEn = E('input', { 'type': 'checkbox', 'checked': schEn ? 'checked' : null, 'style': 'width:auto; margin-right:6px;' });

		var schedCard = E('div', { 'class': 'p-app-card' }, [
			E('div', {}, [
				E('div', { 'class': 'p-app-head' }, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'🕒 3. Agendador Eco Wi-Fi (/sbin/wifi_schedule.sh)',
						'🕒 3. Wi-Fi Eco Scheduler (/sbin/wifi_schedule.sh)',
						'🕒 3. Programador Eco Wi-Fi (/sbin/wifi_schedule.sh)'
					)),
					E('span', { 'class': 'p-badge ' + (schEn ? 'p-badge-on' : 'p-badge-off') },
						schEn ? ('● CRON ' + (apps.sched_off || '00:00') + ' → ' + (apps.sched_on || '06:00')) : '○ DESATIVADO')
				]),
				E('div', { 'class': 'p-app-sub' }, tr3(
					'Desliga os amplificadores de rádio de 2.4 GHz, 5 GHz e 6 GHz durante a madrugada (mantendo o cabo 2.5G e a LAN ativos) e religa pela manhã reaplicando todas as otimizações RF e SFE.',
					'Powers down the 2.4 GHz, 5 GHz, and 6 GHz radio amplifiers overnight (keeping 2.5G Ethernet and LAN active) and wakes them in the morning while re-applying all RF and SFE tuning.',
					'Apaga los amplificadores de radio de 2.4 GHz, 5 GHz y 6 GHz durante la madrugada (manteniendo el cable 2.5G activo) y los enciende por la mañana.'
				)),
				E('div', { 'class': 'p-form-grid' }, [
					E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Desligar Rádios às:', 'Turn Radios OFF at:', 'Apagar Radios a las:')), inSchOff ]),
					E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Religar Rádios às:', 'Turn Radios ON at:', 'Encender Radios a las:')), inSchOn ]),
					E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Dias da Semana:', 'Days of Week:', 'Días de la Semana:')), selSchDays ])
				]),
				E('label', { 'style': 'display:flex; align-items:center; font-size:13px; font-weight:700; cursor:pointer; margin:6px 0;' }, [
					chkSchEn,
					tr3('Ativar Agendamento Automático no Cron', 'Enable Automatic Cron Schedule', 'Activar Programación Automática en Cron')
				])
			]),
			E('div', { 'class': 'p-btn-row' }, [
				E('button', {
					'class': 'p-btn p-btn-primary',
					'click': function() {
						var enVal = chkSchEn.checked ? '1' : '0';
						callSetSchedule('save', enVal, inSchOff.value || '00:00', inSchOn.value || '06:00', selSchDays.value || '*').then(function() {
							ui.addNotification(null, E('p', {}, tr3('Cronograma Eco Wi-Fi salvo com sucesso!', 'Wi-Fi Eco Schedule saved!', '¡Horario Eco Wi-Fi guardado!')), 'info');
							setTimeout(function() { window.location.reload(); }, 1000);
						});
					}
				}, tr3('💾 Salvar Cronograma', '💾 Save Schedule', '💾 Guardar Horario')),
				E('button', {
					'class': 'p-btn p-btn-outline',
					'click': function() {
						callSetSchedule('test_up', '', '', '', '').then(function() {
							ui.addNotification(null, E('p', {}, tr3('Comando de religamento RF + calibração SFE enviado!', 'RF Wake + SFE calibration command sent!', '¡Comando de encendido RF enviado!')), 'info');
						});
					}
				}, tr3('☀️ Religar & Recalibrar RF Agora', '☀️ Wake & Recalibrate RF Now', '☀️ Encender y Recalibrar RF Ahora'))
			])
		]);
		grid.appendChild(schedCard);

		// =========================================================================
		// 4. WAKE-ON-LAN (TABELA COMPLETA DE DISPOSITIVOS + DISPARO MANUAL)
		// =========================================================================
		var wolHosts = Array.isArray(apps.wol_hosts) ? apps.wol_hosts : [];
		var wolCard = E('div', { 'class': 'p-app-card p-app-card-full' });

		wolCard.appendChild(E('div', { 'class': 'p-app-head' }, [
			E('div', {}, [
				E('h3', { 'class': 'p-app-title' }, tr3(
					'⚡ 4. Central Wake-on-LAN (etherwake Magic Packet na Ponte br-lan)',
					'⚡ 4. Wake-on-LAN Center (etherwake Magic Packet on br-lan Bridge)',
					'⚡ 4. Central Wake-on-LAN (etherwake Magic Packet en Puente br-lan)'
				)),
				E('div', { 'class': 'p-app-sub', 'style': 'margin-bottom:6px;' }, tr3(
					'Acorde remotamente qualquer PC Gamer, servidor NAS ou console conectado ao roteador enviando um quadro Ethernet Layer-2 0x0842 (Magic Packet) direto pela bridge br-lan.',
					'Remotely wake any Gaming PC, NAS server, or console connected to the router by broadcasting an Ethernet Layer-2 0x0842 frame (Magic Packet) directly across the br-lan bridge.',
					'Despierte remotamente cualquier PC Gamer, servidor NAS o consola conectada al router enviando un paquete mágico Ethernet Layer-2 0x0842 directo por el puente br-lan.'
				))
			]),
			E('span', { 'class': 'p-badge p-badge-on' }, wolHosts.length + ' ' + tr3('HOSTS DETECTADOS', 'DETECTED HOSTS', 'HOSTS DETECTADOS'))
		]));

		var wolTable = E('table', { 'class': 'p-wol-table' }, [
			E('tr', {}, [
				E('th', {}, tr3('Dispositivo (Hostname)', 'Device (Hostname)', 'Dispositivo (Hostname)')),
				E('th', {}, 'IP LAN'),
				E('th', {}, 'MAC Address'),
				E('th', {}, tr3('Estado ARP', 'ARP State', 'Estado ARP')),
				E('th', { 'style': 'text-align:right;' }, tr3('Disparo Rápido', 'Quick Wake', 'Disparo Rápido'))
			])
		]);

		if (wolHosts.length === 0) {
			wolTable.appendChild(E('tr', {}, [
				E('td', { 'colspan': '5', 'style': 'text-align:center; color:#64748b; padding:14px;' },
					tr3('Nenhum cliente listado em /tmp/dhcp.leases no momento. Digite o MAC manualmente abaixo.', 'No clients listed in /tmp/dhcp.leases right now. Enter MAC manually below.', 'Ningún cliente en /tmp/dhcp.leases. Ingrese el MAC manualmente abajo.'))
			]));
		} else {
			wolHosts.forEach(function(h) {
				var isOnline = (h.online === '1');
				wolTable.appendChild(E('tr', {}, [
					E('td', {}, E('strong', {}, h.name || 'Device')),
					E('td', { 'style': 'font-family:monospace;' }, h.ip || '-'),
					E('td', { 'style': 'font-family:monospace; font-weight:700;' }, h.mac),
					E('td', {}, E('span', { 'class': 'p-badge ' + (isOnline ? 'p-badge-on' : 'p-badge-off') },
						isOnline ? tr3('● Online na Tabela ARP', '● Online in ARP Table', '● En línea en ARP') : tr3('○ Em Standby / Hibernando', '○ Standby / Sleeping', '○ En Standby / Hibernando'))),
					E('td', { 'style': 'text-align:right;' }, [
						E('button', {
							'class': 'p-btn p-btn-purple',
							'style': 'padding:5px 10px; font-size:11.5px;',
							'click': function() {
								callWakeOnLan(h.mac).then(function(r) {
									if (r && r.success) {
										ui.addNotification(null, E('p', {}, tr3('⚡ Magic Packet enviado para ', '⚡ Magic Packet sent to ', '⚡ Magic Packet enviado a ') + h.name + ' (' + h.mac + ')!'), 'info');
									}
								});
							}
						}, tr3('⚡ Acordar PC', '⚡ Wake PC', '⚡ Despertar PC'))
					])
				]));
			});
		}
		wolCard.appendChild(wolTable);

		var inCustomMac = E('input', {
			'type': 'text',
			'placeholder': 'AA:BB:CC:DD:EE:FF',
			'style': 'width:220px; padding:7px 10px; border:1px solid #cbd5e1; border-radius:6px; font-family:monospace; font-size:12.5px;'
		});
		wolCard.appendChild(E('div', { 'class': 'p-btn-row', 'style': 'margin-top:14px;' }, [
			E('span', { 'style': 'font-size:12.5px; font-weight:700; color:#475569;' }, tr3('Acordar MAC Manual:', 'Wake Custom MAC:', 'Despertar MAC Manual:')),
			inCustomMac,
			E('button', {
				'class': 'p-btn p-btn-purple',
				'click': function() {
					var mac = (inCustomMac.value || '').trim();
					if (!mac) return;
					callWakeOnLan(mac).then(function(r) {
						if (r && r.success) {
							ui.addNotification(null, E('p', {}, tr3('⚡ Magic Packet enviado para ', '⚡ Magic Packet sent to ', '⚡ Magic Packet enviado a ') + r.mac), 'info');
						} else {
							ui.addNotification(null, E('p', {}, tr3('Endereço MAC inválido! Use o formato AA:BB:CC:DD:EE:FF.', 'Invalid MAC address! Use AA:BB:CC:DD:EE:FF.', '¡Dirección MAC inválida!')), 'error');
						}
					});
				}
			}, tr3('⚡ Disparar Magic Packet', '⚡ Send Magic Packet', '⚡ Enviar Magic Packet'))
		]));
		grid.appendChild(wolCard);

		// =========================================================================
		// 5. IPTV MULTICAST (igmpproxy) + DNS CRIPTOGRAFADO (DoH) + ANTI-QUIC
		// =========================================================================
		var igmpEn = apps.igmp_enabled === '1';
		var dohEn  = apps.doh_enabled === '1';
		var quicEn = apps.quic_blocked === '1';

		var netEnginesCard = E('div', { 'class': 'p-app-card' }, [
			E('div', {}, [
				E('div', { 'class': 'p-app-head' }, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'📺 5. Motores de Rede: IPTV Multicast, DNS DoH & Filtro QUIC',
						'📺 5. Network Engines: IPTV Multicast, DoH DNS & QUIC Filter',
						'📺 5. Motores de Red: IPTV Multicast, DNS DoH y Filtro QUIC'
					)),
					E('span', { 'class': 'p-badge ' + ((dohEn || quicEn || igmpEn) ? 'p-badge-on' : 'p-badge-off') },
						((dohEn ? 1 : 0) + (quicEn ? 1 : 0) + (igmpEn ? 1 : 0)) + '/3 ' + tr3('ATIVOS', 'ACTIVE', 'ACTIVOS'))
				]),
				E('div', { 'class': 'p-app-sub' }, tr3(
					'Controle individual com status em tempo real dos 3 aceleradores de rede local: DNS-over-HTTPS criptografado (Cloudflare + Google), Bloqueio de Bypass UDP/443 QUIC e Proxy Multicast IGMPv2/v3 + McastEnhance (para IPTV sem inundar o Wi-Fi).',
					'Individual control with real-time status for the 3 local network engines: encrypted DNS-over-HTTPS (Cloudflare + Google), UDP/443 QUIC bypass blocker, and IGMPv2/v3 Multicast Proxy + McastEnhance (for IPTV without flooding Wi-Fi).',
					'Control individual con estado en tiempo real de los 3 motores de red: DNS-over-HTTPS cifrado, bloqueo de bypass UDP/443 QUIC y Proxy Multicast IGMPv2/v3 + McastEnhance.'
				)),
				E('div', { 'style': 'display:flex; flex-direction:column; gap:10px; margin:10px 0;' }, [
					// Row 1: DoH
					E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding:10px 12px; background:' + (dohEn ? '#f0fdf4' : '#f8fafc') + '; border:1px solid ' + (dohEn ? '#86efac' : '#e2e8f0') + '; border-radius:8px;' }, [
						E('div', {}, [
							E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
								E('strong', { 'style': 'font-size:13px;' }, '🔒 DNS-over-HTTPS (https-dns-proxy)'),
								E('span', { 'class': 'p-badge ' + (dohEn ? 'p-badge-on' : 'p-badge-off') },
									dohEn ? tr3('● LIGADO (:5053/:5054)', '● ENABLED (:5053/:5054)', '● ENCENDIDO (:5053/:5054)') : tr3('○ DESLIGADO', '○ DISABLED', '○ APAGADO'))
							]),
							E('div', { 'style': 'font-size:11px; color:#64748b; margin-top:2px;' }, 'Cloudflare (127.0.0.1:5053) + Google (127.0.0.1:5054)')
						]),
						E('div', { 'style': 'display:flex; gap:6px;' }, [
							E('button', {
								'class': 'p-btn ' + (dohEn ? 'p-btn-outline' : 'p-btn-success'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (dohEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('doh', '1').then(function() {
										ui.addNotification(null, E('p', {}, tr3('🔒 DNS-over-HTTPS ativado!', '🔒 DNS-over-HTTPS enabled!', '🔒 ¡DNS-over-HTTPS activado!')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Ligar DoH', 'Enable DoH', 'Activar DoH')),
							E('button', {
								'class': 'p-btn ' + (dohEn ? 'p-btn-danger' : 'p-btn-outline'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (!dohEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('doh', '0').then(function() {
										ui.addNotification(null, E('p', {}, tr3('🔓 DNS-over-HTTPS desligado.', '🔓 DNS-over-HTTPS disabled.', '🔓 DNS-over-HTTPS desactivado.')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Desligar', 'Disable', 'Apagar'))
						])
					]),
					// Row 2: QUIC Filter
					E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding:10px 12px; background:' + (quicEn ? '#f0fdf4' : '#f8fafc') + '; border:1px solid ' + (quicEn ? '#86efac' : '#e2e8f0') + '; border-radius:8px;' }, [
						E('div', {}, [
							E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
								E('strong', { 'style': 'font-size:13px;' }, tr3('🛡️ Filtro Anti-Bypass QUIC (UDP 443)', '🛡️ Anti-Bypass QUIC Filter (UDP 443)', '🛡️ Filtro Anti-Bypass QUIC (UDP 443)')),
								E('span', { 'class': 'p-badge ' + (quicEn ? 'p-badge-on' : 'p-badge-off') },
									quicEn ? tr3('● LIGADO (BLOQUEANDO UDP/443)', '● ENABLED (BLOCKING UDP/443)', '● ENCENDIDO (BLOQUEANDO UDP/443)') : tr3('○ DESLIGADO (UDP/443 LIBERADO)', '○ DISABLED (UDP/443 OPEN)', '○ APAGADO (UDP/443 LIBRE)'))
							]),
							E('div', { 'style': 'font-size:11px; color:#64748b; margin-top:2px;' }, tr3('Força navegadores a respeitarem o DoH e o SQM CAKE', 'Forces browsers to respect DoH and SQM CAKE', 'Fuerza a los navegadores a respetar DoH y SQM CAKE'))
						]),
						E('div', { 'style': 'display:flex; gap:6px;' }, [
							E('button', {
								'class': 'p-btn ' + (quicEn ? 'p-btn-outline' : 'p-btn-primary'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (quicEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('quic_block', '1').then(function() {
										ui.addNotification(null, E('p', {}, tr3('🛡️ Filtro QUIC (UDP/443) ativado!', '🛡️ QUIC Filter (UDP/443) enabled!', '🛡️ ¡Filtro QUIC (UDP/443) activado!')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Bloquear QUIC', 'Block QUIC', 'Bloquear QUIC')),
							E('button', {
								'class': 'p-btn ' + (quicEn ? 'p-btn-danger' : 'p-btn-outline'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (!quicEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('quic_block', '0').then(function() {
										ui.addNotification(null, E('p', {}, tr3('🔓 UDP/443 restaurado e liberado!', '🔓 UDP/443 restored and unblocked!', '🔓 ¡UDP/443 restaurado y liberado!')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Restaurar / Liberar', 'Restore / Unblock', 'Restaurar / Liberar'))
						])
					]),
					// Row 3: IPTV Multicast (mcproxy / igmpproxy)
					E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding:10px 12px; background:' + (igmpEn ? '#f0fdf4' : '#f8fafc') + '; border:1px solid ' + (igmpEn ? '#86efac' : '#e2e8f0') + '; border-radius:8px;' }, [
						E('div', {}, [
							E('div', { 'style': 'display:flex; align-items:center; gap:8px; flex-wrap:wrap;' }, [
								E('strong', { 'style': 'font-size:13px;' }, '📺 IPTV Multicast (mcproxy / IGMPv3)'),
								E('span', { 'class': 'p-badge ' + (igmpEn ? 'p-badge-on' : 'p-badge-off') },
									igmpEn ? tr3('● LIGADO (IGMPv3 + SNOOPING ATIVO)', '● ENABLED (IGMPv3 + SNOOPING ON)', '● ENCENDIDO (IGMPv3 + SNOOPING ACTIVO)') : tr3('○ DESLIGADO', '○ DISABLED', '○ APAGADO'))
							]),
							E('div', { 'style': 'font-size:11px; color:#64748b; margin-top:2px;' }, tr3('Roteia pacotes IGMPv2/v3 entre WAN e br-lan com conversão Multicast-to-Unicast no Wi-Fi', 'Routes IGMPv2/v3 packets between WAN and br-lan with Wi-Fi Multicast-to-Unicast conversion', 'Enruta paquetes IGMPv2/v3 entre WAN y br-lan con conversión Multicast-to-Unicast en Wi-Fi'))
						]),
						E('div', { 'style': 'display:flex; gap:6px;' }, [
							E('button', {
								'class': 'p-btn ' + (igmpEn ? 'p-btn-outline' : 'p-btn-primary'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (igmpEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('igmpproxy', '1').then(function() {
										ui.addNotification(null, E('p', {}, tr3('📺 IPTV Multicast (IGMPv3 + McastEnhance) ligado!', '📺 IPTV Multicast (IGMPv3 + McastEnhance) enabled!', '📺 ¡IPTV Multicast (IGMPv3 + McastEnhance) activado!')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Ligar IPTV', 'Enable IPTV', 'Encender IPTV')),
							E('button', {
								'class': 'p-btn ' + (igmpEn ? 'p-btn-danger' : 'p-btn-outline'),
								'style': 'padding:6px 11px; font-size:11.5px;' + (!igmpEn ? ' opacity:0.65;' : ''),
								'click': function() {
									callSetService('igmpproxy', '0').then(function() {
										ui.addNotification(null, E('p', {}, tr3('📺 IPTV Multicast desligado.', '📺 IPTV Multicast disabled.', '📺 IPTV Multicast desactivado.')), 'info');
										setTimeout(function() { window.location.reload(); }, 900);
									});
								}
							}, tr3('Desligar IPTV', 'Disable IPTV', 'Apagar IPTV'))
						])
					])
				])
			])
		]);
		grid.appendChild(netEnginesCard);

		// =========================================================================
		// 6. ESCUDO OPKG (REPOSITÓRIO 19.07.10 + PACOTES CRÍTICOS TRAVADOS EM HOLD)
		// =========================================================================
		var opkgOk = apps.opkg_feeds_ok === '1';
		var heldCnt = parseInt(apps.opkg_held_count || '0', 10);

		var opkgCard = E('div', { 'class': 'p-app-card' }, [
			E('div', {}, [
				E('div', { 'class': 'p-app-head' }, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'📦 6. Escudo de Pacotes OPKG & Failover Nativo de WAN',
						'📦 6. OPKG Package Shield & Native WAN Failover',
						'📦 6. Escudo de Paquetes OPKG y Failover Nativo de WAN'
					)),
					E('span', { 'class': 'p-badge ' + ((opkgOk && heldCnt > 50) ? 'p-badge-on' : 'p-badge-warn') },
						(opkgOk && heldCnt > 50) ? ('● BLINDADO (' + heldCnt + ' PKGS HOLD)') : '◐ REQUER BLINDAGEM')
				]),
				E('div', { 'class': 'p-app-sub' }, tr3(
					'1) Correção do Erro 76 do opkg update: substituímos as 76 URLs internas quebradas da Qualcomm pelos 5 repositórios oficiais archive.openwrt.org/releases/19.07.10 (arm_cortex-a7_neon-vfpv4). 2) Travamento Hold: blindamos ' + (heldCnt || 195) + ' pacotes críticos (kernel 5.4.213, kmod-*, hostapd, qca-*, sqm, wireguard, luci-base) com "hold" para impedir que instalações acidentais sobrescrevam os drivers Wi-Fi 7 ou nossas melhorias!',
					'1) Fix for opkg update Error 76: replaced the 76 dead internal Qualcomm URLs with the 5 official archive.openwrt.org/releases/19.07.10 (arm_cortex-a7_neon-vfpv4) feeds. 2) Hold Shield: locked ' + (heldCnt || 195) + ' critical packages (kernel 5.4.213, kmod-*, hostapd, qca-*, sqm, wireguard, luci-base) with "hold" so accidental upgrades never overwrite Wi-Fi 7 drivers or our patches!',
					'1) Corrección del Error 76 de opkg update: reemplazamos las 76 URLs internas muertas de Qualcomm por los 5 repositorios oficiales archive.openwrt.org/releases/19.07.10. 2) Blindaje Hold: bloqueamos ' + (heldCnt || 195) + ' paquetes críticos (kernel, kmod-*, hostapd, qca-*, sqm, wireguard) con "hold" para proteger los drivers Wi-Fi 7.'
				)),
				E('div', { 'class': 'p-stat-strip' }, [
					E('span', {}, [ E('strong', {}, 'Feeds 19.07.10: '), opkgOk ? '✅ Online (Exit Code 0)' : '⚠️ Pendente' ]),
					E('span', {}, [ E('strong', {}, tr3('Pacotes Protegidos (Hold): ', 'Protected Packages (Hold): ', 'Paquetes Protegidos (Hold): ')), String(heldCnt) ]),
					E('span', {}, [ E('strong', {}, 'WAN Ativa: '), (silicon.wisp_en === '1') ? ('WISP (' + (silicon.wisp_ssid || 'Wi-Fi') + ' · Métrica 20)') : 'Cabo 2.5G (Métrica 10)' ])
				]),
				E('div', { 'style': 'font-size:11.5px; color:#475569; background:#f1f5f9; padding:8px 10px; border-radius:6px; margin-bottom:10px;' }, tr3(
					'💡 Por que removemos o mwan3 do irmão Predator X7 5G? No X7 5G o mwan3 só existe por causa do modem 5G SIM (rmnet_data0). No T7, o failover entre Cabo WAN (Métrica 10) e WISP Wi-Fi (Métrica 20) já é feito nativamente pela tabela FIB do Kernel Linux com zero custo de CPU e 100% compatível com o acelerador SFE!',
					'💡 Why did we remove mwan3 from the sibling Predator X7 5G? On the X7 5G, mwan3 only exists for its 5G SIM modem (rmnet_data0). On the T7, failover between Ethernet WAN (Metric 10) and WISP Wi-Fi (Metric 20) is handled natively by the Linux Kernel FIB table with zero CPU overhead and 100% SFE compatibility!',
					'💡 ¿Por qué eliminamos mwan3 del hermano Predator X7 5G? En el X7 5G, mwan3 solo existe para el módem 5G SIM (rmnet_data0). ¡En el T7, el failover entre Cable WAN (Métrica 10) y WISP Wi-Fi (Métrica 20) lo realiza nativamente el Kernel Linux sin sobrecarga de CPU!'
				))
			]),
			E('div', { 'class': 'p-btn-row' }, [
				E('button', {
					'class': 'p-btn p-btn-success',
					'click': function() {
						callSetService('opkg_shield', '1').then(function() {
							ui.addNotification(null, E('p', {}, tr3('🛡️ Escudo OPKG aplicado: feeds 19.07.10 restaurados, pacotes críticos travados em HOLD e opkg update disparado!', '🛡️ OPKG Shield applied: 19.07.10 feeds restored, critical packages locked in HOLD, and opkg update triggered!', '🛡️ Escudo OPKG aplicado: repositorios 19.07.10 restaurados y paquetes críticos bloqueados en HOLD!')), 'info');
							setTimeout(function() { window.location.reload(); }, 2000);
						});
					}
				}, tr3('🛡️ Blindar Pacotes Críticos (Hold) & Rodar opkg update', '🛡️ Lock Critical Packages (Hold) & Run opkg update', '🛡️ Blindar Paquetes Críticos (Hold) y Ejecutar opkg update')),
				E('a', {
					'class': 'p-btn p-btn-outline',
					'href': L.url('admin', 'system', 'opkg')
				}, tr3('📦 Abrir Gerenciador de Software LuCI', '📦 Open LuCI Software Manager', '📦 Abrir Gestor de Software LuCI'))
			])
		]);
		grid.appendChild(opkgCard);

		// =========================================================================
		// 7. AUTO-OTIMIZADOR ESPECTRAL QUALCOMM ICM
		// =========================================================================
		var icmResultBox = E('div', { 'style': 'display:none; margin-top:10px; padding:10px 14px; background:#f0fdf4; border:1px solid #86efac; border-radius:8px; font-size:12.5px; color:#166534;' });
		var icmCard = E('div', { 'class': 'p-app-card p-app-card-full' }, [
			E('div', { 'class': 'p-app-head' }, [
				E('div', {}, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'📡 7. Auto-Otimizador Espectral Qualcomm (qca-icm + cfg80211tool ACS)',
						'📡 7. Qualcomm Spectral Auto-Optimizer (qca-icm + cfg80211tool ACS)',
						'📡 7. Auto-Optimizador Espectral Qualcomm (qca-icm + cfg80211tool ACS)'
					)),
					E('div', { 'class': 'p-app-sub', 'style': 'margin-bottom:4px;' }, tr3(
						'Analisa a telemetria física dos rádios IPQ5332 + QCN9224 (Piso de Ruído em dBm e % de Tempo Livre no Ar via Clear Channel Assessment) nas 3 bandas e sintoniza automaticamente os canais mais limpos preservando 160 MHz / 240 MHz em 5 GHz e 320 MHz em 6 GHz.',
						'Analyzes physical telemetry from IPQ5332 + QCN9224 radios (Noise Floor in dBm and % Free Airtime via Clear Channel Assessment) across all 3 bands and automatically tunes the cleanest channels while preserving 160 MHz / 240 MHz on 5 GHz and 320 MHz on 6 GHz.',
						'Analiza la telemetría física de los radios IPQ5332 + QCN9224 (Piso de Ruido en dBm y % de Tiempo Libre en el Aire) en las 3 bandas y sintoniza automáticamente los canales más limpios.'
					))
				]),
				E('span', { 'class': 'p-badge p-badge-on' }, '● QUALCOMM ICM + hostapd ' + (apps.hapd_ver || 'v2.11'))
			]),
			icmResultBox,
			E('div', { 'class': 'p-btn-row' }, [
				E('button', {
					'class': 'p-btn p-btn-primary',
					'click': function(ev) {
						var btn = ev.currentTarget;
						btn.disabled = true;
						btn.textContent = tr3('⏳ Medindo piso de ruído e CCA nas 3 bandas...', '⏳ Measuring noise floor and CCA across 3 bands...', '⏳ Midiendo piso de ruido y CCA en las 3 bandas...');
						callOptimizeChannels().then(function(r) {
							btn.disabled = false;
							btn.textContent = tr3('🚀 Escanear Ruído & Otimizar Canais Agora', '🚀 Scan Noise & Optimize Channels Now', '🚀 Escanear Ruido y Optimizar Canales Ahora');
							if (r && r.success) {
								icmResultBox.style.display = 'block';
								icmResultBox.innerHTML = '<strong>✅ ' + tr3('Otimização Espectral Concluída:', 'Spectral Optimization Completed:', 'Optimización Espectral Completada:') + '</strong> ' +
									'2.4 GHz → <b>CH ' + r.ch0 + '</b> (NF ' + r.nf0 + ' dBm · ' + r.free0 + '% Free) &nbsp;|&nbsp; ' +
									'5 GHz → <b>CH ' + r.ch1 + '</b> (NF ' + r.nf1 + ' dBm · ' + r.free1 + '% Free) &nbsp;|&nbsp; ' +
									'6 GHz → <b>CH ' + r.ch2 + '</b> (NF ' + r.nf2 + ' dBm · ' + r.free2 + '% Free)';
							}
						});
					}
				}, tr3('🚀 Escanear Ruído & Otimizar Canais Agora', '🚀 Scan Noise & Optimize Channels Now', '🚀 Escanear Ruido y Optimizar Canales Ahora'))
			])
		]);
		grid.appendChild(icmCard);

		// =========================================================================
		// 8. DIAGNÓSTICO DE ROTA, MTU REAL (PMTU) & LINK FÍSICO 2.5G
		// =========================================================================
		var iperfRun = apps.iperf_running === '1';
		var selDiagTarget = E('select', {}, [
			E('option', { 'value': '1.1.1.1' }, '1.1.1.1 (Cloudflare Anycast)'),
			E('option', { 'value': '8.8.8.8' }, '8.8.8.8 (Google Public DNS)'),
			E('option', { 'value': '9.9.9.9' }, '9.9.9.9 (Quad9 Security)'),
			E('option', { 'value': '192.168.76.1' }, '192.168.76.1 (Pilha Local T7 br-lan)')
		]);
		var inDiagCustom = E('input', {
			'type': 'text',
			'placeholder': tr3('Ou digite IP/Domínio (opcional)', 'Or enter custom IP/Host (optional)', 'O ingrese IP/Dominio (opcional)')
		});
		var selDiagSize = E('select', {}, [
			E('option', { 'value': '1500' }, '1500 Bytes (Padrão Fibra / Ethernet / WISP)'),
			E('option', { 'value': '1492' }, '1492 Bytes (Padrão PPPoE Operadoras)'),
			E('option', { 'value': '1420' }, '1420 Bytes (Padrão Túnel WireGuard VPN)'),
			E('option', { 'value': '1280' }, '1280 Bytes (Mínimo Oficial IPv6 RFC 8200)')
		]);

		var diagSummaryBanner = E('div', {
			'style': 'display:none; margin-top:10px; padding:10px 14px; background:#f0fdf4; border:1px solid #86efac; border-radius:8px; font-size:12.5px; color:#166534;'
		});
		var diagTerminal = E('pre', {
			'style': 'display:none; margin-top:10px; padding:12px 14px; background:#0f172a; color:#38bdf8; border-radius:8px; font-family:monospace; font-size:12px; line-height:1.45; overflow-x:auto; max-height:300px; white-space:pre-wrap;'
		});

		var diagCard = E('div', { 'class': 'p-app-card p-app-card-full' }, [
			E('div', { 'class': 'p-app-head' }, [
				E('div', {}, [
					E('h3', { 'class': 'p-app-title' }, tr3(
						'📏 8. Raio-X de MTU Real da Internet (tracepath PMTU), Porta 2.5G (ethtool 5.10) & iperf 2.0.13',
						'📏 8. Real Internet Path MTU X-Ray (tracepath PMTU), 2.5G Port (ethtool 5.10) & iperf 2.0.13',
						'📏 8. Rayos-X de MTU Real de Internet (tracepath PMTU), Puerto 2.5G (ethtool 5.10) e iperf 2.0.13'
					)),
					E('div', { 'class': 'p-app-sub', 'style': 'margin-bottom:4px;' }, tr3(
						'Dispara pacotes com a trava "Don\'t Fragment" (DF=1) usando o motor iputils-tracepath v20210202 para descobrir o MTU real (PMTU) de ponta a ponta e identificar gargalos de PPPoE (1492), CGNAT ou VPN (1420). O ajuste automático TCP MSS Clamping (mtu_fix=1) já roda 100% sozinho no firewall do T7.',
						'Sends packets with the "Don\'t Fragment" (DF=1) bit using iputils-tracepath v20210202 to discover end-to-end Path MTU (PMTU) and detect PPPoE (1492), CGNAT, or VPN (1420) bottlenecks. Automatic TCP MSS Clamping (mtu_fix=1) runs 24/7 in the T7 firewall.',
						'Envía paquetes con el bit "Don\'t Fragment" (DF=1) usando iputils-tracepath v20210202 para descubrir el MTU real (PMTU) de extremo a extremo. El ajuste automático TCP MSS Clamping (mtu_fix=1) ya funciona solo 24/7.'
					))
				]),
				E('div', { 'style': 'display:flex; gap:6px; flex-wrap:wrap;' }, [
					E('span', { 'class': 'p-badge p-badge-on' }, tr3('● TCP MSS CLAMPING AUTOMÁTICO ATIVO', '● AUTO TCP MSS CLAMPING ACTIVE', '● TCP MSS CLAMPING AUTOMÁTICO ACTIVO')),
					E('span', { 'class': 'p-badge ' + (iperfRun ? 'p-badge-on' : 'p-badge-off') },
						iperfRun ? '● IPERF :5001 ATIVO' : '○ IPERF :5001 STANDBY')
				])
			]),
			E('div', { 'class': 'p-form-grid', 'style': 'margin-top:8px;' }, [
				E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Servidor Alvo (Destino):', 'Target Server:', 'Servidor Destino:')), selDiagTarget ]),
				E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Host/IP Customizado (Opcional):', 'Custom Host/IP (Optional):', 'Host/IP Personalizado (Opcional):')), inDiagCustom ]),
				E('div', { 'class': 'p-field' }, [ E('label', {}, tr3('Tamanho Inicial do Pacote (DF=1):', 'Initial Packet Size (DF=1):', 'Tamaño Inicial del Paquete (DF=1):')), selDiagSize ])
			]),
			diagSummaryBanner,
			diagTerminal,
			E('div', { 'class': 'p-btn-row' }, [
				E('button', {
					'class': 'p-btn p-btn-primary',
					'click': function(ev) {
						var btn = ev.currentTarget;
						var origTxt = btn.textContent;
						var tgt = (inDiagCustom.value || '').trim() || selDiagTarget.value || '1.1.1.1';
						var sz = selDiagSize.value || '1500';
						btn.disabled = true;
						btn.textContent = tr3('⏳ Medindo saltos e PMTU até ' + tgt + '...', '⏳ Probing hops and PMTU to ' + tgt + '...', '⏳ Midiendo saltos y PMTU hacia ' + tgt + '...');
						callRunNetDiag('pmtu', tgt, sz).then(function(r) {
							btn.disabled = false;
							btn.textContent = origTxt;
							if (r && r.success) {
								var p = parseInt(r.pmtu || '1500', 10);
								var verdict = tr3('1500 bytes (Caminho Limpo Sem Fragmentação)', '1500 bytes (Clean Path Without Fragmentation)', '1500 bytes (Ruta Limpia Sin Fragmentación)');
								if (p === 1492) verdict = tr3('1492 bytes (Enlace PPPoE detectado — protegido pelo MSS Clamping)', '1492 bytes (PPPoE link detected — protected by MSS Clamping)', '1492 bytes (Enlace PPPoE detectado — protegido por MSS Clamping)');
								else if (p <= 1420) verdict = p + tr3(' bytes (Túnel VPN / Encapsulamento detectado — protegido pelo MSS Clamping)', ' bytes (VPN Tunnel / Encapsulation detected — protected by MSS Clamping)', ' bytes (Túnel VPN detectado — protegido por MSS Clamping)');
								else if (p < 1500) verdict = p + tr3(' bytes (Redução de MTU na rota da operadora — protegido pelo MSS Clamping)', ' bytes (Carrier MTU reduction — protected by MSS Clamping)', ' bytes (Reducción de MTU en operadora — protegido por MSS Clamping)');

								diagSummaryBanner.style.display = 'block';
								diagSummaryBanner.innerHTML = '<strong>✅ ' + tr3('Resultado PMTU Discovery:', 'PMTU Discovery Result:', 'Resultado PMTU Discovery:') + '</strong> ' +
									'PMTU = <b>' + verdict + '</b> &nbsp;|&nbsp; ' +
									tr3('Interface de Saída: ', 'Exit Interface: ', 'Interfaz de Salida: ') + '<b>' + (r.wan_dev || 'eth0') + '</b> (MTU ' + (r.wan_mtu || '1500') + ') &nbsp;|&nbsp; ' +
									'TCP MSS Clamping: <b>' + tr3('Ativo (Automático)', 'Active (Automatic)', 'Activo (Automático)') + '</b>';
								diagTerminal.style.display = 'block';
								diagTerminal.textContent = r.output || '';
							}
						});
					}
				}, tr3('📏 Testar MTU Real da Internet (tracepath PMTU)', '📏 Test Real Internet MTU (tracepath PMTU)', '📏 Probar MTU Real de Internet (tracepath PMTU)')),
				E('button', {
					'class': 'p-btn p-btn-outline',
					'click': function(ev) {
						var btn = ev.currentTarget;
						var origTxt = btn.textContent;
						btn.disabled = true;
						btn.textContent = tr3('⏳ Lendo registradores NBASE-T 2.5G...', '⏳ Reading 2.5G NBASE-T registers...', '⏳ Leyendo registros NBASE-T 2.5G...');
						callRunNetDiag('ethtool', '', '').then(function(r) {
							btn.disabled = false;
							btn.textContent = origTxt;
							if (r && r.success) {
								diagSummaryBanner.style.display = 'block';
								diagSummaryBanner.innerHTML = '<strong>🔌 ' + tr3('Inspeção Física da Porta 2.5G (ethtool v5.10) & Offloads GSO/GRO Concluída', '2.5G Port Physical Inspection (ethtool v5.10) & GSO/GRO Offloads Completed', 'Inspección Física del Puerto 2.5G (ethtool v5.10) Completada') + '</strong>';
								diagTerminal.style.display = 'block';
								diagTerminal.textContent = r.output || '';
							}
						});
					}
				}, tr3('🔌 Raio-X da Porta 2.5G (ethtool 5.10)', '🔌 2.5G Port X-Ray (ethtool 5.10)', '🔌 Rayos-X del Puerto 2.5G (ethtool 5.10)')),
				E('button', {
					'class': 'p-btn ' + (iperfRun ? 'p-btn-danger' : 'p-btn-success'),
					'click': function() {
						callRunNetDiag(iperfRun ? 'iperf_stop' : 'iperf_start', '', '').then(function(r) {
							if (r && r.success) {
								diagSummaryBanner.style.display = 'block';
								diagSummaryBanner.innerHTML = '<strong>🚀 iperf v2.0.13 Multi-Thread (pthreads):</strong> ' + (r.output || '').replace(/\n/g, '<br>');
								setTimeout(function() { window.location.reload(); }, 1800);
							}
						});
					}
				}, iperfRun ? tr3('⏹️ Parar Servidor iperf (:5001)', '⏹️ Stop iperf Server (:5001)', '⏹️ Detener Servidor iperf (:5001)') : tr3('🚀 Ligar Servidor iperf 2.0.13 (:5001)', '🚀 Start iperf 2.0.13 Server (:5001)', '🚀 Iniciar Servidor iperf 2.0.13 (:5001)'))
			])
		]);
		grid.appendChild(diagCard);

		root.appendChild(grid);
		return root;
	}
});
