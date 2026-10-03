# Update Post for OpenWrt Forum
**Thread:** `[RESEARCH / GUIDE] Acer Predator Connect T7 (Qualcomm IPQ5332 Wi-Fi 7) – Root Shell Unlock, 2.5Gbps AP Mode & MTD Backups`  
**URL:** https://forum.openwrt.org/t/research-guide-acer-predator-connect-t7-qualcomm-ipq5332-wi-fi-7-root-shell-unlock-2-5gbps-ap-mode-mtd-backups/254042  
**Date:** October 3, 2026  

---

### [UPDATE] Official v1.01.000027 Firmware, Safe A/B Dual-Boot Strategy, Native LuCI on Port 80 & 2.5Gbps Bridge Netfilter Bypass

Hi everyone,

Following up on our initial findings and our discussion regarding hardware parity with the X7 5G CPE, I wanted to share a major progress update and several low-level networking breakthroughs on the **Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7)**.

All new scripts, partition dumps, and configuration suites are live in our open-source repository:  
👉 **GitHub:** [https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7](https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7)

Here is a summary of what we tested, verified, and stabilized on physical hardware:

---

### 1. 🔍 Discovery of Latest Stock Firmware `v1.01.000027` (v27)
By reverse-engineering Acer's OTA update infrastructure (`imgupgrade.acer.com.tw`), we discovered and fetched the latest official firmware build **`v1.01.000027`** (August 2024), which supersedes the factory OEM build (`v1.01.000024`).

**Key improvements verified in v27:**
* Updated Qualcomm QSDK Wi-Fi drivers and ART radio parameter handling.
* Fixed kernel memory leaks in bridge multicast forwarding.
* Addressed `odhcpd` prefix delegation edge cases.
* Security patches for OpenSSL and WPA3-SAE handshake parsing.

---

### 2. 🛡️ Safe A/B Dual-Boot Strategy (Zero Risk of Bricking)
The T7 features a 1 GB SPI NAND with duplicate 240 MB system image slots:
* **Slot 1 (`rootfs` / `mtd21`):** Retained **100% UNTOUCHED** with factory v24 as a golden fail-safe recovery image.
* **Slot 2 (`rootfs_1` / `mtd20`):** Flashed with our upgraded and optimized v27 system.

#### How Slot Switching & Recovery Works:
Qualcomm's U-Boot determines the active boot slot through the dual `BOOTCONFIG` partitions (`mtd3` and `mtd4`), which store the binary `primaryboot` indicator (`1` for Slot 1, `2` for Slot 2).

#### 🚨 What happens if Slot 2 breaks or crashes? (Practical Reality & Recovery)

In real-world bench testing, we evaluated the different recovery paths:
* **Why not UART?** Retail T7 boards have unpopulated UART test pads covered with black solder resist/mask without pins or tin — soldering wires is impractical for most users.
* **Why not rely solely on Qualcomm Watchdog?** If a kernel hang or driver loop occurs early before the watchdog counter arms, the SoC can freeze indefinitely rather than falling back cleanly.

Therefore, we established two foolproof recovery workflows depending on system state:

1. **If the OS is reachable (Terminal / SSH / Telnet):**
   Run our 1-line tool directly on the router:
   ```sh
   /usr/sbin/boot-acer
   ```
   *(Or remotely from Windows via `04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/executar_chaveamento_slot1_recovery.py`).*  
   This updates `primaryboot = 1` in `/proc/boot_info` and syncs `mtd3`/`mtd4` in 3 seconds.

2. **If the router DOES NOT boot (Complete OS Brick / Loop): The Hardware WPS Button Failsafe Web Recovery**
   * Power off the router (unplug power cable).
   * Hold the physical **WPS button** on the router chassis.
   * Plug in power while keeping the **WPS button held for 5 to 10 seconds** until the LEDs flash into recovery pattern.
   * U-Boot spins up an **Emergency Failsafe Web Recovery interface at `http://192.168.1.1`**.
   * Set your PC Ethernet adapter to static IP `192.168.1.66` (Netmask `255.255.255.0`, Gateway `192.168.1.1`).
   * Navigate to `http://192.168.1.1` in your browser and upload the appropriate FIT script from our repo:
     * **`restaurar_slot1_acer.itb`**: Flashes `primaryboot = 1` to NAND and boots **Slot 1 (Factory OEM v24)**.
     * **`chavear_slot2_acer.itb`**: Flashes `primaryboot = 0` to NAND and boots **Slot 2 (v27 LuCI)**.
   * U-Boot unpacks the `.itb` in RAM, executes the embedded bootloader script, rewrites the `bootconfig` blocks on NAND, and automatically reboots into the chosen slot. No disassembly or UART required!

---

### 3. 🌐 Native LuCI Restored on Standard Port 80
Acer deliberately crippled OpenWrt's native LuCI interface by commenting out the init hooks inside `/etc/init.d/uhttpd` and running their proprietary `lighttpd` web server instead.

We restored native LuCI:
* Uncommented `config_load uhttpd` and `config_foreach start_instance uhttpd` in `/etc/init.d/uhttpd`.
* Bound `uhttpd` directly to `0.0.0.0:80` and `[::]:80`.
* Granted full read/write permissions to `Admin` and `root` in `rpcd`.
* Disabled `lighttpd.init` completely.
* **Result:** A clean, responsive OpenWrt LuCI interface on port 80 without proprietary bloat.

---

### 4. ⚡ 2.5 Gbps AP Mode & Netfilter Bridge Bypass Fix
When configuring the T7 as a high-performance Access Point (bridging `eth0` 2.5G WAN into `br-lan` alongside the LAN switch ports and disabling DHCP), we encountered an interesting issue: **Wi-Fi 7 clients on 6 GHz were failing to receive DHCP offers from the upstream router.**

#### Root Cause:
The Linux kernel was filtering bridge frames through netfilter iptables (`net.bridge.bridge-nf-call-iptables = 1`), causing broadcast DHCP Discover/Offer packets traversing the software bridge between `ath2` (Wi-Fi 7) and `eth0` (WAN/Uplink) to be dropped.

#### The Solution:
We disabled netfilter bridge inspection in `/etc/sysctl.d/99-performance.conf`:
```ini
net.bridge.bridge-nf-call-iptables = 0
net.bridge.bridge-nf-call-ip6tables = 0
net.bridge.bridge-nf-call-arptables = 0
```
* **Performance Gain:** `br-lan` now behaves as a pure Layer-2 hardware switch with zero CPU overhead for local switching.
* **Compatibility:** All multicast and broadcast protocols (**mDNS, Apple AirPlay, Chromecast, Sonos, DLNA, and DHCP relay**) now pass transparently at full 2.5 Gbps wire speed.
* **Router Mode Safe:** In standard router mode, WAN protection remains 100% active because Internet routing occurs at Layer-3.

---

### 5. 🧹 Debloat & +50 MB RAM Reclaimed
We identified several orphan background daemons inherited from the X7 5G CPE that were continuously polling non-existent serial ports and consuming CPU cycles:
* **Cellular Daemons:** `at_ril`, `ril`, `modem_readd`, `modem-monitor`, `modem_datausage`, `ipqcm`.
* **Telemetry & Crash Repositories:** `monitord`, `sodd`, `cwmp`, `mqtt_client`, `breakpad`.
* **Unused File Sharing:** `samba4`, `ksmbd`.

Halting and disabling these services freed **over 50 MB of RAM** (available memory increased from ~508 MB to ~572 MB) and reduced CPU load to 0.00.

---

### 6. 📶 Wi-Fi 7 (802.11be) & Roaming Fine-Tuning
* **6 GHz (Qualcomm QCN9224):** Set to 320 MHz channel width (`HT320`) on PSC channel 37 with WPA3-SAE and mandatory PMF (`ieee80211w=2`), negotiating **5.7648 Gb/s physical link rate**.
* **5 GHz (Qualcomm QCN6432):** Configured on 80 MHz (`HT80`) clean non-DFS channel, delivering rock-solid 1.44 Gbps link rate across 4 beamforming antennas (8.38 dBi gain, ~35 dBm EIRP).
* **Seamless Roaming (802.11k & 802.11v):** Enabled `bss_transition=1`, `rrm_neighbor_report=1`, `rrm_beacon_report=1`, and `wnm_sleep_mode=1` across all radios for zero-lag handoffs on modern Android and Apple (iOS/macOS) devices.
* **DTIM Period = 2:** Tuned to Apple mobility specifications, optimizing client battery life without introducing push notification latency.

---

### 7. 🌐 Universal IPv6 Hybrid Mode (`odhcpd`)
To eliminate the recurring syslog alert (*"no public prefix on lan thus we don't announce a default route"*), we configured `odhcpd` in **hybrid mode** on both `lan` and `wan6` (`dhcpv6`, `ra`, `ndp` in `hybrid`, with `master=1` on WAN6).
* In double-NAT / AP environments, it automatically functions as an NDP proxy relay.
* If connected directly to an ISP ONT with prefix delegation (`/56` or `/60`), it promotes itself to an authoritative server.

---

### 8. 📦 1-Click Backup & Automation Suite
For users running Windows, we added an interactive terminal launcher (`RESTAURAR_OU_BACKUP_T7.bat`) and standalone Python automation scripts that allow applying the AP configuration, taking a 1:1 overlay snapshot, or rolling back slots with a single double-click.

Feel free to test the scripts or explore the extracted DTS and partition dumps in the repository. Happy to answer questions or help anyone testing Qualcomm IPQ53xx targets!
