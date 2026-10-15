--[[
LuCI - Lua Configuration Interface

Copyright 2014 Steven Barth <steven@midlink.org>
Copyright 2014 Dave Taht <dave.taht@bufferbloat.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

$Id$
]]--

local wa = require "luci.tools.webadmin"
local fs = require "nixio.fs"
local net = require "luci.model.network".init()
local sys = require "luci.sys"
--local ifaces = net:get_interfaces()
local ifaces = sys.net:devices()
local path = "/usr/lib/sqm"
local run_path = "/tmp/run/sqm/available_qdiscs"

local uci = require "luci.model.uci".cursor()
local active_lang = (uci:get("luci", "main", "lang") or "pt_br"):lower()
local function tr3(ptStr, enStr, esStr)
	if active_lang:find("^en") then return enStr or ptStr end
	if active_lang:find("^es") then return esStr or enStr or ptStr end
	return ptStr
end

m = Map("sqm", tr3(
		"Gerenciamento Inteligente de Filas (SQM CAKE Anti-Bufferbloat)",
		"Smart Queue Management (SQM CAKE Anti-Bufferbloat)",
		"Gestión Inteligente de Colas (SQM CAKE Anti-Bufferbloat)"
	),
	tr3(
		"Com o <abbr title=\"Smart Queue Management\">SQM CAKE</abbr> ativado, o roteador controla o Bufferbloat (latência sob carga), distribui a banda de forma justa entre todos os dispositivos (Triple-Isolate) e prioriza pacotes de jogos, voz e vídeo na WAN.<br /><b>Dica de Performance:</b> Digite as velocidades diretamente em <b>MB / Mega</b> (ex: <b>800</b> para 800 Mega). Quando desativado, o roteador opera com <b>Aceleração Pura de Hardware Qualcomm PPE-DS + SFE (2.5 Gbps, 0% CPU)</b>.",
		"With <abbr title=\"Smart Queue Management\">SQM CAKE</abbr> enabled, the router eliminates Bufferbloat (latency under load), enforces fair per-host bandwidth sharing (Triple-Isolate), and prioritizes gaming, voice, and video traffic on WAN.<br /><b>Performance Tip:</b> Enter speeds directly in <b>MB / Mbps</b> (e.g., <b>800</b> for 800 Mbps). When disabled, the router runs on <b>Pure Qualcomm PPE-DS + SFE Hardware Acceleration (2.5 Gbps, 0% CPU)</b>.",
		"Con <abbr title=\"Smart Queue Management\">SQM CAKE</abbr> activado, el router controla el Bufferbloat (latencia bajo carga), distribuye el ancho de banda equitativamente (Triple-Isolate) y prioriza juegos, voz y video en la WAN.<br /><b>Consejo de Rendimiento:</b> Ingrese las velocidades directamente en <b>MB / Mbps</b> (ej: <b>800</b> para 800 Mega). Cuando está desactivado, el router opera con <b>Aceleración Pura de Hardware Qualcomm PPE-DS + SFE (2.5 Gbps, 0% CPU)</b>."
	))

s = m:section(TypedSection, "queue", tr3(
	"Filas de Controle de Tráfego (WAN / Interfaces)",
	"Traffic Control Queues (WAN / Interfaces)",
	"Colas de Control de Tráfico (WAN / Interfaces)"
))
s:tab("tab_basic", tr3("Configurações Básicas (Velocidade em MB)", "Basic Settings (Speed in MB/Mbps)", "Configuración Básica (Velocidad en MB)"))
s:tab("tab_qdisc", tr3("Disciplina de Fila (CAKE / QoS)", "Queue Discipline (CAKE / QoS)", "Disciplina de Cola (CAKE / QoS)"))
s:tab("tab_linklayer", tr3("Adaptação de Camada de Enlace (Fibra / PPPoE)", "Link Layer Adaptation (Fiber / PPPoE)", "Adaptación de Capa de Enlace (Fibra / PPPoE)"))
s.addremove = true -- set to true to allow adding SQM instances in the GUI
s.anonymous = true

-- BASIC
e = s:taboption("tab_basic", Flag, "enabled", tr3(
	"Ativar controle SQM CAKE nesta interface (Nota A+ no Waveform)",
	"Enable SQM CAKE shaping on this interface (Waveform Grade A+)",
	"Activar control SQM CAKE en esta interfaz (Nota A+ en Waveform)"
))
e.rmempty = false

function e.write(self, section, value)
	if value == "1" then
		luci.sys.init.enable("sqm")
		m.message = tr3(
			"SQM CAKE ativado com sucesso (no-split-gso ativo e bypass SFE pausado para evitar congelamento em 6 GHz).",
			"SQM CAKE enabled successfully (no-split-gso active and SFE bypass paused to prevent 6 GHz freeze).",
			"SQM CAKE activado con éxito (no-split-gso activo y bypass SFE pausado para evitar congelamiento en 6 GHz)."
		)
	else
		luci.sys.call("echo 0 > /sys/kernel/debug/ecm/front_end_ipv4_stop 2>/dev/null; echo 0 > /sys/kernel/debug/ecm/front_end_ipv6_stop 2>/dev/null")
		m.message = tr3(
			"SQM desativado — Aceleração de Hardware Qualcomm PPE-DS + SFE Fast-Path 2.5 Gbps reativada.",
			"SQM disabled — Qualcomm PPE-DS + SFE Fast-Path 2.5 Gbps Hardware Acceleration re-enabled.",
			"SQM desactivado — Aceleración de Hardware Qualcomm PPE-DS + SFE Fast-Path 2.5 Gbps reactivada."
		)
	end
	return Flag.write(self, section, value)
end


n = s:taboption("tab_basic", ListValue, "interface", tr3("Interface de Rede (WAN):", "Network Interface (WAN):", "Interfaz de Red (WAN):"))
for _, iface in ipairs(ifaces) do
	if not (iface == "lo" or iface:match("^ifb.*")) then
		local nets = net:get_interface(iface)
		nets = nets and nets:get_networks() or {}
		for k, v in pairs(nets) do
			nets[k] = nets[k].sid
		end
		nets = table.concat(nets, ",")
		n:value(iface, ((#nets > 0) and "%s (%s)" % {iface, nets} or iface))
	end
end
n.rmempty = false


dl = s:taboption("tab_basic", Value, "download", tr3(
	"Velocidade de Download em MB / Mbps (Entrada / Ingress) — digite em Mega (ex: 800 para 800 MB, 0 = desativado):",
	"Download Speed in MB / Mbps (Ingress) — enter in Mbps (e.g., 800 for 800 Mbps, 0 = disabled):",
	"Velocidad de Descarga en MB / Mbps (Entrada / Ingress) — ingrese en Mega (ej: 800 para 800 MB, 0 = desactivado):"
))
dl.datatype = "and(uinteger,min(0))"
dl.default = "800"
dl.placeholder = "800"
dl.rmempty = false
function dl.cfgvalue(self, section)
	local val = Value.cfgvalue(self, section)
	local num = tonumber(val)
	if num and num > 10000 then
		return tostring(math.floor(num / 1000))
	end
	return val
end
function dl.write(self, section, value)
	local num = tonumber(value)
	if num and num > 10000 then
		value = tostring(math.floor(num / 1000))
	end
	return Value.write(self, section, value)
end

ul = s:taboption("tab_basic", Value, "upload", tr3(
	"Velocidade de Upload em MB / Mbps (Saída / Egress) — digite em Mega (ex: 400 para 400 MB, 0 = desativado):",
	"Upload Speed in MB / Mbps (Egress) — enter in Mbps (e.g., 400 for 400 Mbps, 0 = disabled):",
	"Velocidad de Subida en MB / Mbps (Salida / Egress) — ingrese en Mega (ej: 400 para 400 MB, 0 = desactivado):"
))
ul.datatype = "and(uinteger,min(0))"
ul.default = "400"
ul.placeholder = "400"
ul.rmempty = false
function ul.cfgvalue(self, section)
	local val = Value.cfgvalue(self, section)
	local num = tonumber(val)
	if num and num > 10000 then
		return tostring(math.floor(num / 1000))
	end
	return val
end
function ul.write(self, section, value)
	local num = tonumber(value)
	if num and num > 10000 then
		value = tostring(math.floor(num / 1000))
	end
	return Value.write(self, section, value)
end

dbl = s:taboption("tab_basic", Flag, "debug_logging", tr3(
	"Criar arquivo de log de diagnóstico em /var/run/sqm/${Interface_name}.[start|stop]-sqm.log",
	"Create diagnostic log file under /var/run/sqm/${Interface_name}.[start|stop]-sqm.log",
	"Crear archivo de registro de diagnóstico en /var/run/sqm/${Interface_name}.[start|stop]-sqm.log"
))
dbl.rmempty = false


verb = s:taboption("tab_basic", ListValue, "verbosity", tr3(
	"Nível de detalhamento de logs do SQM no registro do sistema (syslog):",
	"SQM log verbosity level in system log (syslog):",
	"Nivel de detalle de registros de SQM en el sistema (syslog):"
))
verb:value("0", tr3("Silencioso (0)", "Silent (0)", "Silencioso (0)"))
verb:value("1", tr3("Apenas Erros (1)", "Errors Only (1)", "Solo Errores (1)"))
verb:value("2", tr3("Avisos / Warnings (2)", "Warnings (2)", "Advertencias / Warnings (2)"))
verb:value("5", tr3("Informativo (Padrão)", "Info (Default)", "Informativo (Predeterminado)"))
verb:value("8", tr3("Depuração / Debug (8)", "Debug (8)", "Depuración / Debug (8)"))
verb:value("10", tr3("Rastreamento / Trace (10)", "Trace (10)", "Rastreo / Trace (10)"))
verb.default = "5"
verb.rmempty = true




-- QDISC

local val_qdisc_name = ""
c = s:taboption("tab_qdisc", ListValue, "qdisc", tr3(
	"Algoritmo de enfileiramento (Qdisc) ativo no Kernel:",
	"Active Kernel Queuing Discipline (Qdisc):",
	"Algoritmo de encolamiento (Qdisc) activo en el Kernel:"
))
c:value("fq_codel", tr3("fq_codel ( Clássico )", "fq_codel ( Classic )", "fq_codel ( Clásico )"))

if fs.stat(run_path) then
	for file in fs.dir(run_path) do
		c:value( file )
	end
end
c.default = "cake"
c.rmempty = false

local help_tr = {
	["piece_of_cake.qos"] = tr3(
		"Recomendado (Padrão Ouro Predator T7): Usa o motor CAKE em fila única justa por host (Triple-Isolate) com proteção no-split-gso para máxima estabilidade em Fibra/PPPoE.",
		"Recommended (Predator T7 Golden Standard): Uses CAKE in fair per-host single-queue mode (Triple-Isolate) with no-split-gso protection for Fiber/PPPoE.",
		"Recomendado (Estándar de Oro Predator T7): Utiliza CAKE en modo justo por host (Triple-Isolate) con protección no-split-gso para Fibra/PPPoE."
	),
	["layer_cake.qos"] = tr3(
		"Usa o motor CAKE com múltiplas faixas de prioridade DiffServ (Voz, Vídeo, Melhor Esforço e Background).",
		"Uses CAKE with multiple DiffServ priority tiers (Voice, Video, Best Effort, and Background).",
		"Utiliza CAKE con múltiples niveles de prioridad DiffServ (Voz, Video, Mejor Esfuerzo y Fondo)."
	),
	["simple.qos"] = tr3(
		"Script clássico HTB + FQ_CoDel com 3 faixas de prioridade.",
		"Classic 3-tier HTB + FQ_CoDel script.",
		"Script clásico HTB + FQ_CoDel con 3 niveles de prioridad."
	),
	["simplest.qos"] = tr3(
		"Script leve HTB + FQ_CoDel de fila única.",
		"Lightweight single-queue HTB + FQ_CoDel script.",
		"Script ligero HTB + FQ_CoDel de cola única."
	),
	["simplest_tbf.qos"] = tr3(
		"Script TBF + FQ_CoDel para testes básicos.",
		"Basic TBF + FQ_CoDel script.",
		"Script básico TBF + FQ_CoDel."
	)
}

local qos_desc = ""
sc = s:taboption("tab_qdisc", ListValue, "script", tr3(
	"Script de configuração de fila (QoS):",
	"Queue setup script (QoS):",
	"Script de configuración de cola (QoS):"
))
for file in fs.dir(path) do
	if string.find(file, ".qos$") and not fs.stat(path .. "/" .. file .. ".hidden") then
		sc:value(file)
		qos_desc = qos_desc .. "<p><b>" .. file .. ":</b><br />"
		if help_tr[file] then
			qos_desc = qos_desc .. help_tr[file] .. "</p>"
		else
			fh = io.open(path .. "/" .. file .. ".help", "r")
			if fh then
				qos_desc = qos_desc .. fh:read("*a") .. "</p>"
			else
				qos_desc = qos_desc .. tr3("Sem descrição adicional.", "No additional description.", "Sin descripción adicional.") .. "</p>"
			end
		end
	end
end
sc.default = "piece_of_cake.qos"
sc.rmempty = false
sc.description = qos_desc

ad = s:taboption("tab_qdisc", Flag, "qdisc_advanced", tr3(
	"Exibir e utilizar Configurações Avançadas de Fila (permanecem ativas enquanto esta caixa estiver marcada).",
	"Show and Use Advanced Queue Configuration (active as long as this box is checked).",
	"Mostrar y utilizar Configuración Avanzada de Cola (activa mientras esta casilla esté marcada)."
))
ad.default = false
ad.rmempty = true

squash_dscp  = s:taboption("tab_qdisc", ListValue, "squash_dscp", tr3(
	"Zerar marcações DSCP nos pacotes de entrada (Ingress):",
	"Squash DSCP markings on inbound packets (Ingress):",
	"Borrar marcas DSCP en paquetes entrantes (Ingress):"
))
squash_dscp:value("1", tr3("ZERAR (SQUASH - Recomendado)", "SQUASH (Recommended)", "BORRAR (SQUASH - Recomendado)"))
squash_dscp:value("0", tr3("NÃO ZERAR (Preservar DSCP da WAN)", "DO NOT SQUASH (Preserve WAN DSCP)", "NO BORRAR (Preservar DSCP de WAN)"))
squash_dscp.default = "1"
squash_dscp.rmempty = true
squash_dscp:depends("qdisc_advanced", "1")

squash_ingress = s:taboption("tab_qdisc", ListValue, "squash_ingress", tr3(
	"Ignorar marcações DSCP na fila de entrada (Ingress):",
	"Ignore DSCP markings on ingress queue:",
	"Ignorar marcas DSCP en la cola de entrada (Ingress):"
))
squash_ingress:value("1", tr3("Ignorar (Fila única justa)", "Ignore (Fair single queue)", "Ignorar (Cola única justa)"))
squash_ingress:value("0", tr3("Permitir (Respeitar classes DSCP)", "Allow (Respect DSCP tiers)", "Permitir (Respetar clases DSCP)"))
squash_ingress.default = "1"
squash_ingress.rmempty = true
squash_ingress:depends("qdisc_advanced", "1")

iecn = s:taboption("tab_qdisc", ListValue, "ingress_ecn", tr3(
	"Notificação Explícita de Congestionamento (ECN) nos pacotes de entrada (Download):",
	"Explicit Congestion Notification (ECN) on inbound packets (Download):",
	"Notificación Explícita de Congestión (ECN) en paquetes entrantes (Descarga):"
))
iecn:value("ECN", tr3("ECN Ativo (Padrão)", "ECN Enabled (Default)", "ECN Activo (Predeterminado)"))
iecn:value("NOECN", tr3("Sem ECN (NOECN)", "No ECN (NOECN)", "Sin ECN (NOECN)"))
iecn.default = "ECN"
iecn.rmempty = true
iecn:depends("qdisc_advanced", "1")

eecn = s:taboption("tab_qdisc", ListValue, "egress_ecn", tr3(
	"Notificação Explícita de Congestionamento (ECN) nos pacotes de saída (Upload):",
	"Explicit Congestion Notification (ECN) on outbound packets (Upload):",
	"Notificación Explícita de Congestión (ECN) en paquetes salientes (Subida):"
))
eecn:value("NOECN", tr3("Sem ECN (Padrão)", "No ECN (Default)", "Sin ECN (Predeterminado)"))
eecn:value("ECN", tr3("ECN Ativo", "ECN Enabled", "ECN Activo"))
eecn.default = "NOECN"
eecn.rmempty = true
eecn:depends("qdisc_advanced", "1")

ad2 = s:taboption("tab_qdisc", Flag, "qdisc_really_really_advanced", tr3(
	"Exibir parâmetros de Engenharia do Kernel (necessário manter marcado para preservar o fix no-split-gso).",
	"Show Kernel Engineering Parameters (keep checked to preserve the no-split-gso fix).",
	"Mostrar parámetros de Ingeniería del Kernel (mantener marcado para conservar el fix no-split-gso)."
))
ad2.default = false
ad2.rmempty = true
ad2:depends("qdisc_advanced", "1")

ilim = s:taboption("tab_qdisc", Value, "ilimit", tr3(
	"Limite máximo de pacotes na fila de Download (deixe em branco para automático):",
	"Hard packet limit on Download queue (leave empty for automatic):",
	"Límite máximo de paquetes en cola de Descarga (dejar en blanco para automático):"
))
ilim.isnumber = true
ilim.datatype = "and(uinteger,min(0))"
ilim.rmempty = true
ilim:depends("qdisc_really_really_advanced", "1")

elim = s:taboption("tab_qdisc", Value, "elimit", tr3(
	"Limite máximo de pacotes na fila de Upload (deixe em branco para automático):",
	"Hard packet limit on Upload queue (leave empty for automatic):",
	"Límite máximo de paquetes en cola de Subida (dejar en blanco para automático):"
))
elim.datatype = "and(uinteger,min(0))"
elim.rmempty = true
elim:depends("qdisc_really_really_advanced", "1")


itarg = s:taboption("tab_qdisc", Value, "itarget", tr3(
	"Alvo de latência para Download (ex: 5ms; deixe em branco para seleção automática):",
	"Latency target for Download (e.g., 5ms; leave empty for automatic):",
	"Objetivo de latencia para Descarga (ej: 5ms; dejar en blanco para automático):"
))
itarg.datatype = "string"
itarg.rmempty = true
itarg:depends("qdisc_really_really_advanced", "1")

etarg = s:taboption("tab_qdisc", Value, "etarget", tr3(
	"Alvo de latência para Upload (ex: 5ms; deixe em branco para seleção automática):",
	"Latency target for Upload (e.g., 5ms; leave empty for automatic):",
	"Objetivo de latencia para Subida (ej: 5ms; dejar en blanco para automático):"
))
etarg.datatype = "string"
etarg.rmempty = true
etarg:depends("qdisc_really_really_advanced", "1")



iqdisc_opts = s:taboption("tab_qdisc", Value, "iqdisc_opts", tr3(
	"Opções avançadas do CAKE no Download (Ingress) — mantenha 'no-split-gso':",
	"Advanced CAKE options on Download (Ingress) — keep 'no-split-gso':",
	"Opciones avanzadas de CAKE en Descarga (Ingress) — mantenga 'no-split-gso':"
))
iqdisc_opts.rmempty = true
iqdisc_opts:depends("qdisc_really_really_advanced", "1")

eqdisc_opts = s:taboption("tab_qdisc", Value, "eqdisc_opts", tr3(
	"Opções avançadas do CAKE no Upload (Egress) — mantenha 'no-split-gso' (evita queda de upload em PPPoE):",
	"Advanced CAKE options on Upload (Egress) — keep 'no-split-gso' (prevents PPPoE upload drop):",
	"Opciones avanzadas de CAKE en Subida (Egress) — mantenga 'no-split-gso' (evita caída de subida en PPPoE):"
))
eqdisc_opts.rmempty = true
eqdisc_opts:depends("qdisc_really_really_advanced", "1")

-- LINKLAYER
ll = s:taboption("tab_linklayer", ListValue, "linklayer", tr3(
	"Camada de enlace física para cálculo de cabeçalho:",
	"Physical link layer for header overhead calculation:",
	"Capa de enlace física para cálculo de encabezado:"
))
ll:value("none", tr3("Nenhuma (none)", "None", "Ninguna (none)"))
ll:value("ethernet", tr3("Ethernet / Fibra Óptica GPON / PPPoE (Recomendado)", "Ethernet / GPON Fiber / PPPoE (Recommended)", "Ethernet / Fibra Óptica GPON / PPPoE (Recomendado)"))
ll:value("atm", tr3("ATM (ADSL legado)", "ATM (Legacy ADSL)", "ATM (ADSL antiguo)"))
ll.default = "ethernet"

po = s:taboption("tab_linklayer", Value, "overhead", tr3(
	"Overhead por pacote em bytes (Recomendado: 44 bytes para Fibra GPON / PPPoE):",
	"Per-Packet Overhead in bytes (Recommended: 44 bytes for GPON Fiber / PPPoE):",
	"Overhead por paquete en bytes (Recomendado: 44 bytes para Fibra GPON / PPPoE):"
))
po.datatype = "and(integer,min(-1500))"
po.default = 44
po.isnumber = true
po.rmempty = true
po:depends("linklayer", "ethernet")
po:depends("linklayer", "atm")


adll = s:taboption("tab_linklayer", Flag, "linklayer_advanced", tr3(
	"Exibir opções avançadas de enlace (necessário apenas se MTU > 1500).",
	"Show advanced link-layer options (only needed if MTU > 1500).",
	"Mostrar opciones avanzadas de enlace (solo necesario si MTU > 1500)."
))
adll.rmempty = true
adll:depends("linklayer", "ethernet")
adll:depends("linklayer", "atm")

smtu = s:taboption("tab_linklayer", Value, "tcMTU", tr3(
	"Tamanho máximo para cálculo de tabelas, tcMTU (bytes):",
	"Maximum size for rate table calculations, tcMTU (bytes):",
	"Tamaño máximo para cálculo de tablas, tcMTU (bytes):"
))
smtu.datatype = "and(uinteger,min(0))"
smtu.default = 2047
smtu.isnumber = true
smtu.rmempty = true
smtu:depends("linklayer_advanced", "1")

stsize = s:taboption("tab_linklayer", Value, "tcTSIZE", tr3(
	"Número de entradas na tabela de taxas, TSIZE:",
	"Number of entries in rate tables, TSIZE:",
	"Número de entradas en la tabla de tasas, TSIZE:"
))
stsize.datatype = "and(uinteger,min(0))"
stsize.default = 128
stsize.isnumber = true
stsize.rmempty = true
stsize:depends("linklayer_advanced", "1")

smpu = s:taboption("tab_linklayer", Value, "tcMPU", tr3(
	"Tamanho mínimo de pacote, MPU (bytes — recomendado 64 para Ethernet/Fibra):",
	"Minimum packet size, MPU (bytes — 64 recommended for Ethernet/Fiber):",
	"Tamaño mínimo de paquete, MPU (bytes — recomendado 64 para Ethernet/Fibra):"
))
smpu.datatype = "and(uinteger,min(0))"
smpu.default = 64
smpu.isnumber = true
smpu.rmempty = true
smpu:depends("linklayer_advanced", "1")

lla = s:taboption("tab_linklayer", ListValue, "linklayer_adaptation_mechanism", tr3(
	"Mecanismo de adaptação de camada de enlace:",
	"Link-layer adaptation mechanism:",
	"Mecanismo de adaptación de capa de enlace:"
))
lla:value("default", tr3("Automático / CAKE Nativo (Padrão)", "Automatic / Native CAKE (Default)", "Automático / CAKE Nativo (Predeterminado)"))
lla:value("cake")
lla:value("htb_private")
lla:value("tc_stab")
lla.default = "default"
lla.rmempty = true
lla:depends("linklayer_advanced", "1")

function m.on_after_commit(self)
	luci.sys.call("uci commit sqm 2>/dev/null; /etc/init.d/sqm reload >/dev/null 2>&1 &")
end

return m
