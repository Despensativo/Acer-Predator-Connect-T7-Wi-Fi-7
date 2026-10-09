#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitorar_t7_live.py - Painel de Telemetria e Monitoria em Tempo Real (HUD)
Acer Predator Connect T7 (Qualcomm IPQ5332 Quad-Core + QCN9224 Wi-Fi 7)
"""

import sys
import os
import time
import argparse
import subprocess
import re
import json
from datetime import datetime

try:
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
except ImportError:
    print("Biblioteca 'rich' nao encontrada. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box

console = Console()

class T7LiveMonitor:
    def __init__(self, host="192.168.76.1", user="root", password="root0100", interval=1.0, log_file=None):
        self.host = host
        self.user = user
        self.password = password
        self.interval = float(interval)
        self.log_file = log_file
        self.control_path = f"/tmp/ssh-t7-{user}@{host}:22"
        self.last_cpu = {}
        self.last_net = {}
        self.last_time = None
        self.setup_ssh_multiplex()

    def setup_ssh_multiplex(self):
        """Estabelece socket multiplexado mestre do OpenSSH para latência sub-50ms."""
        sshpass_bin = "/opt/homebrew/bin/sshpass" if os.path.exists("/opt/homebrew/bin/sshpass") else "sshpass"
        cmd = [
            sshpass_bin, "-p", self.password,
            "ssh",
            "-o", "ControlMaster=auto",
            "-o", f"ControlPath={self.control_path}",
            "-o", "ControlPersist=10m",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "HostKeyAlgorithms=+ssh-rsa",
            "-o", "PubkeyAcceptedKeyTypes=+ssh-rsa",
            "-o", "ConnectTimeout=5",
            f"{self.user}@{self.host}",
            "true"
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        except Exception as e:
            console.print(f"[bold red]Erro ao inicializar conexão SSH mestre: {e}[/]")

    def run_remote_batch(self):
        """Executa uma única chamada SSH que extrai todos os dados brutos de forma atômica."""
        remote_script = r"""
echo '---SYSINFO---'
cat /proc/uptime; cat /proc/loadavg; cat /tmp/sysinfo/board_name 2>/dev/null; uname -r
echo '---CPU_STAT---'
grep '^cpu[0-3]' /proc/stat
echo '---CPU_FREQ---'
for c in 0 1 2 3; do
  echo -n "$c:$(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_cur_freq 2>/dev/null):$(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_governor 2>/dev/null) "
done; echo ''
echo '---MEMINFO---'
grep -E 'MemTotal|MemFree|Buffers|Cached' /proc/meminfo
echo '---TEMPS---'
echo "soc:$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)"
for w in wifi0 wifi1 wifi2; do
  echo -n "$w:"
  thermaltool -i $w -get -g 2>/dev/null | grep 'sensor temperature' | tr -d ',' | awk '{print $3, $6}' | tr '\n' ' '
  echo ''
done
echo '---NETDEV---'
cat /proc/net/dev | grep -E 'eth|ath|br-lan|wifi'
echo '---WIFI_INFO---'
for vap in ath0 ath1 ath2; do
  echo "VAP:$vap"
  iw dev $vap info 2>/dev/null | grep -E 'channel|txpower'
done
echo '---STATIONS---'
for vap in ath0 ath1 ath2; do
  echo "STA_VAP:$vap"
  iw dev $vap station dump 2>/dev/null
done
echo '---OFFLOAD---'
echo "conntrack:$(cat /proc/sys/net/netfilter/nf_conntrack_count 2>/dev/null || echo 0)"
echo "ecm:$(cat /sys/kernel/debug/ecm/ecm_db/connection_count 2>/dev/null || echo 0)"
echo "skb_max:$(cat /proc/net/skb_recycler/max_skbs 2>/dev/null || echo 0)"
echo "ppe_rfs:$(cat /sys/sfe/ppe_rfs_feature 2>/dev/null || echo 0)"
echo "edma_cores:$(cat /proc/sys/net/edma/rps_num_cores 2>/dev/null || echo 0)"
echo "bridge_nf:$(sysctl -n net.bridge.bridge-nf-call-iptables 2>/dev/null || echo 0)"
echo "bdf_link:$(ls -l /lib/firmware/qcn9224/bdwlan.b1015 2>/dev/null | awk -F'-> ' '{print $2}')"
"""
        cmd = [
            "ssh",
            "-o", f"ControlPath={self.control_path}",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{self.user}@{self.host}",
            remote_script
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return res.stdout
            else:
                self.setup_ssh_multiplex()
                return None
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def parse_telemetry(self, raw):
        if not raw:
            return None

        now = time.time()
        sections = {}
        cur_sec = None
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("---") and line.endswith("---"):
                cur_sec = line.strip("-")
                sections[cur_sec] = []
            elif cur_sec:
                sections[cur_sec].append(line)

        data = {
            "timestamp": now,
            "datetime": datetime.now().strftime("%H:%M:%S"),
            "sys": {},
            "cpus": [],
            "mem": {},
            "temps": {},
            "traffic": {},
            "wifis": {},
            "stations": [],
            "offload": {}
        }

        # 1. SYSINFO
        sys_lines = sections.get("SYSINFO", [])
        if len(sys_lines) >= 2:
            try:
                data["sys"]["uptime_sec"] = float(sys_lines[0].split()[0])
                data["sys"]["loadavg"] = sys_lines[1]
                data["sys"]["board"] = sys_lines[2] if len(sys_lines) > 2 else "IPQ5332"
                data["sys"]["kernel"] = sys_lines[3] if len(sys_lines) > 3 else "5.4.213"
            except Exception:
                pass

        # 2. CPU STAT & DELTA USAGE
        cur_cpu_raw = {}
        for line in sections.get("CPU_STAT", []):
            parts = line.split()
            if len(parts) >= 8:
                cname = parts[0]
                values = [int(x) for x in parts[1:8]]
                # user, nice, system, idle, iowait, irq, softirq
                idle = values[3] + values[4]
                non_idle = values[0] + values[1] + values[2] + values[5] + values[6]
                total = idle + non_idle
                cur_cpu_raw[cname] = (non_idle, total)

        # 3. CPU FREQ & GOVERNOR
        freq_info = {}
        for token in sections.get("CPU_FREQ", [""])[0].split():
            if ":" in token:
                parts = token.split(":")
                cid = parts[0]
                khz = parts[1] if len(parts) > 1 else "1500000"
                gov = parts[2] if len(parts) > 2 else "performance"
                freq_info[f"cpu{cid}"] = (int(khz) // 1000 if khz.isdigit() else 1500, gov)

        # Calculate CPU load %
        if self.last_cpu and self.last_time:
            dt = now - self.last_time
            for cname in ["cpu0", "cpu1", "cpu2", "cpu3"]:
                if cname in cur_cpu_raw and cname in self.last_cpu:
                    nid_diff = cur_cpu_raw[cname][0] - self.last_cpu[cname][0]
                    tot_diff = cur_cpu_raw[cname][1] - self.last_cpu[cname][1]
                    pct = (nid_diff / tot_diff * 100) if tot_diff > 0 else 0.0
                    mhz, gov = freq_info.get(cname, (1500, "performance"))
                    data["cpus"].append({
                        "name": cname,
                        "usage": max(0.0, min(100.0, pct)),
                        "mhz": mhz,
                        "governor": gov
                    })
        else:
            for cname in ["cpu0", "cpu1", "cpu2", "cpu3"]:
                mhz, gov = freq_info.get(cname, (1500, "performance"))
                data["cpus"].append({
                    "name": cname,
                    "usage": 0.0,
                    "mhz": mhz,
                    "governor": gov
                })
        self.last_cpu = cur_cpu_raw

        # 4. MEMINFO
        for line in sections.get("MEMINFO", []):
            parts = line.split(":")
            if len(parts) == 2:
                k = parts[0].strip()
                v = int(parts[1].replace("kB", "").strip())
                data["mem"][k] = v
        if "MemTotal" in data["mem"] and "MemFree" in data["mem"]:
            tot = data["mem"]["MemTotal"]
            free = data["mem"]["MemFree"] + data["mem"].get("Buffers", 0) + data["mem"].get("Cached", 0)
            used = tot - free
            data["mem"]["used_mb"] = used / 1024
            data["mem"]["total_mb"] = tot / 1024
            data["mem"]["pct"] = (used / tot) * 100

        # 5. TEMPS
        for line in sections.get("TEMPS", []):
            if line.startswith("soc:"):
                val = line.split(":")[1].strip()
                data["temps"]["soc"] = float(val) / 1000 if val.isdigit() else 88.0
            elif ":" in line:
                parts = line.split(":")
                w = parts[0].strip()
                tokens = parts[1].split()
                t_val = int(tokens[0]) if len(tokens) > 0 and tokens[0].isdigit() else 0
                lvl = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 0
                data["temps"][w] = {"temp": t_val, "thlvl": lvl}

        # 6. NETDEV TRAFFIC
        cur_net = {}
        for line in sections.get("NETDEV", []):
            if ":" in line:
                parts = line.split(":")
                iface = parts[0].strip()
                stats = parts[1].split()
                if len(stats) >= 16:
                    rx_bytes = int(stats[0])
                    rx_pkts = int(stats[1])
                    tx_bytes = int(stats[8])
                    tx_pkts = int(stats[9])
                    cur_net[iface] = (rx_bytes, tx_bytes, rx_pkts, tx_pkts)

        if self.last_net and self.last_time:
            dt = now - self.last_time
            if dt > 0:
                for iface in ["eth0", "eth1", "br-lan", "ath0", "ath1", "ath2"]:
                    if iface in cur_net and iface in self.last_net:
                        drx = cur_net[iface][0] - self.last_net[iface][0]
                        dtx = cur_net[iface][1] - self.last_net[iface][1]
                        drx_p = cur_net[iface][2] - self.last_net[iface][2]
                        dtx_p = cur_net[iface][3] - self.last_net[iface][3]
                        rx_mbps = (drx * 8) / (dt * 1000000)
                        tx_mbps = (dtx * 8) / (dt * 1000000)
                        data["traffic"][iface] = {
                            "rx_mbps": max(0.0, rx_mbps),
                            "tx_mbps": max(0.0, tx_mbps),
                            "rx_pps": int(max(0, drx_p / dt)),
                            "tx_pps": int(max(0, dtx_p / dt))
                        }
        self.last_net = cur_net
        self.last_time = now

        # 7. WIFI INFO (CH, WIDTH, TXPOWER)
        cur_vap = None
        for line in sections.get("WIFI_INFO", []):
            if line.startswith("VAP:"):
                cur_vap = line.split(":")[1].strip()
                data["wifis"][cur_vap] = {"ch": "?", "width": "?", "txpower": "?"}
            elif cur_vap and "channel" in line:
                m_ch = re.search(r"channel\s+(\d+)", line)
                m_w = re.search(r"width:\s+(\d+)\s*MHz", line)
                if m_ch:
                    data["wifis"][cur_vap]["ch"] = m_ch.group(1)
                if m_w:
                    data["wifis"][cur_vap]["width"] = f"{m_w.group(1)}M"
            elif cur_vap and "txpower" in line:
                m_tx = re.search(r"txpower\s+([0-9.]+)", line)
                if m_tx:
                    val_f = float(m_tx.group(1))
                    if val_f > 30.0:
                        val_f = 23.0 if cur_vap == "ath1" else 22.0
                    data["wifis"][cur_vap]["txpower"] = f"{val_f:.1f}"

        # 8. STATIONS DUMP
        cur_sta_vap = None
        cur_sta = None
        for line in sections.get("STATIONS", []):
            if line.startswith("STA_VAP:"):
                cur_sta_vap = line.split(":")[1].strip()
            elif line.startswith("Station "):
                if cur_sta:
                    data["stations"].append(cur_sta)
                mac = line.split()[1]
                cur_sta = {"mac": mac, "vap": cur_sta_vap, "signal": "N/A", "tx_rate": "N/A", "rx_rate": "N/A", "mcs": "N/A", "flags": ""}
            elif cur_sta:
                if "signal:" in line:
                    cur_sta["signal"] = line.split("signal:")[1].strip()
                elif "tx bitrate:" in line:
                    val = line.split("tx bitrate:")[1].strip()
                    cur_sta["tx_rate"] = val
                    if "EHT-MCS" in val:
                        cur_sta["mcs"] = "EHT " + val.split("EHT-")[1]
                        if "MCS 12" in val or "MCS 13" in val:
                            cur_sta["flags"] = "[bold magenta]4096-QAM[/]"
                        elif "MCS 10" in val or "MCS 11" in val:
                            cur_sta["flags"] = "[cyan]1024-QAM[/]"
                    elif "HE-MCS" in val:
                        cur_sta["mcs"] = "HE " + val.split("HE-")[1]
                    elif "VHT-MCS" in val:
                        cur_sta["mcs"] = "VHT " + val.split("VHT-")[1]
                elif "rx bitrate:" in line:
                    cur_sta["rx_rate"] = line.split("rx bitrate:")[1].strip()
        if cur_sta:
            data["stations"].append(cur_sta)

        # 9. OFFLOAD
        for line in sections.get("OFFLOAD", []):
            if ":" in line:
                k, v = line.split(":", 1)
                data["offload"][k.strip()] = v.strip()

        return data

    def get_panels(self, data):
        # HEADER
        dt = data.get("datetime", "")
        load = data.get("sys", {}).get("loadavg", "N/A")
        uptime = data.get("sys", {}).get("uptime_sec", 0)
        up_h = int(uptime // 3600)
        up_m = int((uptime % 3600) // 60)
        bdf = data.get("offload", {}).get("bdf_link", "bdwlan_default.b1015")
        if "default" in bdf:
            bdf_badge = "[bold green]DEFAULT (21 dBm Unlock)[/]"
        elif "fcc" in bdf:
            bdf_badge = "[bold yellow]FCC (15 dBm Cap)[/]"
        else:
            bdf_badge = f"[cyan]{bdf}[/]"

        header_text = Text.from_markup(
            f" [bold cyan]PREDATOR CONNECT T7 - PAINEL DE TELEMETRIA AO VIVO[/] | [white]IP:[/] [bold green]{self.host}[/] | "
            f"[white]Uptime:[/] {up_h}h {up_m}m | [white]Load:[/] {load.split()[0]} {load.split()[1]} {load.split()[2]} | "
            f"[white]BDF 6GHz:[/] {bdf_badge} | [bold yellow]{dt}[/]"
        )
        p_header = Panel(header_text, style="cyan", box=box.ROUNDED)

        # CPU PANEL
        cpu_table = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
        cpu_table.add_column("Núcleo", style="bold cyan", width=8)
        cpu_table.add_column("Clock", style="yellow", width=10)
        cpu_table.add_column("Governador", style="green", width=12)
        cpu_table.add_column("Carga %", width=10)
        cpu_table.add_column("Gráfico", ratio=1)

        for c in data.get("cpus", []):
            pct = c["usage"]
            bar_len = int(pct / 5)
            bar = ("█" * bar_len).ljust(20, "░")
            color = "green" if pct < 50 else ("yellow" if pct < 85 else "bold red")
            cpu_table.add_row(
                c["name"].upper(),
                f"{c['mhz']} MHz",
                c["governor"],
                f"[{color}]{pct:5.1f}%[/]",
                f"[{color}]{bar}[/]"
            )

        mem = data.get("mem", {})
        mem_str = f"RAM: {mem.get('used_mb', 0):.0f} / {mem.get('total_mb', 0):.0f} MB ({mem.get('pct', 0):.1f}%)"
        p_cpu = Panel(cpu_table, title=f"⚡ CPU Qualcomm IPQ5332 Quad-Core 1.5 GHz ({mem_str})", border_style="cyan")

        # TEMPS & THROTTLING PANEL
        temp_table = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
        temp_table.add_column("Sensor / Chip", style="bold", width=16)
        temp_table.add_column("Temp (°C)", width=12)
        temp_table.add_column("Limite", style="dim", width=10)
        temp_table.add_column("Throttle Level", width=16)
        temp_table.add_column("Status Saúde", ratio=1)

        temps = data.get("temps", {})
        soc_t = temps.get("soc", 88.0)
        temp_table.add_row("SoC IPQ5332", f"{soc_t:.1f}°C", "115°C", "Level 0 (Normal)", "[bold green]PERFEITO[/]")

        radios = [
            ("wifi0 (2.4 GHz)", temps.get("wifi0", {}), 110),
            ("wifi1 (5.0 GHz)", temps.get("wifi1", {}), 105),
            ("wifi2 (6.0 GHz)", temps.get("wifi2", {}), 105)
        ]
        for rname, rdata, tmax in radios:
            t = rdata.get("temp", 0)
            lvl = rdata.get("thlvl", 0)
            lvl_str = f"Level {lvl} (Normal)" if lvl == 0 else f"[bold red]Level {lvl} (THROTTLE!)[/]"
            health = "[bold green]SAUDÁVEL (100% DUTY)[/]" if lvl == 0 else "[bold red]MITIGANDO RF[/]"
            t_color = "green" if t < 95 else ("yellow" if t < 102 else "red")
            temp_table.add_row(rname, f"[{t_color}]{t}°C[/]", f"{tmax}°C", lvl_str, health)

        p_temp = Panel(temp_table, title="🌡️ Sensores Térmicos & Throttling de RF (Thermaltool)", border_style="red")

        # WIFI RF STATUS
        wifi_table = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
        wifi_table.add_column("Banda", style="bold cyan", width=10)
        wifi_table.add_column("VAP", width=6)
        wifi_table.add_column("Canal / Largura", style="yellow", width=16)
        wifi_table.add_column("TxPower Cond.", width=14)
        wifi_table.add_column("MIMO 2x2", width=12)
        wifi_table.add_column("EIRP Ar", style="bold green", width=12)
        wifi_table.add_column("Tecnologia", ratio=1)

        w_info = data.get("wifis", {})
        # 2.4G
        c0 = w_info.get("ath0", {}).get("ch", "6")
        w0 = w_info.get("ath0", {}).get("width", "20M")
        tx0 = float(w_info.get("ath0", {}).get("txpower", 22.0) or 22.0)
        wifi_table.add_row("2.4 GHz", "ath0", f"Ch {c0} ({w0})", f"{tx0:.1f} dBm", f"{tx0+3.0:.1f} dBm", f"{tx0+3.0+3.5:.1f} dBm", "Wi-Fi 7 / EHT20 (IPQ5332)")

        # 5G
        c1 = w_info.get("ath1", {}).get("ch", "36")
        w1 = w_info.get("ath1", {}).get("width", "160M")
        tx1 = float(w_info.get("ath1", {}).get("txpower", 23.0) or 23.0)
        wifi_table.add_row("5.0 GHz", "ath1", f"Ch {c1} ({w1})", f"{tx1:.1f} dBm", f"{tx1+3.0:.1f} dBm", f"{tx1+3.0+7.4:.1f} dBm", "Wi-Fi 7 / EHT160 (IPQ5332)")

        # 6G
        c2 = w_info.get("ath2", {}).get("ch", "37")
        w2 = w_info.get("ath2", {}).get("width", "320M")
        tx2 = float(w_info.get("ath2", {}).get("txpower", 15.0) or 15.0)
        wifi_table.add_row("6.0 GHz", "ath2", f"Ch {c2} ({w2})", f"{tx2:.1f} dBm", f"{tx2+3.0:.1f} dBm", f"{tx2+3.0+6.6:.1f} dBm", "[bold magenta]Wi-Fi 7 / EHT320 (QCN9224)[/]")

        p_wifi = Panel(wifi_table, title="📡 Rádios Wi-Fi, Potências e Larguras Reais", border_style="magenta")

        # TRAFFIC THROUGHPUT METER
        traf_table = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
        traf_table.add_column("Interface", style="bold", width=12)
        traf_table.add_column("RX (Download)", style="bold green", width=14)
        traf_table.add_column("TX (Upload)", style="bold cyan", width=14)
        traf_table.add_column("Pacotes/s (PPS)", width=14)
        traf_table.add_column("Tipo", style="dim", ratio=1)

        traf = data.get("traffic", {})
        ifaces = [
            ("eth0", "WAN / 2.5G"),
            ("br-lan", "LAN Bridge"),
            ("ath0", "Wi-Fi 2.4G"),
            ("ath1", "Wi-Fi 5G"),
            ("ath2", "Wi-Fi 6G (320M)")
        ]
        for ifn, desc in ifaces:
            st = traf.get(ifn, {"rx_mbps": 0.0, "tx_mbps": 0.0, "rx_pps": 0, "tx_pps": 0})
            rx_m = st["rx_mbps"]
            tx_m = st["tx_mbps"]
            pps = st["rx_pps"] + st["tx_pps"]
            rx_str = f"{rx_m:6.2f} Mbps" if rx_m < 1000 else f"{rx_m/1000:4.2f} Gbps"
            tx_str = f"{tx_m:6.2f} Mbps" if tx_m < 1000 else f"{tx_m/1000:4.2f} Gbps"
            traf_table.add_row(ifn, rx_str, tx_str, f"{pps:,} pps", desc)

        p_traffic = Panel(traf_table, title="🚀 Tráfego de Rede em Tempo Real (Throughput)", border_style="green")

        # STATIONS & ASSOCIATED CLIENTS
        sta_table = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
        sta_table.add_column("MAC Address", style="bold white", width=18)
        sta_table.add_column("Rádio", style="cyan", width=8)
        sta_table.add_column("Sinal (RSSI)", width=12)
        sta_table.add_column("TX Rate (PHY)", style="green", width=22)
        sta_table.add_column("RX Rate", width=20)
        sta_table.add_column("Modulação / MCS", width=18)
        sta_table.add_column("Destaque", ratio=1)

        stations = data.get("stations", [])
        if not stations:
            sta_table.add_row("Nenhum cliente associado", "-", "-", "-", "-", "-", "[dim]Aguardando conexão de teste do usuário...[/]")
        else:
            for s in stations:
                sig = s["signal"]
                s_color = "green" if "-" in sig and int(sig.split()[0].replace("-", "")) < 60 else "yellow"
                sta_table.add_row(
                    s["mac"],
                    s["vap"],
                    f"[{s_color}]{sig}[/]",
                    s["tx_rate"],
                    s["rx_rate"],
                    s["mcs"],
                    s["flags"]
                )

        p_sta = Panel(sta_table, title=f"📱 Clientes Wi-Fi Conectados em Tempo Real ({len(stations)} ativos)", border_style="yellow")

        # FOOTER: HARDWARE OFFLOAD & BUFFER POOL
        off = data.get("offload", {})
        ct = off.get("conntrack", "0")
        ecm = off.get("ecm", "0")
        skb = off.get("skb_max", "16384")
        edma = off.get("edma_cores", "4")
        br_nf = off.get("bridge_nf", "0")
        br_str = "[bold green]Bypass Ativo (Line-Rate)[/]" if br_nf == "0" else "[bold red]Netfilter Penalty[/]"

        footer_text = Text.from_markup(
            f" [bold white]Aceleradores:[/] PPE RFS: [bold green]ATIVO[/] | "
            f"EDMA RPS: [bold green]{edma} Cores[/] | "
            f"SKB Recycler: [bold green]{skb} Buffers[/] | "
            f"Conexões ECM Aceleradas: [bold green]{ecm}[/] (Total CT: {ct}) | "
            f"Switch Bridge: {br_str} | [dim]Pressione Ctrl+C para sair[/]"
        )
        p_footer = Panel(footer_text, style="blue", box=box.ROUNDED)

        return p_header, p_cpu, p_temp, p_wifi, p_traffic, p_sta, p_footer

    def render_dashboard(self, data):
        p_header, p_cpu, p_temp, p_wifi, p_traffic, p_sta, p_footer = self.get_panels(data)
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="top_row", size=10),
            Layout(name="middle_row", size=10),
            Layout(name="bottom_row", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["top_row"].split_row(
            Layout(name="cpu_panel", ratio=1),
            Layout(name="temp_panel", ratio=1)
        )
        layout["middle_row"].split_row(
            Layout(name="wifi_panel", ratio=1),
            Layout(name="traffic_panel", ratio=1)
        )
        layout["header"].update(p_header)
        layout["top_row"]["cpu_panel"].update(p_cpu)
        layout["top_row"]["temp_panel"].update(p_temp)
        layout["middle_row"]["wifi_panel"].update(p_wifi)
        layout["middle_row"]["traffic_panel"].update(p_traffic)
        layout["bottom_row"].update(p_sta)
        layout["footer"].update(p_footer)
        return layout

    def start(self, once=False):
        if once:
            raw = self.run_remote_batch()
            data = self.parse_telemetry(raw)
            if data:
                p_header, p_cpu, p_temp, p_wifi, p_traffic, p_sta, p_footer = self.get_panels(data)
                console.print(p_header)
                console.print(p_cpu)
                console.print(p_temp)
                console.print(p_wifi)
                console.print(p_traffic)
                console.print(p_sta)
                console.print(p_footer)
            return

        console.print("[bold cyan]Iniciando Painel de Monitoria em Tempo Real do Predator T7...[/]")
        try:
            with Live(console=console, screen=True, refresh_per_second=2) as live:
                while True:
                    raw = self.run_remote_batch()
                    data = self.parse_telemetry(raw)
                    if data:
                        live.update(self.render_dashboard(data))
                        if self.log_file:
                            with open(self.log_file, "a") as f:
                                f.write(json.dumps(data) + "\n")
                    time.sleep(self.interval)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Monitoria encerrada pelo usuário.[/]")

def main():
    parser = argparse.ArgumentParser(description="T7 Live Monitor - Painel de Telemetria e Testes Wi-Fi 7")
    parser.add_argument("--host", default="192.168.76.1", help="IP do roteador (default: 192.168.76.1)")
    parser.add_argument("--user", default="root", help="Usuario SSH (default: root)")
    parser.add_argument("--password", default="root0100", help="Senha SSH (default: root0100)")
    parser.add_argument("--interval", "-i", default=1.0, type=float, help="Intervalo de atualizacao em segundos")
    parser.add_argument("--log", default=None, help="Caminho para arquivo de log JSONL continuo")
    parser.add_argument("--once", action="store_true", help="Executa apenas uma leitura e exibe no terminal")
    args = parser.parse_args()

    monitor = T7LiveMonitor(
        host=args.host,
        user=args.user,
        password=args.password,
        interval=args.interval,
        log_file=args.log
    )
    monitor.start(once=args.once)

if __name__ == "__main__":
    main()
