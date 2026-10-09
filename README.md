<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

<p align="center">
  <b>🌐 Language / Idioma:</b>
  <a href="README.md"><b>🇺🇸 English</b></a> |
  <a href="README_PT.md">🇧🇷 Português (Brasil)</a>
</p>

# Acer Predator Connect T7 — Root Unlock, Native LuCI, Wi-Fi 7 & Dual-Boot Architecture

> **Project Status (October 2026)**: Running in production on **Slot 2 (`rootfs_1`)** with **Official Firmware v1.01.000027 (v27)**, native **LuCI on Port 80**, **Wi-Fi 7 (320 MHz / 5.76 Gbps)** with 802.11k/v Roaming, and comprehensive debloat. **Slot 1 (`rootfs`) and U-Boot are retained 100% untouched from factory as the definitive anti-brick failsafe**.

> **Keywords / SEO**: Acer Predator Connect T7, Wi-Fi 7 router unlock, Qualcomm IPQ5332, MLO 6GHz, root access dropbear, telnet unlock, unbrick predator t7, openwrt predator t7, dual-boot slot rollback, firmware dump MTD.

> ⚠️ **CRITICAL WARNING**: **DO NOT** execute any of the scripts or optimization processes over a Wi-Fi connection. Modifying network interfaces or flashing over wireless may drop your connection mid-process and soft-brick the router. **Always use a wired (Ethernet) connection when running the management suite.**

---

## ⚡ QUICK INSTALLATION (TESTED & HOMOLOGATED ENVIRONMENT)

> [!IMPORTANT]
> ### 💻 RECOMMENDED ENVIRONMENT: WINDOWS + POWERSHELL
> The entire automation toolkit, `.cfg` injection routines, port probes, and flash partition flashers have been **thoroughly tested, validated, and homologated on Windows with PowerShell**.  
> To guarantee **100% success and zero risk of unexpected issues**, use a Windows PC connected directly to the router via Ethernet cable.

### 🚀 Official Method (1-Line Windows PowerShell — Zero Manual Downloads):
Open **PowerShell** on Windows (as standard User or Administrator) and paste the official command below:

```powershell
irm https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.ps1 | iex
```

#### 📦 What this command does automatically:
1. **Workspace Setup:** Downloads and organizes suite files into `Desktop\Acer-Predator-Connect-T7`.
2. **Ensures Python 3.14:** Detects Python installation; if missing, installs it silently via WinGet and permanently configures user `PATH`.
3. **Live Network Probe:** Scans the local network, discovers your Predator T7 IP, and verifies Web (80), Telnet (23), and SSH (22) status.
4. **Smart Workflow:**
   * **If the router is factory locked:** Generates the unlock `.cfg` directly on your Desktop, launches the restore page in your browser, and monitors reboot.
   * **If the router is already unlocked:** Opens straight into the **Master Management Suite** for Slot 2 flashing, LuCI activation, dual-boot switching, or Telnet hardening.
5. **Automatic Diagnostic Logging (`LOG_PREDATOR_T7.txt`):** Every step, probe, flash write, and integrity verification is automatically logged in real time to `Desktop\LOG_PREDATOR_T7.txt`. If you run into any unexpected issue or need assistance, simply share this file!

---

### 📂 Offline Alternative (If you already downloaded or cloned the repository):
If you have already downloaded the `.zip` or cloned the repository:
* **On Windows:** Double-click directly on **`EXECUTAR_T7.bat`** (or run `.\iniciar.ps1` in PowerShell).  
  *(Fully immune to path loss when launched as Administrator).*

---

## 🔑 IP Addresses, Unified Credentials & Wi-Fi Networks

Credentials across the ecosystem are **100% unified** between the unlock backup `.cfg` (Slot 1) and the **Custom OpenWrt ROM** (Slot 2):

| Parameter | Default Configuration (.cfg Unlock & Custom ROM Slot 2) |
| :--- | :--- |
| **LAN IP Address** | **`192.168.76.1`** (Official Default) |
| **Web GUI (Port 80)** | **`http://192.168.76.1/`** (Native LuCI on Slot 2 / OEM Web on Slot 1) |
| **Web / SSH User** | **`root`** (or **`Admin`** on OEM Web) |
| **System / Root Password** | **`root0100`** (Unified password for Web, SSH and Telnet) |
| **SSH Port (Terminal)** | Port **`22`** (Active Dropbear) |
| **Telnet Port (Rescue)** | Port **`23`** (Direct root ash shell for automation) |
| **Wi-Fi Network 2.4 GHz** | **`PREDATOR T7_2.4GHz`** / **`Predator_T7_2.4G`** |
| **Wi-Fi Network 5 GHz** | **`PREDATOR T7_5GHz`** / **`Predator_T7_5G`** |
| **Wi-Fi Network 6 GHz (Wi-Fi 7)** | **`PREDATOR T7_6GHz`** / **`Predator_T7_6G`** (WPA3-SAE) |
| **Wi-Fi Password (All Bands)** | **`123456789`** (Default for 2.4G, 5G, and 6G) |

> [!TIP]
> **Backup Reference Document:**  
> Detailed instructions and credentials for the `.cfg` unlock file are preserved in:  
> [`02_BACKUPS_E_DUMPS/Configuracoes_CFG/INFORMACOES_DO_BACKUP_CFG.txt`](02_BACKUPS_E_DUMPS/Configuracoes_CFG/INFORMACOES_DO_BACKUP_CFG.txt)

> [!WARNING]
> ### 🛡️ The Golden Rule for Changing Passwords
> **NEVER delete or rename the `root` or `Admin` accounts.**  
> Both accounts share UID 0. OpenWrt and LuCI expect `root`, while background cron routines and original Qualcomm/Acer daemons depend on `Admin`.  
> If you update your password in the terminal, **always update both accounts** to keep them synchronized:
> ```sh
> passwd root
> passwd Admin
> ```

---

## ⚡ Quick Feature Summary

* 🛡️ **Safe A/B Dual-Boot with Factory Reserve:** Slot 1 (`mtd21` / original factory OEM firmware that came with the device) and **U-Boot** are kept **100% factory untouched**. All custom modifications run exclusively on Slot 2 (`mtd20` / v27).
* 🔄 **Instant 1-Command Rollback:** If Slot 2 ever encounters an issue, typing `/usr/sbin/boot-acer` restores boot to Slot 1 in seconds.
* 🌐 **Native LuCI on Port 80:** Acer's proprietary web server (`lighttpd`) is disabled and LuCI (`uhttpd`) takes over port 80 by default, with automatic routing fallback (`/pub/dist/index.html` -> LuCI).
* 📶 **Calibrated Turbo Wi-Fi 7:** 6 GHz radio in 320 MHz width (5.76 Gbps) with *Preamble Puncturing*, *Target Wake Time* (TWT for mobile battery saving), *BSS Coloring*, 4x4 Beamforming, OFDMA, and Fast Roaming 802.11k/v/r (<50ms).
* ⚖️ **Multicore RPS Calibration (4 CPUs):** Network port packet queues distributed across all 4 Qualcomm IPQ5332 cores with optimized TCP buffers.
* 🧹 **Clean System Debloat:** Orphaned cellular daemons from model X7 (`at_ril`, `modem_readd`), heavy OEM telemetry (`monitord`, `sodd`, `cwmp`, `breakpad`), and Samba halted, freeing **+50 MB of RAM**.
* 📋 **Real-Time Automatic Diagnostic Logging:** The toolkit continuously logs all operational details into `Desktop\LOG_PREDATOR_T7.txt`, making troubleshooting and community support immediate and effortless.

---

## 1. 🛡️ Dual-Boot A/B Architecture & Anti-Brick Protection

The Acer Predator Connect T7 features a 1 GB SPI NAND flash partitioned into a dual redundant structure managed by the Qualcomm IPQ5332 SoC:

```
       +-----------------------------------------------------------+
       |                  1 GB SPI NAND FLASH                      |
       +-----------------------------------------------------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
     [SLOT 1 - A]                                        [SLOT 2 - B]
  Partition: mtd21 (rootfs)                          Partition: mtd20 (rootfs_1)
  State: UNTOUCHED / OEM RESERVE                     State: ACTIVE IN PRODUCTION
  Firmware: Device Native Factory Version            Firmware: Optimized v1.01.000027
            (e.g., v24, v26, or v27 depending on batch)
  Role: Factory Anti-Brick Failsafe Image            Role: LuCI Port 80 + Wi-Fi 7
  U-Boot: 100% Factory Untouched                     U-Boot: 100% Factory Untouched
```

### What Controls Active Boot?
U-Boot reads partitions `mtd3` (`0:BOOTCONFIG`) and `mtd4` (`0:BOOTCONFIG1`), which store the `primaryboot` variable:
* **`primaryboot = 1`:** Bootloader boots **Slot 1** (Factory OEM protected).
* **`primaryboot = 2` (or `0`):** Bootloader boots **Slot 2** (OpenWrt v27 with LuCI).

---

### 🚨 What to Do If Slot 2 Breaks or Crashes?

#### Scenario A: Router is Still Reachable via Terminal (Telnet or SSH)
Run a single command in the router terminal:
```sh
/usr/sbin/boot-acer
```
The script writes `primaryboot = 1` across both boot partitions and reboots back into **factory Slot 1**.

*(Windows alternative: choose Option [2] Dual-Boot switch in the management suite).*

#### Scenario B: Hardware Failsafe Recovery (WPS Button on IP `192.168.1.1`)
Because **U-Boot remains 100% untouched**, hardware web recovery is always intact:
1. Unplug the power adapter.
2. Press and hold the **physical WPS button** on the router chassis.
3. Plug the power adapter back in while **holding WPS for 5 to 10 seconds** until the LEDs flash into recovery mode. Release the button.
4. U-Boot launches an **Emergency Web Recovery page on `http://192.168.1.1`**.
5. Set your PC network card to static IP `192.168.1.66` (Netmask `255.255.255.0`, Gateway `192.168.1.1`).
6. Open your browser to `http://192.168.1.1` and upload the recovery image:
   * **`restaurar_slot1_acer.itb`:** Restores boot to **Slot 1 (Native factory OEM firmware)**.
   * **`chavear_slot2_acer.itb`:** Restores boot to **Slot 2 (LuCI v27)**.

#### Scenario C: Clean Reflash of Slot 2 from Scratch
To reinstall Slot 2 completely:
1. Boot into Slot 1.
2. In the Management Suite menu, choose option **`[1] Flash Custom OpenWrt + Root to Slot 2`**.
3. The script transfers the custom v27 ROM via local HTTP, verifies MD5 checksums, flashes the partitions, and wipes overlay clean with 147 MB free space.

---

## 2. 📶 Radio Channels and Wi-Fi 7 Tuning

| Radio | Frequency | Width / Channel | Physical Link Rate | Features & Roaming |
| :--- | :--- | :--- | :--- | :--- |
| **`wifi2`** | 6 GHz | **HT320 (320 MHz)** / Auto | **5.7648 Gb/s** | WPA3-SAE, Mandatory PMF, 802.11k/v, DTIM=2, TWT, Puncturing |
| **`wifi1`** | 5 GHz | **HT80 (80 MHz)** / Auto | **1.44 Gb/s** | 4 Beamforming Antennas (8.38 dBi), 802.11k/v, DTIM=2 |
| **`wifi0`** | 2.4 GHz | `HT20` / Auto | 688 Mb/s | WPA2-PSK AES (Universal legacy compatibility & IoT) |

> [!NOTE]
> **Regarding TX Power (dBm):** The 5 GHz radio already runs at the physical ceiling of the Qualcomm FEM amplifiers (~27.3 dBm conducted / ~35 dBm EIRP). The 6 GHz radio is factory-calibrated under the international LPI (Low Power Indoor - 5 dBm/MHz) mask. Forcing higher software power on 320 MHz channels saturates the front-ends and causes EVM constellation distortion on 4096-QAM, lowering real-world throughput. Factory calibration provides the optimal balance of speed and stability.

---

## 3. 🔒 Post-Installation Hardening: Managing Telnet

The **Telnet (port 23)** service is active during unlock to ensure any computer can connect and recover the device without SSH key mismatches. It listens **strictly on the local LAN** and is blocked 100% on WAN.

To disable Telnet after completing your setup:
* **On the router terminal:** run:
  ```sh
  desativar-telnet
  ```
  *(To reactivate whenever needed, simply run: `ativar-telnet`)*.
* **From your PC:** Select option **`[3] Manage Telnet (Hardening)`** in the Management Suite.

---

## 4. 🔗 Research Protocol: Acer Predator Connect X7 (5G CPE)

The **Acer Predator Connect X7** shares the same base Qualcomm IPQ5332 SoC, but integrates a 5G cellular M.2 modem (Snapdragon X62) with official firmware `v50`.

> [!CAUTION]
> **SAFETY LOCK ACTIVE:** The v27 images in this repository are **EXCLUSIVE to the Predator Connect T7**. Flashing these images onto an X7 will cause a **BRICK**. The flashing script detects hardware and strictly blocks unauthorized models.

* Owners of the X7 model can use option **`[5] Acer Connect X7 Research & Diagnostic Area`** to capture read-only diagnostic dumps and assist in reverse-engineering the 5G modem.

---

<p align="center">
  <b>Developed by the OpenWrt Community & Independent Reverse Engineering</b><br>
  MIT License — Free for use, study, and enhancement.
</p>
