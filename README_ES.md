<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

<p align="center">
  <b>🌐 Idioma / Language:</b>
  <a href="README_PT.md">🇧🇷 Português (Brasil)</a> |
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_ES.md"><b>🇪🇸 Español</b></a>
</p>

# Acer Predator Connect T7 — Desbloqueo Root, LuCI Nativo, Wi-Fi 7 y Guía de Restablecimiento de Fábrica

> **Estado del Proyecto (Octubre / 2026)**: Desbloqueo instantáneo en 1 minuto mediante restauración maestra nativa (`cfg_restauracao_master_v2.cfg`). Firmware oficial de Acer con **interfaz web LuCI nativa en el puerto 80**, **Wi-Fi 7 (320 MHz / 5.76 Gbps)**, Roaming Rápido 802.11k/v, **Centro de Wi-Fi Inteligente**, UPnP optimizado y debloat total de telemetrías. **Slot 1 (`rootfs`) y U-Boot conservados 100% intactos de fábrica como salvaguarda definitiva anti-brick**.

> ⚠️ **AVISO CRÍTICO**: Realice siempre la configuración con el ordenador conectado mediante **cable de red Ethernet** directamente a uno de los puertos LAN del router. No realice el procedimiento a través de Wi-Fi para evitar desconexiones en medio del proceso.

---

## ⚡ 1. RECOMENDACIÓN PREVIA: ESTAR EN LA VERSIÓN v27
> [!TIP]
> **Recomendación Importante:**  
> Asegúrese de que su router esté actualizado a la versión oficial **v1.01.000027 (v27)** antes de aplicar el desbloqueo. La versión v27 incluye las calibraciones de radio Wi-Fi 7 más recientes, soporte completo para canales de 320 MHz y correcciones críticas en el kernel Qualcomm.

---

## 🎁 2. BENEFICIOS DEL DESBLOQUEO (¿POR QUÉ DESBLOQUEAR?)

1. 🔓 **Acceso Root y SSH Nativo en la LAN:** Puertos `22` (SSH) y `23` (Telnet) liberados en la red local sin bloqueos de Acer.
2. 🌐 **Interfaz LuCI Oficial de OpenWrt Completa:** Panel completo en el puerto 80 con control total de firewall, DHCP, rutas, VLANs y diagnósticos de procesos.
3. 🚀 **Wi-Fi 7 Totalmente Desbloqueado:** Banda de 6 GHz con ancho de banda máximo de **320 MHz (5.76 Gbps)**, Roaming Rápido 802.11k/v y WPA3-SAE.
4. 🎛️ **Centro de Wi-Fi Inteligente:** Exclusivo con ajustes y liberación máxima de los recursos del Wi-Fi, fácil e intuitivo. ¡Permite modificar configuraciones y guardar todas las frecuencias juntas con un solo clic!
5. 🛡️ **Blindaje Anti-Deadlock:** Eliminación definitiva de los módulos defectuosos de Qualcomm (`whc` y `wsplc`) que provocaban concurrencia interna e inestabilidad en el Wi-Fi.
6. 🧹 **Debloat Máximo:** Desactivación de telemetrías invasivas y servicios celulares innecesarios heredados del modelo X7, liberando **más de 50 MB de memoria RAM**.
7. 🎮 **UPnP / NAT-PMP para Juegos:** Apertura automática de puertos para PS5, Xbox, Switch y PC con NAT Abierta/Moderada y menor latencia.
8. 🛡️ **Seguridad Total Anti-Brick:** El Slot 1 y el U-Boot permanecen **100% de fábrica intactos**, con retorno garantizado en cualquier momento: ¡haciendo el reset desde OpenWrt o mediante el botón físico vuelve de inmediato al estado de fábrica!
9. 🌐 **Idiomas 100% Organizados:** Interfaz LuCI y todos los nuevos menús personalizados del Centro de Wi-Fi perfectamente localizados y alineados en **Portugués (Brasil)**, **Inglés** y **Español**, sin textos cortados ni confusos.

---

## 🛑 3. AVISO CRÍTICO: ¡NUNCA RESTAURE COPIAS DE SEGURIDAD ANTIGUAS!

> [!CAUTION]
> ### ⚠️ REGLA DE ORO TRAS EL DESBLOQUEO:
> **Tras desbloquear el router aplicando nuestro paquete maestro, ¡NUNCA restaure ninguna copia de seguridad (`.cfg`) antigua realizada antes del desbloqueo!**  
> Si restaura una copia de seguridad antigua de la interfaz oficial de Acer, se **sobrescribirá la configuración, se borrarán los módulos de LuCI, se eliminará el panel de Wi-Fi y se volverán a bloquear los puertos SSH y Telnet**.  
>  
> 👉 **Cómo personalizar su red:**  
> Si desea cambiar el nombre del Wi-Fi, poner su propia contraseña o cambiar rangos de IP, **hágalo siempre manualmente desde la pantalla de LuCI después del desbloqueo**.

---

## 🔑 4. CREDENCIALES Y DATOS PREDETERMINADOS TRAS LA RESTAURACIÓN

| Parámetro | Configuración Predeterminada |
| :--- | :--- |
| **Dirección IP LAN** | **`192.168.76.1`** |
| **Interfaz Web (Puerto 80)** | **`http://192.168.76.1/`** (OpenWrt LuCI) |
| **Usuario Web / SSH** | **`root`** (o **`admin`**) |
| **Contraseña Maestra Unificada** | **`root0100`** *(Web, SSH y Telnet)* |
| **Archivo del Paquete Maestro** | **`cfg_restauracao_master_v2.cfg`** *(en la raíz)* |
| **Red Wi-Fi 2.4 GHz** | **`PREDATOR T7_2.4GHz`** |
| **Red Wi-Fi 5 GHz** | **`PREDATOR T7_5GHz`** |
| **Red Wi-Fi 6 GHz (Wi-Fi 7)** | **`PREDATOR T7_6GHz`** |
| **Contraseña Wi-Fi (todas las redes)** | **`123456789`** |

---

## 🚀 5. PASO A PASO DE LA INSTALACIÓN (1 MINUTO)

> ⚠️ **Conecte el ordenador mediante cable de red Ethernet al puerto LAN del T7. No lo haga por Wi-Fi.**

1. **Acceda a la Pantalla Directa de Restauración OEM:**  
   Abra el navegador y pegue:
   ```text
   https://192.168.76.1/pub/dist/index.html#/system/backRestore
   ```
   *(O navegue: inicie sesión ➔ Menú lateral izquierdo `System` ➔ `Backup & restore`)*.
2. **Cargue el Archivo Maestro:**  
   En la sección inferior **Restore**:
   * Haga clic en **`Browse`** (o Seleccionar archivo) y elija:  
     `cfg_restauracao_master_v2.cfg`
   * Haga clic en el botón **`Restore`**.
3. **Observe las Luces LED Durante el Arranque:**
   * 🔴 **LED Frontal Rojo:** ¡Es **normal** en el primer arranque! El chip Qualcomm calibra las radios y cumple los **60 segundos obligatorios de escucha de radar DFS (CAC)** en la banda de 5 GHz. Espere aproximadamente **2 minutos y 25 segundos**.
   * 🔵 **LED Frontal Azul:** Tan pronto como las 3 radios estén activas, la luz frontal cambia a **Azul**. ¡El Wi-Fi está listo para usar!
   * 🌐 **LED Superior Mayor:** Solo se enciende cuando conecta el cable de internet al puerto **WAN 2.5G**.
4. **Entre a la Nueva Interfaz LuCI:**  
   Acceda a `http://192.168.76.1` e inicie sesión con usuario `root` y contraseña `root0100`.

---

## 🔄 6. CÓMO RESTABLECER / RESETEAR (3 NIVELES — ANULAR DESBLOQUEO Y VOLVER A STOCK)

### 🟢 Nivel 1: Soft Reset (Restaurar manteniendo el Desbloqueo y LuCI)
*Utilícelo si desconfiguró el Wi-Fi o la red y desea volver al estado limpio y optimizado del proyecto.*
* **Cómo hacerlo:** Acceda a la pantalla de restauración y vuelva a aplicar el archivo `cfg_restauracao_master_v2.cfg`. El router reiniciará con LuCI y Wi-Fi 7 calibrados.

---

### 🟡 Nivel 2: Hard Reset (Restablecer 100% de Fábrica como vino de Tienda)
*Utilícelo si va a vender el router o enviarlo a garantía de Acer.*
* **Cómo hacerlo:**
  1. Con el router encendido, mantenga presionado el botón **Reset** en la parte trasera durante **10 a 12 segundos** con un clip.
  2. El router borrará la partición de datos (`overlay`) y reiniciará en el firmware original bloqueado de fábrica de Acer.
  3. *(Para desbloquear nuevamente en el futuro, simplemente repita la Sección 5 de esta guía).*

---

### 🔴 Nivel 3: Modo de Emergencia de Hardware (WPS Failsafe en la IP `192.168.1.1` — Reinstalar ROM Oficial Stock)
*Utilícelo en caso de que bloquee la red y el router ya no responda en la IP 192.168.76.1.*  
Dado que el **U-Boot original de Acer está 100% intacto**, el dispositivo nunca sufre brick permanente. En esta pantalla de bajo nivel puede regrabar la **ROM Oficial Stock completa del fabricante** directamente en la memoria flash:

> [!IMPORTANT]
> **Precauciones Obligatorias para el Modo de Emergencia:**
> 1. **Cable de Red Obligatorio:** El modo U-Boot de emergencia no dispone de Wi-Fi. El ordenador DEBE estar conectado por cable de red al puerto LAN del T7.
> 2. **Aislamiento de Red (Evitar Conflicto de IP):** Conecte el ordenador **directamente** al router T7. Desconecte otros módems u otros routers que puedan usar el rango `192.168.1.1`. Desactive también el Wi-Fi de su ordenador durante el proceso.
> 3. **Navegador en Modo Incógnito:** Utilice una ventana de navegación privada (o limpie la caché del navegador) para evitar que páginas antiguas interfieran.

#### Pasos para Subir la ROM Oficial:
1. Desconecte la fuente de alimentación de la toma de corriente.
2. Mantenga presionado el botón físico **WPS** en la carcasa del T7.
3. Conecte la fuente de alimentación manteniendo presionado el botón **WPS durante 8 a 10 segundos** hasta que el LED parpadee en ritmo de recuperación.
4. En su ordenador, configure la IP manual de su tarjeta de red Ethernet en:  
   * **Dirección IP:** `192.168.1.50`  
   * **Máscara de subred:** `255.255.255.0`  
   * **Puerta de enlace:** `192.168.1.1`  
5. Abra el navegador en modo incógnito y acceda a:
   ```text
   http://192.168.1.1
   ```
6. En la página web de emergencia de Acer (U-Boot Web Recovery):
   * Haga clic en el campo de selección de archivo.
   * Seleccione el archivo de imagen de la ROM Stock oficial de Acer:  
     👉 **`01_FIRMWARES_E_IMAGENS/Stock_OEM_Recovery/nand-4k-ipq5332-single_101000027.img`** *(Versión v27 recomendada)*  
     *(o `nand-4k-ipq5332-single_101000024.img` si desea la versión v24)*.
   * Haga clic en **Upload / Upgrade**.
   * La grabación avanzará escribiendo directamente en la memoria flash NAND. Espere a que concluya el proceso y el router reinicie por sí solo.
7. Vuelva a configurar la tarjeta de red de su ordenador en "Obtener dirección IP automáticamente (DHCP)". El router volverá a responder en la IP oficial `192.168.76.1` 100% original de fábrica.

---

## 🛠️ 7. NIVEL DEV: CAMBIO DE SLOTS DE BOOT (AVANZADO)

> [!WARNING]
> **Exclusivo para Desarrolladores:** Los usuarios estándar no necesitan esta sección.

El Acer Predator Connect T7 cuenta con particionamiento A/B dual en la memoria NAND:
* **Slot 1 (`rootfs` / `mtd21`):** Firmware de fábrica OEM protegido.
* **Slot 2 (`rootfs_1` / `mtd20`):** Firmware OpenWrt Personalizado con LuCI.

### Cambio de Slots mediante U-Boot Web Failsafe (`http://192.168.1.1`):
En el modo de recuperación U-Boot (manteniendo presionado WPS al encender), acceda a `http://192.168.1.1` en una ventana de incógnito y suba el archivo binario deseado de la carpeta `dev/`:
* **Para forzar el arranque en el Slot 1 (OEM de Fábrica):** Suba 👉 **`dev/chaveador_slot1_acer_oem.bin`**
* **Para forzar el arranque en el Slot 2 (OpenWrt Custom):** Suba 👉 **`dev/chaveador_slot2_openwrt.bin`**

### Cuando el router ya esté desbloqueado (SSH / Telnet):
No es necesario subir archivos ni introducir comandos complejos de partición. Al estar conectado mediante SSH (`puerto 22`) o Telnet (`puerto 23`), simplemente ejecute los comandos nativos integrados en el sistema:
* **Para alternar al Slot 1 (OEM de Fábrica):**
  ```sh
  /usr/sbin/boot-acer
  ```
* **Para alternar al Slot 2 (OpenWrt Custom):**
  ```sh
  /usr/sbin/boot-openwrt
  ```
*El comando escribe automáticamente la configuración de arranque en la flash y reinicia el router en el slot seleccionado.*

---

## 📡 8. LLAMADA A LA COMUNIDAD: MODELO PREDATOR X7 (5G CPE)

> [!IMPORTANT]
> ### 🤝 ¿Posee el modelo Acer Predator Connect X7?
> ¡Ayude a la comunidad enviando una copia de seguridad de su dispositivo!  
> 
> * **Cómo colaborar:**  
>   1. En su Predator X7, realice un restablecimiento de fábrica limpio.  
>   2. Complete la configuración inicial en el panel web.  
>   3. Vaya a la pantalla de copias de seguridad (`System` ➔ `Backup & restore`) y descargue el archivo `.cfg`.  
>   4. Envíenos el archivo a través de uno de los canales de la comunidad:  
>      * 👉 **Abriendo una Issue en GitHub:** [GitHub Issues del Proyecto](https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/issues)  
>      * 👉 **En el Foro de OpenWrt:** Respondiendo o enviando un mensaje privado en el [Hilo Oficial del Proyecto](https://forum.openwrt.org/t/research-guide-acer-predator-connect-t7-qualcomm-ipq5332-wi-fi-7-root-shell-unlock-2-5gbps-ap-mode-mtd-backups/254042)  
> * **¿Por qué es importante?**  
>   El X7 comparte el mismo procesador que el T7, pero incorpora un módem celular 5G M.2 (Snapdragon X62). Con su copia de seguridad limpia, podremos mapear las particiones y crear una suite personalizada a la medida para el modelo X7 con la misma precisión que la del T7.

---

## 🤝 9. AGRADECIMIENTOS ESPECIALES Y CRÉDITOS

* 🏆 **Agradecimiento Especial a [Diego Augusto (BESTYALL)](https://forum.openwrt.org/u/bestyall):**  
  Un agradecimiento fundamental a **[Diego Augusto](https://forum.openwrt.org/u/bestyall)** por su valentía y dedicación pionera al arriesgar su propio router físico en las fases iniciales del proyecto. ¡Sus exhaustivas pruebas de laboratorio, informes de comportamiento en tiempo real y detallados comentarios fueron piezas clave para el perfeccionamiento y la maduración definitiva de esta solución de desbloqueo!

* 🌐 **Idiomas 100% Organizados y Localizados:**  
  Gracias a las continuas pruebas y aportaciones de la comunidad, la ROM cuenta ahora con todos los idiomas perfectamente organizados e integrados. La interfaz LuCI y todos los nuevos menús personalizados del **Centro de Wi-Fi Inteligente** están 100% traducidos y adaptados en **Portugués (Brasil)**, **Inglés** y **Español**, garantizando una experiencia nativa, clara e intuitiva para configurar cada detalle de Wi-Fi 7 sin textos cortados ni términos faltantes.

---

<p align="center">
  <b>Desarrollado por la Comunidad OpenWrt e Ingeniería Inversa Independiente</b><br>
  Licencia MIT — Libre para uso, estudio y mejora.
</p>
