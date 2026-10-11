<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

<p align="center">
  <b>🌐 Language / Idioma:</b>
  <a href="README_PT.md">🇧🇷 Português (Brasil)</a> |
  <a href="README.md"><b>🇺🇸 English</b></a> |
  <a href="README_ES.md">🇪🇸 Español</a>
</p>

# Acer Predator Connect T7 — Root Unlock, Native LuCI, Wi-Fi 7 & Factory Reset Guide

> **Project Status (October / 2026)**: Instant 1-minute unlock via native master configuration restore (`cfg_restauracao_master_v2.cfg`). Official Acer firmware featuring **native LuCI Web Interface on Port 80**, **Wi-Fi 7 (320 MHz / 5.76 Gbps)**, 802.11k/v Fast Roaming, **Smart Wi-Fi Center**, optimized UPnP, and complete telemetry debloat. **Slot 1 (`rootfs`) and U-Boot kept 100% stock factory intact as an ultimate anti-brick safety net**.

> ⚠️ **CRITICAL ADVICE**: Always perform setup with your computer connected via **Ethernet network cable** directly to one of the LAN ports on the router. Do not attempt this over Wi-Fi to prevent connection drops midway.

---

## ⚡ 1. PREREQUISITE RECOMMENDATION: FIRMWARE v27
> [!TIP]
> **Important Recommendation:**  
> Ensure your router is updated to official firmware version **v1.01.000027 (v27)** before applying the unlock. Version v27 contains the latest Qualcomm RF calibrations, full 320 MHz channel support, and essential kernel fixes.

---

## 🎁 2. UNLOCK BENEFITS (WHY UNLOCK?)

1. 🔓 **Native Root & SSH Access on LAN:** Ports `22` (SSH) and `23` (Telnet) unlocked on the local network without OEM barriers.
2. 🌐 **Full Official OpenWrt LuCI Interface:** Full management interface on port 80 with complete control over firewall rules, DHCP, routing, VLANs, and system processes.
3. 🚀 **Fully Unlocked Wi-Fi 7:** 6 GHz band operating at maximum channel width of **320 MHz (5.76 Gbps)**, 802.11k/v Fast Roaming, and WPA3-SAE.
4. 🎛️ **Smart Wi-Fi Center:** Exclusive, intuitive dashboard allowing easy Wi-Fi tuning and a one-click button to save all radio bands together!
5. 🛡️ **Anti-Deadlock Shield:** Elimination of defunct Qualcomm Mesh (`whc`) and HomePlug PLC (`wsplc`) services that caused internal race conditions and Wi-Fi drops.
6. 🧹 **Maximum Debloat:** Inactive cellular services inherited from the X7 model and invasive OEM telemetry disabled, freeing up **over 50 MB of RAM**.
7. 🎮 **Gaming UPnP / NAT-PMP:** Automatic port mapping for PS5, Xbox, Nintendo Switch, and PC with Open/Moderate NAT and low latency.
8. 🛡️ **100% Anti-Brick Protection:** Slot 1 and U-Boot remain **100% factory original**: resetting via OpenWrt or using the physical reset button instantly restores factory stock defaults!
9. 🌐 **100% Localized & Organized Languages:** LuCI interface and all custom Wi-Fi menus fully translated and aligned in **Portuguese (Brazil)**, **English**, and **Spanish**.

---

## 🛑 3. CRITICAL WARNING: NEVER RESTORE PRE-UNLOCK BACKUPS!

> [!CAUTION]
> ### ⚠️ GOLDEN RULE POST-UNLOCK:
> **Once unlocked using our master backup package, NEVER restore any old backup (`.cfg`) created prior to the unlock!**  
> Restoring a stock pre-unlock backup will overwrite your system, erase LuCI modules, delete the Wi-Fi dashboard, and lock SSH access again.  
>  
> 👉 **How to customize your network:**  
> If you wish to change your Wi-Fi SSID, password, or IP subnet, **always do so manually through the LuCI interface after unlocking**.

---

## 🔑 4. DEFAULT CREDENTIALS AFTER RESTORATION

| Parameter | Default Configuration |
| :--- | :--- |
| **LAN IP Address** | **`192.168.76.1`** |
| **Web Interface (Port 80)** | **`http://192.168.76.1/`** (OpenWrt LuCI) |
| **Web / SSH Username** | **`root`** (or **`admin`**) |
| **Unified Master Password** | **`root0100`** *(Web, SSH & Telnet)* |
| **Master Package File** | **`cfg_restauracao_master_v2.cfg`** *(located at root)* |
| **2.4 GHz Wi-Fi SSID** | **`PREDATOR T7_2.4GHz`** |
| **5.0 GHz Wi-Fi SSID** | **`PREDATOR T7_5GHz`** |
| **6.0 GHz Wi-Fi SSID (Wi-Fi 7)** | **`PREDATOR T7_6GHz`** |
| **Wi-Fi Password (All Bands)** | **`123456789`** |

---

## 🚀 5. STEP-BY-STEP INSTALLATION (1 MINUTE)

> ⚠️ **Connect your computer via Ethernet cable to a LAN port on the T7. Do not use Wi-Fi.**

1. **Access the Direct OEM Restore Page:**  
   Open your browser and navigate to:
   ```text
   https://192.168.76.1/pub/dist/index.html#/system/backRestore
   ```
   *(Or navigate: login ➔ Left menu `System` ➔ `Backup & restore`)*.
2. **Upload the Master Package:**  
   In the bottom **Restore** section:
   * Click **`Browse`** and select:  
     `cfg_restauracao_master_v2.cfg`
   * Click the **`Restore`** button.
3. **Observe the LEDs During Boot:**
   * 🔴 **Front Red LED:** Completely **normal** on first boot! The Qualcomm driver calibrates RF and undergoes a **mandatory 60-second DFS radar check (CAC)** on 5 GHz. Wait approximately **2 minutes and 25 seconds**.
   * 🔵 **Front Blue LED:** Once all 3 radios are online, the front LED switches to **Blue**. Wi-Fi is ready!
   * 🌐 **Top Large LED:** Only turns on when an active Ethernet cable is plugged into the **WAN 2.5G** port.
4. **Log in to LuCI:**  
   Navigate to `http://192.168.76.1` and log in with username `root` and password `root0100`.

---

## 🔄 6. HOW TO RESET (3 LEVELS — REVERT UNLOCK & RETURN TO STOCK)

### 🟢 Level 1: Soft Reset (Restore Defaults while Keeping Unlock & LuCI)
*Use if you misconfigured Wi-Fi or network settings and want a fresh clean start with LuCI.*
* **How to do it:** Open the restore page and re-apply `cfg_restauracao_master_v2.cfg`.

---

### 🟡 Level 2: Hard Reset (Revert 100% Back to Factory Sealed Stock)
*Use if selling the unit or sending it in for warranty.*
* **How to do it:**
  1. With the router powered on, press and hold the physical **Reset** button on the back for **10 to 12 seconds** using a paperclip.
  2. The router wipes the overlay partition and boots into the stock locked Acer firmware.
  3. *(To unlock again in the future, simply repeat Section 5).*

---

### 🔴 Level 3: Hardware Emergency Mode (WPS Failsafe on IP `192.168.1.1` — Flash Stock ROM)
*Use if you completely broke networking and the router no longer responds on 192.168.76.1.*  
Because the **stock U-Boot is 100% intact**, the device is unbrickable:

> [!IMPORTANT]
> **Emergency Mode Requirements:**
> 1. **Ethernet Cable Required:** U-Boot failsafe has no Wi-Fi. The PC must be wired to a LAN port.
> 2. **Network Isolation (Prevent IP Conflicts):** Connect PC directly to the T7. Unplug other modems/routers using `192.168.1.1`.
> 3. **Incognito Browser:** Use private browsing mode to bypass cached pages.

#### Steps to Re-flash Stock ROM:
1. Unplug power.
2. Hold down the **WPS** button on the router.
3. Plug in power while holding **WPS for 8 to 10 seconds** until the LED flashes in recovery rhythm.
4. Set PC static IP: `192.168.1.50`, subnet `255.255.255.0`, gateway `192.168.1.1`.
5. Open browser incognito at `http://192.168.1.1`.
6. Upload the official Acer firmware image:  
   👉 **`recovery_stock/nand-4k-ipq5332-single_101000027.img`** *(v27 recommended)*.
7. Click **Upgrade** and wait for automatic reboot. Set PC back to DHCP.

---

## 🛠️ 7. DEV LEVEL: BOOT SLOT SWITCHING (ADVANCED)

> [!WARNING]
> **Developers Only:** Standard users do not need this section.

* **Slot 1 (`mtd21`):** Stock OEM Protected Firmware.
* **Slot 2 (`mtd20`):** OpenWrt Custom with LuCI.

### Slot Switching via U-Boot Web Failsafe (`http://192.168.1.1`):
In U-Boot recovery mode (holding WPS during boot), access `http://192.168.1.1` in an incognito window and upload the desired `.bin` file from the `dev/` directory:
* **To force boot into Slot 1 (Stock OEM):** Upload 👉 **`dev/chaveador_slot1_acer_oem.bin`**
* **To force boot into Slot 2 (OpenWrt Custom):** Upload 👉 **`dev/chaveador_slot2_openwrt.bin`**

### When Router is Unlocked (SSH / Telnet):
No file uploading or complex partition commands required. Once logged in via SSH (`port 22`) or Telnet (`port 23`), simply run the built-in system commands:
* **To switch to Slot 1 (Stock OEM):**
  ```sh
  /usr/sbin/boot-acer
  ```
* **To switch to Slot 2 (OpenWrt Custom):**
  ```sh
  /usr/sbin/boot-openwrt
  ```
*The command automatically writes the bootconfig to flash and reboots into the designated slot.*

---

## 📡 8. COMMUNITY CALL: PREDATOR X7 (5G CPE) OWNERS

> [!IMPORTANT]
> If you own an **Acer Predator Connect X7 (5G CPE)**, help the project by sharing a clean factory backup (`.cfg`) taken after a fresh reset and first-run wizard setup!  
>  
> * **How to contribute:**  
>   1. Perform a clean factory reset on your X7.  
>   2. Complete the initial web setup wizard.  
>   3. Download your backup `.cfg` under `System` ➔ `Backup & restore`.  
>   4. Share it with us through either channel:  
>      * 👉 **Open a GitHub Issue:** [Project Issues](https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/issues)  
>      * 👉 **OpenWrt Forum:** Post or PM via the [Official Thread](https://forum.openwrt.org/t/research-guide-acer-predator-connect-t7-qualcomm-ipq5332-wi-fi-7-root-shell-unlock-2-5gbps-ap-mode-mtd-backups/254042)  
> * **Why this matters:**  
>   The X7 features the same SoC but houses an M.2 Snapdragon X62 5G modem. A clean backup allows us to map the firmware partitions and deliver a custom suite for the X7 with the same precision as the T7!

---

## 🤝 9. SPECIAL THANKS & CREDITS

* 🏆 **Special Thanks to [Diego Augusto (BESTYALL)](https://forum.openwrt.org/u/bestyall):**  
  Heartfelt gratitude to **[Diego Augusto](https://forum.openwrt.org/u/bestyall)** for his pioneer dedication and for fearlessly risking his own physical hardware during the early stages of this project. His comprehensive bench tests, real-time feedback, and detailed issue reports were instrumental in perfecting and finalizing this unlock solution!

* 🌐 **100% Organized and Localized Languages:**  
  Thanks to ongoing tests and community feedback, the ROM features cleanly integrated translations. LuCI and all custom **Smart Wi-Fi Center** menus are 100% translated and aligned in **Portuguese (Brazil)**, **English**, and **Spanish**, delivering a native and frictionless Wi-Fi 7 tuning experience.

---

<p align="center">
  <b>Developed by the OpenWrt Community & Independent Reverse Engineering</b><br>
  MIT License — Free to use, study, and improve.
</p>
