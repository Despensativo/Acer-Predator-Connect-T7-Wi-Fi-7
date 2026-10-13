'use strict';
'require view';
'require rpc';
'require ui';
'require poll';
'require dom';

var callGetStatus = rpc.declare({
	object: 'predator',
	method: 'get_status',
	expect: {}
});

var callApplyTopology = rpc.declare({
	object: 'predator',
	method: 'apply_topology',
	params: ['mode', 'ssid', 'key', 'ssid_6g'],
	expect: { success: false }
});

var callToggleFeature = rpc.declare({
	object: 'predator',
	method: 'toggle_feature',
	params: ['feature', 'value'],
	expect: { success: false }
});

var callSetRadio = rpc.declare({
	object: 'predator',
	method: 'set_radio',
	params: ['device', 'channel', 'htmode', 'txpower'],
	expect: { success: false }
});

var callSetAllRadios = rpc.declare({
	object: 'predator',
	method: 'set_all_radios',
	params: ['wifi0', 'wifi1', 'wifi2'],
	expect: { success: false }
});

var callEditVif = rpc.declare({
	object: 'predator',
	method: 'edit_vif',
	params: ['section', 'ssid', 'key', 'encryption'],
	expect: { success: false }
});

var callAddVif = rpc.declare({
	object: 'predator',
	method: 'add_vif',
	params: ['ssid', 'key', 'encryption', 'band_2g', 'band_5g', 'band_6g', 'is_guest', 'is_mld', 'zone'],
	expect: { success: false }
});

var callDelVif = rpc.declare({
	object: 'predator',
	method: 'del_vif',
	params: ['section'],
	expect: { success: false }
});

var callToggleVif = rpc.declare({
	object: 'predator',
	method: 'toggle_vif',
	params: ['section', 'disabled'],
	expect: { success: false }
});

var callRestartWifi = rpc.declare({
	object: 'predator',
	method: 'restart_wifi',
	expect: { success: false }
});

var callToggleRadio = rpc.declare({
	object: 'predator',
	method: 'toggle_radio',
	params: ['device', 'disabled'],
	expect: { success: false }
});

var callGetGuardStatus = rpc.declare({
	object: 'predator',
	method: 'get_guard_status',
	expect: {}
});

var callAckGuard = rpc.declare({
	object: 'predator',
	method: 'ack_guard',
	expect: { success: false }
});

var I18N = {
	en: {
		app_title: 'Predator Connect T7 - Wi-Fi 7 & MLO Center',
		app_descr: 'Comprehensive network manager for the Qualcomm IPQ5332 Tri-Band hardware. Switch recommended topology profiles, tune frequency channels, and configure single, dual, or tri-band networks.',
		active_profile: 'Active Wi-Fi Topology Profile',
				ports_title: 'Physical Ethernet Ports (Cable Status)',
		wan_port_label: 'WAN Port (Internet)',
		lan1_port_label: 'LAN 1 Port',
		lan2_port_label: 'LAN 2 Port',
		port_connected: 'Connected',
		port_disconnected: 'No Cable / Disconnected',
		wpa3_mandatory_notice: 'WPA3 Mandatory',
		radios_title: 'Qualcomm Hardware Radio Settings',
		networks_title: 'Configured Wi-Fi Networks',
		btn_add_network: '➕ Add New Wi-Fi Network',
		
		topo1_title: '1. UNIFIED SMART ROAMING (2.4G + 5G Unified | 6G Dedicated)',
		topo1_desc: '2.4 GHz and 5 GHz share the same SSID with hardware 802.11k/v roaming (BSS Transition & Neighbor Reports). Devices automatically connect to 5 GHz (160 MHz) when nearby and seamlessly transition to 2.4 GHz at long distances with zero drop. 6 GHz (Wi-Fi 7) operates dedicated for ultra-high-speed gaming (up to 5,760 Mbps). 100% safe for 2.4 GHz IoT smart devices.',
		topo1_btn: '🚀 1. Unified Roaming (2.4G+5G | 6G)',
		topo1_tip: 'Same SSID on 2.4G & 5G with 802.11k/v roaming + Dedicated 6G',
		topo1_box_title: '🚀 Unified Smart Roaming Architecture',
		topo1_box_desc: 'Bands 2.4 GHz and 5 GHz are combined under a single network name. Qualcomm hardware 802.11k/v automatically assists devices to roam to 5 GHz (160 MHz) when close to the router, and falls back to 2.4 GHz when moving away. 6 GHz remains dedicated for maximum throughput without contention.',

		topo2_title: '2. MLO TURBO WI-FI 7 (5 GHz + 6 GHz MLD | 2.4 GHz IoT Dedicated) [Recommended]',
		topo2_desc: 'The Golden Standard for Wi-Fi 7: 5 GHz (160 MHz) and 6 GHz (320 MHz) are aggregated into a single Multi-Link Device (MLD) with WPA3-SAE, enabling simultaneous dual-band transmission and 0ms instantaneous handoff. 2.4 GHz operates as an independent WPA2 network (_2.4GHz) to protect 100% of IoT smart devices (bulbs, plugs, switches) from WPA3-only lockouts.',
		topo2_btn: '⚡ 2. MLO Turbo (5G+6G MLD | 2.4G IoT)',
		topo2_tip: 'Wi-Fi 7 Multi-Link aggregation (5G + 6G) with independent 2.4G IoT safety',
		topo2_box_title: '⭐ Wi-Fi 7 Golden Architecture (Recommended)',
		topo2_box_desc: 'Ultra-fast 5 GHz and 6 GHz bands form a unified Multi-Link Device (MLD). Modern Wi-Fi 7 devices transmit simultaneously across both channels, delivering Gigabit+ speeds with zero roaming drops. The 2.4 GHz band remains isolated in pure WPA2, ensuring 100% of your smart home devices (Tuya, Sonoff, Shelly) stay connected.',

		topo3_title: '3. FULL TRI-BAND MLO (2.4G + 5G + 6G Aggregated) [IoT & Stability Warning]',
		topo3_desc: 'All 3 frequency bands aggregated into a single MLD. WARNING: Mandates pure WPA3-SAE across all bands, disconnecting 99% of 2.4 GHz IoT devices. Internal SoC-to-PCIe driver grouping may cause driver instability.',
		topo3_btn: '⚠️ 3. Full Tri-Band MLO (Experimental)',
		topo3_tip: 'Aggregates all 3 bands under WPA3. Breaks most 2.4G IoT smart devices!',
		topo3_box_title: '⚠️ CRITICAL WARNING: IoT Incompatibility & Driver Stability',
		topo3_box_desc: 'The IEEE 802.11be standard strictly requires WPA3-SAE with Protected Management Frames (PMF) on ALL links of an MLD. Grouping 2.4 GHz into the MLD forces 2.4 GHz to pure WPA3, immediately breaking 99% of smart home automation devices (smart bulbs, sockets, ESP8266/ESP32, Sonoff/Tuya). Additionally, grouping the internal SoC radios with the external PCIe radio is experimental on Qualcomm QSDK. Use only for testing with pure Wi-Fi 7 client devices.',

		topo4_title: '4. INDEPENDENT TRI-BAND (3 Separate Dedicated Networks)',
		topo4_desc: 'Each frequency operates on its own dedicated network (_2.4GHz, _5GHz, _6GHz). Complete manual control over which device connects to which radio. No automatic band roaming.',
		topo4_btn: '📡 4. Separate Bands (2.4G / 5G / 6G)',
		topo4_tip: '3 separate networks with manual band selection',
		topo4_box_title: '📡 Independent Manual Band Architecture',
		topo4_box_desc: 'Creates 3 distinct Wi-Fi networks (_2.4GHz, _5GHz, _6GHz). Allows you to manually assign devices to specific radios. No automatic inter-band roaming is performed by the router.',

		topo5_title: '5. UNIFIED SINGLE SSID TRI-BAND (Same Name & Password across 2.4G + 5G + 6G)',
		topo5_desc: 'One single network name and password for the entire home. 2.4 GHz operates in pure WPA2 for 100% smart home IoT compatibility, 5 GHz in WPA2/WPA3 mixed as an intelligent bridge, and 6 GHz in pure WPA3-SAE for gigabit speed. Seamless 802.11k/v roaming across all 3 bands.',
		topo5_btn: '🔄 5. Unified Single SSID (2.4G+5G+6G)',
		topo5_tip: 'Same Wi-Fi name & password on all 3 radios with pure WPA2 IoT on 2.4G',
		topo5_box_title: '🔄 Unified Single SSID Tri-Band Architecture (All-in-One)',
		topo5_box_desc: 'Broadcasts a single unified Wi-Fi name across 2.4 GHz, 5 GHz, and 6 GHz. Radio 2.4 GHz is locked to pure WPA2-PSK (psk2+aes) to guarantee that 100% of smart bulbs, sockets, and IoT sensors connect effortlessly. Radio 5 GHz operates in WPA2/WPA3 Mixed mode to serve as a seamless bridge, and Radio 6 GHz runs pure WPA3-SAE. Hardware 802.11k/v assists your smartphones and laptops to roam to the fastest frequency available.',

		mld_group_label: 'High-Stability Multi-Band Operation',
		mld_group_help: 'Additional networks broadcast across selected bands with 802.11k/v roaming. Wi-Fi 7 MLO (Multi-Link Operation) is exclusive to the Primary Network and is configured via "Profile 4: MLO Turbo" in the top Topology card.',

		radio0_title: 'Radio 0: 2.4 GHz',
		radio1_title: 'Radio 1: 5 GHz',
		radio2_title: 'Radio 2: 6 GHz (Wi-Fi 7)',
		radio_chan: 'Frequency Channel',
		radio_adv_chan: 'Show advanced / DFS / intermediate channels',
		radio_width: 'Channel Width (Bandwidth)',
		radio_txpower: 'Transmit Power (Tx Power)',
		radio_save: 'Save Radio',
		radio_saving: 'Saving Radio...',
		radio0_note: '💡 Channels 1, 6, and 11 are the only non-overlapping channels in 2.4 GHz.',
		radio1_note: '💡 DFS channels (52-140) require radar monitoring. If radar is detected, Wi-Fi temporarily silences to switch channels.',
		radio2_note: '💡 PSC channels (Preferred Scanning Channels: 37, 53, 69...) are the only ones scanned natively by Wi-Fi 6E/7 smartphones.',
		auto_rec: 'Auto (Recommended)',
		auto_psc_rec: 'Auto PSC (Recommended for Smartphones and PCs)',

		th_ssid: 'Network Name (SSID)',
		th_freq: 'Frequency',
		th_pass: 'Wi-Fi Password',
		th_enc: 'Security',
		th_type: 'Type',
		th_status: 'Status',
		th_actions: 'Actions',

		status_on: '🟢 Enabled',
		status_off: '🔴 Disabled',
		type_guest: 'Guest',
		type_main: 'Main (LAN)',
		pass_open: 'No Password (Open)',
		badge_core: '🔒 Primary',
		badge_core_tip: 'This is one of the 3 primary physical router antennas and cannot be deleted, only edited or disabled.',
		btn_turn_on: '▶ Enable',
		btn_turn_off: '⏸ Disable',
		btn_edit: '✏️ Edit',
		btn_delete: '🗑 Delete',
		btn_view_pass: '👁 View',
		btn_hide_pass: '🙈 Hide',
		btn_cancel: 'Cancel',
		btn_save_changes: 'Save Changes',
		btn_apply_profile: 'Confirm & Apply Profile',
		btn_create_network: 'Create Network',

		modal_edit_title: '✏️ Edit Wi-Fi Network',
		modal_add_title: '➕ Add New Wi-Fi Network',
		modal_reload_title: 'Applying changes...',
		modal_reload_msg: 'The Qualcomm Wi-Fi 7 subsystem is restarting and reconfiguring radios. Please wait for automatic reconnection without closing the browser...',
		reload_syncing_subsystem: 'Syncing Qualcomm Wi-Fi 7 Subsystem',
		reload_step_1: 'Step 1/3: Writing RF parameters to hardware registers...',
		reload_step_2: 'Step 2/3: Initializing multi-link daemons and locking frequencies...',
		reload_step_3: 'Step 3/3: Validating radio links and EIRP status...',
		reload_ready: 'All Radios Online!',
		reload_ready_msg: 'Hardware reconfigured successfully. Refreshing page...',
		reload_finalizing: 'Finalizing and reloading...',
		base_name_label: 'Base Name (2.4G + 5G)',
		unified_ssid_label: 'Unified Network Name (SSID)',
		ssid_6g_label: '6 GHz Network Name (Pure Wi-Fi 7)',
		pass_pulled_label: 'Wi-Fi Password (Read from router)',
		pass_placeholder: 'WPA2/WPA3 Password',
		pass_min_digits: 'Password (min. 8 characters)',
		antennas_label: 'Transmit Antennas / Frequencies',
		guest_label: 'Guest Network:',
		guest_desc: 'Isolate clients (Internet only, no access to local devices)',
		wpa3_required_note: '🔒 Pure WPA3-SAE Required: This radio operates in 6 GHz or is part of a Wi-Fi 7 MLO group, which strictly requires WPA3 under international standards.',
		wpa3_optional_note: '💡 This radio operates outside MLO. You can select mixed WPA2/WPA3 for maximum compatibility.',
		wpa3_sae_pure_req: 'WPA3-SAE Pure (Required)',
		wpa2_wpa3_mixed: 'WPA2/WPA3 Personal Mixed (Recommended - All devices)',
		wpa3_sae_pure: 'WPA3-SAE Pure (Maximum Security)',
		owe_open: 'OWE Enhanced Open (Secure Open Wi-Fi 6/7)',
		wpa2_psk_legacy: 'WPA2-PSK (Legacy - 2.4/5 GHz only)',
		open_no_pass: 'Open Network (No Password)',
		del_confirm: 'Are you sure you want to permanently DELETE the network "%s"?',
		err_ssid_empty: 'Network name (SSID) cannot be empty.',
		err_ssid_max: 'Network name (SSID) cannot exceed 32 characters.',
		err_ssid_chars: 'Network name contains invalid characters (\' " ` ; \\).',
		err_pass_min: 'Password must be at least 8 characters.',
		err_pass_max: 'Password cannot exceed 63 characters.',
		err_pass_required: 'Password is required for encrypted networks.',
		warn_clients_disconnect: 'Warning: %s connected device(s) will be temporarily disconnected during profile switch.',
		guard_banner_title: 'Predator Wi-Fi Guard Protection',
		guard_rollback_msg: 'The previous Wi-Fi configuration failed to start (%s) and was automatically reverted to the last working setup.',
		guard_heal_msg: 'Wi-Fi subsystem encountered a temporary stall (%s) and was recovered with a clean restart.',
		guard_btn_dismiss: 'Dismiss',
		guard_unknown_reason: 'radios did not report healthy state',
		err_select_antenna: 'Please select at least one frequency / radio antenna.',
		status_switching: 'Switching Network Status...',
		deleting_network: 'Deleting Network...',
		creating_network: 'Creating New Wi-Fi Network...',
		applying_profile: 'Applying Topology Profile...',
		btn_save_all_radios: '💾 Save All Radios',
		radio_saving_all: 'Saving and applying settings across all 3 radios...',
		btn_restart_wifi: '🔄 Restart Wi-Fi (Unlock Subsystem)',
		btn_restarting_wifi: 'Restarting & Unlocking Wi-Fi...',
		modal_restart_wifi_title: '🔄 Restarting Wi-Fi Subsystem',
		modal_restart_wifi_msg: 'Removing lock files, ensuring primary antennas, and reloading the Qualcomm Wi-Fi driver. Please wait...',
		radio_status_online: '● Online',
		radio_status_starting: '⏳ Initializing / Calibrating...',
		radio_status_offline: '⚠️ Offline / Stalled',
		radio_status_locked: '⚠️ Stalled (/var/run/wifilock)',
		radio_status_disabled: '○ Disabled',
		radio_btn_disable: '⏸ Disable Radio',
		radio_btn_enable: '▶ Enable Radio',
		lock_badge_clean: 'Subsystem Free (No Deadlocks)',
		lock_badge_locked: 'Subsystem Lock Active (/var/run/wifilock)',
		width_80m_rec: '80 MHz (Recommended - Instant Boot without DFS)',
		width_160m_fast: '160 MHz (Ultra Fast - Requires ~60s DFS Check)',
		dfs_alert_title: '⚠️ DFS (Radar) Notice on 160 MHz:',
		dfs_alert_body: 'Operating 160 MHz in 5 GHz utilizes shared radar channels (DFS 52–64). Regulatory standards (IEEE 802.11h / Anatel / FCC) mandate a silent ~60-second radar check during boot or reload before transmitting.',
		dfs_alert_tip: '💡 Tip: 160 MHz enables links up to 2,402 Mbps on compatible devices. For instant zero-second boot, select 80 MHz.',
		tx_auto_22: 'Auto (Recommended - 22 dBm)',
		tx_auto_23: 'Auto (Recommended - 23 dBm)',
		tx_auto_20: 'Auto (Recommended - 20 dBm)',
		tx_economic: 'Economical',
		tx_active_router: '(Active on Router)',
		tx_22_desc: '22 dBm (Max Hardware Power | 158 mW Conducted / 708 mW EIRP)',
		tx_23_desc: '23 dBm (Max Power in 160M | 200 mW Conducted / 2,180 mW EIRP)',
		tx_26_desc: '26 dBm (Max Power in 80M Ch 149+ | 398 mW Conducted / 5,495 mW EIRP)',
		tx_20_desc: '20 dBm (Max Unlocked 320M | 100 mW Conducted / ~1 W EIRP)'
	},
	pt_br: {
		app_title: 'Predator Connect T7 - Central Wi-Fi 7 & MLO',
		app_descr: 'Gerenciador completo de rede para o hardware Tri-Band Qualcomm IPQ5332. Alterne perfis de topologia recomendados, ajuste canais recomendados ou avançados/DFS e crie redes monobanda, duais ou triplas.',
		active_profile: 'Perfil de Topologia Wi-Fi Atual',
				ports_title: 'Portas Físicas Ethernet (Status dos Cabos)',
		wan_port_label: 'Porta WAN (Internet)',
		lan1_port_label: 'Porta LAN 1',
		lan2_port_label: 'Porta LAN 2',
		port_connected: 'Conectado',
		port_disconnected: 'Sem Cabo / Desconectado',
		wpa3_mandatory_notice: 'WPA3 Obrigatório',
		radios_title: 'Ajustes Físicos dos Rádios Qualcomm',
		networks_title: 'Redes Wi-Fi Configuradas',
		btn_add_network: '➕ Adicionar Nova Rede Wi-Fi',

		topo1_title: '1. VELOCIDADE MÁXIMA & ROAMING UNIFICADO (2.4G + 5G Unificados | 6G Dedicado)',
		topo1_desc: '2.4 GHz e 5 GHz compartilham o mesmo nome (SSID) com suporte a roaming 802.11k/v por hardware. Dispositivos migram dinamicamente para 5 GHz (160 MHz) perto do roteador e caem para 2.4 GHz em longas distâncias sem quedas. 6 GHz (Wi-Fi 7) opera dedicado para velocidade máxima gamer (até 5.760 Mbps). 100% seguro para automação IoT.',
		topo1_btn: '🚀 1. Roaming Unificado (2.4G+5G | 6G)',
		topo1_tip: 'Mesmo SSID no 2.4G e 5G com roaming 802.11k/v + 6G Dedicado',
		topo1_box_title: '🚀 Arquitetura de Roaming Unificado Inteligente',
		topo1_box_desc: 'As bandas de 2.4 GHz e 5 GHz são unificadas sob o mesmo nome de rede com 802.11k/v. Celulares e notebooks são guiados automaticamente para os 5 GHz (160 MHz) quando próximos e comutam suavemente para 2.4 GHz quando distantes. O rádio de 6 GHz opera isolado para garantir o máximo rendimento sem interferências.',

		topo2_title: '2. MODO MLO TURBO WI-FI 7 (5 GHz + 6 GHz MLD | 2.4 GHz IoT Dedicado) [Recomendado]',
		topo2_desc: 'O Padrão Ouro do Wi-Fi 7: 5 GHz (160 MHz) e 6 GHz (320 MHz) são agregados em uma única entidade MLD com WPA3-SAE, permitindo transmissão simultânea em dois canais e transição instantânea com 0 ms de atraso. O 2.4 GHz opera como rede independente (_2.4GHz) em WPA2 puro para proteger 100% dos dispositivos IoT (lâmpadas, tomadas, interruptores) contra bloqueios do WPA3.',
		topo2_btn: '⚡ 2. MLO Turbo (5G+6G MLD | 2.4G IoT)',
		topo2_tip: 'Agregação Wi-Fi 7 MLO (5G + 6G) com 2.4G independente para IoT',
		topo2_box_title: '⭐ Arquitetura Wi-Fi 7 Padrão Ouro (Recomendado)',
		topo2_box_desc: 'As duas frequências ultrarrápidas (5 GHz e 6 GHz) formam um grupo Multi-Link Device (MLD). Dispositivos Wi-Fi 7 modernos transmitem simultaneamente nos dois rádios, atingindo velocidades gigabit com transição sem nenhuma perda de pacotes. A banda 2.4 GHz permanece isolada em WPA2 puro, garantindo que 100% dos aparelhos de automação (Tuya, Sonoff, Shelly) continuem funcionando.',

		topo3_title: '3. MLO TRI-BAND TOTAL (2.4G + 5G + 6G Agregados) [Alerta IoT & Instabilidade]',
		topo3_desc: 'Os 3 rádios agregados no mesmo grupo MLD. ALERTA: Obriga WPA3-SAE puro em todas as bandas, desconectando 99% dos aparelhos IoT 2.4 GHz. A comunicação interna do driver Qualcomm entre o SoC e a placa PCIe pode causar instabilidade.',
		topo3_btn: '⚠️ 3. MLO Tri-Band (Experimental)',
		topo3_tip: 'Agrega as 3 bandas com WPA3. Incompatível com lâmpadas e tomadas IoT!',
		topo3_box_title: '⚠️ ALERTA CRÍTICO: Incompatibilidade com IoT e Estabilidade do Driver',
		topo3_box_desc: 'O padrão IEEE 802.11be exige WPA3-SAE com PMF obrigatório em todas as frequências de um grupo MLD. Incluir a banda 2.4 GHz força essa frequência para WPA3 puro, desconectando imediatamente 99% dos aparelhos inteligentes (lâmpadas, tomadas, interruptores Sonoff/Tuya/ESP32). Além disso, o driver Qualcomm QSDK do IPQ5332 apresenta instabilidade ao agregar os rádios do SoC com o rádio PCIe. Recomendado apenas para bancadas de teste com clientes Wi-Fi 7 puros.',

		topo4_title: '4. MODO INDEPENDENTE (3 Redes Wi-Fi Separadas)',
		topo4_desc: 'Cada frequência opera em sua própria rede dedicada (_2.4GHz, _5GHz, _6GHz). Controle manual total sobre qual dispositivo conecta em cada antena. Sem roaming automático entre bandas.',
		topo4_btn: '📡 4. Redes Separadas (2.4G / 5G / 6G)',
		topo4_tip: '3 redes separadas com escolha manual de banda',
		topo4_box_title: '📡 Arquitetura de Redes Independentes',
		topo4_box_desc: 'Cria 3 redes Wi-Fi separadas (_2.4GHz, _5GHz, _6GHz). Permite escolher manualmente em qual rádio cada cliente se conecta. Nenhum roaming automático entre bandas é realizado pelo roteador.',

		topo5_title: '5. REDE ÚNICA TRI-BAND (Mesmo Nome e Senha no 2.4G + 5G + 6G)',
		topo5_desc: 'Um único nome de rede e senha para a casa inteira. O 2.4 GHz opera em WPA2 puro para 100% de compatibilidade com lâmpadas e tomadas IoT, o 5 GHz em WPA2/WPA3 Misto como ponte inteligente, e o 6 GHz em WPA3-SAE puro para velocidade gigabit. Roaming 802.11k/v suave entre as 3 frequências.',
		topo5_btn: '🔄 5. Rede Única (2.4G+5G+6G)',
		topo5_tip: 'Mesmo nome e senha nas 3 bandas com 2.4G em WPA2 puro para IoT',
		topo5_box_title: '🔄 Arquitetura de Rede Única Tri-Band (Tudo-em-Um)',
		topo5_box_desc: 'Transmite o mesmo nome de rede Wi-Fi e a mesma senha em 2.4 GHz, 5 GHz e 6 GHz. A banda 2.4 GHz fica em WPA2-PSK puro (psk2+aes), garantindo que 100% dos seus aparelhos de automação (lâmpadas inteligentes Tuya, interruptores Sonoff, tomadas e câmeras) conectem de primeira sem erros de pareamento. A banda 5 GHz opera em WPA2/WPA3 misto para servir de ponte, e o 6 GHz em WPA3-SAE puro. O roteador utiliza 802.11k/v para guiar celulares e computadores para a frequência mais rápida.',

		mld_group_label: 'Operação Multi-Banda de Alta Estabilidade',
		mld_group_help: 'Redes adicionais transmitem em cada frequência selecionada com roaming inteligente 802.11k/v. O recurso Wi-Fi 7 MLO (Multi-Link Operation) é exclusivo da Rede Principal e deve ser ativado através do "Perfil 4: MLO Turbo" no painel de Topologia acima.',

		radio0_title: 'Rádio 0: 2.4 GHz',
		radio1_title: 'Rádio 1: 5 GHz',
		radio2_title: 'Rádio 2: 6 GHz (Wi-Fi 7)',
		radio_chan: 'Canal de Frequência',
		radio_adv_chan: 'Mostrar canais avançados / DFS / intermediários',
		radio_width: 'Largura de Canal (Bandwidth)',
		radio_txpower: 'Potência de Transmissão (Tx Power)',
		radio_save: 'Salvar Rádio',
		radio_saving: 'Salvando Rádio...',
		radio0_note: '💡 Canais 1, 6 e 11 são os únicos sem sobreposição espectral no 2.4 GHz.',
		radio1_note: '💡 Canais DFS (52-140) exigem monitoramento de radar. Se um radar for detectado, o roteador silencia o Wi-Fi para trocar de canal.',
		radio2_note: '💡 Canais PSC (Preferred Scanning Channels: 37, 53, 69...) são os únicos que smartphones Wi-Fi 6E/7 escutam nativamente.',
		auto_rec: 'Auto (Recomendado)',
		auto_psc_rec: 'Auto PSC (Recomendado para Celulares e PCs)',

		th_ssid: 'Nome da Rede (SSID)',
		th_freq: 'Frequência',
		th_pass: 'Senha Wi-Fi',
		th_enc: 'Criptografia',
		th_type: 'Tipo',
		th_status: 'Status',
		th_actions: 'Ações',

		status_on: '🟢 Ligada',
		status_off: '🔴 Desligada',
		type_guest: 'Convidados',
		type_main: 'Principal (LAN)',
		pass_open: 'Sem Senha (Aberta)',
		badge_core: '🔒 Principal',
		badge_core_tip: 'Esta é uma das 3 antenas físicas principais do roteador e não pode ser excluída, apenas desativada ou editada.',
		btn_turn_on: '▶ Ligar',
		btn_turn_off: '⏸ Desligar',
		btn_edit: '✏️ Editar',
		btn_delete: '🗑 Excluir',
		btn_view_pass: '👁 Ver',
		btn_hide_pass: '🙈 Ocultar',
		btn_cancel: 'Cancelar',
		btn_save_changes: 'Salvar Alterações',
		btn_apply_profile: 'Confirmar e Aplicar Perfil',
		btn_create_network: 'Criar Rede',

		modal_edit_title: '✏️ Editar Rede Wi-Fi',
		modal_add_title: '➕ Adicionar Nova Rede Wi-Fi',
		modal_reload_title: 'Aplicando alterações...',
		modal_reload_msg: 'O subsistema Wi-Fi 7 Qualcomm está reiniciando e reconfigurando os rádios. Aguarde a reconexão automática sem fechar o navegador...',
		reload_syncing_subsystem: 'Sincronizando Sub-sistema Qualcomm Wi-Fi 7',
		reload_step_1: 'Etapa 1/3: Gravando parâmetros nos registradores de RF do silício...',
		reload_step_2: 'Etapa 2/3: Inicializando daemons e travando frequências MLO...',
		reload_step_3: 'Etapa 3/3: Validando retorno dos rádios e status EIRP...',
		reload_ready: 'Todos os Rádios Online!',
		reload_ready_msg: 'Hardware reconfigurado com sucesso. Atualizando tela...',
		reload_finalizing: 'Finalizando e recarregando...',
		base_name_label: 'Nome Base (2.4G + 5G)',
		unified_ssid_label: 'Nome da Rede Unificada (SSID)',
		ssid_6g_label: 'Nome da Rede 6 GHz (Wi-Fi 7 Puro)',
		pass_pulled_label: 'Senha do Wi-Fi (Puxada do Roteador)',
		pass_placeholder: 'Senha WPA2/WPA3',
		pass_min_digits: 'Senha (mínimo 8 dígitos)',
		antennas_label: 'Antenas / Frequências Transmitidas',
		guest_label: 'Rede de Convidados (Guest):',
		guest_desc: 'Isolar clientes (Apenas Internet, sem acesso a outros aparelhos locais)',
		wpa3_required_note: '🔒 WPA3-SAE Puro Obrigatório: Esta antena opera em 6 GHz ou faz parte do grupo Wi-Fi 7 MLO, que exige WPA3 por norma internacional.',
		wpa3_optional_note: '💡 Esta antena opera fora do MLO. Você pode selecionar WPA2/WPA3 misto para compatibilidade total.',
		wpa3_sae_pure_req: 'WPA3-SAE Puro (Obrigatório)',
		wpa2_wpa3_mixed: 'WPA2/WPA3 Pessoal Misto (Recomendado - Todos os dispositivos)',
		wpa3_sae_pure: 'WPA3-SAE Puro (Máxima Segurança)',
		owe_open: 'OWE Enhanced Open (Aberta Segura Wi-Fi 6/7)',
		wpa2_psk_legacy: 'WPA2-PSK (Legado - Apenas 2.4/5 GHz)',
		open_no_pass: 'Rede Aberta (Sem Senha)',
		del_confirm: 'Tem certeza que deseja EXCLUIR permanentemente a rede "%s"?',
		err_ssid_empty: 'O nome da rede não pode ficar vazio.',
		err_ssid_max: 'O nome da rede (SSID) não pode ultrapassar 32 caracteres.',
		err_ssid_chars: 'O nome da rede contém caracteres inválidos (\' " ` ; \\).',
		err_pass_min: 'A senha precisa ter pelo menos 8 caracteres.',
		err_pass_max: 'A senha não pode ultrapassar 63 caracteres.',
		err_pass_required: 'A senha é obrigatória para redes com segurança.',
		warn_clients_disconnect: 'Atenção: %s dispositivo(s) conectado(s) serão desconectados temporariamente durante a troca de perfil.',
		guard_banner_title: 'Proteção Automática Predator Guard',
		guard_rollback_msg: 'A última alteração de Wi-Fi não subiu corretamente (%s) e foi revertida para a configuração estável anterior.',
		guard_heal_msg: 'O Wi-Fi encontrou lentidão para subir (%s) e foi recuperado com reinício limpo dos rádios.',
		guard_btn_dismiss: 'Entendido',
		guard_unknown_reason: 'os rádios não responderam operacionais',
		err_select_antenna: 'Selecione pelo menos uma antena/frequência.',
		status_switching: 'Alternando Status da Rede...',
		deleting_network: 'Excluindo Rede...',
		applying_profile: 'Aplicando Perfil de Topologia...',
		btn_save_all_radios: '💾 Salvar Todos os Rádios',
		radio_saving_all: 'Salvando e aplicando configurações nos 3 rádios simultaneamente...',
		btn_restart_wifi: '🔄 Reiniciar Wi-Fi (Destravar Sub-sistema)',
		btn_restarting_wifi: 'Reiniciando e Destravando Wi-Fi...',
		modal_restart_wifi_title: '🔄 Reiniciando Sub-sistema Wi-Fi',
		modal_restart_wifi_msg: 'Removendo travas órfãs, restabelecendo antenas físicas e recarregando o driver Qualcomm. Aguarde...',
		creating_network: 'Criando Nova Rede Wi-Fi...',
		radio_status_online: '● Online',
		radio_status_starting: '⏳ Inicializando / Calibrando...',
		radio_status_offline: '🟡 Fora do Ar / Reiniciando',
		radio_status_locked: '⚠️ Travado (/var/run/wifilock)',
		radio_status_disabled: '○ Desativado',
		radio_btn_disable: '⏸ Desativar Rádio',
		radio_btn_enable: '▶ Ativar Rádio',
		lock_badge_clean: 'Sub-sistema Livre (Sem Travas)',
		lock_badge_locked: 'Trava Detectada (/var/run/wifilock)',
		width_80m_rec: '80 MHz (Recomendado - Boot Instantâneo sem DFS)',
		width_160m_fast: '160 MHz (Ultra Fast - Requer Checagem DFS ~60s)',
		dfs_alert_title: '⚠️ Aviso de DFS (Radar) em 160 MHz:',
		dfs_alert_body: 'A largura de 160 MHz em 5 GHz ocupa canais compartilhados com radares meteorológicos (faixa DFS 52–64). Por exigência internacional (IEEE 802.11h / Anatel / FCC), o roteador realiza uma checagem obrigatória de ~60 segundos em silêncio de rádio no boot ou recarga antes de liberar a transmissão.',
		dfs_alert_tip: '💡 Dica: Em 160 MHz o link atinge até 2.402 Mbps em dispositivos compatíveis. Para inicialização instantânea (segundo zero no boot), utilize 80 MHz.',
		tx_auto_22: 'Auto (Recomendado - 22 dBm)',
		tx_auto_23: 'Auto (Recomendado - 23 dBm)',
		tx_auto_20: 'Auto (Recomendado - 20 dBm)',
		tx_economic: 'Econômico',
		tx_active_router: '(Ativo no Roteador)',
		tx_22_desc: '22 dBm (Máx Real Hardware | 158 mW Conduzido / 708 mW EIRP)',
		tx_23_desc: '23 dBm (Máx Real em 160M | 200 mW Conduzido / 2.180 mW EIRP)',
		tx_26_desc: '26 dBm (Máx Real em 80M Ch 149+ | 398 mW Conduzido / 5.495 mW EIRP)',
		tx_20_desc: '20 dBm (Máx Real Desbloqueado 320M | 100 mW Conduzido / ~1 W EIRP)'
	},
	es: {
		app_title: 'Predator Connect T7 - Centro Wi-Fi 7 y MLO',
		app_descr: 'Administrador de red completo para el hardware Qualcomm IPQ5332 Tri-Band. Cambie perfiles de topología recomendados, ajuste canales recomendados o avanzados/DFS y cree redes monobanda, duales o triples.',
		active_profile: 'Perfil de Topología Wi-Fi Actual',
				ports_title: 'Puertos Físicos Ethernet (Estado de Cables)',
		wan_port_label: 'Puerto WAN (Internet)',
		lan1_port_label: 'Puerto LAN 1',
		lan2_port_label: 'Puerto LAN 2',
		port_connected: 'Conectado',
		port_disconnected: 'Sin Cable / Desconectado',
		wpa3_mandatory_notice: 'WPA3 Obligatorio',
		radios_title: 'Ajustes Físicos de los Radios Qualcomm',
		networks_title: 'Redes Wi-Fi Configuradas',
		btn_add_network: '➕ Añadir Nueva Red Wi-Fi',

		topo1_title: '1. VELOCIDAD MÁXIMA Y ROAMING UNIFICADO (2.4G + 5G Unificados | 6G Dedicado)',
		topo1_desc: '2.4 GHz y 5 GHz comparten el mismo SSID con roaming 802.11k/v por hardware. Los dispositivos migran dinámicamente a 5 GHz (160 MHz) cerca del router y cambian a 2.4 GHz a larga distancia sin cortes. 6 GHz opera dedicado para velocidad gaming máxima (hasta 5.760 Mbps). 100% seguro para domótica IoT.',
		topo1_btn: '🚀 1. Roaming Unificado (2.4G+5G | 6G)',
		topo1_tip: 'Mismo SSID en 2.4G y 5G con roaming 802.11k/v + 6G Dedicado',
		topo1_box_title: '🚀 Arquitectura de Roaming Unificado Inteligente',
		topo1_box_desc: 'Las bandas de 2.4 GHz y 5 GHz se unifican bajo el mismo nombre de red con 802.11k/v. Celulares y portátiles son guiados automáticamente a 5 GHz (160 MHz) cuando están cerca y cambian suavemente a 2.4 GHz a mayor distancia. El radio de 6 GHz opera aislado para máximo rendimiento.',

		topo2_title: '2. MODO MLO TURBO WI-FI 7 (5 GHz + 6 GHz MLD | 2.4 GHz IoT Dedicado) [Recomendado]',
		topo2_desc: 'El Estándar de Oro de Wi-Fi 7: 5 GHz (160 MHz) y 6 GHz (320 MHz) se agregan en una única entidad MLD con WPA3-SAE, permitiendo transmisión simultánea en dos canales y transición instantánea con 0 ms de retardo. El 2.4 GHz opera como red independiente (_2.4GHz) en WPA2 puro para proteger el 100% de los dispositivos IoT (bombillas, enchufes) contra bloqueos de WPA3.',
		topo2_btn: '⚡ 2. MLO Turbo (5G+6G MLD | 2.4G IoT)',
		topo2_tip: 'Agregación Wi-Fi 7 MLO (5G + 6G) con 2.4G independiente para IoT',
		topo2_box_title: '⭐ Arquitectura Wi-Fi 7 Estándar de Oro (Recomendado)',
		topo2_box_desc: 'Las dos frecuencias ultrarrápidas (5 GHz y 6 GHz) forman un grupo Multi-Link Device (MLD). Los dispositivos Wi-Fi 7 modernos transmiten simultáneamente en ambos radios, alcanzando velocidades gigabit sin pérdida de paquetes. La banda 2.4 GHz permanece aislada en WPA2 puro, garantizando la conexión de todos los dispositivos inteligentes.',

		topo3_title: '3. MLO TRI-BAND TOTAL (2.4G + 5G + 6G Agregados) [Alerta IoT e Inestabilidad]',
		topo3_desc: 'Los 3 radios agregados en el mismo grupo MLD. ALERTA: Obliga WPA3-SAE puro en todas las bandas, desconectando el 99% de dispositivos IoT 2.4 GHz. La comunicación interna del driver Qualcomm puede provocar inestabilidad.',
		topo3_btn: '⚠️ 3. MLO Tri-Band (Experimental)',
		topo3_tip: 'Agrega las 3 bandas con WPA3. ¡Incompatible con bombillas y enchufes IoT!',
		topo3_box_title: '⚠️ ALERTA CRÍTICA: Incompatibilidad con IoT y Estabilidad del Driver',
		topo3_box_desc: 'El estándar IEEE 802.11be exige WPA3-SAE con PMF obligatorio en todas las frecuencias de un grupo MLD. Incluir la banda 2.4 GHz fuerza WPA3 puro, desconectando inmediatamente el 99% de los dispositivos inteligentes (bombillas, enchufes, interruptores Tuya/Sonoff/ESP32). Recomendado solo para pruebas de laboratorio con clientes Wi-Fi 7 puros.',

		topo4_title: '4. MODO INDEPENDIENTE (3 Redes Wi-Fi Separadas)',
		topo4_desc: 'Cada frecuencia opera en su propia red dedicada (_2.4GHz, _5GHz, _6GHz). Control manual total sin roaming automático entre bandas.',
		topo4_btn: '📡 4. Redes Separadas (2.4G / 5G / 6G)',
		topo4_tip: '3 redes separadas con elección manual de banda',
		topo4_box_title: '📡 Arquitectura de Redes Independientes',
		topo4_box_desc: 'Crea 3 redes Wi-Fi separadas (_2.4GHz, _5GHz, _6GHz). Permite elegir manualmente a qué radio se conecta cada cliente. El router no realiza roaming automático entre bandas.',

		topo5_title: '5. RED ÚNICA TRI-BAND (Mismo Nombre y Contraseña en 2.4G + 5G + 6G)',
		topo5_desc: 'Un único nombre de red y contraseña para todo el hogar. 2.4 GHz opera en WPA2 puro para 100% de compatibilidad con domótica IoT, 5 GHz en WPA2/WPA3 Mixto como puente inteligente, y 6 GHz en WPA3-SAE puro para velocidad gigabit. Roaming 802.11k/v fluido entre las 3 frecuencias.',
		topo5_btn: '🔄 5. Red Única (2.4G+5G+6G)',
		topo5_tip: 'Mismo nombre y contraseña en las 3 bandas con 2.4G en WPA2 puro para IoT',
		topo5_box_title: '🔄 Arquitectura de Red Única Tri-Band (Todo-en-Uno)',
		topo5_box_desc: 'Emite el mismo nombre de red Wi-Fi y contraseña en 2.4 GHz, 5 GHz y 6 GHz. La banda 2.4 GHz queda en WPA2-PSK puro (psk2+aes), garantizando que el 100% de sus dispositivos de domótica (bombillas inteligentes, enchufes Tuya/Sonoff) se conecten de inmediato. La banda 5 GHz opera en WPA2/WPA3 mixto como puente, y 6 GHz en WPA3-SAE puro. El hardware 802.11k/v guía sus dispositivos a la frecuencia más veloz.',

		mld_group_label: 'Operación Multi-Banda de Alta Estabilidad',
		mld_group_help: 'Las redes adicionales transmiten en cada frecuencia seleccionada con roaming inteligente 802.11k/v. La función Wi-Fi 7 MLO (Multi-Link Operation) es exclusiva de la Red Principal y debe activarse mediante el "Perfil 4: MLO Turbo" en el panel de Topología superior.',

		radio0_title: 'Radio 0: 2.4 GHz',
		radio1_title: 'Radio 1: 5 GHz',
		radio2_title: 'Radio 2: 6 GHz (Wi-Fi 7)',
		radio_chan: 'Canal de Frecuencia',
		radio_adv_chan: 'Mostrar canales avanzados / DFS / intermedios',
		radio_width: 'Ancho de Canal (Bandwidth)',
		radio_txpower: 'Potencia de Transmisión (Tx Power)',
		radio_save: 'Guardar Radio',
		radio_saving: 'Guardando Radio...',
		radio0_note: '💡 Los canales 1, 6 y 11 son los únicos sin superposición en 2.4 GHz.',
		radio1_note: '💡 Los canales DFS (52-140) requieren monitoreo de radar. Si se detecta un radar, el Wi-Fi se silencia para cambiar de canal.',
		radio2_note: '💡 Los canales PSC (Preferred Scanning Channels: 37, 53, 69...) son los únicos que smartphones Wi-Fi 6E/7 escanean nativamente.',
		auto_rec: 'Auto (Recomendado)',
		auto_psc_rec: 'Auto PSC (Recomendado para Móviles y PCs)',

		th_ssid: 'Nombre de Red (SSID)',
		th_freq: 'Frecuencia',
		th_pass: 'Contraseña Wi-Fi',
		th_enc: 'Cifrado / Seguridad',
		th_type: 'Tipo',
		th_status: 'Estado',
		th_actions: 'Acciones',

		status_on: '🟢 Activa',
		status_off: '🔴 Desactivada',
		type_guest: 'Invitados',
		type_main: 'Principal (LAN)',
		pass_open: 'Sin Contraseña (Abierta)',
		badge_core: '🔒 Principal',
		badge_core_tip: 'Esta es una de las 3 antenas físicas principales del router y no se puede eliminar, solo desactivar o editar.',
		btn_turn_on: '▶ Activar',
		btn_turn_off: '⏸ Desactivar',
		btn_edit: '✏️ Editar',
		btn_delete: '🗑 Eliminar',
		btn_view_pass: '👁 Ver',
		btn_hide_pass: '🙈 Ocultar',
		btn_cancel: 'Cancelar',
		btn_save_changes: 'Guardar Cambios',
		btn_apply_profile: 'Confirmar y Aplicar Perfil',
		btn_create_network: 'Crear Red',

		modal_edit_title: '✏️ Editar Red Wi-Fi',
		modal_add_title: '➕ Añadir Nueva Red Wi-Fi',
		modal_reload_title: 'Aplicando cambios...',
		modal_reload_msg: 'El subsistema Qualcomm Wi-Fi 7 se está reiniciando y reconfigurando los radios. Espere la reconexión automática sin cerrar el navegador...',
		reload_syncing_subsystem: 'Sincronizando Subsistema Qualcomm Wi-Fi 7',
		reload_step_1: 'Paso 1/3: Grabando parámetros en los registros de RF del silicio...',
		reload_step_2: 'Paso 2/3: Inicializando demonios y fijando frecuencias MLO...',
		reload_step_3: 'Paso 3/3: Validando retorno de radios y estado EIRP...',
		reload_ready: '¡Todos los Radios Online!',
		reload_ready_msg: 'Hardware reconfigurado con éxito. Actualizando pantalla...',
		reload_finalizing: 'Finalizando y recargando...',
		base_name_label: 'Nombre Base (2.4G + 5G)',
		unified_ssid_label: 'Nombre de Red Unificada (SSID)',
		ssid_6g_label: 'Nombre de Red 6 GHz (Wi-Fi 7 Puro)',
		pass_pulled_label: 'Contraseña Wi-Fi (Leída del router)',
		pass_placeholder: 'Contraseña WPA2/WPA3',
		pass_min_digits: 'Contraseña (mínimo 8 caracteres)',
		antennas_label: 'Antenas / Frecuencias Transmitidas',
		guest_label: 'Red de Invitados:',
		guest_desc: 'Aislar clientes (Solo Internet, sin acceso a dispositivos locales)',
		wpa3_required_note: '🔒 WPA3-SAE Puro Obligatorio: Esta antena opera en 6 GHz o es parte de un grupo Wi-Fi 7 MLO, que exige WPA3 por norma internacional.',
		wpa3_optional_note: '💡 Esta antena opera fuera de MLO. Puede seleccionar WPA2/WPA3 mixto para máxima compatibilidad.',
		wpa3_sae_pure_req: 'WPA3-SAE Puro (Obligatorio)',
		wpa2_wpa3_mixed: 'WPA2/WPA3 Personal Mixto (Recomendado - Todos los dispositivos)',
		wpa3_sae_pure: 'WPA3-SAE Puro (Máxima Seguridad)',
		owe_open: 'OWE Enhanced Open (Abierta Segura Wi-Fi 6/7)',
		wpa2_psk_legacy: 'WPA2-PSK (Heredado - Solo 2.4/5 GHz)',
		open_no_pass: 'Red Abierta (Sin Contraseña)',
		del_confirm: '¿Está seguro de que desea ELIMINAR permanentemente la red "%s"?',
		err_ssid_empty: 'El nombre de red no puede estar vacío.',
		err_ssid_max: 'El nombre de red (SSID) no puede superar 32 caracteres.',
		err_ssid_chars: 'El nombre de red contiene caracteres inválidos (\' " ` ; \\).',
		err_pass_min: 'La contraseña debe tener al menos 8 caracteres.',
		err_pass_max: 'La contraseña no puede superar 63 caracteres.',
		err_pass_required: 'La contraseña es obligatoria para redes con seguridad.',
		warn_clients_disconnect: 'Atención: %s dispositivo(s) conectado(s) se desconectarán temporalmente durante el cambio de perfil.',
		guard_banner_title: 'Protección Automática Predator Guard',
		guard_rollback_msg: 'El último cambio de Wi-Fi no inició correctamente (%s) y fue revertido a la configuración estable anterior.',
		guard_heal_msg: 'El subsistema Wi-Fi tardó en responder (%s) y fue recuperado con reinicio limpio.',
		guard_btn_dismiss: 'Entendido',
		guard_unknown_reason: 'los radios no respondieron operativos',
		err_select_antenna: 'Seleccione al menos una antena/frecuencia.',
		status_switching: 'Cambiando Estado de Red...',
		deleting_network: 'Eliminando Red...',
		applying_profile: 'Aplicando Perfil de Topología...',
		btn_save_all_radios: '💾 Guardar Todas las Radios',
		radio_saving_all: 'Guardando y aplicando configuraciones en las 3 radios simultáneamente...',
		btn_restart_wifi: '🔄 Reiniciar Wi-Fi (Desbloquear Subsistema)',
		btn_restarting_wifi: 'Reiniciando y Desbloqueando Wi-Fi...',
		modal_restart_wifi_title: '🔄 Reiniciando Subsistema Wi-Fi',
		modal_restart_wifi_msg: 'Eliminando bloqueos huérfanos, restableciendo antenas físicas y recargando el controlador Qualcomm. Espere...',
		creating_network: 'Creando Nueva Red Wi-Fi...',
		radio_status_online: '● En línea',
		radio_status_starting: '⏳ Inicializando / Calibrando...',
		radio_status_offline: '🟡 Fuera de Servicio / Reiniciando',
		radio_status_locked: '⚠️ Bloqueado (/var/run/wifilock)',
		radio_status_disabled: '○ Desactivado',
		radio_btn_disable: '⏸ Desactivar Radio',
		radio_btn_enable: '▶ Activar Radio',
		lock_badge_clean: 'Subsistema Libre (Sin Bloqueos)',
		lock_badge_locked: 'Bloqueo Detectado (/var/run/wifilock)',
		width_80m_rec: '80 MHz (Recomendado - Arranque Instantáneo sin DFS)',
		width_160m_fast: '160 MHz (Ultra Rápido - Requiere Comprobación DFS ~60s)',
		dfs_alert_title: '⚠️ Aviso de DFS (Radar) en 160 MHz:',
		dfs_alert_body: 'El ancho de 160 MHz en 5 GHz ocupa canales compartidos con radares meteorológicos (banda DFS 52–64). Por normativa internacional (IEEE 802.11h / Anatel / FCC), el router realiza una verificación obligatoria de ~60 segundos en silencio durante el arranque o recarga antes de transmitir.',
		dfs_alert_tip: '💡 Consejo: En 160 MHz el enlace alcanza hasta 2.402 Mbps en dispositivos compatibles. Para arranque instantáneo (segundo cero), utilice 80 MHz.',
		tx_auto_22: 'Auto (Recomendado - 22 dBm)',
		tx_auto_23: 'Auto (Recomendado - 23 dBm)',
		tx_auto_20: 'Auto (Recomendado - 20 dBm)',
		tx_economic: 'Económico',
		tx_active_router: '(Activo en el Router)',
		tx_22_desc: '22 dBm (Máx Hardware Real | 158 mW Conducido / 708 mW EIRP)',
		tx_23_desc: '23 dBm (Máx Real en 160M | 200 mW Conducido / 2.180 mW EIRP)',
		tx_26_desc: '26 dBm (Máx Real en 80M Ch 149+ | 398 mW Conducido / 5.495 mW EIRP)',
		tx_20_desc: '20 dBm (Máx Real Desbloqueado 320M | 100 mW Conducido / ~1 W EIRP)'
	}
};

function getActiveLang() {
	var l = (document.documentElement.lang || '').toLowerCase();
	if (!l && document.body) {
		var m = document.body.className.match(/lang_([a-zA-Z_-]+)/);
		if (m) l = m[1].toLowerCase();
	}
	if (l.indexOf('pt') === 0 || l === 'pt_br' || l === 'pt-br') return 'pt_br';
	if (l.indexOf('es') === 0) return 'es';
	return 'en';
}

function t(key, arg1) {
	var lang = getActiveLang();
	var dict = I18N[lang] || I18N.en;
	var str = dict[key] || (I18N.en && I18N.en[key]) || key;
	if (arg1 !== undefined && typeof str === 'string') {
		str = str.replace('%s', arg1);
	}
	return str;
}

function createPasswordInput(placeholder, value) {
	var inp = E('input', {
		'type': 'password',
		'class': 'cbi-input-text',
		'style': 'flex: 1; min-width: 0;',
		'placeholder': placeholder || '',
		'value': value || ''
	});
	var eyeBtn = E('button', {
		'class': 'btn',
		'type': 'button',
		'style': 'padding: 4px 10px; margin-left: 6px; cursor: pointer; font-size: 14px;',
		'title': t('btn_view_pass') + ' / ' + t('btn_hide_pass'),
		'click': function(ev) {
			ev.preventDefault();
			if (inp.type === 'password') {
				inp.type = 'text';
				eyeBtn.textContent = t('btn_hide_pass');
			} else {
				inp.type = 'password';
				eyeBtn.textContent = t('btn_view_pass');
			}
		}
	}, t('btn_view_pass'));

	return {
		wrapper: E('div', { 'style': 'display: flex; align-items: center;' }, [ inp, eyeBtn ]),
		input: inp
	};
}

function safeReloadAfterRestart(titleMsg) {
	var totalSeconds = 45;
	var remaining = totalSeconds;
	var elapsed = 0;

	var countSpan = E('span', { 'id': 'reload_countdown', 'style': 'font-size:24px; font-weight:bold; color:#0275d8; display:inline-block;' }, remaining + 's');
	var progressBar = E('div', {
		'style': 'width:0%; height:8px; background:#0275d8; border-radius:4px; transition:width 1s linear;'
	});
	var stepText = E('div', {
		'id': 'reload_step_text',
		'style': 'font-size:12px; color:#666; margin-top:8px; font-style:italic;'
	}, t('reload_step_1'));

	var modalContent = E('div', { 'style': 'text-align:center; padding:10px 0;' }, [
		E('div', { 'style': 'margin-bottom:12px; font-size:14px; color:#333; line-height:1.4;' }, t('modal_reload_msg')),
		E('div', { 'style': 'background:#f0f2f5; border-radius:6px; padding:15px; margin-bottom:12px;' }, [
			E('div', { 'style': 'margin-bottom:8px; font-size:13px; font-weight:bold; color:#555;' }, [
				'⏳ ', t('reload_syncing_subsystem')
			]),
			countSpan,
			E('div', { 'style': 'background:#e9ecef; border-radius:4px; height:8px; width:100%; margin-top:10px; overflow:hidden;' }, [
				progressBar
			]),
			stepText
		]),
		E('div', { 'class': 'spinning', 'style': 'margin:0 auto;' })
	]);

	ui.showModal(titleMsg || t('modal_reload_title'), [ modalContent ]);

	var reloaded = false;
	var timer = window.setInterval(function() {
		if (reloaded) return;
		elapsed++;
		remaining--;
		if (remaining < 0) remaining = 0;

		if (remaining > 0) {
			countSpan.textContent = remaining + 's';
			var pct = Math.round(((totalSeconds - remaining) / totalSeconds) * 100);
			progressBar.style.width = pct + '%';
		} else {
			countSpan.textContent = '⏳';
			progressBar.style.width = '95%';
		}

		if (remaining > 28) {
			stepText.textContent = t('reload_step_1');
		} else if (remaining > 12) {
			stepText.textContent = t('reload_step_2');
		} else if (remaining > 0) {
			stepText.textContent = t('reload_step_3');
		} else {
			stepText.textContent = t('reload_finalizing');
		}

		// A partir de 8s decorridos, valida ativamente se a trava sumiu e os radios voltaram (fecha cedo em ~10-12s via cabo)
		if (elapsed >= 8) {
			callGetStatus().then(function(res) {
				if (reloaded) return;
				var r = res && res.radios;
				var isClean = r && (r.lock_status === 'clean');
				var isOnline = r && (r.wifi0 && r.wifi0.status === 'online') &&
				                    (r.wifi1 && r.wifi1.status === 'online') &&
				                    (r.wifi2 && r.wifi2.status === 'online');

				if (isClean && isOnline) {
					reloaded = true;
					window.clearInterval(timer);
					progressBar.style.width = '100%';
					progressBar.style.background = '#28a745';
					countSpan.style.color = '#28a745';
					countSpan.textContent = '✅ ' + t('reload_ready');
					stepText.textContent = t('reload_ready_msg');
					window.setTimeout(function() {
						window.location.reload();
					}, 1000);
				}
			}).catch(function() {});
		}

		// Salvaguarda maxima de seguranca (90s para cobrir clientes Wi-Fi reconectando ou checagem DFS de 60s)
		if (elapsed >= 90 && !reloaded) {
			reloaded = true;
			window.clearInterval(timer);
			window.location.reload();
		}
	}, 1000);
}

return view.extend({
	load: function() {
		return Promise.all([
			callGetStatus(),
			callGetGuardStatus().catch(function() { return {}; })
		]);
	},

	renderTopologyModal: function(mode, status) {
		var self = this;
		var title = '';
		var desc = '';
		var isDual = (mode === 'speed_max');

		if (mode === 'speed_max') {
			title = t('topo1_title');
			desc = t('topo1_desc');
		} else if (mode === 'mlo_turbo') {
			title = t('topo2_title');
			desc = t('topo2_desc');
		} else if (mode === 'mlo_full') {
			title = t('topo3_title');
			desc = t('topo3_desc');
		} else if (mode === 'single_ssid') {
			title = t('topo5_title');
			desc = t('topo5_desc');
		} else {
			title = t('topo4_title');
			desc = t('topo4_desc');
		}

		var ifaces = (status && status.interfaces) ? status.interfaces : [];
		var currentKey = (ifaces.length > 0 && ifaces[0].key) ? ifaces[0].key : 'predator0100';
		var currentSsid = (ifaces.length > 0 && ifaces[0].ssid) ? ifaces[0].ssid : 'Predator_T7';

		var ssidInput = E('input', { 'type': 'text', 'class': 'cbi-input-text', 'style': 'width:100%;', 'placeholder': t('th_ssid'), 'value': currentSsid });
		var keyField = createPasswordInput(t('pass_placeholder'), currentKey);
		var ssid6Input = E('input', { 'type': 'text', 'class': 'cbi-input-text', 'style': 'width:100%;', 'placeholder': t('ssid_6g_label'), 'value': currentSsid + '_6G' });

		var infoBox;
		if (mode === 'mlo_full') {
			infoBox = E('div', {
				'style': 'background:#fdf2f2; border:1px solid #f5c6cb; border-left:5px solid #dc3545; border-radius:6px; padding:12px 14px; margin-bottom:15px; font-size:12px; color:#721c24; line-height:1.45;'
			}, [
				E('div', { 'style': 'font-weight:bold; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
					'⚠️ ', t('topo3_box_title')
				]),
				E('div', {}, t('topo3_box_desc'))
			]);
		} else if (mode === 'mlo_turbo') {
			infoBox = E('div', {
				'style': 'background:#e8f8f0; border:1px solid #c3e6cb; border-left:5px solid #28a745; border-radius:6px; padding:12px 14px; margin-bottom:15px; font-size:12px; color:#155724; line-height:1.45;'
			}, [
				E('div', { 'style': 'font-weight:bold; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
					'⭐ ', t('topo2_box_title')
				]),
				E('div', {}, t('topo2_box_desc'))
			]);
		} else if (mode === 'speed_max') {
			infoBox = E('div', {
				'style': 'background:#e8f4fd; border:1px solid #b8daff; border-left:5px solid #007bff; border-radius:6px; padding:12px 14px; margin-bottom:15px; font-size:12px; color:#004085; line-height:1.45;'
			}, [
				E('div', { 'style': 'font-weight:bold; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
					'🚀 ', t('topo1_box_title')
				]),
				E('div', {}, t('topo1_box_desc'))
			]);
		} else if (mode === 'single_ssid') {
			infoBox = E('div', {
				'style': 'background:#e7f5ff; border:1px solid #a5d8ff; border-left:5px solid #1c7ed6; border-radius:6px; padding:12px 14px; margin-bottom:15px; font-size:12px; color:#1864ab; line-height:1.45;'
			}, [
				E('div', { 'style': 'font-weight:bold; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
					'🔄 ', t('topo5_box_title')
				]),
				E('div', {}, t('topo5_box_desc'))
			]);
		} else {
			infoBox = E('div', {
				'style': 'background:#fff8e1; border:1px solid #ffeeba; border-left:5px solid #ffc107; border-radius:6px; padding:12px 14px; margin-bottom:15px; font-size:12px; color:#856404; line-height:1.45;'
			}, [
				E('div', { 'style': 'font-weight:bold; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
					'📡 ', t('topo4_box_title')
				]),
				E('div', {}, t('topo4_box_desc'))
			]);
		}

		var body = [
			E('p', { 'style': 'font-size:14px; margin-bottom:12px; color:#555; line-height:1.4;' }, desc),
			infoBox,
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, isDual ? t('base_name_label') : t('unified_ssid_label')),
				ssidInput
			]),
			isDual ? E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('ssid_6g_label')),
				ssid6Input
			]) : E('span'),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('pass_pulled_label')),
				keyField.wrapper
			])
		];

		if (status && status.stations && status.stations.length > 0) {
			var stCount = status.stations.length;
			var stNames = status.stations.map(function(s) {
				return (s.hostname && s.hostname !== '?') ? s.hostname : (s.ip || s.mac);
			}).slice(0, 4).join(', ');
			if (stCount > 4) stNames += '... (+' + (stCount - 4) + ')';
			body.push(E('div', {
				'style': 'background:#fff8e1; border:1px solid #ffeeba; border-left:4px solid #f39c12; border-radius:4px; padding:10px 12px; margin-bottom:12px; font-size:12px; color:#856404; line-height:1.4;'
			}, [
				E('strong', {}, '⚠️ ' + t('warn_clients_disconnect', stCount)),
				E('div', { 'style': 'font-size:11px; margin-top:3px; color:#6d4c41;' }, stNames)
			]));
		}

		ui.showModal(title, [
			E('div', {}, body),
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'btn', 'click': ui.hideModal }, t('btn_cancel')),
				' ',
				E('button', {
					'class': 'btn cbi-button-action important',
					'click': function() {
						var ssid = ssidInput.value.trim();
						var key = keyField.input.value.trim();
						var s6 = ssid6Input.value.trim();
						if (!ssid) {
							ui.addNotification(null, E('p', t('err_ssid_empty')), 'danger');
							return;
						}
						if (ssid.length > 32) {
							ui.addNotification(null, E('p', t('err_ssid_max')), 'danger');
							return;
						}
						if (/[\\'"`;]/.test(ssid)) {
							ui.addNotification(null, E('p', t('err_ssid_chars')), 'danger');
							return;
						}
						if (!key) {
							key = currentKey;
						}
						if (key.length < 8) {
							ui.addNotification(null, E('p', t('err_pass_min')), 'danger');
							return;
						}
						if (key.length > 63) {
							ui.addNotification(null, E('p', t('err_pass_max')), 'danger');
							return;
						}
						callApplyTopology(mode, ssid, key, s6).then(function(res) {
							if (res && res.error) {
								ui.addNotification(null, E('p', 'Erro: ' + res.error), 'danger');
								return;
							}
							safeReloadAfterRestart(t('applying_profile'));
						});
					}
				}, t('btn_apply_profile'))
			])
		]);
	},

	renderEditNetworkModal: function(ifc) {
		var isMlo = !!ifc.mld;
		var is6G = (ifc.device === 'wifi2');
		var mustBeWpa3 = isMlo || is6G;

		var ssidInput = E('input', {
			'type': 'text',
			'class': 'cbi-input-text',
			'style': 'width:100%;',
			'value': ifc.ssid || ''
		});

		var keyField = createPasswordInput(t('th_pass'), ifc.key || '');

		var encSelect;
		if (mustBeWpa3) {
			encSelect = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%;', 'disabled': true }, [
				E('option', { 'value': 'sae' }, t('wpa3_sae_pure_req'))
			]);
			encSelect.value = 'sae';
		} else {
			var currentEnc = ifc.encryption || 'psk2+aes';
			var normEnc = currentEnc;
			if (normEnc.indexOf('psk2') !== -1 || normEnc === 'psk') normEnc = 'psk2+aes';
			else if (normEnc === 'sae-mixed' || normEnc.indexOf('mixed') !== -1) normEnc = 'sae-mixed';
			else if (normEnc === 'sae') normEnc = 'sae';
			else if (normEnc === 'owe') normEnc = 'owe';
			else if (normEnc === 'none') normEnc = 'none';

			encSelect = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%;' }, [
				E('option', { 'value': 'psk2+aes' }, t('wpa2_psk_legacy')),
				E('option', { 'value': 'sae-mixed' }, t('wpa2_wpa3_mixed')),
				E('option', { 'value': 'sae' }, t('wpa3_sae_pure')),
				E('option', { 'value': 'owe' }, t('owe_open')),
				E('option', { 'value': 'none' }, t('open_no_pass'))
			]);
			encSelect.value = normEnc;
		}

		var securityNote = mustBeWpa3 ?
			E('div', { 'style': 'font-size:12px; color:#c0392b; margin-top:4px;' }, t('wpa3_required_note')) :
			E('div', { 'style': 'font-size:12px; color:#27ae60; margin-top:4px;' }, t('wpa3_optional_note'));

		var body = [
			E('p', { 'style': 'font-size:14px; margin-bottom:15px; color:#555;' },
				(ifc.ssid ? ifc.ssid + ' (' + ifc.device + ')' : ifc.device)),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_ssid') + ':'),
				ssidInput
			]),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_enc') + ':'),
				encSelect,
				securityNote
			]),
			E('div', { 'style': 'margin-bottom:15px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_pass') + ':'),
				keyField.wrapper
			])
		];

		ui.showModal(t('modal_edit_title'), [
			E('div', {}, body),
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'btn', 'click': ui.hideModal }, t('btn_cancel')),
				' ',
				E('button', {
					'class': 'btn cbi-button-action important',
					'click': function() {
						var newSsid = ssidInput.value.trim();
						var newKey = keyField.input.value.trim();
						var newEnc = mustBeWpa3 ? 'sae' : encSelect.value;
						if (!newSsid) {
							ui.addNotification(null, E('p', t('err_ssid_empty')), 'danger');
							return;
						}
						if (newSsid.length > 32) {
							ui.addNotification(null, E('p', t('err_ssid_max')), 'danger');
							return;
						}
						if (/[\\'"`;]/.test(newSsid)) {
							ui.addNotification(null, E('p', t('err_ssid_chars')), 'danger');
							return;
						}
						if (!newKey && ifc.key) {
							newKey = ifc.key;
						}
						if (newEnc !== 'none' && newEnc !== 'owe') {
							if (!newKey) {
								ui.addNotification(null, E('p', t('err_pass_required')), 'danger');
								return;
							}
							if (newKey.length < 8) {
								ui.addNotification(null, E('p', t('err_pass_min')), 'danger');
								return;
							}
							if (newKey.length > 63) {
								ui.addNotification(null, E('p', t('err_pass_max')), 'danger');
								return;
							}
						}
						callEditVif(ifc.section, newSsid, newKey, newEnc).then(function(res) {
							if (res && res.error) {
								ui.addNotification(null, E('p', 'Erro: ' + res.error), 'danger');
								return;
							}
							safeReloadAfterRestart(t('updating_network'));
						});
					}
				}, t('btn_save_changes'))
			])
		]);
	},

	renderAddNetworkModal: function() {
		var ssidIn = E('input', { 'type': 'text', 'class': 'cbi-input-text', 'style': 'width:100%;', 'placeholder': 'Predator_Guest / IoT' });
		var keyField = createPasswordInput(t('pass_min_digits'), '');
		
		var encSelect = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%;' }, [
			E('option', { 'value': 'sae-mixed' }, t('wpa2_wpa3_mixed')),
			E('option', { 'value': 'sae' }, t('wpa3_sae_pure')),
			E('option', { 'value': 'owe' }, t('owe_open')),
			E('option', { 'value': 'psk2+aes' }, t('wpa2_psk_legacy')),
			E('option', { 'value': 'none' }, t('open_no_pass'))
		]);

		var b2 = E('input', { 'type': 'checkbox', 'checked': true });
		var b5 = E('input', { 'type': 'checkbox', 'checked': true });
		var b6 = E('input', { 'type': 'checkbox', 'checked': false });
		var guestBox = E('input', { 'type': 'checkbox', 'checked': false });

		b6.addEventListener('change', function() {
			if (b6.checked) {
				if (encSelect.value === 'psk2+aes' || encSelect.value === 'none') {
					encSelect.value = 'sae-mixed';
				}
			}
		});

		var zoneSelect = E('select', { 'class': 'cbi-input-select', 'style': 'width:100%;' }, [
			E('option', { 'value': 'lan' }, '🏠 Rede Principal (LAN - Acesso Total à Rede Local e Internet)'),
			E('option', { 'value': 'guest' }, '👥 Rede de Visitantes (Guest - Isolada na br-guest / Sem Acesso à LAN)'),
			E('option', { 'value': 'iot' }, '🤖 Rede de Automação IoT (IoT - Isolada na br-iot / 2.4G Domótica)')
		]);

		var content = E('div', {}, [
			E('p', { 'style': 'font-size:14px; margin-bottom:15px; color:#555;' }, t('app_descr')),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_ssid')),
				ssidIn
			]),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_enc')),
				encSelect
			]),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, t('th_pass')),
				keyField.wrapper
			]),
			E('div', { 'style': 'margin-bottom:12px; background:#f9f9f9; padding:10px; border-radius:4px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:6px;' }, t('antennas_label')),
				E('label', { 'style': 'margin-right:20px; font-weight:normal; cursor:pointer;' }, [ b2, ' 2.4 GHz' ]),
				E('label', { 'style': 'margin-right:20px; font-weight:normal; cursor:pointer;' }, [ b5, ' 5 GHz' ]),
				E('label', { 'style': 'font-weight:normal; cursor:pointer;' }, [ b6, ' 6 GHz (Wi-Fi 7)' ])
			]),
			E('div', { 'style': 'margin-bottom:12px; background:#f0f7ff; border:1px solid #cce5ff; padding:10px 12px; border-radius:4px;' }, [
				E('div', { 'style': 'font-weight:bold; color:#004085; display:flex; align-items:center; gap:6px; margin-bottom:4px;' }, [
					'💡 ', t('mld_group_label')
				]),
				E('div', { 'style': 'font-size:12px; color:#004085; line-height:1.4;' }, t('mld_group_help'))
			]),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; margin-bottom:4px;' }, 'Destino / Isolamento de Rede:'),
				zoneSelect,
				E('div', { 'style': 'font-size:11px; color:#666; margin-top:3px;' }, 'Selecione a bridge de destino da rede. Visitantes e IoT são automaticamente isoladas das máquinas locais da LAN.')
			])
		]);

		ui.showModal(t('modal_add_title'), [
			content,
			E('div', { 'class': 'right', 'style': 'margin-top:20px;' }, [
				E('button', { 'class': 'btn', 'click': ui.hideModal }, t('btn_cancel')),
				' ',
				E('button', {
					'class': 'btn cbi-button-action important',
					'click': function() {
						var ssid = ssidIn.value.trim();
						var key = keyField.input.value.trim();
						var enc = encSelect.value;
						if (!ssid) {
							ui.addNotification(null, E('p', t('err_ssid_empty')), 'danger');
							return;
						}
						if (ssid.length > 32) {
							ui.addNotification(null, E('p', t('err_ssid_max')), 'danger');
							return;
						}
						if (/['"`;\\]/.test(ssid)) {
							ui.addNotification(null, E('p', t('err_ssid_chars')), 'danger');
							return;
						}
						if (!b2.checked && !b5.checked && !b6.checked) {
							ui.addNotification(null, E('p', t('err_select_antenna')), 'danger');
							return;
						}
						if (enc !== 'none' && enc !== 'owe') {
							if (!key) {
								ui.addNotification(null, E('p', t('err_pass_required')), 'danger');
								return;
							}
							if (key.length < 8) {
								ui.addNotification(null, E('p', t('err_pass_min')), 'danger');
								return;
							}
							if (key.length > 63) {
								ui.addNotification(null, E('p', t('err_pass_max')), 'danger');
								return;
							}
						}
						var isGuest = (zoneSelect.value === 'guest');
						var zone = zoneSelect.value;
						callAddVif(ssid, key, enc, b2.checked, b5.checked, b6.checked, isGuest, false, zone).then(function(res) {
							if (res && res.error) {
								ui.addNotification(null, E('p', 'Erro: ' + res.error), 'danger');
								return;
							}
							safeReloadAfterRestart(t('creating_network'));
						});
					}
				}, t('btn_create_network'))
			])
		]);
	},

	renderRadioCard: function(devName, labelText, color, recChannels, allChannels, widths, radioData, noticeText) {
		var chanSelect = E('select', { 'id': 'sel-chan-' + devName, 'class': 'cbi-input-select', 'style': 'width:100%;' });
		var widthSelect = E('select', { 'id': 'sel-width-' + devName, 'class': 'cbi-input-select', 'style': 'width:100%;' });
		widths.forEach(function(w) {
			var opt = E('option', { 'value': w.val }, w.label);
			if (w.val == radioData.htmode) opt.selected = true;
			widthSelect.appendChild(opt);
		});
		widthSelect.value = radioData.htmode;

		function populateChannels(showAll) {
			var curVal = chanSelect.value || radioData.channel || 'auto';
			while (chanSelect.firstChild) chanSelect.removeChild(chanSelect.firstChild);
			var list = showAll ? allChannels : recChannels;
			var selectedWidth = widthSelect.value;
			if (devName === 'wifi1' && selectedWidth === 'HT160') {
				list = list.filter(function(c) {
					return c.val === 'auto' || c.val === '36' || c.val === '100';
				});
				if (curVal !== 'auto' && curVal !== '36' && curVal !== '100') {
					curVal = '36';
				}
			} else if (devName === 'wifi2' && selectedWidth === 'HT320') {
				if (!showAll) {
					list = list.filter(function(c) {
						return c.val === 'auto' || c.val === '37' || c.val === '53' || c.val === '69' || c.val === '85' || c.val === '101' || c.val === '117';
					});
				}
			}
			list.forEach(function(c) {
				var opt = E('option', { 'value': c.val }, c.label);
				if (c.val == curVal) opt.selected = true;
				chanSelect.appendChild(opt);
			});
			chanSelect.value = curVal;
		}

		populateChannels(false);

		var toggleAdv = E('input', { 'type': 'checkbox', 'style': 'cursor:pointer; margin-right:6px;' });
		toggleAdv.addEventListener('change', function() {
			populateChannels(toggleAdv.checked);
		});

		var dfsAlertBox = E('div', {
			'id': 'dfs-alert-' + devName,
			'style': 'display:none; margin-top:8px; padding:10px 12px; border-radius:6px; font-size:12px; line-height:1.45; background:#fff8e1; border:1px solid #ffe082; color:#5d4037;'
		}, [
			E('div', { 'style': 'font-weight:bold; color:#e65100; margin-bottom:4px; display:flex; align-items:center; gap:6px;' }, [
				E('span', { 'style': 'font-size:15px;' }, '⚠️'),
				t('dfs_alert_title')
			]),
			E('div', {}, t('dfs_alert_body')),
			E('div', { 'style': 'margin-top:5px; font-size:11px; color:#8d6e63;' }, t('dfs_alert_tip'))
		]);

		function updateDfsNotice() {
			if (devName === 'wifi1') {
				dfsAlertBox.style.display = (widthSelect.value === 'HT160') ? 'block' : 'none';
			} else {
				dfsAlertBox.style.display = 'none';
			}
		}

		widthSelect.addEventListener('change', function() {
			populateChannels(toggleAdv.checked);
			updateDfsNotice();
		});
		updateDfsNotice();

		var txOptionsMap = {
			'wifi0': [
				{ val: 'auto', label: t('tx_auto_22') },
				{ val: '22', label: t('tx_22_desc') },
				{ val: '20', label: '20 dBm (100 mW Conduzido / 446 mW EIRP)' },
				{ val: '17', label: '17 dBm (50 mW Conduzido / 224 mW EIRP)' },
				{ val: '14', label: '14 dBm (25 mW Conduzido / 112 mW EIRP)' },
				{ val: '10', label: '10 dBm (' + t('tx_economic') + ')' }
			],
			'wifi1': [
				{ val: 'auto', label: t('tx_auto_23') },
				{ val: '23', label: t('tx_23_desc') },
				{ val: '26', label: t('tx_26_desc') },
				{ val: '20', label: '20 dBm (100 mW Conduzido / 1.090 mW EIRP)' },
				{ val: '18', label: '18 dBm (63 mW Conduzido / 690 mW EIRP)' },
				{ val: '15', label: '15 dBm (32 mW Conduzido / 345 mW EIRP)' },
				{ val: '12', label: '12 dBm (' + t('tx_economic') + ')' }
			],
			'wifi2': [
				{ val: 'auto', label: t('tx_auto_20') },
				{ val: '20', label: t('tx_20_desc') },
				{ val: '18', label: '18 dBm (63 mW Conduzido / 575 mW EIRP)' },
				{ val: '15', label: '15 dBm (32 mW Conduzido / 288 mW EIRP)' },
				{ val: '13', label: '13 dBm (20 mW Conduzido / 182 mW EIRP)' },
				{ val: '11', label: '11 dBm (13 mW Conduzido / 115 mW EIRP)' },
				{ val: '9',  label: '9 dBm (' + t('tx_economic') + ')' }
			]
		};

		var txList = (txOptionsMap[devName] || [
			{ val: '20', label: '20 dBm' },
			{ val: '15', label: '15 dBm' }
		]).slice();

		var defaultTx = (devName === 'wifi0' ? '22' : (devName === 'wifi1' ? '23' : '20'));
		var curTx = String(radioData.txpower || defaultTx);

		if (!txList.some(function(item) { return item.val == curTx; })) {
			txList.unshift({ val: curTx, label: curTx + ' dBm ' + t('tx_active_router') });
		}

		var txSelect = E('select', { 'id': 'sel-txpower-' + devName, 'class': 'cbi-input-select', 'style': 'width:100%;' });
		txList.forEach(function(opt) {
			var o = E('option', { 'value': opt.val }, opt.label);
			if (opt.val == curTx) o.selected = true;
			txSelect.appendChild(o);
		});
		txSelect.value = curTx;

		var isRadioDis = (radioData.disabled === '1');
		var statusBadge;
		if (isRadioDis) {
			statusBadge = E('span', { 'id': 'radio-status-' + devName, 'style': 'background:#e0e0e0; color:#555; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;' }, t('radio_status_disabled'));
		} else if (radioData.status === 'online') {
			statusBadge = E('span', { 'id': 'radio-status-' + devName, 'style': 'background:#d4edda; color:#155724; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold; border:1px solid #c3e6cb;' }, t('radio_status_online'));
		} else {
			statusBadge = E('span', { 'id': 'radio-status-' + devName, 'style': 'background:#fff3cd; color:#856404; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold; border:1px solid #ffeeba;' }, t('radio_status_starting'));
		}

		return E('div', {
			'style': 'border:1px solid #dcdcdc; border-top:4px solid ' + color + '; border-radius:6px; padding:15px; background:inherit; box-shadow:0 1px 3px rgba(0,0,0,0.06); box-sizing:border-box;'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-top:0; margin-bottom:12px;' }, [
				E('h3', { 'style': 'margin:0; color:' + color + '; font-size:16px;' }, labelText),
				statusBadge
			]),
			E('div', { 'style': 'margin-bottom:8px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; font-size:12px; margin-bottom:4px;' }, t('radio_chan')),
				chanSelect
			]),
			E('div', { 'style': 'margin-bottom:10px; font-size:12px; color:#666;' }, [
				E('label', { 'style': 'cursor:pointer;' }, [
					toggleAdv,
					t('radio_adv_chan')
				])
			]),
			E('div', { 'style': 'margin-bottom:10px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; font-size:12px; margin-bottom:4px;' }, t('radio_width')),
				widthSelect,
				dfsAlertBox
			]),
			E('div', { 'style': 'margin-bottom:12px;' }, [
				E('label', { 'style': 'display:block; font-weight:bold; font-size:12px; margin-bottom:4px;' }, t('radio_txpower')),
				txSelect
			]),
			noticeText ? E('div', { 'style': 'font-size:11px; color:#888; margin-bottom:12px; line-height:1.3;' }, noticeText) : E('span'),
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-top:14px;' }, [
				E('button', {
					'class': 'btn',
					'style': isRadioDis ? 'color:#27ae60; font-weight:bold;' : 'color:#c0392b;',
					'click': function() {
						var newDis = isRadioDis ? '0' : '1';
						callToggleRadio(devName, newDis).then(function() {
							safeReloadAfterRestart(t('radio_saving'));
						});
					}
				}, isRadioDis ? t('radio_btn_enable') : t('radio_btn_disable')),
				E('button', {
					'id': 'btn-save-' + devName,
					'class': 'btn cbi-button-action',
					'click': function() {
						callSetRadio(devName, chanSelect.value, widthSelect.value, txSelect.value).then(function() {
							safeReloadAfterRestart(t('radio_saving'));
						});
					}
				}, t('radio_save'))
			])
		]);
	},

	formatRadioData: function(radios) {
		var r0 = (radios && radios.wifi0) ? radios.wifi0 : {};
		var r1 = (radios && radios.wifi1) ? radios.wifi1 : {};
		var r2 = (radios && radios.wifi2) ? radios.wifi2 : {};

		var p0_cond = parseFloat(r0.real_txpower || r0.txpower || '22.0');
		var p1_cond = parseFloat(r1.real_txpower || r1.txpower || '23.0');
		var p2_cond = parseFloat(r2.real_txpower || r2.txpower || '20.0');

		if (p0_cond > 22.0) p0_cond = 22.0;
		if (r1.htmode === 'HT160' && p1_cond > 23.0) p1_cond = 23.0;
		if (p2_cond > 20.0) p2_cond = 20.0;

		function mw(dbm) { return Math.round(Math.pow(10, dbm / 10)); }
		function fmt(val) { return isNaN(val) ? '0' : Number(val).toLocaleString(); }

		var p0_mimo = p0_cond + 3.01;
		var p1_mimo = p1_cond + 3.01;
		var p2_mimo = p2_cond + 3.01;

		var p0_eirp = p0_cond + 6.50;
		var p1_eirp = p1_cond + 10.38;
		var p2_eirp = p2_cond + 9.62;

		var bdfName = r2.bdf || 'bdwlan_default.b1015';
		var isBdfUnlocked = (bdfName.indexOf('default') !== -1);

		var t0_val = (r0.temp && !isNaN(parseInt(r0.temp)) && parseInt(r0.temp) > 0) ? parseInt(r0.temp) : null;
		var t1_val = (r1.temp && !isNaN(parseInt(r1.temp)) && parseInt(r1.temp) > 0) ? parseInt(r1.temp) : null;
		var t2_val = (r2.temp && !isNaN(parseInt(r2.temp)) && parseInt(r2.temp) > 0) ? parseInt(r2.temp) : null;

		var lvl0 = (r0.level !== undefined && r0.level !== null && r0.level !== '') ? parseInt(r0.level) : 0;
		var lvl1 = (r1.level !== undefined && r1.level !== null && r1.level !== '') ? parseInt(r1.level) : 0;
		var lvl2 = (r2.level !== undefined && r2.level !== null && r2.level !== '') ? parseInt(r2.level) : 0;

		return {
			wifi0: {
				band: '2.4 GHz',
				vap: 'ath0',
				chip: 'IPQ5332 (AHB)',
				ch: (r0.real_channel || r0.channel || '1'),
				bw: (r0.real_width || '20') + 'M',
				cond: p0_cond.toFixed(1) + ' dBm (' + fmt(mw(p0_cond)) + ' mW)',
				mimo: p0_mimo.toFixed(1) + ' dBm (' + fmt(mw(p0_mimo)) + ' mW)',
				eirp: p0_eirp.toFixed(1) + ' dBm (' + fmt(mw(p0_eirp)) + ' mW)',
				temp: t0_val,
				level: lvl0,
				level0Max: 110,
				level1Max: 115,
				level2Max: 120,
				level3Max: 125,
				critTrip: 125,
				color: '#d9534f'
			},
			wifi1: {
				band: '5.0 GHz',
				vap: 'ath1',
				chip: 'QCN9224 DualMAC (PCIe)',
				ch: (r1.real_channel || r1.channel || '36'),
				bw: (r1.real_width || '160') + 'M',
				cond: p1_cond.toFixed(1) + ' dBm (' + fmt(mw(p1_cond)) + ' mW)',
				mimo: p1_mimo.toFixed(1) + ' dBm (' + fmt(mw(p1_mimo)) + ' mW)',
				eirp: p1_eirp.toFixed(1) + ' dBm (' + fmt(mw(p1_eirp)) + ' mW)',
				temp: t1_val,
				level: lvl1,
				level0Max: 105,
				level1Max: 110,
				level2Max: 115,
				level3Max: 120,
				critTrip: 125,
				color: '#0275d8'
			},
			wifi2: {
				band: '6.0 GHz (Wi-Fi 7)',
				vap: 'ath2',
				chip: 'QCN9224 DualMAC (PCIe)',
				ch: (r2.real_channel || r2.channel || '37'),
				bw: (r2.real_width || '320') + 'M',
				cond: p2_cond.toFixed(1) + ' dBm (' + fmt(mw(p2_cond)) + ' mW)' + (p2_cond >= 18 ? ' 🚀 DESBLOQUEADO' : ''),
				mimo: p2_mimo.toFixed(1) + ' dBm (' + fmt(mw(p2_mimo)) + ' mW)',
				eirp: p2_eirp.toFixed(1) + ' dBm (' + fmt(mw(p2_eirp)) + ' mW' + (p2_eirp >= 29 ? ' / ~1 Watt!' : '') + ')',
				temp: t2_val,
				level: lvl2,
				level0Max: 105,
				level1Max: 110,
				level2Max: 115,
				level3Max: 120,
				critTrip: 125,
				bdfName: bdfName,
				isBdfUnlocked: isBdfUnlocked,
				color: '#5cb85c'
			}
		};
	},

	buildTempNode: function(r) {
		if (r.temp === null || r.temp === undefined || isNaN(r.temp)) {
			return E('div', { 'style': 'min-width:215px;' }, [
				E('div', { 'style': 'display:flex; align-items:center; gap:8px;' }, [
					E('span', { 'style': 'font-size:14px; font-weight:bold; color:#7f8c8d;' }, 'Indisponível'),
					E('span', { 'style': 'font-size:10px; background:#e9ecef; color:#495057; padding:1px 7px; border-radius:10px; font-weight:bold;' }, '⚪ Sem leitura')
				]),
				E('div', { 'style': 'font-size:11px; color:#666; margin-top:4px;' }, 'Aguardando telemetria thermaltool')
			]);
		}

		var num = r.temp;
		var color = '#27ae60';
		var statusText = '🟢 Normal (Nível 0 / 0% corte)';
		var badgeBg = '#d4edda';
		var badgeColor = '#155724';

		if (r.level >= 3 || num >= r.level3Max) {
			color = '#c0392b';
			statusText = '🛑 Corte RF (Nível 3 / 100% corte)';
			badgeBg = '#f8d7da';
			badgeColor = '#721c24';
		} else if (r.level === 2) {
			color = '#d35400';
			statusText = '⚠️ Throttling Severo (Nível 2 / 90% corte)';
			badgeBg = '#fff3cd';
			badgeColor = '#856404';
		} else if (r.level === 1) {
			color = '#e67e22';
			statusText = '🟡 Throttling (Nível 1 / 50% corte)';
			badgeBg = '#fef9e7';
			badgeColor = '#b7950b';
		} else if (num >= (r.level0Max - 4)) {
			color = '#f39c12';
			statusText = '🟢 Normal (Perto do teto Nível 0)';
			badgeBg = '#e8f8f0';
			badgeColor = '#1e8449';
		}

		return E('div', { 'style': 'min-width:215px;' }, [
			E('div', { 'style': 'display:flex; align-items:center; gap:8px;' }, [
				E('span', { 'style': 'font-size:15px; font-weight:bold; color:' + color + ';' }, num + '°C'),
				E('span', { 'style': 'font-size:10px; background:' + badgeBg + '; color:' + badgeColor + '; padding:1px 7px; border-radius:10px; font-weight:bold;' }, statusText)
			]),
			E('div', { 'style': 'font-size:11px; color:#555; margin-top:4px; line-height:1.45;' }, [
				E('div', {}, [ '• Nível 0 (0% corte): ', E('strong', { 'style': 'color:#27ae60;' }, 'até ' + r.level0Max + '°C') ]),
				E('div', {}, [ '• Nível 3 (Duty cycle 100%): ', E('strong', { 'style': 'color:#d35400;' }, r.level3Max + '°C') ]),
				E('div', {}, [ '• Trip Crítico Linux (Kernel): ', E('strong', { 'style': 'color:#c0392b;' }, r.critTrip + '°C') ])
			])
		]);
	},

	renderTelemetryCard: function(statusOrRadios) {
		var self = this;
		var statusObj = (statusOrRadios && statusOrRadios.radios) ? statusOrRadios : { radios: statusOrRadios, features: {} };
		var radios = statusObj.radios || {};
		var features = statusObj.features || {};
		var data = self.formatRadioData(radios);
		var r2 = data.wifi2;
		var isBdfUnlocked = r2.isBdfUnlocked;
		var bdfName = r2.bdfName;

		var tRows = ['wifi0', 'wifi1', 'wifi2'].map(function(dev) {
			var r = data[dev];
			return E('tr', { 'style': 'border-bottom:1px solid #eaeaea; font-size:13px;' }, [
				E('td', { 'style': 'padding:10px 12px; font-weight:bold; color:' + r.color + ';' }, [
					r.band, ' ',
					E('span', { 'style': 'font-size:11px; color:#888; font-weight:normal;' }, '(' + r.chip + ')')
				]),
				E('td', { 'style': 'padding:10px 12px;' }, E('code', { 'style': 'font-size:12px; background:#f0f0f0; padding:2px 6px; border-radius:4px;' }, r.vap)),
				E('td', { 'id': 'rf-ch-' + dev, 'style': 'padding:10px 12px; font-weight:bold;' }, 'Canal ' + r.ch + ' (' + r.bw + ')'),
				E('td', { 'id': 'rf-cond-' + dev, 'style': 'padding:10px 12px; color:#111; font-weight:bold;' }, r.cond),
				E('td', { 'id': 'rf-mimo-' + dev, 'style': 'padding:10px 12px; color:#2c3e50; font-weight:bold;' }, r.mimo),
				E('td', { 'id': 'rf-eirp-' + dev, 'style': 'padding:10px 12px; color:#27ae60; font-weight:bold;' }, r.eirp),
				E('td', { 'id': 'rf-temp-' + dev, 'style': 'padding:10px 12px;' }, self.buildTempNode(r))
			]);
		});

		var now = new Date();
		var timeStr = ('0' + now.getHours()).slice(-2) + ':' +
		              ('0' + now.getMinutes()).slice(-2) + ':' +
		              ('0' + now.getSeconds()).slice(-2);

		var badgeLive = E('span', {
			'id': 'rf-live-badge',
			'style': 'background:#e8f8f0; color:#27ae60; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:bold; border:1px solid #a3e4d7; display:inline-flex; align-items:center; gap:5px;'
		}, '🟢 Ao Vivo (2s) • ' + timeStr);

		var badgeBdf = E('span', { 'id': 'rf-bdf-badge', 'style': 'background:#d4edda; color:#155724; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:bold; border:1px solid #c3e6cb;' }, (bdfName.indexOf('default') !== -1) ? '🟢 BDF 6 GHz: Desbloqueada (20 dBm / ~1 W EIRP)' : '🟢 BDF 6 GHz: ' + bdfName + ' (Alta Potência Ativa)');

		var thermalInfoBox = E('div', {
			'style': 'margin-top:14px; padding:12px 16px; background:#fafbfc; border:1px solid #e1e4e8; border-left:4px solid #e67e22; border-radius:4px; font-size:12px; color:#333;'
		}, [
			E('div', { 'style': 'font-weight:bold; margin-bottom:6px; color:#d35400; font-size:13px;' }, '🌡️ Gestão Térmica de Hardware Qualcomm (Política de Duty Cycle do Driver & Trip Crítico):'),
			E('div', { 'style': 'display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px; line-height:1.45;' }, [
				E('div', { 'style': 'background:#fff; padding:8px 10px; border-radius:4px; border:1px solid #eee;' }, [
					E('strong', { 'style': 'color:#27ae60;' }, '1. Nível 0 (Normal / 100% Rendimento): '),
					E('span', { 'style': 'font-weight:bold;' }, 'até 105°C (5G/6G) / 110°C (2.4G)'),
					E('div', { 'style': 'font-size:11px; color:#666; margin-top:2px;' }, 'Teto operacional do Nível 0. O rádio opera em 100% do duty cycle sem qualquer redução ou penalidade.')
				]),
				E('div', { 'style': 'background:#fff; padding:8px 10px; border-radius:4px; border:1px solid #eee;' }, [
					E('strong', { 'style': 'color:#e67e22;' }, '2. Nível 1 & 2 (Mitigação Duty Cycle): '),
					E('span', { 'style': 'font-weight:bold;' }, 'Nível 1 (50%) / Nível 2 (90%)'),
					E('div', { 'style': 'font-size:11px; color:#666; margin-top:2px;' }, 'Redução escalonada de duty cycle (dcoffpercent) gerenciada pelo driver Qualcomm para arrefecimento sem derrubar clientes.')
				]),
				E('div', { 'style': 'background:#fff; padding:8px 10px; border-radius:4px; border:1px solid #eee;' }, [
					E('strong', { 'style': 'color:#d35400;' }, '3. Nível 3 (Mitigação Máxima RF): '),
					E('span', { 'style': 'font-weight:bold;' }, '120°C (5G/6G) / 125°C (2.4G)'),
					E('div', { 'style': 'font-size:11px; color:#666; margin-top:2px;' }, 'Duty cycle 100% desativado (dcoffpercent=100) temporariamente para proteger o silício e FEMs.')
				]),
				E('div', { 'style': 'background:#fff; padding:8px 10px; border-radius:4px; border:1px solid #eee;' }, [
					E('strong', { 'style': 'color:#c0392b;' }, '4. Trip Point Crítico do Kernel Linux: '),
					E('span', { 'style': 'font-weight:bold;' }, '125°C'),
					E('div', { 'style': 'font-size:11px; color:#666; margin-top:2px;' }, 'Limite crítico de hardware do subsistema tsens do Linux: reinicialização preventiva de emergência do SoC.')
				])
			])
		]);

		return E('div', {
			'style': 'margin-bottom:25px; background:#fff; border:1px solid #e1e4e8; border-top:4px solid #16a085; border-radius:6px; padding:16px 20px; box-shadow:0 2px 6px rgba(0,0,0,0.04);'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;' }, [
				E('div', { 'style': 'display:flex; align-items:center; gap:10px; flex-wrap:wrap;' }, [
					E('h3', { 'style': 'margin:0; font-size:15px; color:#2c3e50; font-weight:bold;' }, '📡 Rádios Wi-Fi, Potências e Larguras Reais (Telemetria de RF ao Vivo)'),
					badgeLive
				]),
				badgeBdf
			]),
			E('div', { 'style': 'overflow-x:auto;' }, [
				E('table', { 'style': 'width:100%; border-collapse:collapse; text-align:left;' }, [
					E('thead', {}, [
						E('tr', { 'style': 'background:#f8f9fa; border-bottom:2px solid #dee2e6; font-size:11px; color:#666; text-transform:uppercase; letter-spacing:0.5px;' }, [
							E('th', { 'style': 'padding:8px 12px;' }, 'Banda / Chip'),
							E('th', { 'style': 'padding:8px 12px;' }, 'VAP'),
							E('th', { 'style': 'padding:8px 12px;' }, 'Canal / Largura Real'),
							E('th', { 'style': 'padding:8px 12px;' }, 'TxPower Conduzido [iw dev]'),
							E('th', { 'style': 'padding:8px 12px;' }, 'MIMO 2x2 (Est. Teórica +3 dB)'),
							E('th', { 'style': 'padding:8px 12px;' }, 'EIRP Estimado (Antena + TxBF)'),
							E('th', { 'style': 'padding:8px 12px;' }, 'Temperatura & Mitigação RF')
						])
					]),
					E('tbody', {}, tRows)
				])
			]),
			thermalInfoBox
		]);
	},

	renderFeaturesCard: function(features) {
		var self = this;
		var feats = features || {};

		var featureDefs = [
			{
				id: 'gaming',
				key: 'gaming_mode',
				icon: '🎮',
				name: 'Qualcomm Gaming Mode (Baixa Latência)',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Menor ping & jitter em jogos competitivos',
				offBenefit: 'Agregação máxima para downloads contínuos (Torrents/NAS)',
				desc: 'Minimiza tempos de fila no kernel Qualcomm e prioriza pacotes de jogos (filas AC_VO/VI). Quando desligado, maximiza janelas de buffer para tráfego contínuo.'
			},
			{
				id: 'ani',
				key: 'ani',
				icon: '🛡️',
				name: 'Adaptive Noise Immunity (ANI)',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Imunidade dinâmica contra interferências vizinhas',
				offBenefit: 'Sensibilidade física máxima constante (Bancada RF)',
				desc: 'Calibra dinamicamente o limiar CCA e os filtros OFDM contra ruído e canais poluídos por vizinhos. Desligue apenas em bancadas isoladas de laboratório.'
			},
			{
				id: 'qam4096',
				key: 'qam4096',
				icon: '⚡',
				name: 'Geração Wi-Fi 7 (4096-QAM / 320 MHz)',
				speed: '🔄 Recarrega Rádio 6G (~3s)',
				onBenefit: 'Wi-Fi 7 Pleno (11bea / 320 MHz / MCS 12-13 até 5.764 Mbps)',
				offBenefit: 'Modo Wi-Fi 6E Legado (11axa / HT160 até 2.402 Mbps)',
				desc: 'Alterna entre Wi-Fi 7 pleno (11bea com 320 MHz e 4096-QAM) e Wi-Fi 6E legado (11axa com 160 MHz e 1024-QAM). Desligue apenas se possuir clientes legados com incompatibilidade de handshake EHT.'
			},
			{
				id: 'rnr_6g',
				key: 'rnr_6g',
				icon: '📡',
				name: 'RNR 6 GHz Co-localizado (Reduced Neighbor Report)',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Descoberta instantânea nos beacons 2.4G/5G',
				offBenefit: 'Modo Stealth (Rede 6 GHz oculta para celulares)',
				desc: 'Anuncia a presença do rádio 6 GHz nos beacons de 2.4G e 5G (flags 0x7). Sem isso, celulares demoram a detectar ou ignoram a rede de 6 GHz.'
			},
			{
				id: 'rps',
				key: 'rps',
				icon: '🚀',
				name: 'RPS Quad-Core (Balanceamento de Interrupções)',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Filas divididas nos 4 núcleos ARM (Cortex-A53)',
				offBenefit: 'Fila única na CPU 0 (Pode causar gargalo)',
				desc: 'Distribui as interrupções de tráfego de rede entre todos os 4 núcleos do SoC Qualcomm IPQ5332, garantindo máxima vazão WAN 2.5G e LAN.'
			},
			{
				id: 'puncturing',
				key: 'puncturing',
				icon: '🎯',
				name: 'Wi-Fi 7 Preamble Puncturing Estrito',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Recorta canal interferido mantendo o resto ativo',
				offBenefit: 'Recuo padrão de largura para 80 MHz',
				desc: 'Caso surja ruído pontual de 20 MHz em 160/320 MHz, isola cirurgicamente o pedaço sujo e mantém até 300 MHz funcionais sem desconectar clientes.'
			},
			{
				id: 'beamforming',
				key: 'beamforming',
				icon: '📶',
				name: 'Tx Beamforming Sounding (TxBF)',
				speed: '⚡ Imediato (Sem Reiniciar)',
				onBenefit: 'Sondagem periódica a cada 100ms focando sinal no cliente',
				offBenefit: 'Emissão isotrópica padrão sem sondagem ativa',
				desc: 'Calcula matrizes de fase RF por medição de retorno (sounding) para concentrar o feixe de sinal de rádio diretamente sobre a antena do seu dispositivo.'
			}
		];

		var featureCards = featureDefs.map(function(feat) {
			var isEnabled = (feats[feat.key] !== '0');

			var badgeEl = E('span', {
				'id': 'feat-badge-' + feat.id,
				'style': 'font-size:11px; font-weight:bold; padding:3px 9px; border-radius:12px; display:inline-block; transition:all 0.2s;' +
				         (isEnabled ? 'background:#e8f8f0; color:#27ae60; border:1px solid #a3e4d7;' : 'background:#fdf2f2; color:#c0392b; border:1px solid #f5b7b1;')
			}, isEnabled ? '● ATIVADO' : '○ DESATIVADO');

			var btnEl = E('button', {
				'id': 'feat-btn-' + feat.id,
				'class': isEnabled ? 'cbi-button cbi-button-reset' : 'cbi-button cbi-button-positive',
				'style': 'font-size:12px; font-weight:bold; min-width:115px; cursor:pointer;',
				'data-val': isEnabled ? '1' : '0',
				'click': function(ev) {
					var currentVal = btnEl.getAttribute('data-val') || (isEnabled ? '1' : '0');
					var targetVal = (currentVal === '1') ? '0' : '1';
					btnEl.disabled = true;
					btnEl.textContent = '⏳ Aplicando...';

					if (feat.id === 'qam4096') {
						ui.showModal('Aplicando Modulação Wi-Fi 7...', [
							E('p', { 'class': 'spinning' }, 'Recarregando o subsistema de rádio 6 GHz para alternar entre 4096-QAM (Wi-Fi 7) e 1024-QAM (Wi-Fi 6)... Aguarde ~4 segundos.')
						]);
					}

					callToggleFeature(feat.id, targetVal).then(function(res) {
						if (feat.id === 'qam4096') {
							setTimeout(function() {
								window.location.reload();
							}, 3500);
							return;
						}
						return callGetStatus().then(function(newStatus) {
							self.updateLiveTelemetry(newStatus);
						});
					}).catch(function(err) {
						ui.addNotification(null, E('p', {}, 'Erro ao alterar recurso ' + feat.name + ': ' + (err.message || err)));
					}).finally(function() {
						if (feat.id !== 'qam4096') {
							btnEl.disabled = false;
						}
					});
				}
			}, isEnabled ? '⏸ Desligar' : '▶ Ligar');

			return E('div', {
				'id': 'feat-card-' + feat.id,
				'style': 'background:#fff; border:1px solid #e1e4e8; border-top:3px solid ' + (isEnabled ? '#27ae60' : '#888') + '; border-radius:6px; padding:14px 16px; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 1px 3px rgba(0,0,0,0.03);'
			}, [
				E('div', {}, [
					E('div', { 'style': 'display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px; gap:8px;' }, [
						E('div', { 'style': 'font-weight:bold; font-size:13px; color:#2c3e50; display:flex; align-items:center; gap:6px;' }, [
							E('span', { 'style': 'font-size:16px;' }, feat.icon),
							feat.name
						]),
						badgeEl
					]),
					E('div', { 'style': 'font-size:10px; color:#0275d8; font-weight:bold; margin-bottom:8px;' }, feat.speed),
					E('div', { 'style': 'font-size:12px; color:#555; margin-bottom:10px; line-height:1.45;' }, feat.desc),
					E('div', { 'style': 'font-size:11px; background:#f8f9fa; border-radius:4px; padding:8px 10px; margin-bottom:12px; border-left:3px solid #3498db;' }, [
						E('div', {}, [ E('strong', { 'style': 'color:#27ae60;' }, '✓ Quando Ativo: '), feat.onBenefit ]),
						E('div', { 'style': 'margin-top:4px;' }, [ E('strong', { 'style': 'color:#c0392b;' }, '✗ Quando Desligado: '), feat.offBenefit ])
					])
				]),
				E('div', { 'style': 'display:flex; justify-content:flex-end; align-items:center; border-top:1px solid #f0f0f0; padding-top:8px;' }, [
					btnEl
				])
			]);
		});

		return E('div', {
			'style': 'margin-top:25px; margin-bottom:25px; background:#fff; border:1px solid #e1e4e8; border-top:4px solid #2980b9; border-radius:6px; padding:16px 20px; box-shadow:0 2px 6px rgba(0,0,0,0.04);'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;' }, [
				E('h3', { 'style': 'margin:0; font-size:15px; color:#2c3e50; font-weight:bold;' }, '🎮 Interruptores de Recursos RF & Otimizações de Hardware Qualcomm'),
				E('span', { 'style': 'font-size:11px; color:#666;' }, 'Controle em tempo real de filas, imunidade a ruído, modulações e interrupções da CPU')
			]),
			E('div', { 'style': 'font-size:12px; color:#666; margin-bottom:14px;' }, 'Alterne recursos avançados do driver e do silício Qualcomm IPQ5332 / QCN9224 em tempo real. As preferências são gravadas de forma persistente e restauradas na inicialização.'),
			E('div', { 'style': 'display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:12px;' }, featureCards)
		]);
	},

	renderPortsCard: function(ports) {
		var p = ports || {};
		var wan = p.wan || { speed: '0', duplex: '', carrier: '0' };
		var lan1 = p.lan1 || { speed: '', link: 'down' };
		var lan2 = p.lan2 || { speed: '', link: 'down' };

		var wanIsUp = (wan.carrier === '1');
		var wanSpeedNum = parseInt(wan.speed) || 0;
		var wanSpeedStr = wanIsUp ? (wanSpeedNum >= 2500 ? '2500 Mb/s (2.5 Gbps)' : wanSpeedNum > 0 ? (wanSpeedNum + ' Mb/s') : '2500 Mb/s') : t('port_disconnected');
		var wanBadgeColor = wanIsUp ? '#27ae60' : '#e74c3c';
		var wanDuplexStr = (wanIsUp && wan.duplex) ? (' • ' + wan.duplex.toUpperCase() + ' DUPLEX') : '';

		var lan1IsUp = (lan1.link === 'up');
		var lan1SpeedStr = lan1IsUp ? ((lan1.speed.indexOf('1000') !== -1 ? '1000 Mb/s (1.0 Gbps)' : lan1.speed) + ' • FULL DUPLEX') : t('port_disconnected');
		var lan1BadgeColor = lan1IsUp ? '#27ae60' : '#888';

		var lan2IsUp = (lan2.link === 'up');
		var lan2SpeedStr = lan2IsUp ? ((lan2.speed.indexOf('1000') !== -1 ? '1000 Mb/s (1.0 Gbps)' : lan2.speed) + ' • FULL DUPLEX') : t('port_disconnected');
		var lan2BadgeColor = lan2IsUp ? '#27ae60' : '#888';

		function makePortBox(idPrefix, icon, title, speedText, maxText, badgeColor, isUp) {
			return E('div', {
				'id': idPrefix + '-box',
				'style': 'flex:1; min-width:240px; background:#fff; border:1px solid #e1e4e8; border-top:3px solid ' + badgeColor + '; border-radius:6px; padding:12px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.04);'
			}, [
				E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;' }, [
					E('strong', { 'style': 'font-size:13px; color:#333;' }, [ icon + ' ', title ]),
					E('span', { 'id': idPrefix + '-badge', 'style': 'font-size:11px; background:' + (isUp ? '#e8f8f0' : '#fdf2f2') + '; color:' + (isUp ? '#27ae60' : '#e74c3c') + '; padding:2px 8px; border-radius:12px; font-weight:bold;' }, isUp ? t('port_connected') : t('port_disconnected'))
				]),
				E('div', { 'id': idPrefix + '-speed', 'style': 'font-size:15px; font-weight:bold; color:' + (isUp ? '#111' : '#888') + '; margin-bottom:4px;' }, speedText),
				E('div', { 'style': 'font-size:11px; color:#666;' }, maxText)
			]);
		}

		return E('div', { 'style': 'margin-bottom:25px;' }, [
			E('h3', { 'style': 'margin-top:0; margin-bottom:12px;' }, t('ports_title')),
			E('div', { 'style': 'display:flex; flex-wrap:wrap; gap:14px;' }, [
				makePortBox('port-wan', '🌐', t('wan_port_label') + ' [eth0]', wanSpeedStr + wanDuplexStr, 'Porta Física 2.5 Gbps Ultra High-Speed', wanBadgeColor, wanIsUp),
				makePortBox('port-lan1', '💻', t('lan1_port_label') + ' [Port 1]', lan1SpeedStr, 'Porta Física Gigabit Ethernet (LAN)', lan1BadgeColor, lan1IsUp),
				makePortBox('port-lan2', '💻', t('lan2_port_label') + ' [Port 2]', lan2SpeedStr, 'Porta Física Gigabit Ethernet (LAN)', lan2BadgeColor, lan2IsUp)
			])
		]);
	},

	updateLiveTelemetry: function(status) {
		var self = this;
		if (!status || !status.radios) return;
		var data = self.formatRadioData(status.radios);

		var now = new Date();
		var timeStr = ('0' + now.getHours()).slice(-2) + ':' +
		              ('0' + now.getMinutes()).slice(-2) + ':' +
		              ('0' + now.getSeconds()).slice(-2);

		var liveBadgeEl = document.getElementById('rf-live-badge');
		if (liveBadgeEl) {
			liveBadgeEl.textContent = '🟢 Ao Vivo (2s) • ' + timeStr;
		}

		if (status.features) {
			var feats = status.features;
			var featList = [
				{ id: 'gaming', key: 'gaming_mode' },
				{ id: 'ani', key: 'ani' },
				{ id: 'qam4096', key: 'qam4096' },
				{ id: 'rnr_6g', key: 'rnr_6g' },
				{ id: 'rps', key: 'rps' },
				{ id: 'puncturing', key: 'puncturing' },
				{ id: 'beamforming', key: 'beamforming' }
			];
			featList.forEach(function(f) {
				var val = feats[f.key] || '0';
				var isEn = (val === '1');
				var badgeEl = document.getElementById('feat-badge-' + f.id);
				if (badgeEl) {
					badgeEl.textContent = isEn ? '● ATIVADO' : '○ DESATIVADO';
					badgeEl.style.background = isEn ? '#e8f8f0' : '#fdf2f2';
					badgeEl.style.color = isEn ? '#27ae60' : '#c0392b';
					badgeEl.style.border = isEn ? '1px solid #a3e4d7' : '1px solid #f5b7b1';
				}
				var cardEl = document.getElementById('feat-card-' + f.id);
				if (cardEl) {
					cardEl.style.borderTopColor = isEn ? '#27ae60' : '#888';
				}
				var btnEl = document.getElementById('feat-btn-' + f.id);
				if (btnEl && !btnEl.disabled) {
					btnEl.textContent = isEn ? '⏸ Desligar' : '▶ Ligar';
					btnEl.className = isEn ? 'cbi-button cbi-button-reset' : 'cbi-button cbi-button-positive';
					btnEl.setAttribute('data-val', val);
				}
			});
		}

		['wifi0', 'wifi1', 'wifi2'].forEach(function(dev) {
			var r = data[dev];
			var chEl = document.getElementById('rf-ch-' + dev);
			if (chEl) chEl.textContent = 'Canal ' + r.ch + ' (' + r.bw + ')';

			var condEl = document.getElementById('rf-cond-' + dev);
			if (condEl) condEl.textContent = r.cond;

			var mimoEl = document.getElementById('rf-mimo-' + dev);
			if (mimoEl) mimoEl.textContent = r.mimo;

			var eirpEl = document.getElementById('rf-eirp-' + dev);
			if (eirpEl) eirpEl.textContent = r.eirp;

			var tempEl = document.getElementById('rf-temp-' + dev);
			if (tempEl) {
				dom.content(tempEl, self.buildTempNode(r));
			}
		});

		// Atualiza o Lock Badge dinamicamente
		var lockBadgeEl = document.getElementById('rf-lock-badge');
		if (lockBadgeEl) {
			var isLocked = (status.radios && status.radios.lock_status === 'locked');
			if (isLocked) {
				lockBadgeEl.style.background = '#f8d7da';
				lockBadgeEl.style.color = '#721c24';
				lockBadgeEl.style.border = '1px solid #f5c6cb';
				lockBadgeEl.textContent = '⚠️ ' + t('lock_badge_locked');
			} else {
				lockBadgeEl.style.background = '#d4edda';
				lockBadgeEl.style.color = '#155724';
				lockBadgeEl.style.border = '1px solid #c3e6cb';
				lockBadgeEl.textContent = '🔒 ' + t('lock_badge_clean');
			}
		}

		// Atualiza os Badges de status dos 3 cards dinamicamente
		['wifi0', 'wifi1', 'wifi2'].forEach(function(w) {
			var rBadgeEl = document.getElementById('radio-status-' + w);
			if (rBadgeEl && status.radios && status.radios[w]) {
				var rInfo = status.radios[w];
				var isLocked = (status.radios && status.radios.lock_status === 'locked');
				if (rInfo.disabled === '1') {
					rBadgeEl.style.background = '#e0e0e0';
					rBadgeEl.style.color = '#555';
					rBadgeEl.style.border = 'none';
					rBadgeEl.textContent = t('radio_status_disabled');
				} else if (rInfo.status === 'online') {
					rBadgeEl.style.background = '#d4edda';
					rBadgeEl.style.color = '#155724';
					rBadgeEl.style.border = '1px solid #c3e6cb';
					rBadgeEl.textContent = '● ' + t('radio_status_online');
				} else if (isLocked) {
					rBadgeEl.style.background = '#f8d7da';
					rBadgeEl.style.color = '#721c24';
					rBadgeEl.style.border = '1px solid #f5c6cb';
					rBadgeEl.textContent = t('radio_status_locked');
				} else {
					rBadgeEl.style.background = '#fff3cd';
					rBadgeEl.style.color = '#856404';
					rBadgeEl.style.border = '1px solid #ffeeba';
					rBadgeEl.textContent = t('radio_status_starting');
				}
			}
		});

		if (status.ports) {
			var p = status.ports;
			var wan = p.wan || {};
			var wanUp = (wan.carrier === '1');
			var wanSpeedNum = parseInt(wan.speed) || 0;
			var wanSpeedStr = wanUp ? (wanSpeedNum >= 2500 ? '2500 Mb/s (2.5 Gbps)' : wanSpeedNum > 0 ? (wanSpeedNum + ' Mb/s') : '2500 Mb/s') : t('port_disconnected');
			var wanBadgeColor = wanUp ? '#27ae60' : '#e74c3c';
			var wanDuplexStr = (wanUp && wan.duplex) ? (' • ' + wan.duplex.toUpperCase() + ' DUPLEX') : '';

			var wanSpeedEl = document.getElementById('port-wan-speed');
			if (wanSpeedEl) {
				wanSpeedEl.textContent = wanSpeedStr + wanDuplexStr;
				wanSpeedEl.style.color = wanUp ? '#111' : '#888';
			}
			var wanBadgeEl = document.getElementById('port-wan-badge');
			if (wanBadgeEl) {
				wanBadgeEl.textContent = wanUp ? t('port_connected') : t('port_disconnected');
				wanBadgeEl.style.background = wanUp ? '#e8f8f0' : '#fdf2f2';
				wanBadgeEl.style.color = wanBadgeColor;
			}
			var wanBoxEl = document.getElementById('port-wan-box');
			if (wanBoxEl) wanBoxEl.style.borderTopColor = wanBadgeColor;

			var lan1 = p.lan1 || {};
			var lan1Up = (lan1.link === 'up');
			var lan1SpeedStr = lan1Up ? ((lan1.speed.indexOf('1000') !== -1 ? '1000 Mb/s (1.0 Gbps)' : lan1.speed) + ' • FULL DUPLEX') : t('port_disconnected');
			var lan1BadgeColor = lan1Up ? '#27ae60' : '#888';
			var lan1SpeedEl = document.getElementById('port-lan1-speed');
			if (lan1SpeedEl) {
				lan1SpeedEl.textContent = lan1SpeedStr;
				lan1SpeedEl.style.color = lan1Up ? '#111' : '#888';
			}
			var lan1BadgeEl = document.getElementById('port-lan1-badge');
			if (lan1BadgeEl) {
				lan1BadgeEl.textContent = lan1Up ? t('port_connected') : t('port_disconnected');
				lan1BadgeEl.style.background = lan1Up ? '#e8f8f0' : '#fdf2f2';
				lan1BadgeEl.style.color = lan1BadgeColor;
			}
			var lan1BoxEl = document.getElementById('port-lan1-box');
			if (lan1BoxEl) lan1BoxEl.style.borderTopColor = lan1BadgeColor;

			var lan2 = p.lan2 || {};
			var lan2Up = (lan2.link === 'up');
			var lan2SpeedStr = lan2Up ? ((lan2.speed.indexOf('1000') !== -1 ? '1000 Mb/s (1.0 Gbps)' : lan2.speed) + ' • FULL DUPLEX') : t('port_disconnected');
			var lan2BadgeColor = lan2Up ? '#27ae60' : '#888';
			var lan2SpeedEl = document.getElementById('port-lan2-speed');
			if (lan2SpeedEl) {
				lan2SpeedEl.textContent = lan2SpeedStr;
				lan2SpeedEl.style.color = lan2Up ? '#111' : '#888';
			}
			var lan2BadgeEl = document.getElementById('port-lan2-badge');
			if (lan2BadgeEl) {
				lan2BadgeEl.textContent = lan2Up ? t('port_connected') : t('port_disconnected');
				lan2BadgeEl.style.background = lan2Up ? '#e8f8f0' : '#fdf2f2';
				lan2BadgeEl.style.color = lan2BadgeColor;
			}
			var lan2BoxEl = document.getElementById('port-lan2-box');
			if (lan2BoxEl) lan2BoxEl.style.borderTopColor = lan2BadgeColor;
		}
	},


	render: function(data) {
		var self = this;
		var status = (data && Array.isArray(data)) ? (data[0] || {}) : (data || {});
		var guardStatus = (data && Array.isArray(data)) ? (data[1] || {}) : {};
		var mode = status.mode || 'speed_max';
		var radios = status.radios || {};
		var ifaces = status.interfaces || [];

		var guardBannerNode = null;
		if (guardStatus && guardStatus.rollback_kind) {
			var isRollback = (guardStatus.rollback_kind === 'rollback');
			var reason = guardStatus.reason || t('guard_unknown_reason');
			var guardMsg = isRollback ? t('guard_rollback_msg', reason) : t('guard_heal_msg', reason);
			var bg = isRollback ? '#fff3cd' : '#e8f4fd';
			var border = isRollback ? '#ffeeba' : '#b8daff';
			var barColor = isRollback ? '#e67e22' : '#0275d8';
			var txtColor = isRollback ? '#856404' : '#004085';
			var icon = isRollback ? '🛡️' : '🩺';

			var guardBannerEl = E('div', {
				'id': 'predator-guard-banner',
				'style': 'background:' + bg + '; border:1px solid ' + border + '; border-left:6px solid ' + barColor + '; padding:14px 18px; margin-bottom:20px; border-radius:4px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow:0 1px 3px rgba(0,0,0,0.06);'
			}, [
				E('div', { 'style': 'display:flex; align-items:flex-start; gap:12px; flex:1; min-width:280px;' }, [
					E('span', { 'style': 'font-size:24px; line-height:1;' }, icon),
					E('div', {}, [
						E('div', { 'style': 'font-weight:bold; font-size:14px; color:' + txtColor + '; margin-bottom:2px;' }, t('guard_banner_title')),
						E('div', { 'style': 'font-size:13px; color:' + txtColor + '; line-height:1.4;' }, guardMsg)
					])
				]),
				E('button', {
					'class': 'btn cbi-button-action',
					'style': 'padding:6px 14px; font-size:12px; font-weight:bold; cursor:pointer;',
					'click': function(ev) {
						var btn = ev.target;
						btn.disabled = true;
						callAckGuard().then(function() {
							if (guardBannerEl && guardBannerEl.parentNode) {
								guardBannerEl.parentNode.removeChild(guardBannerEl);
							}
						});
					}
				}, t('guard_btn_dismiss'))
			]);
			guardBannerNode = guardBannerEl;
		}

		// Mode Banner info
		var bannerColor = '#0275d8';
		var bannerTitle = t('topo1_title');
		var bannerDesc = t('topo1_desc');

		if (mode === 'mlo_turbo') {
			bannerColor = '#5cb85c';
			bannerTitle = t('topo2_title');
			bannerDesc = t('topo2_desc');
		} else if (mode === 'mlo_full') {
			bannerColor = '#6f42c1';
			bannerTitle = t('topo3_title');
			bannerDesc = t('topo3_desc');
		} else if (mode === 'single_ssid') {
			bannerColor = '#17a2b8';
			bannerTitle = t('topo5_title');
			bannerDesc = t('topo5_desc');
		} else if (mode === 'separate') {
			bannerColor = '#f0ad4e';
			bannerTitle = t('topo4_title');
			bannerDesc = t('topo4_desc');
		}

		var modeBanner = E('div', {
			'style': 'background:#f8f9fa; border-left:6px solid ' + bannerColor + '; padding:18px; margin-bottom:25px; border-radius:4px; box-shadow:0 1px 3px rgba(0,0,0,0.05);'
		}, [
			E('div', { 'style': 'display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:14px;' }, [
				E('div', { 'style': 'flex:1; min-width:320px;' }, [
					E('div', { 'style': 'font-size:11px; font-weight:bold; color:#777; text-transform:uppercase; letter-spacing:1px;' }, t('active_profile')),
					E('div', { 'style': 'font-size:17px; font-weight:bold; color:#222; margin:4px 0;' }, [
						E('span', { 'style': 'display:inline-block; width:10px; height:10px; border-radius:50%; background:' + bannerColor + '; margin-right:8px;' }),
						bannerTitle
					]),
					E('div', { 'style': 'font-size:13px; color:#555; line-height:1.4;' }, bannerDesc)
				]),
				E('div', { 'style': 'display:flex; flex-wrap:wrap; gap:6px;' }, [
					E('button', {
						'class': 'btn cbi-button-action',
						'style': (mode === 'speed_max' ? 'font-weight:bold; outline:2px solid #0275d8;' : ''),
						'title': t('topo1_tip'),
						'click': function() { self.renderTopologyModal('speed_max', status); }
					}, t('topo1_btn')),
					E('button', {
						'class': 'btn cbi-button-action',
						'style': (mode === 'mlo_turbo' ? 'font-weight:bold; outline:2px solid #5cb85c;' : ''),
						'title': t('topo2_tip'),
						'click': function() { self.renderTopologyModal('mlo_turbo', status); }
					}, t('topo2_btn')),
					E('button', {
						'class': 'btn cbi-button-action',
						'style': (mode === 'mlo_full' ? 'font-weight:bold; outline:2px solid #6f42c1;' : ''),
						'title': t('topo3_tip'),
						'click': function() { self.renderTopologyModal('mlo_full', status); }
					}, t('topo3_btn')),
					E('button', {
						'class': 'btn',
						'style': (mode === 'separate' ? 'font-weight:bold; outline:2px solid #f0ad4e;' : ''),
						'title': t('topo4_tip'),
						'click': function() { self.renderTopologyModal('separate', status); }
					}, t('topo4_btn')),
					E('button', {
						'class': 'btn cbi-button-action',
						'style': (mode === 'single_ssid' ? 'font-weight:bold; outline:2px solid #17a2b8;' : ''),
						'title': t('topo5_tip'),
						'click': function() { self.renderTopologyModal('single_ssid', status); }
					}, t('topo5_btn'))
				])
			])
		]);

		// Radios Data & Channels
		var r0 = radios.wifi0 || { channel: '6', htmode: 'HT40', txpower: '22' };
		var r1 = radios.wifi1 || { channel: '36', htmode: 'HT80', txpower: '23' };
		var r2 = radios.wifi2 || { channel: '37', htmode: 'HT320', txpower: '20' };

		var autoLabel = t('auto_rec');
		var autoPscLabel = t('auto_psc_rec');

		var rec24 = [
			{ val: 'auto', label: autoLabel },
			{ val: '1', label: 'Canal 1 (2412 MHz)' },
			{ val: '6', label: 'Canal 6 (2437 MHz)' },
			{ val: '11', label: 'Canal 11 (2462 MHz)' }
		];
		var all24 = [
			{ val: 'auto', label: autoLabel },
			{ val: '1', label: 'Canal 1 (2412 MHz)' }, { val: '2', label: 'Canal 2 (2417 MHz)' },
			{ val: '3', label: 'Canal 3 (2422 MHz)' }, { val: '4', label: 'Canal 4 (2427 MHz)' },
			{ val: '5', label: 'Canal 5 (2432 MHz)' }, { val: '6', label: 'Canal 6 (2437 MHz)' },
			{ val: '7', label: 'Canal 7 (2442 MHz)' }, { val: '8', label: 'Canal 8 (2447 MHz)' },
			{ val: '9', label: 'Canal 9 (2452 MHz)' }, { val: '10', label: 'Canal 10 (2457 MHz)' },
			{ val: '11', label: 'Canal 11 (2462 MHz)' },
			{ val: '12', label: 'Canal 12 (2467 MHz - Não transmitido no perfil US)' },
			{ val: '13', label: 'Canal 13 (2472 MHz - Não transmitido no perfil US)' }
		];

		var rec5 = [
			{ val: 'auto', label: autoLabel },
			{ val: '36', label: 'Canal 36 (5180 MHz)' }, { val: '40', label: 'Canal 40 (5200 MHz)' },
			{ val: '44', label: 'Canal 44 (5220 MHz)' }, { val: '48', label: 'Canal 48 (5240 MHz)' },
			{ val: '149', label: 'Canal 149 (5745 MHz)' }, { val: '153', label: 'Canal 153 (5765 MHz)' },
			{ val: '157', label: 'Canal 157 (5785 MHz)' }, { val: '161', label: 'Canal 161 (5805 MHz)' }
		];
		var all5 = [
			{ val: 'auto', label: autoLabel },
			{ val: '36', label: 'Canal 36 (5180 MHz)' }, { val: '40', label: 'Canal 40 (5200 MHz)' },
			{ val: '44', label: 'Canal 44 (5220 MHz)' }, { val: '48', label: 'Canal 48 (5240 MHz)' },
			{ val: '52', label: 'Canal 52 (5260 MHz - DFS)' }, { val: '56', label: 'Canal 56 (5280 MHz - DFS)' },
			{ val: '60', label: 'Canal 60 (5300 MHz - DFS)' }, { val: '64', label: 'Canal 64 (5320 MHz - DFS)' },
			{ val: '100', label: 'Canal 100 (5500 MHz - DFS)' }, { val: '104', label: 'Canal 104 (5520 MHz - DFS)' },
			{ val: '108', label: 'Canal 108 (5540 MHz - DFS)' }, { val: '112', label: 'Canal 112 (5560 MHz - DFS)' },
			{ val: '116', label: 'Canal 116 (5580 MHz - DFS)' }, { val: '120', label: 'Canal 120 (5600 MHz - DFS)' },
			{ val: '124', label: 'Canal 124 (5620 MHz - DFS)' }, { val: '128', label: 'Canal 128 (5640 MHz - DFS)' },
			{ val: '132', label: 'Canal 132 (5660 MHz - DFS)' }, { val: '136', label: 'Canal 136 (5680 MHz - DFS)' },
			{ val: '140', label: 'Canal 140 (5700 MHz - DFS)' }, { val: '144', label: 'Canal 144 (5720 MHz - DFS)' },
			{ val: '149', label: 'Canal 149 (5745 MHz)' }, { val: '153', label: 'Canal 153 (5765 MHz)' },
			{ val: '157', label: 'Canal 157 (5785 MHz)' }, { val: '161', label: 'Canal 161 (5805 MHz)' },
			{ val: '165', label: 'Canal 165 (5825 MHz)' }
		];

		var rec6 = [
			{ val: 'auto', label: autoPscLabel },
			{ val: '37', label: 'Canal 37 PSC (6135 MHz)' }, { val: '53', label: 'Canal 53 PSC (6215 MHz)' },
			{ val: '69', label: 'Canal 69 PSC (6295 MHz)' }, { val: '85', label: 'Canal 85 PSC (6375 MHz)' },
			{ val: '101', label: 'Canal 101 PSC (6455 MHz)' }, { val: '117', label: 'Canal 117 PSC (6535 MHz)' },
			{ val: '133', label: 'Canal 133 PSC (6615 MHz)' }, { val: '149', label: 'Canal 149 PSC (6695 MHz)' },
			{ val: '165', label: 'Canal 165 PSC (6775 MHz)' }, { val: '181', label: 'Canal 181 PSC (6855 MHz)' },
			{ val: '197', label: 'Canal 197 PSC (6935 MHz)' }, { val: '213', label: 'Canal 213 PSC (7015 MHz)' },
			{ val: '229', label: 'Canal 229 PSC (7095 MHz)' }
		];
		var all6 = [
			{ val: 'auto', label: autoPscLabel },
			{ val: '1', label: 'Canal 1 (5955 MHz)' }, { val: '5', label: 'Canal 5 PSC (5975 MHz)' },
			{ val: '9', label: 'Canal 9 (5995 MHz)' }, { val: '13', label: 'Canal 13 (6015 MHz)' },
			{ val: '17', label: 'Canal 17 (6035 MHz)' }, { val: '21', label: 'Canal 21 PSC (6055 MHz)' },
			{ val: '25', label: 'Canal 25 (6075 MHz)' }, { val: '29', label: 'Canal 29 (6095 MHz)' },
			{ val: '33', label: 'Canal 33 (6115 MHz)' }, { val: '37', label: 'Canal 37 PSC (6135 MHz)' },
			{ val: '41', label: 'Canal 41 (6155 MHz)' }, { val: '45', label: 'Canal 45 (6175 MHz)' },
			{ val: '49', label: 'Canal 49 (6195 MHz)' }, { val: '53', label: 'Canal 53 PSC (6215 MHz)' },
			{ val: '57', label: 'Canal 57 (6235 MHz)' }, { val: '61', label: 'Canal 61 (6255 MHz)' },
			{ val: '65', label: 'Canal 65 (6275 MHz)' }, { val: '69', label: 'Canal 69 PSC (6295 MHz)' },
			{ val: '73', label: 'Canal 73 (6315 MHz)' }, { val: '77', label: 'Canal 77 (6335 MHz)' },
			{ val: '81', label: 'Canal 81 (6355 MHz)' }, { val: '85', label: 'Canal 85 PSC (6375 MHz)' },
			{ val: '89', label: 'Canal 89 (6395 MHz)' }, { val: '93', label: 'Canal 93 (6415 MHz)' },
			{ val: '97', label: 'Canal 97 (6435 MHz)' }, { val: '101', label: 'Canal 101 PSC (6455 MHz)' },
			{ val: '105', label: 'Canal 105 (6475 MHz)' }, { val: '109', label: 'Canal 109 (6495 MHz)' },
			{ val: '113', label: 'Canal 113 (6515 MHz)' }, { val: '117', label: 'Canal 117 PSC (6535 MHz)' },
			{ val: '121', label: 'Canal 121 (6555 MHz)' }, { val: '125', label: 'Canal 125 (6575 MHz)' },
			{ val: '129', label: 'Canal 129 (6595 MHz)' }, { val: '133', label: 'Canal 133 PSC (6615 MHz)' },
			{ val: '137', label: 'Canal 137 (6635 MHz)' }, { val: '141', label: 'Canal 141 (6655 MHz)' },
			{ val: '145', label: 'Canal 145 (6675 MHz)' }, { val: '149', label: 'Canal 149 PSC (6695 MHz)' },
			{ val: '153', label: 'Canal 153 (6715 MHz)' }, { val: '157', label: 'Canal 157 (6735 MHz)' },
			{ val: '161', label: 'Canal 161 (6755 MHz)' }, { val: '165', label: 'Canal 165 PSC (6775 MHz)' },
			{ val: '169', label: 'Canal 169 (6795 MHz)' }, { val: '173', label: 'Canal 173 (6815 MHz)' },
			{ val: '177', label: 'Canal 177 (6835 MHz)' }, { val: '181', label: 'Canal 181 PSC (6855 MHz)' },
			{ val: '185', label: 'Canal 185 (6875 MHz)' }, { val: '189', label: 'Canal 189 (6895 MHz)' },
			{ val: '193', label: 'Canal 193 (6915 MHz)' }, { val: '197', label: 'Canal 197 PSC (6935 MHz)' },
			{ val: '201', label: 'Canal 201 (6955 MHz)' }, { val: '205', label: 'Canal 205 (6975 MHz)' },
			{ val: '209', label: 'Canal 209 (6995 MHz)' }, { val: '213', label: 'Canal 213 PSC (7015 MHz)' },
			{ val: '217', label: 'Canal 217 (7035 MHz)' }, { val: '221', label: 'Canal 221 (7055 MHz)' },
			{ val: '225', label: 'Canal 225 (7075 MHz)' }, { val: '229', label: 'Canal 229 PSC (7095 MHz)' },
			{ val: '233', label: 'Canal 233 (7115 MHz)' }
		];

		var card0 = this.renderRadioCard(
			'wifi0', t('radio0_title'), '#d9534f',
			rec24, all24,
			[
				{ val: 'HT40', label: 'Auto (20/40 MHz)' },
				{ val: 'HT20', label: '20 MHz' },
				{ val: 'HT40', label: '40 MHz' }
			],
			r0,
			t('radio0_note')
		);

		var card1 = this.renderRadioCard(
			'wifi1', t('radio1_title'), '#0275d8',
			rec5, all5,
			[
				{ val: 'HT80', label: t('width_80m_rec') },
				{ val: 'HT160', label: t('width_160m_fast') },
				{ val: 'HT40', label: '20/40 MHz' },
				{ val: 'HT20', label: '20 MHz' }
			],
			r1,
			t('radio1_note')
		);

		var card2 = this.renderRadioCard(
			'wifi2', t('radio2_title'), '#5cb85c',
			rec6, all6,
			[
				{ val: 'HT320', label: 'Auto (Máx 320 MHz)' },
				{ val: 'HT320', label: '320 MHz (Full Width)' },
				{ val: 'HT160', label: '160 MHz' },
				{ val: 'HT80', label: '80 MHz' },
				{ val: 'HT40', label: '40 MHz' },
				{ val: 'HT20', label: '20 MHz' }
			],
			r2,
			t('radio2_note')
		);

		var radiosGrid = E('div', {
			'style': 'display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:15px; margin-bottom:30px;'
		}, [ card0, card1, card2 ]);

		// Network List Table
		var rows = [];
		ifaces.forEach(function(ifc) {
			var devLabel = (ifc.device === 'wifi0') ? '2.4 GHz' : (ifc.device === 'wifi1') ? '5 GHz' : '6 GHz';
			var devBadgeColor = (ifc.device === 'wifi0') ? '#d9534f' : (ifc.device === 'wifi1') ? '#0275d8' : '#5cb85c';
			var isDis = (ifc.disabled === '1');
			var isGuest = (ifc.network === 'guest');

			var mldBadge = (ifc.mld) ? E('span', { 'style': 'background:#5cb85c; color:#fff; padding:2px 6px; border-radius:3px; margin-left:6px; font-size:11px; font-weight:bold;' }, 'MLO') : E('span');

			var isCore = (ifc.section === 'wifi0_ap' || ifc.section === 'wifi1_ap' || ifc.section === 'wifi2_ap');

			var statusBadge = isDis ?
				E('span', { 'style': 'color:#e74c3c; font-weight:bold;' }, t('status_off')) :
				E('span', { 'style': 'color:#27ae60; font-weight:bold;' }, t('status_on'));

			// Password cell with inline toggle eye
			var passCellContent;
			if (!ifc.key || ifc.encryption === 'none') {
				passCellContent = E('em', { 'style': 'color:#888;' }, t('pass_open'));
			} else {
				var passSpan = E('span', { 'style': 'font-family:monospace; margin-right:6px;' }, '••••••••');
				var isRevealed = false;
				var tableEyeBtn = E('button', {
					'class': 'btn',
					'type': 'button',
					'style': 'padding:2px 6px; font-size:11px; cursor:pointer;',
					'title': t('btn_view_pass') + ' / ' + t('btn_hide_pass'),
					'click': function() {
						isRevealed = !isRevealed;
						if (isRevealed) {
							passSpan.textContent = ifc.key;
							tableEyeBtn.textContent = '🙈';
						} else {
							passSpan.textContent = '••••••••';
							tableEyeBtn.textContent = '👁';
						}
					}
				}, '👁');
				passCellContent = E('div', { 'style': 'display:flex; align-items:center;' }, [ passSpan, tableEyeBtn ]);
			}

			var actionBtns = [
				E('button', {
					'class': isDis ? 'btn cbi-button-action' : 'btn cbi-button-neutral',
					'style': 'padding:4px 8px; font-size:12px; margin-right:4px;',
					'title': isDis ? t('btn_turn_on') : t('btn_turn_off'),
					'click': function() {
						callToggleVif(ifc.section, isDis ? '0' : '1').then(function() {
							safeReloadAfterRestart(t('status_switching'));
						});
					}
				}, isDis ? t('btn_turn_on') : t('btn_turn_off')),
				E('button', {
					'class': 'btn cbi-button-action',
					'style': 'padding:4px 8px; font-size:12px; margin-right:4px;',
					'title': t('btn_edit'),
					'click': function() { self.renderEditNetworkModal(ifc); }
				}, t('btn_edit'))
			];

			if (!isCore) {
				actionBtns.push(E('button', {
					'class': 'btn cbi-button-negative',
					'style': 'padding:4px 8px; font-size:12px;',
					'title': t('btn_delete'),
					'click': function() {
						if (confirm(t('del_confirm', ifc.ssid))) {
							callDelVif(ifc.section).then(function() {
								safeReloadAfterRestart(t('deleting_network'));
							});
						}
					}
				}, t('btn_delete')));
			} else {
				actionBtns.push(E('span', {
					'style': 'font-size:11px; color:#888; margin-left:4px;',
					'title': t('badge_core_tip')
				}, t('badge_core')));
			}

			rows.push(E('tr', { 'class': 'tr' }, [
				E('td', { 'class': 'td' }, [ E('strong', {}, ifc.ssid), mldBadge ]),
				E('td', { 'class': 'td' }, E('span', { 'style': 'color:#fff; background:' + devBadgeColor + '; padding:2px 8px; border-radius:3px; font-size:12px; font-weight:bold;' }, devLabel)),
				E('td', { 'class': 'td' }, passCellContent),
				E('td', { 'class': 'td' }, ifc.encryption.toUpperCase()),
				E('td', { 'class': 'td' }, isGuest ? E('span', { 'style': 'color:#e67e22; font-weight:bold;' }, t('type_guest')) : t('type_main')),
				E('td', { 'class': 'td' }, statusBadge),
				E('td', { 'class': 'td right', 'style': 'white-space:nowrap;' }, actionBtns)
			]));
		});

		var networksTable = E('div', { 'style': 'width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; margin-bottom:25px;' }, [
			E('table', { 'class': 'table cbi-section-table', 'style': 'width:100%; margin-bottom:0;' }, [
				E('tr', { 'class': 'tr table-titles' }, [
					E('th', { 'class': 'th' }, t('th_ssid')),
					E('th', { 'class': 'th' }, t('th_freq')),
					E('th', { 'class': 'th' }, t('th_pass')),
					E('th', { 'class': 'th' }, t('th_enc')),
					E('th', { 'class': 'th' }, t('th_type')),
					E('th', { 'class': 'th' }, t('th_status')),
					E('th', { 'class': 'th right' }, t('th_actions'))
				]),
				E('tbody', {}, rows)
			])
		]);

		var networkHeader = E('div', { 'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:25px; margin-bottom:12px;' }, [
			E('h3', { 'style': 'margin:0;' }, t('networks_title')),
			E('button', {
				'class': 'btn cbi-button-action important',
				'style': 'font-size:14px; padding:6px 14px;',
				'click': function() { self.renderAddNetworkModal(); }
			}, t('btn_add_network'))
		]);

		var isLocked = (status.radios && status.radios.lock_status === 'locked');
		var lockBadge = isLocked ?
			E('span', { 'id': 'rf-lock-badge', 'style': 'background:#f8d7da; color:#721c24; border:1px solid #f5c6cb; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; display:inline-flex; align-items:center; gap:4px;' }, [
				'⚠️ ', t('lock_badge_locked')
			]) :
			E('span', { 'id': 'rf-lock-badge', 'style': 'background:#d4edda; color:#155724; border:1px solid #c3e6cb; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; display:inline-flex; align-items:center; gap:4px;' }, [
				'🔒 ', t('lock_badge_clean')
			]);

		var radiosHeader = E('div', {
			'style': 'display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:25px; margin-bottom:12px;'
		}, [
			E('div', { 'style': 'display:flex; align-items:center; gap:10px;' }, [
				E('h3', { 'style': 'margin:0;' }, t('radios_title')),
				lockBadge
			]),
			E('div', { 'style': 'display:flex; align-items:center; gap:10px; flex-wrap:wrap;' }, [
				E('button', {
					'id': 'btn-save-all-radios',
					'class': 'btn cbi-button-action important',
					'style': 'background:#27ae60; color:#fff; border:none; padding:7px 16px; font-size:13px; font-weight:bold; border-radius:4px; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 1px 3px rgba(0,0,0,0.2);',
					'title': t('btn_save_all_radios'),
					'click': function() {
						var c0 = (document.getElementById('sel-chan-wifi0') || {}).value;
						var w0 = (document.getElementById('sel-width-wifi0') || {}).value;
						var p0 = (document.getElementById('sel-txpower-wifi0') || {}).value;

						var c1 = (document.getElementById('sel-chan-wifi1') || {}).value;
						var w1 = (document.getElementById('sel-width-wifi1') || {}).value;
						var p1 = (document.getElementById('sel-txpower-wifi1') || {}).value;

						var c2 = (document.getElementById('sel-chan-wifi2') || {}).value;
						var w2 = (document.getElementById('sel-width-wifi2') || {}).value;
						var p2 = (document.getElementById('sel-txpower-wifi2') || {}).value;

						callSetAllRadios({
							channel: c0, htmode: w0, txpower: p0
						}, {
							channel: c1, htmode: w1, txpower: p1
						}, {
							channel: c2, htmode: w2, txpower: p2
						}).then(function() {
							safeReloadAfterRestart(t('radio_saving_all'));
						});
					}
				}, t('btn_save_all_radios')),
				E('button', {
					'class': 'btn cbi-button-action',
					'style': 'background:#e67e22; color:#fff; border:none; padding:7px 14px; font-size:13px; font-weight:bold; border-radius:4px; cursor:pointer;',
					'title': t('btn_restart_wifi'),
					'click': function() {
						callRestartWifi().then(function() {
							safeReloadAfterRestart(t('btn_restarting_wifi'));
						});
					}
				}, t('btn_restart_wifi'))
			])
		]);

		// Polling inteligente ao vivo a cada 2s (pausa automaticamente se a aba/janela estiver em segundo plano ou fechada)
		poll.add(function() {
			if (document.hidden)
				return Promise.resolve();

			return callGetStatus().then(function(newStatus) {
				self.updateLiveTelemetry(newStatus);
			}).catch(function() {});
		}, 2);

		var mapChildren = [
			E('h2', {}, t('app_title')),
			E('div', { 'class': 'cbi-map-descr' }, t('app_descr'))
		];
		if (guardBannerNode) {
			mapChildren.push(guardBannerNode);
		}
		mapChildren.push(
			modeBanner,
			networkHeader,
			networksTable,
			self.renderPortsCard(status.ports),
			radiosHeader,
			radiosGrid,
			self.renderTelemetryCard(status),
			self.renderFeaturesCard(status.features)
		);

		return E('div', { 'class': 'cbi-map' }, mapChildren);
	},
	handleSaveApply: null,
	handleSave: null,
	handleReset: null
});
