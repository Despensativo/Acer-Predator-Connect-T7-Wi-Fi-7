'use strict';
'require view';
'require form';
'require ui';
'require fs';
'require request';

return view.extend({
	load: function() {
		return Promise.all([
			request.get('/cgi-bin/predator-dev?action=status').then(function(res) {
				return res.json();
			}).catch(function() {
				return {
					active_slot: 1,
					failsafe_enabled: true,
					boot_fail_count: 0,
					max_retries: 3,
					safe_uptime: 75,
					logging_enabled: true,
					retention_days: 7,
					log_files: []
				};
			})
		]);
	},

	render: function(data) {
		var status = data[0];
		var m, s, o;

		m = new form.Map('predator_dev', _('Modo DEV & Fail-Safe Dual-Boot'),
			_('Configurações avançadas de desenvolvimento para o Acer Predator Connect T7: proteção anti-bootloop inteligente entre partições (Slot 1 / Slot 2) e histórico persistente de logs de boot por até 7 dias.'));

		/* ==================== CARD DE STATUS E AÇÕES ==================== */
		s = m.section(form.NamedSection, 'general', 'dev', _('Estado do Sistema'));

		s.render = function() {
			var slotBadge = status.active_slot == 1
				? '<span class="label" style="background:#007bff; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">Slot 1 (Principal)</span>'
				: '<span class="label" style="background:#28a745; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">Slot 2 (Alternativo)</span>';

			var loopBadge = status.boot_fail_count >= status.max_retries
				? '<span class="label" style="background:#dc3545; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">ALERTA DE BOOTLOOP (' + status.boot_fail_count + '/' + status.max_retries + ')</span>'
				: '<span class="label" style="background:#17a2b8; color:#fff; padding:4px 8px; border-radius:4px;">' + status.boot_fail_count + ' / ' + status.max_retries + ' tentativas</span>';

			var totalFiles = (status.log_files && status.log_files.length) || 0;

			var html = '<div class="cbi-section-node">' +
				'<table class="table" style="width:100%; margin-bottom:15px;">' +
				'<tr><td style="width:30%;"><strong>Partição em Execução:</strong></td><td>' + slotBadge + '</td></tr>' +
				'<tr><td><strong>Proteção Anti-Bootloop:</strong></td><td>' + (status.failsafe_enabled ? '✅ Ativa' : '❌ Desativada') + ' (' + loopBadge + ')</td></tr>' +
				'<tr><td><strong>Logs de Boot Armazenados:</strong></td><td><strong>' + totalFiles + '</strong> arquivo(s) salvos em <code>/data/boot_logs/</code></td></tr>' +
				'</table>' +
				'<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:15px;">' +
				'<a href="/cgi-bin/predator-dev?action=download" class="cbi-button cbi-button-apply" style="text-decoration:none; display:inline-flex; align-items:center; gap:5px;">📥 Baixar Todos os Logs (.tar.gz)</a>' +
				'<button type="button" id="btn-view-log" class="cbi-button cbi-button-action">📄 Ver Último Log de Boot</button>' +
				'<button type="button" id="btn-reset-counter" class="cbi-button cbi-button-neutral">🔄 Zerar Contador de Falhas</button>' +
				'<button type="button" id="btn-switch-slot" class="cbi-button cbi-button-reset" style="background:#e0a800; color:#fff;">🔀 Alternar Partição Agora</button>' +
				'</div>' +
				'<div style="background:#f8f9fa; border:1px solid #dee2e6; border-radius:6px; padding:12px; margin-bottom:15px;">' +
				'<strong style="color:#333;">🛠️ Imagens FIT do Alternador de Boot V2 (Web Recovery U-Boot):</strong>' +
				'<p style="font-size:12px; color:#666; margin:6px 0 10px;">Para recuperação física se o roteador não subir o sistema: ligue segurando o botão WPS para entrar no Web Recovery (192.168.1.1) e faça upload da imagem FIT para alternar a partição na NAND:</p>' +
				'<div style="display:flex; gap:10px; flex-wrap:wrap;">' +
				'<a href="/cgi-bin/predator-dev?action=download_slot1" class="cbi-button" style="text-decoration:none; background:#007bff; color:#fff;">💾 Baixar FIT Slot 1 (OEM v24)</a>' +
				'<a href="/cgi-bin/predator-dev?action=download_slot2" class="cbi-button" style="text-decoration:none; background:#28a745; color:#fff;">💾 Baixar FIT Slot 2 (OpenWrt)</a>' +
				'</div>' +
				'</div>' +
				'<div id="log-view-box" style="display:none; margin-top:15px;">' +
				'<h4>Último Log de Inicialização Completo:</h4>' +
				'<textarea id="log-content" style="width:100%; height:300px; font-family:monospace; font-size:12px; background:#1e1e1e; color:#00ff66; padding:10px; border-radius:4px; box-sizing:border-box;" readonly></textarea>' +
				'</div>' +
				'</div>';

			var node = E('div', { 'class': 'cbi-section' }, [
				E('h3', {}, _('Painel de Controle e Diagnóstico')),
				E('div', {}, '')
			]);
			node.lastElementChild.innerHTML = html;

			// Handlers de clique
			setTimeout(function() {
				var btnView = document.getElementById('btn-view-log');
				var logBox = document.getElementById('log-view-box');
				var logText = document.getElementById('log-content');
				if (btnView && logBox && logText) {
					btnView.addEventListener('click', function() {
						if (logBox.style.display === 'none') {
							btnView.innerText = '⏳ Carregando log...';
							request.get('/cgi-bin/predator-dev?action=latest').then(function(res) {
								logText.value = res.text();
								logBox.style.display = 'block';
								btnView.innerText = '❌ Ocultar Log';
							}).catch(function(err) {
								ui.addNotification(null, E('p', {}, 'Erro ao carregar log: ' + err.message), 'error');
								btnView.innerText = '📄 Ver Último Log de Boot';
							});
						} else {
							logBox.style.display = 'none';
							btnView.innerText = '📄 Ver Último Log de Boot';
						}
					});
				}

				var btnReset = document.getElementById('btn-reset-counter');
				if (btnReset) {
					btnReset.addEventListener('click', function() {
						request.get('/cgi-bin/predator-dev?action=reset').then(function() {
							ui.addNotification(null, E('p', {}, 'Contador de falhas de boot zerado com sucesso!'), 'info');
							location.reload();
						});
					});
				}

				var btnSwitch = document.getElementById('btn-switch-slot');
				if (btnSwitch) {
					btnSwitch.addEventListener('click', function() {
						var otherSlot = status.active_slot == 1 ? 2 : 1;
						ui.showModal(_('Confirmar Alternância de Slot'), [
							E('p', {}, _('Tem certeza que deseja alternar para o <strong>Slot ' + otherSlot + '</strong> e reiniciar o roteador agora?')),
							E('div', { 'class': 'right' }, [
								E('button', {
									'class': 'cbi-button cbi-button-neutral',
									'click': ui.hideModal
								}, _('Cancelar')),
								' ',
								E('button', {
									'class': 'cbi-button cbi-button-action',
									'style': 'background:#dc3545; color:#fff;',
									'click': function() {
										ui.hideModal();
										ui.showModal(_('Reiniciando...'), [
											E('p', { 'class': 'spinning' }, _('Chaveando bootconfig e reiniciando o roteador... Aguarde cerca de 60 segundos.'))
										]);
										request.get('/cgi-bin/predator-dev?action=switch');
									}
								}, _('Confirmar e Reiniciar'))
							])
						]);
					});
				}
			}, 100);

			return node;
		};

		/* ==================== CONFIGURAÇÕES FAIL-SAFE ==================== */
		s = m.section(form.NamedSection, 'failsafe', 'failsafe', _('Proteção Fail-Safe Anti-Bootloop'));
		s.anonymous = true;

		o = s.option(form.Flag, 'enabled', _('Ativar Fail-Safe Anti-Bootloop'),
			_('Se o roteador reiniciar de forma abrupta ou falhar durante o boot X vezes consecutivas, ele alternará automaticamente para a partição oposta saudável.'));
		o.default = '1';
		o.rmempty = false;

		o = s.option(form.ListValue, 'max_retries', _('Limite de Falhas Consecutivas'),
			_('Quantidade máxima de inicializações com falha antes de realizar o chaveamento automático.'));
		o.value('2', _('2 tentativas'));
		o.value('3', _('3 tentativas (Recomendado)'));
		o.value('4', _('4 tentativas'));
		o.value('5', _('5 tentativas'));
		o.default = '3';
		o.depends('enabled', '1');

		o = s.option(form.Value, 'safe_uptime', _('Janela de Confirmação Saudável (segundos)'),
			_('Tempo contínuo de funcionamento necessário para que o sistema considere o boot um sucesso e zere o contador de falhas.'));
		o.datatype = 'uinteger';
		o.default = '75';
		o.depends('enabled', '1');

		/* ==================== CONFIGURAÇÕES DE LOG PERSISTENTE ==================== */
		s = m.section(form.NamedSection, 'logging', 'logging', _('Registro Persistente de Boot (Histórico de 7 Dias)'));
		s.anonymous = true;

		o = s.option(form.Flag, 'enabled', _('Ativar Gravação Automática de Logs'),
			_('Grava um relatório completo (dmesg do kernel, logread dos serviços, diagnóstico do chip Wi-Fi 7 e traço de hardware) em cada inicialização na flash interna.'));
		o.default = '1';
		o.rmempty = false;

		o = s.option(form.ListValue, 'retention_days', _('Período de Retenção'),
			_('Tempo máximo para manter os arquivos de log na memória flash antes da limpeza automática.'));
		o.value('3', _('3 dias'));
		o.value('7', _('7 dias (Padrão)'));
		o.value('14', _('14 dias'));
		o.default = '7';
		o.depends('enabled', '1');

		o = s.option(form.Flag, 'compress', _('Compactar Logs (.gz)'),
			_('Reduz o tamanho de cada log em até 80% (~35 KB por inicialização), economizando espaço na flash.'));
		o.default = '1';
		o.depends('enabled', '1');

		return m.render();
	}
});
